from typing import Collection, Callable

from lagom import Container, FunctionCollection


def _func_a(input: str) -> str:
    return f"func_a({input})"


def _func_b(input: str) -> str:
    return f"func_b({input})"


def test_function_collections_are_built_from_lists_of_funcs(container: Container):
    container[Collection[Callable[[str], str]]] = [_func_b, _func_a]  # type: ignore # sadly collection still can't be used like this
    assert type(container[Collection[Callable[[str], str]]]) == FunctionCollection  # type: ignore # sadly collection still can't be used like this


def test_the_function_collection_type_can_be_used_as_the_definition(
    container: Container,
):
    container[FunctionCollection[Callable[[str], str]]] = [_func_b, _func_a]
    assert (
        type(container[FunctionCollection[Callable[[str], str]]]) == FunctionCollection
    )
