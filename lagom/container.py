import functools
import io
import logging
import typing

from .compilaton import mypyc_attr

from types import FunctionType, MethodType
from typing import (
    Dict,
    Type,
    Any,
    TypeVar,
    Callable,
    Set,
    List,
    Optional,
    cast,
    Union,
)

from .definitions import (
    normalise,
    Singleton,
    Alias,
    ConstructionWithoutContainer,
    UnresolvableTypeDefinition,
)
from .exceptions import (
    UnresolvableType,
    DuplicateDefinition,
    InvalidDependencyDefinition,
    RecursiveDefinitionError,
    DependencyNotDefined,
    TypeOnlyAvailableAsAwaitable,
    CircularDefinitionError,
)
from .interfaces import (
    SpecialDepDefinition,
    WriteableContainer,
    TypeResolver,
    DefinitionsSource,
    ExtendableContainer,
    ContainerDebugInfo,
    CallTimeContainerUpdate,
)
from .markers import injectable
from .updaters import update_container_singletons
from .util.logging import NullLogger
from .util.reflection import (
    FunctionSpec,
    CachingReflector,
    remove_optional_type,
    remove_awaitable_type,
)
from .wrapping import apply_argument_updater

UNRESOLVABLE_TYPES = [
    str,
    int,
    float,
    bool,
    bytes,
    bytearray,
    io.BytesIO,
    io.BufferedIOBase,
    io.BufferedRandom,
    io.BufferedReader,
    io.BufferedRWPair,
    io.BufferedWriter,
    io.FileIO,
    io.IOBase,
    io.RawIOBase,
    io.TextIOBase,
    typing.IO,
    typing.TextIO,
    typing.BinaryIO,
]

X = TypeVar("X")

Unset: Any = object()


