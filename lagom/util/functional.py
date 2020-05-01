"""Code to help understand functions
"""
import inspect
from typing import Callable


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
