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
