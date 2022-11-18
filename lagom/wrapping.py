"""
Code in this module is used to wrap and decorate functions that have been
bound to a container
"""
import functools
import inspect
from typing import Callable

from .exceptions import UnableToInvokeBoundFunction
from .injection_context import TemporaryInjectionContext
from .interfaces import ReadableContainer, ContainerBoundFunction
from .util.reflection import FunctionSpec


class ContainerBoundFunc:
    """
    Represents a function that has been bound to a container
    """

    _argument_updater: Callable
    _base_injection_context: TemporaryInjectionContext
    _inner_func: Callable

    def __init__(self, inner_func, base_injection_context, argument_updater):
        self._inner_func = inner_func
        self._base_injection_context = base_injection_context
        self._argument_updater = argument_updater

    def __call__(self, *args, **kwargs):
        argument_updater = self._argument_updater
        inner_func = self._inner_func
        bound_args, bound_kwargs = argument_updater(
            self._base_injection_context, args, kwargs
        )
        return inner_func(*bound_args, **bound_kwargs)

    def rebind(self, container: ReadableContainer):
        return ContainerBoundFunc(
            self._inner_func,
            self._base_injection_context.rebound_to(container),
            self._argument_updater,
        )


class ContainerAsyncBoundFunc:
    """
    Represents an async function that has been bound to a container
    """

    _argument_updater: Callable
    _base_injection_context: TemporaryInjectionContext
    _inner_func: Callable

    def __init__(self, inner_func, base_injection_context, argument_updater):
        self._inner_func = inner_func
        self._base_injection_context = base_injection_context
        self._argument_updater = argument_updater

    async def __async_call__(self, *args, **kwargs):
        argument_updater = self._argument_updater
        inner_func = self._inner_func
        bound_args, bound_kwargs = argument_updater(
            self._base_injection_context, args, kwargs
        )
        return await inner_func(*bound_args, **bound_kwargs)

    def as_coroutine(self):
        """
        returns a coroutine that wraps this class. Some class methods
        also get added to the coroutine. This is so it acts like a class with
        an __asynccall__ magic method.
        """

        async def _coroutine_func(*args, **kwargs):
            return await self.__async_call__(*args, **kwargs)

        _coroutine_func.rebind = self.rebind  # type: ignore

        return _coroutine_func

    def rebind(self, container: ReadableContainer):
        return ContainerAsyncBoundFunc(
            self._inner_func,
            self._base_injection_context.rebound_to(container),
            self._argument_updater,
        ).as_coroutine()


def apply_argument_updater(
    func,
    base_injection_context,
    argument_updater,
    spec: FunctionSpec,
    catch_errors=False,
) -> ContainerBoundFunction:
    """
    Takes a function and binds it to a container with an update function
    """
    inner_func = func if not catch_errors else _wrap_func_in_error_handling(func, spec)
    if inspect.iscoroutinefunction(func):

        _bound_func = ContainerAsyncBoundFunc(
            inner_func, base_injection_context, argument_updater
        ).as_coroutine()

    else:

        _bound_func = ContainerBoundFunc(
            inner_func, base_injection_context, argument_updater
        )

    return functools.wraps(func)(_bound_func)


def _wrap_func_in_error_handling(func, spec: FunctionSpec):
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
