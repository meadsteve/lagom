from typing import Callable


from lagom import Container
from lagom.experimental.definitions import PlainFunction


class ClassNeedingAFunction:
    def __init__(self, adder: Callable[[int, int], int]):
        self.adder = adder

    def trigger(self, x, y):
        adder = self.adder
        return adder(x, y)


def add_stuff(x: int, y: int) -> int:
    return x + y


def test_ways_of_constructing_functions_can_be_provided(container: Container):
    container[Callable[[int, int], int]] = PlainFunction(add_stuff)
    erm = container[ClassNeedingAFunction]
    assert erm.trigger(2, 3) == 5
