import functools
import inspect
from typing import Dict, Type, Union, Any, TypeVar, Callable

from .interfaces import SpecialDepDefinition
from .exceptions import UnresolvableType, DuplicateDefinition
from .definitions import normalise

UNRESOLVABLE_TYPES = [str, int, float, bool]

X = TypeVar("X")

DepDefinition = Any


class Container:
    _registered_types: Dict[Type, SpecialDepDefinition]

    def __init__(self):
        self._registered_types = {}

    def define(self, dep: Union[Type[X], Type], resolver: DepDefinition) -> None:
        if dep in self._registered_types:
            raise DuplicateDefinition()
        self._registered_types[dep] = normalise(resolver, self)

    def resolve(self, dep_type: Type[X], suppress_error=False) -> X:
        try:
            if dep_type in UNRESOLVABLE_TYPES:
                raise UnresolvableType(f"Cannot construct type {dep_type}")
            registered_type = self._registered_types.get(dep_type, dep_type)
            return self._build(registered_type)
        except UnresolvableType as inner_error:
            if not suppress_error:
                raise UnresolvableType(
                    f"Cannot construct type {dep_type.__name__}"
                ) from inner_error
            return None  # type: ignore

    def partial(self, func: Callable[..., X], keys_to_skip=None) -> Callable[..., X]:
        spec = inspect.getfullargspec(func)
        bindable_deps = self._infer_dependencies(
            spec, suppress_error=True, keys_to_skip=keys_to_skip or []
        )
        return functools.partial(func, **bindable_deps)

    def __getitem__(self, dep: Type[X]) -> X:
        return self.resolve(dep)

    def __setitem__(self, dep: Type, resolver: DepDefinition):
        self.define(dep, resolver)

    def _build(self, dep_type: Any) -> Any:
        if isinstance(dep_type, SpecialDepDefinition):
            return dep_type.get_instance(self._build)
        return self._reflection_build(dep_type)

    def _reflection_build(self, dep_type: Type[X]) -> X:
        spec = inspect.getfullargspec(dep_type.__init__)
        sub_deps = self._infer_dependencies(spec)
        return dep_type(**sub_deps)  # type: ignore

    def _infer_dependencies(
        self, spec: inspect.FullArgSpec, suppress_error=False, keys_to_skip=[]
    ):
        sub_deps = {
            key: self.resolve(sub_dep_type, suppress_error=suppress_error)
            for (key, sub_dep_type) in spec.annotations.items()
            if key != "return" and sub_dep_type != Any and key not in keys_to_skip
        }
        filtered_deps = {key: dep for (key, dep) in sub_deps.items() if dep is not None}
        return filtered_deps
