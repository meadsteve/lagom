import functools
import inspect
from typing import Union, Type, Optional, Callable, TypeVar, Any

from .exceptions import InvalidDependencyDefinition
from .interfaces import SpecialDepDefinition
from .util.functional import arity

X = TypeVar("X")


class Construction(SpecialDepDefinition[X]):
    constructor: Callable[[], X]

    def __init__(self, constructor):
        self.constructor = constructor

    def get_instance(self, _build_func) -> X:
        call = self.constructor  # type: ignore
        return call()


class Alias(SpecialDepDefinition[X]):
    alias_type: Type[X]

    def __init__(self, alias_type):
        self.alias_type = alias_type

    def get_instance(self, build_func) -> X:
        return build_func(self.alias_type)


class Singleton(SpecialDepDefinition[X]):
    singleton_type: Union[Type[X], Construction[X]]
    _instance: Optional[X]

    def __init__(self, singleton_type: Union[Type[X], Construction[X]]):
        self.singleton_type = singleton_type
        self._instance = None

    def get_instance(self, build_func) -> X:
        if self._has_instance:
            return self._instance  # type: ignore
        return self._set_instance(build_func(self.singleton_type))

    @property
    def _has_instance(self):
        return self._instance is not None

    def _set_instance(self, instance: X):
        self._instance = instance
        return instance


def normalise(resolver: Any, container) -> SpecialDepDefinition:
    if isinstance(resolver, SpecialDepDefinition):
        return resolver
    elif inspect.isfunction(resolver):
        return _build_lambda_constructor(resolver, container)
    elif not inspect.isclass(resolver):
        return Singleton(lambda: resolver)  # type: ignore
    else:
        return Alias(resolver)


def _build_lambda_constructor(resolver: Callable, container) -> Construction:
    artiy = arity(resolver)
    if artiy == 0:
        return Construction(resolver)
    if artiy == 1:
        return Construction(functools.partial(resolver, container))
    raise InvalidDependencyDefinition(f"Arity {arity} functions are not supported")
