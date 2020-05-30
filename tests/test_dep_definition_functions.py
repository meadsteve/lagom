from dataclasses import dataclass
from typing import Generator, Any

import pytest

from lagom import Container
from lagom.decorators import dependency_definition
from lagom.exceptions import MissingReturnType

global finally_was_executed
finally_was_executed = False


@dataclass
class MyComplexDep:
    some_number: int


@dataclass
class WrapperOfSomeKind:
    inner: MyComplexDep


def test_functions_that_are_typed_can_be_used_by_a_container(container: Container):
    @dependency_definition(container)
    def my_constructor() -> MyComplexDep:
        return MyComplexDep(some_number=5)

    assert container[MyComplexDep] == MyComplexDep(some_number=5)


def test_the_functions_return_new_instances_each_time(container: Container):
    @dependency_definition(container)
    def my_constructor() -> MyComplexDep:
        return MyComplexDep(some_number=5)

    first = container[MyComplexDep]
    second = container[MyComplexDep]
    assert first is not second


def test_definition_functions_can_yield_instead_of_returning(container: Container):
    @dependency_definition(container)
    def my_constructor() -> Generator[MyComplexDep, Any, Any]:
        yield MyComplexDep(some_number=5)

    first = container[MyComplexDep]
    assert first.some_number == 5


def test_when_yielding_finally_can_be_used(container: Container):
    global finally_was_executed
    finally_was_executed = False

    @dependency_definition(container)
    def my_constructor() -> Generator[MyComplexDep, Any, Any]:
        global finally_was_executed
        try:
            yield MyComplexDep(some_number=5)
        finally:
            finally_was_executed = True

    container.resolve(MyComplexDep)
    assert finally_was_executed is True


def test_functions_can_be_made_into_singletons(container: Container):
    @dependency_definition(container, singleton=True)
    def my_constructor() -> MyComplexDep:
        return MyComplexDep(some_number=5)

    first = container[MyComplexDep]
    second = container[MyComplexDep]
    assert first is second


def test_definition_functions_get_an_instance_of_the_container(container: Container):
    container[MyComplexDep] = MyComplexDep(some_number=3)

    @dependency_definition(container)
    def my_constructor(c: Container) -> WrapperOfSomeKind:
        return WrapperOfSomeKind(c[MyComplexDep])

    assert container[WrapperOfSomeKind].inner == container[MyComplexDep]


def test_singleton_definition_functions_get_an_instance_of_the_container(
    container: Container,
):
    container[MyComplexDep] = MyComplexDep(some_number=3)

    @dependency_definition(container, singleton=True)
    def my_constructor(c: Container) -> WrapperOfSomeKind:
        return WrapperOfSomeKind(c[MyComplexDep])

    assert container[WrapperOfSomeKind].inner == container[MyComplexDep]


def test_functions_that_are_not_typed_raise_an_error(container: Container):
    with pytest.raises(MissingReturnType):

        @dependency_definition(container)
        def my_constructor():
            return MyComplexDep(some_number=5)
