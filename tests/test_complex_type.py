from typing import List

import pytest

from lagom import Container


class MySimpleDep:
    stuff: str

    def __init__(self, stuff):
        self.stuff = stuff


class MyMoreComplicatedDep:
    complicated_stuff: str

    def __init__(self, dep: List[MySimpleDep]):
        self.stuff = ",".join([d.stuff for d in dep])


@pytest.fixture
def container_with_list(container: Container):
    container.define(
        List[MySimpleDep], lambda: [MySimpleDep("One"), MySimpleDep("Two")],
    )
    return container


def test_works_for_list_types(container_with_list: Container):
    resolved = container_with_list.resolve(List[MySimpleDep])
    assert [x.stuff for x in resolved] == ["One", "Two"]


def test_works_for_inferred_list_types(container_with_list: Container):
    resolved = container_with_list.resolve(MyMoreComplicatedDep)
    assert resolved.stuff == "One,Two"
