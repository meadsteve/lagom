from typing import Collection, Callable

from lagom import Container, FunctionCollection


def _func_a(input: str) -> str:
    return f"func_a({input})"


def _func_b(input: str) -> str:
    return f"func_b({input})"


SomeSignature = Callable[[str], str]


def test_function_collections_are_built_from_lists_of_funcs(container: Container):
    container[Collection[SomeSignature]] = [_func_b, _func_a]  # type: ignore # sadly collection still can't be used like this
    assert type(container[Collection[SomeSignature]]) == FunctionCollection  # type: ignore # sadly collection still can't be used like this


def test_the_function_collection_type_can_be_used_as_the_definition(
    container: Container,
):
    container[FunctionCollection[SomeSignature]] = [_func_b, _func_a]
    assert type(container[FunctionCollection[SomeSignature]]) == FunctionCollection
