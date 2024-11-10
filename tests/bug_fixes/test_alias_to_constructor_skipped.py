"""
https://github.com/meadsteve/lagom/issues/150
"""

from lagom import Container


class Something:
    def __init__(self, value="the default"):
        self.value = value


class SomethingInterface:
    value: str


def test_an_alias_doesnt_skip_a_defined_constructor():
    container = Container()
    container[Something] = lambda: Something("the correct value")
    container[SomethingInterface] = Something  # type: ignore

    assert container[SomethingInterface].value == "the correct value"
