import pytest

from lagom.util.functional import arity


@pytest.mark.parametrize(
    "test_func,expected_arity",
    [(lambda: 0, 0), (lambda x: x, 1), (lambda x, y: x + y, 2)],
)
def test_we_can_get_arity_from_functions(test_func, expected_arity: int):
    assert arity(test_func) == expected_arity
