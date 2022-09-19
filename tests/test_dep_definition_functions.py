from dataclasses import dataclass
from typing import Iterator, Generator, ContextManager, ClassVar

import pytest

from lagom import Container, UnresolvableTypeDefinition
from lagom.decorators import dependency_definition, context_dependency_definition
from lagom.exceptions import MissingReturnType


@dataclass
class MyComplexDep:
    finally_was_executed: ClassVar[bool] = False
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
    def my_constructor() -> Iterator[MyComplexDep]:
        yield MyComplexDep(some_number=5)

    first = container[MyComplexDep]
    assert first.some_number == 5


def test_when_yielding_finally_can_be_used(container: Container):
    MyComplexDep.finally_was_executed = False

    @dependency_definition(container)
    def my_constructor() -> Iterator[MyComplexDep]:
        try:
            yield MyComplexDep(some_number=5)
        finally:
            MyComplexDep.finally_was_executed = True

    dep = container.resolve(MyComplexDep)
    assert isinstance(dep, MyComplexDep)
    assert MyComplexDep.finally_was_executed is True


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


def test_yielding_definition_functions_get_an_instance_of_the_container(
    container: Container,
):
    container[MyComplexDep] = MyComplexDep(some_number=3)

    @dependency_definition(container)
    def my_constructor(c: Container) -> Generator[WrapperOfSomeKind, None, None]:
        yield WrapperOfSomeKind(c[MyComplexDep])

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


def test_context_managers_can_be_defined_from_a_generator(container: Container):
    @context_dependency_definition(container)
    def my_constructor() -> Iterator[MyComplexDep]:
        try:
            yield MyComplexDep(some_number=3)
        finally:
            pass

    with container[ContextManager[MyComplexDep]] as dep:  # type: ignore
        assert dep.some_number == 3


def test_defining_a_context_manager_does_not_define_the_managed_type_itself(
    container: Container,
):
    @context_dependency_definition(container)
    def my_constructor() -> Iterator[MyComplexDep]:
        try:
            yield MyComplexDep(some_number=3)
        finally:
            pass

    definition = container.get_definition(MyComplexDep)
    assert isinstance(definition, UnresolvableTypeDefinition) or definition is None
