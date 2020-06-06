import pytest

from lagom import Container
from lagom.exceptions import DuplicateDefinition


class InitialDep:
    pass


class SomeMockForTesting(InitialDep):
    pass


class SomeMockThatDoesntEventExtend:
    pass


def test_deps_can_be_overridden_by_a_child_class(container: Container):
    container.define(InitialDep, lambda: SomeMockForTesting())
    resolved = container.resolve(InitialDep)
    assert type(resolved) == SomeMockForTesting


def test_deps_can_be_overridden_by_anything(container: Container):
    container.define(InitialDep, lambda: SomeMockThatDoesntEventExtend())  # type: ignore
    resolved = container.resolve(InitialDep)
    assert type(resolved) == SomeMockThatDoesntEventExtend


def test_explicit_definitions_can_only_be_made_once(container: Container):
    container.define(InitialDep, lambda: SomeMockForTesting())

    with pytest.raises(DuplicateDefinition):
        container.define(
            InitialDep, lambda: SomeMockThatDoesntEventExtend()  # type: ignore
        )
