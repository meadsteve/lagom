from typing import Generator, AsyncGenerator

import pytest

from lagom import Container, bind_to_container
from lagom.exceptions import UnresolvableType


class MyDep:
    value: str = "testing"


container = Container()


def example_function(resolved: MyDep, message: str) -> str:
    return resolved.value + message


def example_generator(resolved: MyDep, message: str) -> Generator:
    yield resolved.value + message


@bind_to_container(container)
def another_example_function(resolved: MyDep, message: str) -> str:
    return resolved.value + message


def test_partial_application_can_be_applied_to_functions():
    partial = container.partial(example_function)
    assert partial(message=" world") == "testing world"


def test_a_decorator_can_be_used_to_bind_as_well():
    assert another_example_function(message=" hello") == "testing hello"


def test_partial_application_can_be_applied_to_generators():
    partial = container.partial(example_generator)
    results = []
    for result in partial(message=" world"):
        results.append(result)
    assert results == ["testing world"]
