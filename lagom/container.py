import functools
import inspect
from copy import copy
from typing import Dict, Type, Any, TypeVar, Callable, Set, List, Optional

from .interfaces import SpecialDepDefinition, ReadableContainer, TypeResolver
from .exceptions import UnresolvableType, DuplicateDefinition
from .definitions import normalise, Singleton, Construction
from .util.reflection import RETURN_ANNOTATION
from .wrapping import bound_function

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

    def __init__(self, container: Optional["Container"] = None):
        """
        :param container: Optional container if provided the existing definitions will be copied
        """
        self._registered_types = {}
        self._explicitly_registered_types = set()
        if container:
            self._registered_types = copy(container._registered_types)

    def define(self, dep: Type[X], resolver: TypeResolver[X]) -> None:
        """Register how to construct an object of type X

        >>> from tests.examples import SomeClass
        >>> c = Container()
        >>> c.define(SomeClass, lambda: SomeClass())

        :param dep: The type to be constructed
        :param resolver: A definition of how to construct it
        :return:
        """
        if dep in self._explicitly_registered_types:
            raise DuplicateDefinition()
        self._registered_types[dep] = normalise(resolver)
        self._explicitly_registered_types.add(dep)

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

        :param dep_type: The type of object to construct
        :param suppress_error: if true returns None on failure
        :param skip_definitions:
        :return:
        """
        try:
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
        self, func: Callable[..., X], keys_to_skip=None, shared: List[Type] = None
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

        :param func:
        :param keys_to_skip:
        :param shared:
        :return:
        """
        if shared:
            return self._partial_with_shared_singletons(func, shared)
        spec = inspect.getfullargspec(func)

        def _bind_func():
            bindable_deps = self._infer_dependencies(
                spec, suppress_error=True, keys_to_skip=keys_to_skip or []
            )
            return functools.partial(func, **bindable_deps)

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
        spec = inspect.getfullargspec(dep_type.__init__)
        sub_deps = self._infer_dependencies(spec)
        try:
            return dep_type(**sub_deps)  # type: ignore
        except TypeError as type_error:
            raise UnresolvableType(dep_type) from type_error

    def _infer_dependencies(
        self, spec: inspect.FullArgSpec, suppress_error=False, keys_to_skip=None
    ):
        keys_to_skip = keys_to_skip or []
        sub_deps = {
            key: self.resolve(sub_dep_type, suppress_error=suppress_error)
            for (key, sub_dep_type) in spec.annotations.items()
            if key != RETURN_ANNOTATION
            and sub_dep_type != Any
            and key not in keys_to_skip
        }
        filtered_deps = {key: dep for (key, dep) in sub_deps.items() if dep is not None}
        return filtered_deps

    def _partial_with_shared_singletons(
        self, func: Callable[..., X], shared: List[Type]
    ):
        def _cloned_container():
            temp_container = self.clone()
            # For each of the shared dependencies resolve before invocation
            # and replace with a singleton
            for type_def in shared:
                temp_container[type_def] = Singleton(
                    Construction(lambda: self.resolve(type_def))
                )
            return temp_container

        def _bind_func():
            temp_container = _cloned_container()
            return temp_container.partial(func, shared=[])

        return bound_function(_bind_func, func)
