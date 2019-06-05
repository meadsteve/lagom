import inspect
from typing import Callable


def arity(func: Callable) -> int:
    return len(inspect.signature(func).parameters)
