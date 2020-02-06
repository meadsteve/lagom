import inspect
from typing import TypeVar, Callable

INTROSPECTION_ATTRS = (
    "__module__",
    "__name__",
    "__qualname__",
    "__doc__",
    "__annotations__",
)

T = TypeVar("T")


def decorated_wrapper(wrapped: T, original) -> T:
    for attr in INTROSPECTION_ATTRS:
        if hasattr(original, attr):
            setattr(wrapped, attr, getattr(original, attr))
    return wrapped


def bound_function(
    function_builder: Callable[[], Callable], original_function: Callable
):
    if inspect.iscoroutinefunction(original_function):

        async def _wrapped_function(*args, **kwargs):
            return await function_builder()(*args, **kwargs)

    else:

        def _wrapped_function(*args, **kwargs):
            return function_builder()(*args, **kwargs)

    return decorated_wrapper(_wrapped_function, original_function)
