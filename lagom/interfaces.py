from abc import ABC, abstractmethod
from typing import Generic, TypeVar

X = TypeVar("X")


class SpecialDepDefinition(ABC, Generic[X]):
    @abstractmethod
    def get_instance(self, build_func) -> X:
        pass
