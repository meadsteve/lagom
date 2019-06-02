import pytest

from lagom import Construction, Container


class InitialDep:
    pass


class SomeMockForTesting(InitialDep):
    pass


class SomeMockThatDoesntEventExtend:
    pass


@pytest.fixture
def container():
    c = Container()
    c.define(InitialDep, Construction(lambda: InitialDep()))
    return c


def test_deps_can_be_overridden_by_a_child_class(container: Container):
    container.define(InitialDep, Construction(lambda: SomeMockForTesting()))
    resolved = container.resolve(InitialDep)
    assert type(resolved) == SomeMockForTesting


def test_deps_can_be_overridden_by_anything(container: Container):
    container.define(InitialDep, Construction(lambda: SomeMockThatDoesntEventExtend()))
    resolved = container.resolve(InitialDep)
    assert type(resolved) == SomeMockThatDoesntEventExtend
