"""Extra information about the reflection API
"""
import inspect
from functools import lru_cache
from typing import (
    Dict,
    Type,
    Callable,
    get_type_hints,
    Optional,
    Awaitable,
    Any,
    Mapping,
    Sequence,
)

import typing

RETURN_ANNOTATION = "return"


_TYPE_AWAITABLE = type(typing.Awaitable)


class FunctionSpec:
    """
    Describes the arguments of a function
    """

    args: Sequence[str]
    annotations: Mapping[str, Type]
    defaults: Mapping[str, Any]
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

    def without_argument(self, arg_to_remove: str):
        """
        Returns the function spec with the specified argument removed
        :param arg_to_remove:
        :return:
        """
        new_args = [arg for arg in self.args if arg != arg_to_remove]
        return FunctionSpec(new_args, self.annotations, self.defaults, self.return_type)


class CachingReflector:
    """
    Takes a function and returns an object representing
    the function's type signature. Results are cached
    so subsequent calls do not need to call the reflection
    API.
    """

    @property
    def overview_of_cache(self) -> Dict[str, str]:
        """
        Gives a humanish readable representation of what has been reflected on.
        Removed since lru cache is now used
        :return:
        """
        return {"hidden": ""}

    @lru_cache(maxsize=1024)
    def get_function_spec(self, func) -> FunctionSpec:
        """
        Returns details about the function's signature
        :param func:
        :return:
        """
        return reflect(func)


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


def remove_optional_type(dep_type) -> Optional[Type]:
    """if the Type is Optional[T] returns T else None

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


def remove_awaitable_type(dep_type) -> Optional[Type]:
    """if the Type is Awaitable[T] returns T else None

    :param dep_type:
    :return:
    """
    if isinstance(dep_type, _TYPE_AWAITABLE) or (
        hasattr(dep_type, "_name") and dep_type._name == "Awaitable"
    ):
        return dep_type.__args__[0]  # type: ignore
    return None
