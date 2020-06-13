import pytest

from lagom import Container


class A:
    def __init__(self, b: "B"):
        pass


class B:
    def __init__(self, a: "A"):
        pass


@pytest.mark.skip(reason="Up next to be fixed")
def test_definition_loops_return_a_sensible_error(container: Container):
    resolved = container.resolve(B)
