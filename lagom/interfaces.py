"""
Interfaces shared by modules within the lagom package
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

X = TypeVar("X")


class SpecialDepDefinition(ABC, Generic[X]):
    """
    Represents a special way of loading a dependency.
    """

    @abstractmethod
    def get_instance(self, build_func, container) -> X:
        """ constructs the represented type(X).

        :param build_func: a function that can be called to build a type
        :param container: an instance of the current container
        :return:
        """
        pass
