from dataclasses import dataclass

import pytest

from lagom import Container
from lagom.decorators import dependency_definition


@dataclass
class MyComplexDep:
    some_number: int


def test_functions_that_are_typed_can_be_used_by_a_container(container: Container):
    @dependency_definition(container)
    def my_constructor() -> MyComplexDep:
        return MyComplexDep(some_number=5)

    assert container[MyComplexDep] == MyComplexDep(some_number=5)


def test_functions_that_are_not_typed_raise_an_error(container: Container):

    with pytest.raises(SyntaxError):

        @dependency_definition(container)
        def my_constructor():
            return MyComplexDep(some_number=5)
