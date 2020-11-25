from abc import ABC, abstractmethod
import pytest

from lagom import Container, Alias
from lagom.exceptions import UnresolvableType


class MySimpleAbc(ABC):
    stuff: str = "empty"

    @abstractmethod
    def bloop(self):
        pass


class MySimpleDep(MySimpleAbc):
    stuff: str

    def __init__(self, stuff):
        self.stuff = stuff

    def bloop(self):
        return "beep"


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
    container.define(MySimpleAbc, lambda: MySimpleDep("hooray"))  # type: ignore
    return container


def test_registered_concrete_class_is_loaded(container_with_abc: Container):
    resolved = container_with_abc.resolve(MySimpleAbc)  # type: ignore
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


def test_trying_to_build_an_abc_raises_an_error(container: Container):
    with pytest.raises(UnresolvableType) as e_info:
        container.resolve(MySimpleAbc)  # type: ignore
    assert "Unable to construct Abstract type MySimpleAbc" in str(e_info.value)
    assert "Try defining an alias or a concrete class to construct" in str(e_info.value)
