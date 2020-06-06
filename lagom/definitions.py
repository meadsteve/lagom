"""
Classes representing specific ways of representing dependencies
"""
import inspect
from typing import Union, Type, Optional, Callable, TypeVar, Any

from .exceptions import InvalidDependencyDefinition
from .interfaces import SpecialDepDefinition, ReadableContainer
from .util.functional import arity

X = TypeVar("X")


class ConstructionWithoutContainer(SpecialDepDefinition[X]):
    """Wraps a callable for constructing a type"""

    def __init__(self, constructor):
        self.constructor = constructor

    def get_instance(self, container: ReadableContainer) -> X:
        resolver = self.constructor
        return resolver()


class ConstructionWithContainer(SpecialDepDefinition[X]):
    """Wraps a callable for constructing a type"""

    def __init__(self, constructor):
        self.constructor = constructor

    def get_instance(self, container: ReadableContainer) -> X:
        resolver = self.constructor
        return resolver(container)


def construction(
    resolver: Callable,
) -> Union[ConstructionWithContainer, ConstructionWithoutContainer]:
    """
    Takes a callable and returns a type definition
    :param reflector:
    :param resolver:
    :return:
    """
    func_arity = arity(resolver)
    if func_arity == 0:
        return ConstructionWithoutContainer(resolver)
    if func_arity == 1:
        return ConstructionWithContainer(resolver)
    raise InvalidDependencyDefinition(f"Arity {func_arity} functions are not supported")


class Alias(SpecialDepDefinition[X]):
    """When one class is asked for the other should be returned"""

    alias_type: Type[X]

    def __init__(self, alias_type):
        self.alias_type = alias_type

    def get_instance(self, container: ReadableContainer) -> X:
        return container.resolve(self.alias_type, skip_definitions=True)


class Singleton(SpecialDepDefinition[X]):
    """Builds only once then saves the built instance"""

    singleton_type: SpecialDepDefinition
    _instance: Optional[X]

    def __init__(self, singleton_type):
        self.singleton_type = normalise(singleton_type)
        self._instance = None

    def get_instance(self, container: ReadableContainer) -> X:
        if self._has_instance:
            return self._instance  # type: ignore
        instance = self.singleton_type.get_instance(container)
        return self._set_instance(instance)

    @property
    def _has_instance(self):
        return self._instance is not None

    def _set_instance(self, instance: X):
        self._instance = instance
        return instance


def normalise(resolver: Any) -> SpecialDepDefinition:
    """
    :param resolver:
    :return:
    """
    if isinstance(resolver, SpecialDepDefinition):
        return resolver
    elif inspect.isfunction(resolver):
        return construction(resolver)
    elif not inspect.isclass(resolver):
        return Singleton(lambda: resolver)
    else:
        return Alias(resolver)
