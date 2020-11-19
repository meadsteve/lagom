"""Extra information about the reflection API
"""
import inspect
from threading import Lock
from typing import Dict, Type, List, Callable, get_type_hints, Optional, Awaitable, Any

RETURN_ANNOTATION = "return"


class FunctionSpec:
    """
    Describes the arguments of a function
    """

    args: List
    annotations: Dict[str, Type]
    defaults: Dict[str, Any]
    return_type: Optional[Type]
    arity: int

    def __init__(self, args, annotations, defaults, return_type):
        self.args = args
        self.annotations = annotations
        self.defaults = defaults
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
    _thread_lock: Lock

    def __init__(self):
        self._reflection_cache = {}
        self._thread_lock = Lock()

    @property
    def overview_of_cache(self) -> Dict[str, str]:
        """
        Gives a humanish readable representation of what has been reflected on
        :return:
        """
        return {k.__qualname__: repr(v) for (k, v) in self._reflection_cache.items()}

    def get_function_spec(self, func) -> FunctionSpec:
        """
        Returns details about the function's signature
        :param func:
        :return:
        """
        if func in self._reflection_cache:
            return self._reflection_cache[func]
        return self._perform_reflection(func)

    def _perform_reflection(self, func):
        try:
            self._thread_lock.acquire()
            if func in self._reflection_cache:
                return self._reflection_cache[func]
            self._reflection_cache[func] = reflect(func)
            return self._reflection_cache[func]
        finally:
            self._thread_lock.release()


def reflect(func: Callable) -> FunctionSpec:
    """
    Extension to inspect.getfullargspec with a little more.
    :param func:
    :return:
    """
    spec = inspect.getfullargspec(func)
    annotations = get_type_hints(func)
    defaults = _get_default_args(func)
    ret = annotations.pop(RETURN_ANNOTATION, None)
    if ret and inspect.iscoroutinefunction(func):
        ret = Awaitable[ret]  # type: ignore # todo: figure this out
    return FunctionSpec(spec.args, annotations, defaults, ret)


def _get_default_args(func):
    arguments = inspect.signature(func).parameters.items()
    return {
        name: argument.default
        for name, argument in arguments
        if argument.default is not inspect.Parameter.empty
    }


def remove_optional_type(dep_type):
    """ if the Type is Optional[T] returns T else None

    :param dep_type:
    :return:
    """
    try:
        # Hacky: an optional type has [T, None] in __args__
        if len(dep_type.__args__) == 2 and dep_type.__args__[1] == None.__class__:
            return dep_type.__args__[0]
    except:
        pass
    return None
