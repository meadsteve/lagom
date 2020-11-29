"""
Interfaces shared by modules within the lagom package
"""
from abc import ABC, abstractmethod
from typing import (
    Generic,
    TypeVar,
    Type,
    Any,
    Callable,
    Union,
    List,
    Set,
    Optional,
    Dict,
)

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
    def partial(
        self, func: Callable[..., X], shared: List[Type] = None,
    ) -> Callable[..., X]:
        pass

    @abstractmethod
    def magic_partial(
        self,
        func: Callable[..., X],
        shared: List[Type] = None,
        keys_to_skip: List[str] = None,
        skip_pos_up_to: int = 0,
    ) -> Callable[..., X]:
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


class WriteableContainer(ReadableContainer):
    """
    Represents a container that is mutable and can have
    new definitions added.

    """

    @abstractmethod
    def __setitem__(self, dep: Type[X], resolver: "TypeResolver[X]"):
        """
        forwards to WriteableContainer.define

        :param dep:
        :param resolver:
        :return:
        """
        pass

    @abstractmethod
    def define(
        self, dep: Type[X], resolver: "TypeResolver[X]"
    ) -> "SpecialDepDefinition":
        """
        Sets the resolver for type "dep"

        :param dep:
        :param resolver:
        :return:
        """
        pass


class ExtendableContainer(ReadableContainer):
    """
    A container that is extentable can be cloned with the clone
    being mutable enabling extension.
    """

    @abstractmethod
    def clone(self) -> WriteableContainer:
        """ returns a copy of the container in a mutable state
        so new updates can be applied
        :return:
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


class DefinitionsSource(ABC):
    """
    Stores the mapppings between a type and the definition of how
    to construct that type
    """

    @abstractmethod
    def get_definition(self, dep_type: Type[X]) -> Optional[SpecialDepDefinition[X]]:
        """
        For a supplied type returns the definition of how to build that type.
        If unknown None is returned
        :param dep_type:
        """
        pass

    @property
    @abstractmethod
    def defined_types(self) -> Set[Type]:
        """
        The list of types that have been explicitly defined
        :return:
        """
        pass


class ContainerDebugInfo(ABC):
    """
    This object provides an overview of the state of a dependency injection
    container
    """

    @property
    @abstractmethod
    def defined_types(self) -> Set[Type]:
        """
        The list of types that have been explicitly defined
        :return:
        """
        pass

    @property
    @abstractmethod
    def reflection_cache_overview(self) -> Dict[str, str]:
        """
        A summary of what runtime reflection has been performed by lagom
        This will be empty if types have only be loaded from explicit
        definitions
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
