from typing import Generator, AsyncGenerator, Any

import pytest

from lagom import Container, bind_to_container
from lagom.exceptions import UnresolvableType


class MyDep:
    value: str

    def __init__(self, value="testing"):
        self.value = value


container = Container()


def example_function(resolved: MyDep, message: str) -> str:
    return resolved.value + message


def example_generator(resolved: MyDep, message: str) -> Generator[str, Any, Any]:
    yield resolved.value + message
    yield resolved.value + " finished"


@bind_to_container(container)
def another_example_function(resolved: MyDep, message: str) -> str:
    return resolved.value + message


def test_partial_application_can_be_applied_to_functions():
    partial = container.partial(example_function)
    assert partial(message=" world") == "testing world"


def test_a_decorator_can_be_used_to_bind_as_well():
    assert another_example_function(message=" hello") == "testing hello"


def test_container_values_can_be_overridden():
    assert (
        another_example_function(resolved=MyDep("replaced"), message=" hello")
        == "replaced hello"
    )


def test_incorrect_arguments_are_handled_well():
    with pytest.raises(TypeError) as err:
        another_example_function(not_the_message=" no")
    assert "unexpected keyword argument 'not_the_message'" in str(err.value)


def test_positional_arguments_raise_an_error():
    with pytest.raises(TypeError) as err:
        another_example_function("woo")
    assert "takes 0 positional arguments but 1 was given" in str(err.value)


def test_partial_application_can_be_applied_to_generators():
    partial = container.partial(example_generator)
    results = []
    for result in partial(message=" world"):
        results.append(result)
    assert results == ["testing world", "testing finished"]
