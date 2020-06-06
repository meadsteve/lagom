import pytest

from lagom import Singleton, Container


class MyBasicDep:
    pass


class MyMoreComplicatedDep:
    def __init__(self, some_number):
        self.sum_number = some_number


class MyCompositeDep:
    def __init__(self, a: MyBasicDep, b: MyMoreComplicatedDep):
        self.a = a
        self.b = b


@pytest.fixture
def container_with_deps(container: Container):
    container.define(MyBasicDep, Singleton(MyBasicDep))
    container.define(MyMoreComplicatedDep, Singleton(lambda: MyMoreComplicatedDep(5)))
    container.define(MyCompositeDep, Singleton(MyCompositeDep))
    return container


def test_singleton_is_only_resolved_once(container_with_deps: Container):
    first = container_with_deps.resolve(MyBasicDep)
    second = container_with_deps.resolve(MyBasicDep)
    assert first is not None
    assert first is second


def test_singleton_can_have_construction_logic(container_with_deps: Container):
    first = container_with_deps.resolve(MyMoreComplicatedDep)
    second = container_with_deps.resolve(MyMoreComplicatedDep)
    assert first.sum_number == 5
    assert first is second


def test_singleton_can_compose_other_dependencies(container_with_deps: Container):
    first = container_with_deps.resolve(MyCompositeDep)
    second = container_with_deps.resolve(MyCompositeDep)
    assert type(first.a) == MyBasicDep
    assert type(first.b) == MyMoreComplicatedDep
    assert first is second
