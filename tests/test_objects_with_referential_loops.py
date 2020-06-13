from typing import Optional

import pytest

from lagom import Container


class A1:
    def __init__(self, b: "B1"):
        pass


class B1:
    def __init__(self, a: "A1"):
        pass


class A2:
    def __init__(self, b: "B2"):
        pass


class B2:
    def __init__(self, a: Optional["A2"] = None):
        pass


def test_definition_loops_return_a_sensible_error(container: Container):
    resolved = container.resolve(B1)


def test_infinite_loops_can_be_explicitly_avoided(container: Container):
    container[A2] = lambda: A2(B2())
    resolved = container.resolve(B2)
    assert isinstance(resolved, B2)
