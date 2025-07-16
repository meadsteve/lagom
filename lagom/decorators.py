"""
This module provides decorators for hooking an
application into the container.s
"""

import inspect
from contextlib import contextmanager, asynccontextmanager
from functools import wraps
from types import FunctionType
from typing import (
    List,
    Type,
    Callable,
    Tuple,
    TypeVar,
    ContextManager,
    AsyncContextManager,
    Optional,
)

from .container import Container
from .definitions import (
    Singleton,
    construction,
    yielding_construction,
    async_construction,
)
from .exceptions import (
    MissingReturnType,
    ClassesCannotBeDecorated,
    InvalidDependencyDefinition,
)
from .interfaces import SpecialDepDefinition
from .util.reflection import reflect

T = TypeVar("T")
R = TypeVar("R")


def bind_to_container(
    container: Container, shared: Optional[List[Type]] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    def _decorator(func):
        if not isinstance(func, FunctionType):
            raise ClassesCannotBeDecorated()
        return wraps(func)(container.partial(func, shared=shared))

    return _decorator


def magic_bind_to_container(
    container: Container, shared: Optional[List[Type]] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """Decorates the function so that it's uses the container to construct things

    >>> from tests.examples import SomeClass
    >>> c = Container()
    >>> @magic_bind_to_container(c)
    ... def say_hello_from(sayer: SomeClass):
    ...    return f"hello from {sayer}"
    >>> say_hello_from()
    'hello from <tests.examples.SomeClass object at ...>'

    """

    def _decorator(func):
        if not isinstance(func, FunctionType):
            raise ClassesCannotBeDecorated()
        return wraps(func)(container.magic_partial(func, shared=shared))

    return _decorator


def dependency_definition(container: Container, singleton: bool = False):
    """Registers the provided function with the container
    The return type of the decorated function will be reflected and whenever
    the container is asked for this type the function will be called

    >>> from tests.examples import SomeClass, SomeExtendedClass
    >>> c = Container()
    >>> @dependency_definition(c)
    ... def build_some_class_but_extended() -> SomeClass:
    ...    return SomeExtendedClass()
    >>> c.resolve(SomeClass)
    <tests.examples.SomeExtendedClass object at ...>

    """

    def _decorator(func):
        definition_func, return_type = _extract_definition_func_and_type(func)  # type: ignore

        if singleton:
            container.define(return_type, Singleton(definition_func))
        else:
            container.define(return_type, definition_func)
        return func

    return _decorator


def context_dependency_definition(container: Container):
    """
    Turns the decorated function into a definition for a context manager
    in the given container.

    >>> from tests.examples import SomeClass
    >>> from typing import Iterator
    >>>
    >>> c = Container()
    >>>
    >>> @context_dependency_definition(c)
    ... def my_constructor() -> Iterator[SomeClass]:
    ...     try:
    ...         yield SomeClass()
    ...     finally:
    ...         pass # Any tidy up or resource closing could happen here
    >>> with c[ContextManager[SomeClass]] as something:
    ...     something
    <tests.examples.SomeClass ...>

    with container[ContextManager[MyComplexDep]] as dep:  # type: ignore
        assert dep.some_number == 3
    """

    def _decorator(func):
        if not inspect.isgeneratorfunction(func) and not inspect.isasyncgenfunction(
            func
        ):
            raise InvalidDependencyDefinition(
                "context_dependency_definition must be given a generator"
            )
        dep_type = _generator_type(reflect(func).return_type)
        if inspect.isgeneratorfunction(func):
            container.define(ContextManager[dep_type], contextmanager(func))  # type: ignore
        if inspect.isasyncgenfunction(func):
            container.define(AsyncContextManager[dep_type], asynccontextmanager(func))  # type: ignore
        return func

    return _decorator


def _extract_definition_func_and_type(
    func,
) -> Tuple[SpecialDepDefinition, Type[T]]:
    """
    Takes a function or a generator and returns a function and the return type.
    :param func:
    :return:
    """

    return_type = reflect(func).return_type
    if not return_type:
        raise MissingReturnType(
            f"Function {func.__name__} used as a definition must have a return type"
        )
    if inspect.iscoroutinefunction(func):
        return async_construction(func), return_type
    if not inspect.isgeneratorfunction(func) and not inspect.isasyncgenfunction(func):
        return construction(func), return_type

    return (
        yielding_construction(func),
        _generator_type(return_type),
    )


def _generator_type(return_type):
    return return_type.__args__[0]  # todo: something less hacky