@mypyc_attr(allow_interpreted_subclasses=True)
class Container(
    WriteableContainer, ExtendableContainer, DefinitionsSource, ContainerDebugInfo
):
    """Dependency injection container

    Lagom is a dependency injection container designed to give you "just enough"
    help with building your dependencies. The intention is that almost
    all of your code doesn't know about or rely on lagom. Lagom will
    only be involved at the top level to pull everything together.

    >>> from tests.examples import SomeClass
    >>> c = Container()
    >>> c[SomeClass]
    <tests.examples.SomeClass object at ...>

    Objects are constructed as they are needed

    >>> from tests.examples import SomeClass
    >>> c = Container()
    >>> first = c[SomeClass]
    >>> second = c[SomeClass]
    >>> first != second
    True

    And construction logic can be defined
    >>> from tests.examples import SomeClass, SomeExtendedClass
    >>> c = Container()
    >>> c[SomeClass] = SomeExtendedClass
    >>> c[SomeClass]
    <tests.examples.SomeExtendedClass object at ...>
    """

    _registered_types: Dict[Type, SpecialDepDefinition]
    _parent_definitions: DefinitionsSource
    _reflector: CachingReflector
    _undefined_logger: logging.Logger

    def __init__(
        self,
        container: Optional["Container"] = None,
        log_undefined_deps: Union[bool, logging.Logger] = False,
    ):
        """
        :param container: Optional container if provided the existing definitions will be copied
        :param log_undefined_deps indicates if a log message should be emmited when an undefined dep is loaded
        """

        # ContainerDebugInfo is always registered
        # This means consumers can consume an overview of the container
        # without hacking anything custom together.
        self._registered_types = {
            ContainerDebugInfo: ConstructionWithoutContainer(lambda: self)
        }

        if container:
            self._parent_definitions = container
            self._reflector = container._reflector
        else:
            self._parent_definitions = EmptyDefinitionSet()
            self._reflector = CachingReflector()

        if not log_undefined_deps:
            self._undefined_logger = NullLogger()
        elif log_undefined_deps is True:
            self._undefined_logger = logging.getLogger(__name__)
        else:
            self._undefined_logger = cast(logging.Logger, log_undefined_deps)

    def define(self, dep: Type[X], resolver: TypeResolver[X]) -> SpecialDepDefinition:
        """Register how to construct an object of type X

        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> c.define(SomeClass, lambda: SomeClass())
        <lagom.definitions.ConstructionWithoutContainer ...>

        :param dep: The type to be constructed
        :param resolver: A definition of how to construct it
        :return:
        """
        if dep in UNRESOLVABLE_TYPES:
            raise InvalidDependencyDefinition()
        if dep in self._registered_types:
            raise DuplicateDefinition()
        if dep is resolver:
            # This is a special case for things like container[Foo] = Foo
            return self.define(dep, Alias(dep, skip_definitions=True))
        definition = normalise(resolver)
        self._registered_types[dep] = definition
        self._registered_types[Optional[dep]] = definition  # type: ignore

        # For awaitables we add a convenience exception to be thrown if code hints on the type
        # without the awaitable.
        awaitable_type = remove_awaitable_type(dep)
        if awaitable_type:
            # Unless there's already a sync version defined.
            if awaitable_type not in self.defined_types:
                self._registered_types[awaitable_type] = UnresolvableTypeDefinition(
                    TypeOnlyAvailableAsAwaitable(awaitable_type), awaitable_type
                )
        return definition

    @property
    def defined_types(self) -> Set[Type]:
        """The types the container has explicit build instructions for

        :return:
        """
        return self._parent_definitions.defined_types.union(
            self._registered_types.keys()
        )

    @property
    def reflection_cache_overview(self) -> Dict[str, str]:
        return self._reflector.overview_of_cache

    def temporary_singletons(
        self, singletons: Optional[List[Type]] = None
    ) -> "_TemporaryInjectionContext":
        """
        Returns a context that loads a new container with singletons that only exist
        for the context.

        >>> from tests.examples import SomeClass
        >>> base_container = Container()
        >>> def my_func():
        ...     with base_container.temporary_singletons([SomeClass]) as c:
        ...         assert c[SomeClass] is c[SomeClass]
        >>> my_func()

        :param singletons: items which should be considered singletons within the context
        :return:
        """
        updater = (
            functools.partial(update_container_singletons, singletons=singletons)
            if singletons
            else None
        )
        return _TemporaryInjectionContext(self, updater)

    def resolve(
        self, dep_type: Type[X], suppress_error=False, skip_definitions=False
    ) -> X:
        """Constructs an object of type X

         If the object can't be constructed an exception will be raised unless
         supress errors is true

        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> c.resolve(SomeClass)
        <tests.examples.SomeClass object at ...>

        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> c.resolve(int)
        Traceback (most recent call last):
        ...
        lagom.exceptions.UnresolvableType: ...

        Optional wrappers are stripped out to be what is being asked for
        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> c.resolve(Optional[SomeClass])
        <tests.examples.SomeClass object at ...>

        :param dep_type: The type of object to construct
        :param suppress_error: if true returns None on failure
        :param skip_definitions:
        :return:
        """
        return self._resolve(
            dep_type, suppress_error, skip_definitions, type_stack=set()
        )

    def _resolve(
        self,
        dep_type: Type[X],
        suppress_error=False,
        skip_definitions=False,
        default: X = Unset,
        type_stack: Optional[Set[Type]] = None,
    ) -> X:
        if not skip_definitions:
            definition = self.get_definition(dep_type)
            if definition:
                return definition.get_instance(self)

        optional_dep_type = remove_optional_type(dep_type)
        if optional_dep_type:
            return self.resolve(optional_dep_type, suppress_error=True)

        return self._reflection_build_with_err_handling(
            dep_type, suppress_error, default=default, type_stack=type_stack
        )

    def partial(
        self,
        func: Callable[..., X],
        shared: Optional[List[Type]] = None,
        container_updater: Optional[CallTimeContainerUpdate] = None,
    ) -> Callable[..., X]:
        """Takes a callable and returns a callable bound to the container
        When invoking the new callable if any arguments have a default set
        to the special marker object "injectable" then they will be constructed by
        the container. For automatic injection without the marker use "magic_partial"
        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> def my_func(something: SomeClass = injectable):
        ...     return f"Successfully called with {something}"
        >>> bound_func = c.magic_partial(my_func)
        >>> bound_func()
        'Successfully called with <tests.examples.SomeClass object at ...>'

        :param func: the function to bind to the container
        :param shared: items which should be considered singletons on a per call level
        :param container_updater: An optional callable to update the container before resolution
        :return:
        """
        spec = self._get_spec_without_self(func)
        keys_to_bind = (
            key for (key, arg) in spec.defaults.items() if arg is injectable
        )
        keys_and_types = [(key, spec.annotations[key]) for key in keys_to_bind]

        _injection_context = self.temporary_singletons(shared)
        update_container = container_updater if container_updater else _update_nothing

        def _update_args(supplied_args, supplied_kwargs):
            keys_to_skip = set(supplied_kwargs.keys())
            keys_to_skip.update(spec.args[0 : len(supplied_args)])
            with _injection_context as invocation_container:
                update_container(invocation_container, supplied_args, supplied_kwargs)
                kwargs = {
                    key: invocation_container.resolve(dep_type)
                    for (key, dep_type) in keys_and_types
                    if key not in keys_to_skip
                }
            kwargs.update(supplied_kwargs)
            return supplied_args, kwargs

        return apply_argument_updater(func, _update_args, spec)

    def magic_partial(
        self,
        func: Callable[..., X],
        shared: Optional[List[Type]] = None,
        keys_to_skip: Optional[List[str]] = None,
        skip_pos_up_to: int = 0,
        container_updater: Optional[CallTimeContainerUpdate] = None,
    ) -> Callable[..., X]:
        """Takes a callable and returns a callable bound to the container
        When invoking the new callable if any arguments can be constructed by the container
        then they can be ommited.
        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> def my_func(something: SomeClass):
        ...   return f"Successfully called with {something}"
        >>> bound_func = c.magic_partial(my_func)
        >>> bound_func()
        'Successfully called with <tests.examples.SomeClass object at ...>'

        :param func: the function to bind to the container
        :param shared: items which should be considered singletons on a per call level
        :param keys_to_skip: named arguments which the container shouldnt build
        :param skip_pos_up_to: positional arguments which the container shouldnt build
        :param container_updater: An optional callable to update the container before resolution
        :return:
        """
        spec = self._get_spec_without_self(func)

        update_container = container_updater if container_updater else _update_nothing
        _injection_context = self.temporary_singletons(shared)

        def _update_args(supplied_args, supplied_kwargs):
            final_keys_to_skip = (keys_to_skip or []) + list(supplied_kwargs.keys())
            final_skip_pos_up_to = max(skip_pos_up_to, len(supplied_args))
            with _injection_context as invocation_container:
                update_container(invocation_container, supplied_args, supplied_kwargs)
                kwargs = invocation_container._infer_dependencies(
                    spec,
                    suppress_error=True,
                    keys_to_skip=final_keys_to_skip,
                    skip_pos_up_to=final_skip_pos_up_to,
                )
            kwargs.update(supplied_kwargs)
            return supplied_args, kwargs

        return apply_argument_updater(func, _update_args, spec, catch_errors=True)

    def clone(self) -> "Container":
        """returns a copy of the container
        :return:
        """
        return Container(self, log_undefined_deps=self._undefined_logger)

    def get_definition(self, dep_type: Type[X]) -> Optional[SpecialDepDefinition[X]]:
        """
        Will return the definition in this container. If none has been defined any
        definition in the parent container will be used.

        :param dep_type:
        :return:
        """
        definition = self._registered_types.get(dep_type, Unset)
        if definition is Unset:
            return self._parent_definitions.get_definition(dep_type)
        return definition

    def __getitem__(self, dep: Type[X]) -> X:
        return self.resolve(dep)

    def __setitem__(self, dep: Type[X], resolver: TypeResolver[X]):
        self.define(dep, resolver)

    def _reflection_build_with_err_handling(
        self,
        dep_type: Type[X],
        suppress_error: bool,
        *,
        default: X = Unset,
        type_stack: Optional[Set[Type]] = None,
    ) -> X:
        try:
            return self._reflection_build(
                dep_type, default=default, type_stack=type_stack
            )
        except UnresolvableType as inner_error:
            if not suppress_error:
                raise UnresolvableType(dep_type) from inner_error
            return None  # type: ignore
        except RecursionError as recursion_error:
            raise RecursiveDefinitionError(dep_type) from recursion_error

    def _reflection_build(
        self,
        dep_type: Type[X],
        *,
        default: X = Unset,
        type_stack: Optional[Set[Type]] = None,
    ) -> X:
        type_stack = set(type_stack or [])
        if dep_type in type_stack:
            raise CircularDefinitionError(dep_type, type_stack)
        type_stack.add(dep_type)
        self._undefined_logger.warning(
            f"Undefined dependency. Using reflection for {dep_type}",
            extra={"undefined_dependency": dep_type},
        )
        spec = self._reflector.get_function_spec(dep_type.__init__)
        if dep_type in UNRESOLVABLE_TYPES:
            if default is not Unset:
                return default
            raise UnresolvableType(dep_type)
        sub_deps = self._infer_dependencies(
            spec, types_to_skip={dep_type}, type_stack=type_stack
        )
        try:
            return dep_type(**sub_deps)  # type: ignore
        except TypeError as type_error:
            raise UnresolvableType(dep_type) from type_error

    def _infer_dependencies(
        self,
        spec: FunctionSpec,
        suppress_error=False,
        keys_to_skip: Optional[List[str]] = None,
        skip_pos_up_to=0,
        types_to_skip: Optional[Set[Type]] = None,
        type_stack: Optional[Set[Type]] = None,
    ):
        dep_keys_to_skip: List[str] = []
        dep_keys_to_skip.extend(spec.args[0:skip_pos_up_to])
        dep_keys_to_skip.extend(keys_to_skip or [])
        types_to_skip = types_to_skip or set()
        sub_deps = {
            key: self._resolve(
                sub_dep_type,
                suppress_error=suppress_error,
                default=spec.defaults.get(key, Unset),
                type_stack=type_stack,
            )
            for (key, sub_dep_type) in spec.annotations.items()
            if sub_dep_type != Any
            and (key not in dep_keys_to_skip)
            and (sub_dep_type not in types_to_skip)
        }
        return {key: dep for (key, dep) in sub_deps.items() if dep is not None}

    def _get_spec_without_self(self, func: Callable[..., X]) -> FunctionSpec:
        if isinstance(func, (FunctionType, MethodType)):
            return self._reflector.get_function_spec(func)
        t = cast(Type[X], func)
        return self._reflector.get_function_spec(t.__init__).without_argument("self")


