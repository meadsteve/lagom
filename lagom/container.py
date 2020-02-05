import functools
import inspect
from copy import copy
from typing import Dict, Type, Union, Any, TypeVar, Callable, Set, List, Optional

from .interfaces import SpecialDepDefinition
from .exceptions import UnresolvableType, DuplicateDefinition
from .definitions import normalise, Singleton, Construction
from .util.reflection import RETURN_ANNOTATION

UNRESOLVABLE_TYPES = [str, int, float, bool]

X = TypeVar("X")

DepDefinition = Any


class Container:
    _registered_types: Dict[Type, SpecialDepDefinition]
    _explicitly_registered_types: Set[Type]

    def __init__(self, container: Optional["Container"] = None):
        self._registered_types = {}
        self._explicitly_registered_types = set()
        if container:
            self._registered_types = copy(container._registered_types)

    def define(
        self,
        dep: Type[X],
        resolver: Union[
            Type[X], Callable[[], X], Callable[[Any], X], SpecialDepDefinition[X], X
        ],
    ) -> None:
        if dep in self._explicitly_registered_types:
            raise DuplicateDefinition()
        self._registered_types[dep] = normalise(resolver, self)
        self._explicitly_registered_types.add(dep)

    def resolve(self, dep_type: Type[X], suppress_error=False) -> X:
        try:
            if dep_type in UNRESOLVABLE_TYPES:
                raise UnresolvableType(dep_type)
            registered_type = self._registered_types.get(dep_type, dep_type)
            return self._build(registered_type)
        except UnresolvableType as inner_error:
            if not suppress_error:
                raise UnresolvableType(dep_type) from inner_error
            return None  # type: ignore

    def partial(
        self, func: Callable[..., X], keys_to_skip=None, shared: List[Type] = None
    ) -> Callable[..., X]:
        if shared:
            return self._partial_with_shared_singletons(func, shared)
        spec = inspect.getfullargspec(func)

        def _bind_func():
            bindable_deps = self._infer_dependencies(
                spec, suppress_error=True, keys_to_skip=keys_to_skip or []
            )
            return functools.partial(func, **bindable_deps)

        if inspect.iscoroutinefunction(func):

            async def _async_wrapper(*args, **kwargs):
                return await _bind_func()(*args, **kwargs)  # type: ignore

            return _async_wrapper

        # This function exists so that binding can be used in places
        # that rely on `inspect.is_function` to return True.
        # The output from functools.partial will evaluate to False so we
        # need to wrap the call.
        def _compatibility_wrapper(*args, **kwargs):
            return _bind_func()(*args, **kwargs)

        return _compatibility_wrapper

    def clone(self):
        return Container(self)

    def __getitem__(self, dep: Type[X]) -> X:
        return self.resolve(dep)

    def __setitem__(
        self,
        dep: Type[X],
        resolver: Union[
            Type[X], Callable[[], X], Callable[[Any], X], SpecialDepDefinition[X], X
        ],
    ):
        self.define(dep, resolver)

    def _build(self, dep_type: Any) -> Any:
        if isinstance(dep_type, SpecialDepDefinition):
            return dep_type.get_instance(self._build)
        return self._reflection_build(dep_type)

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

        if inspect.iscoroutinefunction(func):

            async def _async_function(*args, **kwargs):
                temp_container = _cloned_container()
                temp_bound_func = temp_container.partial(func, shared=[])
                return await temp_bound_func(*args, **kwargs)

            return _async_function
        else:

            def _function(*args, **kwargs):
                temp_container = _cloned_container()
                temp_bound_func = temp_container.partial(func, shared=[])
                return temp_bound_func(*args, **kwargs)

            return _function
