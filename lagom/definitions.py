import inspect
from typing import Union, Type, Optional, Callable, TypeVar, Any

from .exceptions import InvalidDependencyDefinition
from .interfaces import SpecialDepDefinition
from .util.functional import arity

X = TypeVar("X")


class Construction(SpecialDepDefinition[X]):
    constructor: Union[Callable[[], X], Callable[[Any], X]]

    def __init__(self, constructor):
        if arity(constructor) > 1:
            raise InvalidDependencyDefinition(
                f"Arity {arity} functions are not supported"
            )
        self.constructor = constructor

    def get_instance(self, _build_func, container) -> X:
        resolver = self.constructor
        artiy = arity(resolver)
        if artiy == 0:
            return resolver()  # type: ignore
        if artiy == 1:
            return resolver(container)  # type: ignore
        raise Exception("The constructor should have stopped us getting here")


class Alias(SpecialDepDefinition[X]):
    alias_type: Type[X]

    def __init__(self, alias_type):
        self.alias_type = alias_type

    def get_instance(self, build_func, _container) -> X:
        return build_func(self.alias_type)


class Singleton(SpecialDepDefinition[X]):
    singleton_type: Any
    _instance: Optional[X]

    def __init__(self, singleton_type):
        self.singleton_type = normalise(singleton_type)
        self._instance = None

    def get_instance(self, build_func, _container) -> X:
        if self._has_instance:
            return self._instance  # type: ignore
        return self._set_instance(build_func(self.singleton_type))

    @property
    def _has_instance(self):
        return self._instance is not None

    def _set_instance(self, instance: X):
        self._instance = instance
        return instance


def normalise(resolver: Any) -> SpecialDepDefinition:
    if isinstance(resolver, SpecialDepDefinition):
        return resolver
    elif inspect.isfunction(resolver):
        return Construction(resolver)
    elif not inspect.isclass(resolver):
        return Singleton(lambda: resolver)
    else:
        return Alias(resolver)
