from random import random
from typing import Generator, Any

import pytest

from lagom import Container, bind_to_container


class SomeCache:
    def __init__(self):
        self._init_random = random()

    def value(self):
        return self._init_random


class MyDepOne:
    value: Any

    def __init__(self, cache: SomeCache):
        self.value = cache.value()


class MyDepTwo:
    other_value: Any

    def __init__(self, cache: SomeCache):
        self.other_value = cache.value()


container = Container()


@bind_to_container(container)
def example_function(dep_one: MyDepOne, dep_two: MyDepTwo):
    return {"a": dep_one.value, "b": dep_two.other_value}


@bind_to_container(container, shared=[SomeCache])
def example_function_with_invocation_level_sharing(
    dep_one: MyDepOne, dep_two: MyDepTwo
):
    return {"a": dep_one.value, "b": dep_two.other_value}


def test_by_default_all_resources_are_reconstructed():
    result = example_function()
    assert result["a"] != result["b"]


def test_invocation_level_singletons_can_be_defined():
    result = example_function_with_invocation_level_sharing()
    assert result["a"] == result["b"]


def test_invocation_level_singletons_are_not_shared_across_calls():
    call_one = example_function_with_invocation_level_sharing()
    call_two = example_function_with_invocation_level_sharing()

    assert call_one["a"] != call_two["a"]
