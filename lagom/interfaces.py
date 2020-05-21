"""
Interfaces shared by modules within the lagom package
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Any, Callable, Union, List, Set

X = TypeVar("X")


BuildingFunction = Callable[[Any], Any]


class ReadableContainer(ABC):
    """
    Represents a container that can resolve dependencies
    """

    @abstractmethod
    def resolve(
        self, dep_type: Type[X], suppress_error=False, skip_definitions=False
    ) -> X:
        """Constructs an object of type X
        """
        pass

    @abstractmethod
    def __getitem__(self, dep: Type[X]) -> X:
        """Shortcut to calling resolve
        """
        pass

    @property
    @abstractmethod
    def defined_types(self) -> Set[Type]:
        """Set of all the types defined in the container
        """
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


T = TypeVar("T")

"""
The TypeResolver represents the way that lagom can be
told about how to define a type. Any of these types
can be assigned to the container.
"""
TypeResolver = Union[
    Type[T],  # An alias from one type to the next
    Callable[[], T],  # A resolution function
    Callable[[ReadableContainer], T],  # A resolution function that takes the container
    SpecialDepDefinition[T],  # From the definitions module
    T,  # Just an instance of the type - A singleton
]
