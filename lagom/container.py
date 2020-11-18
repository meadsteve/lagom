import functools
import logging
from copy import copy
from typing import (
    Dict,
    Type,
    Any,
    TypeVar,
    Callable,
    Set,
    List,
    Optional,
    Generic,
    cast,
    Union,
)

from .interfaces import SpecialDepDefinition, ReadableContainer, TypeResolver
from .exceptions import (
    UnresolvableType,
    DuplicateDefinition,
    InvalidDependencyDefinition,
    RecursiveDefinitionError,
)
from .markers import injectable
from .definitions import normalise, Singleton, construction
from .util.logging import NullLogger
from .util.reflection import FunctionSpec, CachingReflector
from .wrapping import apply_argument_updater

UNRESOLVABLE_TYPES = [str, int, float, bool]

X = TypeVar("X")


class Container(ReadableContainer):
    """ Dependency injection container

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
    _explicitly_registered_types: Set[Type]
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
        self._explicitly_registered_types = set()

        if container:
            self._registered_types = copy(container._registered_types)
            self._reflector = container._reflector
        else:
            self._registered_types = {}
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
        if dep in self._explicitly_registered_types:
            raise DuplicateDefinition()
        definition = normalise(resolver)
        self._registered_types[dep] = definition
        self._explicitly_registered_types.add(dep)
        return definition

    @property
    def defined_types(self) -> Set[Type]:
        """The types the container has explicit build instructions for

        :return:
        """
        return set(self._registered_types.keys())

    @property
    def reflection_cache_overview(self) -> Dict[str, str]:
        return self._reflector.overview_of_cache

    def temporary_singletons(
        self, singletons: List[Type] = None
    ) -> "_TemporaryInjectionContext[Container]":
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
            functools.partial(_update_container_singletons, singletons=singletons)
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
        try:
            optional_dep_type = _remove_optional_type(dep_type)
            if optional_dep_type:
                return self.resolve(optional_dep_type, suppress_error=True)
            if dep_type in UNRESOLVABLE_TYPES:
                raise UnresolvableType(dep_type)
            type_to_build = (
                self._registered_types.get(dep_type, dep_type)
                if not skip_definitions
                else dep_type
            )
            if isinstance(type_to_build, SpecialDepDefinition):
                return type_to_build.get_instance(self)
            return self._reflection_build(type_to_build)
        except UnresolvableType as inner_error:
            if not suppress_error:
                raise UnresolvableType(dep_type) from inner_error
            return None  # type: ignore
        except RecursionError as recursion_error:
            raise RecursiveDefinitionError(dep_type) from recursion_error

    def partial(
        self, func: Callable[..., X], shared: List[Type] = None,
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
        :return:
        """
        spec = self._reflector.get_function_spec(func)
        keys_to_bind = (
            key for (key, arg) in spec.defaults.items() if arg is injectable
        )
        keys_and_types = [(key, spec.annotations[key]) for key in keys_to_bind]

        _injection_context = self.temporary_singletons(shared)

        def _update_args(supplied_args, supplied_kwargs):
            keys_to_skip = set(supplied_kwargs.keys())
            keys_to_skip.update(spec.args[0 : len(supplied_args)])
            with _injection_context as c:
                kwargs = {
                    key: c.resolve(dep_type)
                    for (key, dep_type) in keys_and_types
                    if key not in keys_to_skip
                }
            kwargs.update(supplied_kwargs)
            return supplied_args, kwargs

        return apply_argument_updater(func, _update_args, spec)

    def magic_partial(
        self,
        func: Callable[..., X],
        shared: List[Type] = None,
        keys_to_skip: List[str] = None,
        skip_pos_up_to: int = 0,
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
        :return:
        """

        spec = self._reflector.get_function_spec(func)

        _injection_context = self.temporary_singletons(shared)

        def _update_args(supplied_args, supplied_kwargs):
            final_keys_to_skip = (keys_to_skip or []) + list(supplied_kwargs.keys())
            final_skip_pos_up_to = max(skip_pos_up_to, len(supplied_args))
            with _injection_context as c:
                kwargs = c._infer_dependencies(
                    spec,
                    suppress_error=True,
                    keys_to_skip=final_keys_to_skip,
                    skip_pos_up_to=final_skip_pos_up_to,
                )
            kwargs.update(supplied_kwargs)
            return supplied_args, kwargs

        return apply_argument_updater(func, _update_args, spec, catch_errors=True)

    def clone(self):
        """ returns a copy of the container
        :return:
        """
        return Container(self, log_undefined_deps=self._undefined_logger)

    def __getitem__(self, dep: Type[X]) -> X:
        return self.resolve(dep)

    def __setitem__(self, dep: Type[X], resolver: TypeResolver[X]):
        self.define(dep, resolver)

    def _reflection_build(self, dep_type: Type[X]) -> X:
        self._undefined_logger.warning(
            f"Undefined dependency. Using reflection for {dep_type}",
            extra={"undefined_dependency": dep_type},
        )
        spec = self._reflector.get_function_spec(dep_type.__init__)
        sub_deps = self._infer_dependencies(spec, types_to_skip={dep_type})
        try:
            return dep_type(**sub_deps)  # type: ignore
        except TypeError as type_error:
            raise UnresolvableType(dep_type) from type_error

    def _infer_dependencies(
        self,
        spec: FunctionSpec,
        suppress_error=False,
        keys_to_skip: List[str] = None,
        skip_pos_up_to=0,
        types_to_skip: Set[Type] = None,
    ):
        supplied_arguments = spec.args[0:skip_pos_up_to]
        keys_to_skip = (keys_to_skip or []) + supplied_arguments
        types_to_skip = types_to_skip or set()
        sub_deps = {
            key: self.resolve(sub_dep_type, suppress_error=suppress_error)
            for (key, sub_dep_type) in spec.annotations.items()
            if sub_dep_type != Any
            and (key not in keys_to_skip)
            and (sub_dep_type not in types_to_skip)
        }
        return {key: dep for (key, dep) in sub_deps.items() if dep is not None}


C = TypeVar("C", bound=ReadableContainer)


class _TemporaryInjectionContext(Generic[C]):

    _base_container: C

    def __init__(
        self, container: C, update_function: Optional[Callable[[C], C]] = None
    ):
        self._base_container = container
        if update_function:
            self._build_temporary_container = lambda: update_function(
                self._base_container
            )
        else:
            self._build_temporary_container = lambda: self._base_container

    def __enter__(self) -> C:
        return self._build_temporary_container()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def _remove_optional_type(dep_type):
    """ if the Type is Optional[T] returns T else None

    :param dep_type:
    :return:
    """
    try:
        # Hacky: an optional type has [T, None] in __args__
        if len(dep_type.__args__) == 2 and dep_type.__args__[1] == None.__class__:
            return dep_type.__args__[0]
    except:
        pass
    return None


def _update_container_singletons(container: Container, singletons: List[Type]):
    new_container = container.clone()
    loaders = {dep: construction(lambda: container.resolve(dep)) for dep in singletons}
    for (dep, loader) in loaders.items():
        new_container[dep] = Singleton(loader)
    return new_container
