import inspect
from typing import TypeVar, Callable, List

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


# A function builder is wrapped around a supplied function and
# bound to the container. When called a new function will be returned
# which is the same as the original function but with some arguments supplied
# from the container. The arguments tell the container what it doesn't need to build
# first argument is a list of kwargs to skip the second the number of positional arguments
# to ignore.
FunctionBuilder = Callable[[List[str], int], Callable]


def bound_function(function_builder: FunctionBuilder, original_function: Callable):
    if inspect.iscoroutinefunction(original_function):

        async def _wrapped_function(*args, **kwargs):
            named_args_to_skip = list(kwargs.keys())
            pos_args_to_skip = len(args)
            return await function_builder(named_args_to_skip, pos_args_to_skip)(
                *args, **kwargs
            )

    else:

        def _wrapped_function(*args, **kwargs):
            named_args_to_skip = list(kwargs.keys())
            pos_args_to_skip = len(args)
            return function_builder(named_args_to_skip, pos_args_to_skip)(
                *args, **kwargs
            )

    return decorated_wrapper(_wrapped_function, original_function)
