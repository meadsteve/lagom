"""
This module provides decorators for hooking an
application into the container.s
"""
import inspect
from typing import List, Type, Callable, Tuple, TypeVar

from .definitions import Singleton
from .container import Container
from .exceptions import MissingReturnType
from .util.reflection import reflect

T = TypeVar("T")


def bind_to_container(container: Container, shared: List[Type] = None):
    def _decorator(func):
        return container.partial(func, shared=shared)

    return _decorator


def magic_bind_to_container(container: Container, shared: List[Type] = None):
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
        return container.magic_partial(func, shared=shared)

    return _decorator


def dependency_definition(container: Container, singleton: bool = False):
    """ Registers the provided function with the container
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


def _extract_definition_func_and_type(func,) -> Tuple[Callable[[], T], Type[T]]:
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

    if not inspect.isgeneratorfunction(func):
        return func, return_type

    # it's  a generator we need to request a value when loading
    def value_from_gen():
        return next(func())

    return value_from_gen, return_type.__args__[0]  # todo: something less hacky
