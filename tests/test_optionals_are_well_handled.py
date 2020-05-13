from typing import Optional

from lagom import Container


class MySimpleDep:
    extra_stuff = "yes"


class MyComplexDep:
    extra_stuff = "yes"

    def __init__(self, something):
        pass


class MyDepWithAnOptional:
    success = "yes"

    def __init__(self, dep: Optional[MySimpleDep] = None):
        self.dep = dep


class MyDepWithAnOptionalThatCantBeBuilt:
    success = "yes"

    def __init__(self, dep: Optional[MyComplexDep] = "weird default"):  # type: ignore
        self.dep = dep


def test_missing_optional_dependencies_cause_no_errors(container: Container):
    resolved = container.resolve(MyDepWithAnOptionalThatCantBeBuilt)
    assert resolved.success == "yes"  # type: ignore


def test_defaults_for_optional_types_are_honoured(container: Container):
    resolved = container.resolve(MyDepWithAnOptionalThatCantBeBuilt)
    assert resolved.dep == "weird default"  # type: ignore


def test_optional_dependencies_are_understood_and_injected(container: Container):
    resolved = container.resolve(MyDepWithAnOptional)
    assert resolved.dep.extra_stuff == "yes"  # type: ignore


def test_we_can_ask_for_optional_things_that_cant_be_constructed(container: Container):
    assert container.resolve(Optional[MyComplexDep]) is None
