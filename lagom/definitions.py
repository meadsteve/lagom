from dataclasses import dataclass
from typing import Generic, Union, Type, Optional, Callable, TypeVar


X = TypeVar("X")


@dataclass
class Construction(Generic[X]):
    constructor: Callable[[], X]

    def construct(self):
        call = self.constructor
        return call()


@dataclass
class Alias(Generic[X]):
    alias_type: Type[X]


class Singleton(Generic[X]):
    singleton_type: Union[Type[X], Construction[X]]
    _instance: Optional[X]

    def __init__(self, singleton_type: Union[Type[X], Construction[X]]):
        self.singleton_type = singleton_type
        self._instance = None

    @property
    def instance(self):
        return self._instance

    @property
    def has_instance(self):
        return self._instance is not None

    def set_instance(self, instance: X):
        self._instance = instance
        return instance


DEFINITION_TYPES = [Alias, Construction, Singleton]
Resolver = Union[Construction[X], Singleton[X], Alias[X]]
