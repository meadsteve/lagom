import pytest

from lagom.util.functional import arity, FunctionCollection


def _func_a():
    pass


def _func_b():
    pass


@pytest.mark.parametrize(
    "test_func,expected_arity",
    [(lambda: 0, 0), (lambda x: x, 1), (lambda x, y: x + y, 2)],
)
def test_we_can_get_arity_from_functions(test_func, expected_arity: int):
    assert arity(test_func) == expected_arity


def test_function_collections_are_the_same_if_they_have_the_same_functions():
    assert FunctionCollection(_func_a, _func_b) == FunctionCollection(_func_a, _func_b)


def test_function_collections_are_iterable():
    collected_funcs = [func for func in FunctionCollection(_func_a, _func_b)]
    assert collected_funcs == [_func_a, _func_b]
