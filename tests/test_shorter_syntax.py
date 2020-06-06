from abc import ABC

from lagom import Container


class MySimpleDep:
    stuff: str

    def __init__(self, stuff):
        self.stuff = stuff


class MyMoreComplicatedDep:
    stuff: str

    def __init__(self, dep: MySimpleDep):
        self.stuff = dep.stuff


class AnotherAbc(ABC):
    stuff: str = "empty"


class AnotherConcrete(AnotherAbc):
    stuff = "full"


def test_deps_can_be_referenced_by_square_brackets(container: Container):
    container[MySimpleDep] = lambda: MySimpleDep("hooray")
    resolved = container[MySimpleDep]
    assert resolved.stuff == "hooray"


def test_construction_type_can_be_omitted(container: Container):
    container[MySimpleDep] = lambda: MySimpleDep("hooray")
    resolved = container[MySimpleDep]
    assert resolved.stuff == "hooray"


def test_singleton_type_can_be_omitted(container: Container):
    container[MySimpleDep] = MySimpleDep("hooray")
    one = container[MySimpleDep]
    two = container[MySimpleDep]
    assert one is not None
    assert one is two


def test_alias_can_be_omitted(container: Container):
    container[AnotherAbc] = AnotherConcrete
    resolved = container[AnotherAbc]
    assert type(resolved) == AnotherConcrete
    assert resolved.stuff == "full"
