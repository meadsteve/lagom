"""
Exceptions raised by the library
"""
from abc import ABC
from typing import Type


class LagomException(Exception, ABC):
    """All exceptions in this library are instances of a LagomException"""

    pass


class InvalidDependencyDefinition(ValueError, LagomException):
    """The provided construction logic is not valid"""

    pass


class DuplicateDefinition(ValueError, LagomException):
    """The type has already been defined somewhere else"""

    pass


class UnresolvableType(ValueError, LagomException):
    """The type cannot be constructed"""

    dep_type: str

    def __init__(self, dep_type: Type):
        """

        :param dep_type: The type that could not be constructed
        """
        self.dep_type = (
            dep_type.__name__ if hasattr(dep_type, "__name__") else str(dep_type)
        )
        super().__init__(
            f"Unable to construct dependency of type {self.dep_type} "
            "The constructor probably has some unresolvable dependencies"
        )
