from typing import Generator, Any

import pytest

from lagom import Container, bind_to_container


class MyDep:
    value: str

    def __init__(self, value="testing"):
        self.value = value


container = Container()


def example_function(message: str, resolved: MyDep) -> str:
    return resolved.value + message


def example_generator(message: str, resolved: MyDep) -> Generator[str, Any, Any]:
    yield resolved.value + message
    yield resolved.value + " finished"


@bind_to_container(container)
def another_example_function(message: str, resolved: MyDep) -> str:
    return resolved.value + message


def test_partial_application_can_be_applied_to_functions_with_named_args():
    partial = container.partial(example_function)
    assert partial(message=" world") == "testing world"


def test_partial_application_can_be_applied_to_functions_with_positional_args_first():
    partial = container.partial(example_function)
    assert partial(" world") == "testing world"


def test_a_decorator_can_be_used_to_bind_as_well():
    assert another_example_function(message=" hello") == "testing hello"


def test_a_decorator_can_be_used_to_bind_and_with_positional_arguments():
    assert another_example_function(" hello") == "testing hello"


def test_container_values_can_be_overridden():
    assert (
        another_example_function(resolved=MyDep("replaced"), message=" hello")
        == "replaced hello"
    )


def test_incorrect_arguments_are_handled_well():
    with pytest.raises(TypeError) as err:
        another_example_function(not_the_message=" no")
    assert "unexpected keyword argument 'not_the_message'" in str(err.value)


def test_partial_application_can_be_applied_to_generators():
    partial = container.partial(example_generator)
    results = []
    for result in partial(message=" world"):
        results.append(result)
    assert results == ["testing world", "testing finished"]
