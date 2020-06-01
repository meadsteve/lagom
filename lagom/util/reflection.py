"""Extra information about the reflection API
"""
import inspect
from typing import Dict, Type, List, Callable

RETURN_ANNOTATION = "return"


class FunctionSpec:
    """
    Describes the arguments of a function
    """

    args: List
    annotations: Dict[str, Type]
    return_type: Type

    def __init__(self, args, annotations, return_type):
        self.args = args
        self.annotations = annotations
        self.return_type = return_type


class CachingReflector:
    """
    Takes a function and returns an object representing
    the function's type signature. Results are cached
    so subsequent calls do not need to call the reflection
    API.
    """

    _reflection_cache: Dict[Callable, FunctionSpec]

    def __init__(self):
        self._reflection_cache = {}

    def get_function_spec(self, func) -> FunctionSpec:
        """
        Returns details about the function's signature
        :param func:
        :return:
        """
        if func not in self._reflection_cache:
            spec = inspect.getfullargspec(func)
            ret = spec.annotations.pop(RETURN_ANNOTATION, None)
            self._reflection_cache[func] = FunctionSpec(
                spec.args, spec.annotations, ret
            )
        return self._reflection_cache[func]
