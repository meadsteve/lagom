import inspect
from random import random
from typing import Any, ClassVar


from lagom import Container, bind_to_container, Singleton


class SomeCache:
    loaded: ClassVar[bool] = False

    def __init__(self):
        SomeCache.loaded = True
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


def test_by_default_all_resources_are_reconstructed(container: Container):
    @bind_to_container(container)
    def example_function(dep_one: MyDepOne, dep_two: MyDepTwo):
        return {"a": dep_one.value, "b": dep_two.other_value}

    result = example_function()
    assert result["a"] != result["b"]


def test_invocation_level_singletons_can_be_defined(container: Container):
    @bind_to_container(container, shared=[SomeCache])
    def example_function_with_invocation_level_sharing(
        dep_one: MyDepOne, dep_two: MyDepTwo
    ):
        return {"a": dep_one.value, "b": dep_two.other_value}

    result = example_function_with_invocation_level_sharing()
    assert result["a"] == result["b"]


def test_invocation_level_singletons_are_not_shared_across_calls(container: Container):
    @bind_to_container(container, shared=[SomeCache])
    def example_function_with_invocation_level_sharing(
        dep_one: MyDepOne, dep_two: MyDepTwo
    ):
        return {"a": dep_one.value, "b": dep_two.other_value}

    call_one = example_function_with_invocation_level_sharing()
    call_two = example_function_with_invocation_level_sharing()

    assert call_one["a"] != call_two["a"]


def test_that_shared_types_are_lazy_loaded(container: Container):
    SomeCache.loaded = False

    @bind_to_container(container, shared=[SomeCache])
    def example_function_that_defines_but_doesnt_use_sharing():
        return "ok"

    example_function_that_defines_but_doesnt_use_sharing()
    assert not SomeCache.loaded


def test_partial_application_returns_something_that_is_considered_a_function(
    container: Container,
):
    @bind_to_container(container, shared=[SomeCache])
    def example_function_with_shared():
        return "ok"

    inspect.isfunction(example_function_with_shared)


def test_invocation_level_singletons_respect_container_singletons(container: Container):

    container[SomeCache] = Singleton(SomeCache)

    @bind_to_container(container, shared=[SomeCache])
    def example_function_with_invocation_level_sharing(
        dep_one: MyDepOne, dep_two: MyDepTwo
    ):
        return {"a": dep_one.value, "b": dep_two.other_value}

    result_one = example_function_with_invocation_level_sharing()
    result_two = example_function_with_invocation_level_sharing()

    assert result_one["a"] == result_one["b"]
    assert result_one["a"] == result_two["a"]
