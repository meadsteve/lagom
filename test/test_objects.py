from typing import List

import pytest

from lagom import Construction, Container


class MySimpleDep:
    stuff: str

    def __init__(self, stuff):
        self.stuff = stuff


class MyMoreComplicatedDep:
    complicated_stuff: str

    def __init__(self, dep: MySimpleDep):
        self.stuff = "complicated " + dep.stuff


@pytest.fixture
def container():
    c = Container()
    c.define(MySimpleDep, Construction(lambda: MySimpleDep("Top stuff")))
    return c


def test_works_for_registered_types(container):
    resolved = container.resolve(MySimpleDep)
    assert resolved.stuff == "Top stuff"


def test_works_if_every_item_in_the_constructor_can_be_figured_out(container):
    resolved = container.resolve(MyMoreComplicatedDep)
    assert resolved.stuff == "complicated Top stuff"


@pytest.mark.parametrize("dep", [MySimpleDep, MyMoreComplicatedDep])
def test_dependencies_are_built_each_request(container: Container, dep):
    first = container.resolve(dep)
    second = container.resolve(dep)
    assert first is not second
