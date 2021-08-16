from typing import Callable

from lagom import Container, FunctionCollection


def _func_a(input: str) -> str:
    return f"func_a({input})"


def _func_b(input: str) -> str:
    return f"func_b({input})"


SomeSignature = Callable[[str], str]


def test_a_function_collection_can_be_used_by_a_container(
    container: Container,
):
    container[FunctionCollection[SomeSignature]] = FunctionCollection(_func_a, _func_b)
    assert container[FunctionCollection[SomeSignature]] == [_func_a, _func_b]
