import functools
from copy import copy
from typing import Dict, Type, Any, TypeVar, Callable, Set, List, Optional

from .interfaces import SpecialDepDefinition, ReadableContainer, TypeResolver
from .exceptions import (
    UnresolvableType,
    DuplicateDefinition,
    InvalidDependencyDefinition,
)
from .definitions import normalise, Singleton, construction
from .util.reflection import FunctionSpec, CachingReflector
from .wrapping import bound_function, wrap_func_in_error_handling

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

    def __init__(self, container: Optional["Container"] = None):
        """
        :param container: Optional container if provided the existing definitions will be copied
        """
        self._explicitly_registered_types = set()

        if container:
            self._registered_types = copy(container._registered_types)
            self._reflector = container._reflector
        else:
            self._registered_types = {}
            self._reflector = CachingReflector()

    def define(self, dep: Type[X], resolver: TypeResolver[X]) -> None:
        """Register how to construct an object of type X

        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> c.define(SomeClass, lambda: SomeClass())

        :param dep: The type to be constructed
        :param resolver: A definition of how to construct it
        :return:
        """
        if dep in UNRESOLVABLE_TYPES:
            raise InvalidDependencyDefinition()
        if dep in self._explicitly_registered_types:
            raise DuplicateDefinition()
        self._registered_types[dep] = normalise(resolver)
        self._explicitly_registered_types.add(dep)

    @property
    def defined_types(self) -> Set[Type]:
        """The types the container has explicit build instructions for

        :return:
        """
        return set(self._registered_types.keys())

    @property
    def reflection_cache_overview(self) -> Dict[str, str]:
        return self._reflector.overview_of_cache

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

    def partial(
        self,
        func: Callable[..., X],
        shared: List[Type] = None,
        keys_to_skip=None,
        skip_pos_up_to: int = 0,
    ) -> Callable[..., X]:
        """Takes a callable and returns a callable bound to the container
        When invoking the new callable if any arguments can be constructed by the container
        then they can be ommited.
        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> def my_func(something: SomeClass):
        ...   return f"Successfully called with {something}"
        >>> bound_func = c.partial(my_func)
        >>> bound_func()
        'Successfully called with <tests.examples.SomeClass object at ...>'

        :param func: the function to bind to the container
        :param shared: items which should be considered singletons on a per call level
        :param keys_to_skip: named arguments which the container shouldnt build
        :param skip_pos_up_to: positional arguments which the container shouldnt build
        :return:
        """
        if shared:
            container_loader = self._container_with_singletons_builder(shared)
        else:

            def container_loader():
                return self

        spec = self._reflector.get_function_spec(func)

        func_with_error_handling = wrap_func_in_error_handling(func, spec)

        def _bind_func(extra_keys_to_skip=None, extra_skip_pos_up_to=0):
            final_keys_to_skip = (keys_to_skip or []) + (extra_keys_to_skip or [])
            final_skip_pos_up_to = max(skip_pos_up_to, extra_skip_pos_up_to)
            bindable_deps = container_loader()._infer_dependencies(
                spec,
                suppress_error=True,
                keys_to_skip=final_keys_to_skip,
                skip_pos_up_to=final_skip_pos_up_to,
            )
            return functools.partial(func_with_error_handling, **bindable_deps)

        return bound_function(_bind_func, func)

    def clone(self):
        """ returns a copy of the container
        :return:
        """
        return Container(self)

    def __getitem__(self, dep: Type[X]) -> X:
        return self.resolve(dep)

    def __setitem__(self, dep: Type[X], resolver: TypeResolver[X]):
        self.define(dep, resolver)

    def _reflection_build(self, dep_type: Type[X]) -> X:
        spec = self._reflector.get_function_spec(dep_type.__init__)
        sub_deps = self._infer_dependencies(spec)
        try:
            return dep_type(**sub_deps)  # type: ignore
        except TypeError as type_error:
            raise UnresolvableType(dep_type) from type_error

    def _infer_dependencies(
        self,
        spec: FunctionSpec,
        suppress_error=False,
        keys_to_skip=None,
        skip_pos_up_to=0,
    ):
        supplied_arguments = spec.args[0:skip_pos_up_to]
        keys_to_skip = (keys_to_skip or []) + supplied_arguments
        sub_deps = {
            key: self.resolve(sub_dep_type, suppress_error=suppress_error)
            for (key, sub_dep_type) in spec.annotations.items()
            if sub_dep_type != Any and key not in keys_to_skip
        }
        filtered_deps = {key: dep for (key, dep) in sub_deps.items() if dep is not None}
        return filtered_deps

    def _container_with_singletons_builder(self, singletons: List[Type]):
        loaders = {dep: construction(lambda: self.resolve(dep)) for dep in singletons}

        def _clone_container():
            temp_container = self.clone()
            # For each of the shared dependencies resolve before invocation
            # and replace with a singleton
            for (dep, loader) in loaders.items():
                temp_container[dep] = Singleton(loader)
            return temp_container

        return _clone_container


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
