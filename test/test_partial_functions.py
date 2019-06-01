import pytest

from lagom import Container, bind_to_container
from lagom.exceptions import UnresolvableType


class MyDep:
    value: str = "testing"


container = Container()


def example_function(resolved: MyDep, message: str) -> str:
    return resolved.value + message


@bind_to_container(container)
def another_example_function(resolved: MyDep, message: str) -> str:
    return resolved.value + message


def test_partial_application_can_be_applied_to_functions():
    partial = container.partial(example_function)
    assert partial(message=" world") == "testing world"


def test_a_decorator_can_be_used_to_bind_as_well():
    assert another_example_function(message=" hello") == "testing hello"
