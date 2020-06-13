import pytest

from lagom import Container


class MySimpleDep:
    stuff: str

    def __init__(self, stuff):
        self.stuff = stuff


class MyMoreComplicatedDep:
    complicated_stuff: str

    def __init__(self, dep: MySimpleDep):
        self.stuff = "complicated " + dep.stuff


class DepAsAForwardRef:
    def __init__(self, dep: "SomethingDefinedLater") -> None:
        pass


class SomethingDefinedLater:
    pass


class TypedSelf:
    def __init__(self: "TypedSelf"):
        pass


@pytest.fixture
def container_with_simple_dep(container: Container):
    container.define(MySimpleDep, lambda: MySimpleDep("Top stuff"))
    return container


def test_works_for_registered_types(container_with_simple_dep):
    resolved = container_with_simple_dep.resolve(MySimpleDep)
    assert resolved.stuff == "Top stuff"


def test_works_if_every_item_in_the_constructor_can_be_figured_out(
    container_with_simple_dep,
):
    resolved = container_with_simple_dep.resolve(MyMoreComplicatedDep)
    assert resolved.stuff == "complicated Top stuff"


@pytest.mark.parametrize("dep", [MySimpleDep, MyMoreComplicatedDep])
def test_dependencies_are_built_each_request(container_with_simple_dep: Container, dep):
    first = container_with_simple_dep.resolve(dep)
    second = container_with_simple_dep.resolve(dep)
    assert first is not second


def test_forward_refs_are_fine(container: Container):
    resolved = container.resolve(DepAsAForwardRef)
    assert isinstance(resolved, DepAsAForwardRef)


def test_explicitly_typing_self_doesnt_cause_problems(container: Container):
    resolved = container.resolve(TypedSelf)
    assert isinstance(resolved, TypedSelf)
