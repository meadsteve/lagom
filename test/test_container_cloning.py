import pytest

from lagom import Construction, Container
from lagom.exceptions import DuplicateDefinition


class InitialDep:
    pass


class SomeMockForTesting(InitialDep):
    pass


class SomeOtherMockForTesting(InitialDep):
    pass


def test_container_can_be_cloned_and_maintains_separate_deps(container: Container):
    new_container = container.clone()
    new_container.define(InitialDep, Construction(lambda: SomeMockForTesting()))

    assert isinstance(new_container[InitialDep], SomeMockForTesting)
    assert isinstance(container[InitialDep], InitialDep)


def test_a_cloned_container_can_have_deps_overwritten(container: Container):
    container.define(InitialDep, Construction(lambda: SomeMockForTesting()))
    new_container = container.clone()
    new_container.define(InitialDep, Construction(lambda: SomeOtherMockForTesting()))

    assert isinstance(new_container[InitialDep], SomeOtherMockForTesting)
