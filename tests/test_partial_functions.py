import inspect
from typing import Generator, Any, ClassVar

import pytest

from lagom import Container, bind_to_container
from lagom.exceptions import UnableToInvokeBoundFunction


class MyDep:
    loaded: ClassVar[bool] = False
    value: str

    def __init__(self, value="testing"):
        MyDep.loaded = True
        self.value = value


class CantBeAutoConstructed:
    def __init__(self, something):
        pass


container = Container()


def example_function(message: str, resolved: MyDep) -> str:
    return resolved.value + message


def example_generator(message: str, resolved: MyDep) -> Generator[str, Any, Any]:
    yield resolved.value + message
    yield resolved.value + " finished"


@bind_to_container(container)
def another_example_function(message: str, resolved: MyDep) -> str:
    """
    I am DOCS
    """
    return resolved.value + message


@bind_to_container(container)
def failing_to_construct_function(try_to_resolve: CantBeAutoConstructed) -> str:
    return "doesnt matter"


def test_partial_application_can_be_applied_to_functions_with_named_args():
    partial = container.partial(example_function)
    assert partial(message=" world") == "testing world"


def test_partial_application_returns_something_that_is_considered_a_function():
    partial = container.partial(example_function)
    inspect.isfunction(partial)


def test_partial_application_can_be_applied_to_functions_with_positional_args_first():
    partial = container.partial(example_function)
    assert partial(" world") == "testing world"


def test_passed_in_arguments_are_used_over_container_generated_ones_when_positional():
    partial = container.partial(example_function)
    assert partial(" world", MyDep("overridden")) == "overridden world"


def test_passed_in_arguments_are_used_over_container_generated_ones_when_named():
    partial = container.partial(example_function)
    assert partial(message=" world", resolved=MyDep("overridden")) == "overridden world"


def test_a_decorator_can_be_used_to_bind_as_well():
    assert another_example_function(message=" hello") == "testing hello"


def test_a_decorator_can_be_used_to_bind_and_with_positional_arguments():
    assert another_example_function(" hello") == "testing hello"


def test_container_values_can_be_overridden():
    assert (
        another_example_function(resolved=MyDep("replaced"), message=" hello")
        == "replaced hello"
    )


def test_missing_call_arguments_results_in_sensible_error_messages():
    with pytest.raises(TypeError) as err:
        another_example_function()
    assert "another_example_function() missing 1 required positional argument" in str(
        err.value
    )


def test_incorrect_arguments_are_handled_well():
    with pytest.raises(TypeError) as err:
        another_example_function(not_the_message=" no")
    assert "unexpected keyword argument 'not_the_message'" in str(err.value)


def test_if_a_typed_argument_cant_be_constructed_a_helpful_exception_is_returned():
    with pytest.raises(UnableToInvokeBoundFunction) as err:
        failing_to_construct_function()
    assert (
        "The container could not construct the following types: CantBeAutoConstructed"
        in str(err.value)
    )


def test_partial_application_can_be_applied_to_generators():
    partial = container.partial(example_generator)
    results = []
    for result in partial(message=" world"):
        results.append(result)
    assert results == ["testing world", "testing finished"]


def test_deps_are_loaded_at_call_time_not_definition_time():
    MyDep.loaded = False

    @bind_to_container(container)
    def some_random_unused_function(message: str, resolved: MyDep) -> str:
        return resolved.value + message

    assert not MyDep.loaded


def test_name_and_docs_are_kept():
    assert another_example_function.__name__ == "another_example_function"
    assert another_example_function.__doc__ == "\n    I am DOCS\n    "
