"""
Interfaces shared by modules within the lagom package
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Any, Callable

X = TypeVar("X")


BuildingFunction = Callable[[Any], Any]


class ReadableContainer(ABC):
    @abstractmethod
    def resolve(
        self, dep_type: Type[X], suppress_error=False, skip_definitions=False
    ) -> X:
        pass

    @abstractmethod
    def __getitem__(self, dep: Type[X]) -> X:
        pass


class SpecialDepDefinition(ABC, Generic[X]):
    """
    Represents a special way of loading a dependency.
    """

    @abstractmethod
    def get_instance(self, container: ReadableContainer) -> X:
        """ constructs the represented type(X).

        :param container: an instance of the current container
        :return:
        """
        pass
