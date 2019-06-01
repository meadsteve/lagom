from typing import List

import pytest

from lagom import Construction, Container


class MySimpleDep:
    stuff: str

    def __init__(self, stuff):
        self.stuff = stuff


class MyMoreComplicatedDep:
    complicated_stuff: str

    def __init__(self, dep: List[MySimpleDep]):
        self.stuff = ",".join([d.stuff for d in dep])


@pytest.fixture
def container():
    c = Container()
    c.define(
        List[MySimpleDep],
        Construction(lambda: [MySimpleDep("One"), MySimpleDep("Two")]),
    )
    return c


def test_works_for_list_types(container: Container):
    resolved = container.resolve(List[MySimpleDep])
    assert [x.stuff for x in resolved] == ["One", "Two"]


def test_works_for_inferred_list_types(container: Container):
    resolved = container.resolve(MyMoreComplicatedDep)
    assert resolved.stuff == "One,Two"
