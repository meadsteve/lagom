from abc import ABC
from typing import List

import pytest

from lagom import Construction, Container, Alias


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
def container():
    c = Container()
    c.define(MySimpleAbc, Construction(lambda: MySimpleDep("hooray")))
    return c


def test_registered_concrete_class_is_loaded(container: Container):
    resolved = container.resolve(MySimpleAbc)
    assert resolved.stuff == "hooray"


def test_registered_concrete_class_is_used_for_other_objects(container: Container):
    resolved = container.resolve(MyMoreComplicatedDep)
    assert resolved.stuff == "hooray"


def test_alias_can_be_defined(container: Container):
    container.define(AnotherAbc, Alias(AnotherConcrete))
    resolved = container.resolve(AnotherAbc)
    assert resolved.stuff == "full"
