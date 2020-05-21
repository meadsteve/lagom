"""
Exceptions raised by the library
"""
from abc import ABC
from typing import Type

import typing


class LagomException(Exception, ABC):
    """All exceptions in this library are instances of a LagomException"""

    pass


class InvalidDependencyDefinition(ValueError, LagomException):
    """The provided construction logic is not valid"""

    pass


class MissingReturnType(SyntaxError, LagomException):
    """The function provided doesnt type hint a return"""

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
        # This first check makes 3.6 behave the same as 3.7 and later
        if hasattr(typing, "GenericMeta") and isinstance(dep_type, typing.GenericMeta):
            self.dep_type = str(dep_type)
        elif hasattr(dep_type, "__name__"):
            self.dep_type = dep_type.__name__
        else:
            self.dep_type = str(dep_type)
        super().__init__(
            f"Unable to construct dependency of type {self.dep_type} "
            "The constructor probably has some unresolvable dependencies"
        )
