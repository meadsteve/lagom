import functools
import inspect
from typing import Dict, Type, Union, Any, TypeVar, Callable

from lagom.util.functional import arity
from .exceptions import UnresolvableType, InvalidDependencyDefinition
from .definitions import Resolver, Construction, Singleton, Alias, DEFINITION_TYPES

UNRESOLVABLE_TYPES = [str, int, float, bool]

X = TypeVar("X")

DepDefinition = Any


class Container:
    _registered_types: Dict[Type, Resolver] = {}

    def define(self, dep: Union[Type[X], Type], resolver: DepDefinition) -> None:
        self._registered_types[dep] = self._normalise(resolver)

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

    def partial(self, func: Callable, keys_to_skip=[]) -> Callable:
        spec = inspect.getfullargspec(func)
        bindable_deps = self._infer_dependencies(
            spec, suppress_error=True, keys_to_skip=keys_to_skip
        )
        return functools.partial(func, **bindable_deps)

    def __getitem__(self, dep: Type[X]) -> X:
        return self.resolve(dep)

    def __setitem__(self, dep: Type, resolver: DepDefinition):
        self.define(dep, resolver)

    def _normalise(self, resolver: DepDefinition) -> Resolver:
        if type(resolver) in DEFINITION_TYPES:
            return resolver
        elif inspect.isfunction(resolver):
            return self._build_lambda_constructor(resolver)
        elif not inspect.isclass(resolver):
            return Singleton(lambda: resolver)  # type: ignore
        else:
            return Alias(resolver)

    def _build_lambda_constructor(self, resolver: Callable) -> Construction:
        artiy = arity(resolver)
        if artiy == 0:
            return Construction(resolver)
        if artiy == 1:
            return Construction(functools.partial(resolver, self))
        raise InvalidDependencyDefinition(f"Arity {arity} functions are not supported")

    def _build(self, dep_type: Any) -> Any:
        if isinstance(dep_type, Alias):
            return self.resolve(dep_type.alias_type)
        if isinstance(dep_type, Construction):
            return dep_type.construct()
        if isinstance(dep_type, Singleton):
            return self._load_singleton(dep_type)
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

    def _load_singleton(self, singleton: Singleton):
        if singleton.has_instance:
            return singleton.instance
        return singleton.set_instance(self._build(singleton.singleton_type))
