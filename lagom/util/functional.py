"""Code to help understand functions
"""
import inspect
from typing import Callable, TypeVar, Generic, Iterator


def arity(func: Callable) -> int:
    """Returns the arity(number of args)
    Given a callable this function returns the number of arguments it expects
    >>> arity(lambda: 5)
    0
    >>> arity(lambda x: x)
    1

    :param func:
    :return:
    """
    return len(inspect.signature(func).parameters)


F = TypeVar("F", bound=Callable)


class FunctionCollection(Generic[F]):
    """
    Represents a collection of functions that is hashable.
    """

    def __init__(self, *checkers: F):
        self._checkers = checkers
        self.hash = hash(tuple(self._checkers))

    def __len__(self) -> int:
        return len(self._checkers)

    def __contains__(self, item) -> bool:
        return item in self._checkers

    def __iter__(self) -> Iterator[F]:
        return iter(self._checkers)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        if isinstance(other, FunctionCollection):
            return self.hash == other.hash
        if isinstance(other, list):
            return tuple(other) == self._checkers
        return False
