"""
Code in this module is used to wrap and decorate functions that have been
bound to a container
"""
import functools
import inspect

from .exceptions import UnableToInvokeBoundFunction
from .util.reflection import FunctionSpec


def apply_argument_updater(func, spec: FunctionSpec, argument_updater):
    func_with_error_handling = wrap_func_in_error_handling(func, spec)
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def _bound_func(*args, **kwargs):
            bound_args, bound_kwargs = argument_updater(args, kwargs)
            return await func_with_error_handling(*bound_args, **bound_kwargs)

    else:

        @functools.wraps(func)
        def _bound_func(*args, **kwargs):
            bound_args, bound_kwargs = argument_updater(args, kwargs)
            return func_with_error_handling(*bound_args, **bound_kwargs)

    return _bound_func


def wrap_func_in_error_handling(func, spec: FunctionSpec):
    """
    Takes a func and its spec and returns a function that's the same
    but with more useful TypeError messages
    :param func:
    :param spec:
    :return:
    """

    @functools.wraps(func)
    def _error_handling_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as error:
            # if it wasn't in kwargs the container couldn't build it
            unresolvable_deps = [
                dep_type
                for (name, dep_type) in spec.annotations.items()
                if name not in kwargs.keys()
            ]
            raise UnableToInvokeBoundFunction(str(error), unresolvable_deps)

    return _error_handling_func
