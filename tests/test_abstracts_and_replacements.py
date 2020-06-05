from abc import ABC
import pytest

from lagom import Container, Alias


class MySimpleAbc(ABC):
    stuff: str = "empty"

    def bloop(self):
        return "beep"


class MySimpleDep(MySimpleAbc):
    stuff: str

    def __init__(self, stuff):
        self.stuff = stuff


class MyMoreComplicatedDep:
    complicated_stuff: str

    def __init__(self, dep: MySimpleAbc):
        self.stuff = dep.stuff


class AnotherAbc(ABC):
    stuff: str = "empty"


class AnotherConcrete(AnotherAbc):
    stuff = "full"


@pytest.fixture
def container_with_abc(container: Container):
    container.define(MySimpleAbc, lambda: MySimpleDep("hooray"))
    return container


def test_registered_concrete_class_is_loaded(container_with_abc: Container):
    resolved = container_with_abc.resolve(MySimpleAbc)
    assert resolved.stuff == "hooray"


def test_registered_concrete_class_is_used_for_other_objects(
    container_with_abc: Container,
):
    resolved = container_with_abc.resolve(MyMoreComplicatedDep)
    assert resolved.stuff == "hooray"


def test_alias_can_be_defined(container_with_abc: Container):
    container_with_abc.define(AnotherAbc, Alias(AnotherConcrete))
    resolved = container_with_abc.resolve(AnotherAbc)
    assert resolved.stuff == "full"


def test_aliases_can_be_pointless_and_self_referential(container: Container):
    container.define(AnotherConcrete, Alias(AnotherConcrete))
    resolved = container.resolve(AnotherConcrete)
    assert resolved.stuff == "full"