@mypyc_attr(allow_interpreted_subclasses=True)
class ExplicitContainer(Container):
    def resolve(
        self, dep_type: Type[X], suppress_error=False, skip_definitions=False
    ) -> X:
        definition = self.get_definition(dep_type)
        if not definition:
            if suppress_error:
                return None  # type: ignore
            raise DependencyNotDefined(dep_type)
        return definition.get_instance(self)

    def define(self, dep, resolver):
        definition = super().define(dep, resolver)
        if isinstance(definition, Alias):
            raise InvalidDependencyDefinition(
                "Aliases are not valid in an explicit container"
            )
        if isinstance(definition, Singleton) and isinstance(
            definition.singleton_type, Alias
        ):
            raise InvalidDependencyDefinition(
                "Aliases are not valid inside singletons in an explicit container"
            )
        return definition

    def clone(self):
        """returns a copy of the container
        :return:
        """
        return ExplicitContainer(self, log_undefined_deps=self._undefined_logger)


class EmptyDefinitionSet(DefinitionsSource):
    """
    Represents the starting state for a collection of dependency definitions
    i.e. None and everything has to be built with reflection
    """

    def get_definition(self, dep_type: Type[X]) -> Optional[SpecialDepDefinition[X]]:
        """
        No types are defined in the empty set
        :param dep_type:
        :return:
        """
        return None

    @property
    def defined_types(self) -> Set[Type]:
        return set()


class _TemporaryInjectionContext:
    _base_container: Container

    def __init__(
        self,
        container: Container,
        update_function: Optional[Callable[[Container], Container]] = None,
    ):
        self._base_container = container
        if update_function:
            self._build_temporary_container = lambda: update_function(
                self._base_container
            )
        else:
            self._build_temporary_container = lambda: self._base_container.clone()

    def __enter__(self) -> Container:
        return self._build_temporary_container()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def _update_nothing(_c: WriteableContainer, _a: typing.Collection, _k: Dict):
    return None
