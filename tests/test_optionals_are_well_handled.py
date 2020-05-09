from typing import Optional

from lagom import Container


class MySimpleDep:
    extra_stuff = "yes"


class MyDepWithAnOptional:
    success = "yes"

    def __init__(self, dep: Optional[MySimpleDep] = None):
        self.dep = dep


def test_missing_optional_dependencies_cause_no_errors(container: Container):
    resolved = container.resolve(MyDepWithAnOptional)
    assert resolved.dep.extra_stuff == "yes"  # type: ignore


def test_works_for_registered_types(container: Container):
    resolved = container.resolve(MyDepWithAnOptional)
    assert resolved.dep.extra_stuff == "yes"  # type: ignore
