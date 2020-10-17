import pytest

from lagom import Container
from lagom.exceptions import InvalidDependencyDefinition


class MyBasicDep:
    basic_value = 5


class ComplexDep:
    def __init__(self, some_dep):
        self.value = some_dep.basic_value


def test_lambda_arity_zero_works(container: Container):
    container.define(MyBasicDep, lambda: MyBasicDep())
    assert type(container[MyBasicDep]) == MyBasicDep


def test_lambda_arity_one_is_passed_the_container(container: Container):
    container.define(MyBasicDep, lambda: MyBasicDep())
    container.define(ComplexDep, lambda c: ComplexDep(c[MyBasicDep]))
    assert container[ComplexDep].value == 5


def test_lambda_arity_two_results_in_an_error(container: Container):
    with pytest.raises(InvalidDependencyDefinition):
        container.define(MyBasicDep, lambda _x, _y: MyBasicDep)  # type: ignore
