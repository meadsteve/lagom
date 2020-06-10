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
    arity: int

    def __init__(self, args, annotations, return_type):
        self.args = args
        self.annotations = annotations
        self.return_type = return_type
        self.arity = len(args)

    def __repr__(self):
        def _arg_type_string(arg):
            return self.annotations[arg].__name__ if arg in self.annotations else "?"

        signature = ", ".join(_arg_type_string(arg) for arg in self.args)
        if self.return_type:
            return f"({signature}) -> {self.return_type.__name__}"
        else:
            return f"({signature})"


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

    @property
    def overview_of_cache(self) -> Dict[str, str]:
        return {k.__qualname__: repr(v) for (k, v) in self._reflection_cache.items()}

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
