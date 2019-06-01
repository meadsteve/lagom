import pytest

from lagom import Singleton, Construction, Container


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
def container():
    c = Container()
    c.define(MyBasicDep, Singleton(MyBasicDep))
    c.define(
        MyMoreComplicatedDep, Singleton(Construction(lambda: MyMoreComplicatedDep(5)))
    )
    c.define(MyCompositeDep, Singleton(MyCompositeDep))
    return c


def test_singleton_is_only_resolved_once(container: Container):
    first = container.resolve(MyBasicDep)
    second = container.resolve(MyBasicDep)
    assert first is not None
    assert first is second


def test_singleton_can_have_construction_logic(container: Container):
    first = container.resolve(MyMoreComplicatedDep)
    second = container.resolve(MyMoreComplicatedDep)
    assert first.sum_number == 5
    assert first is second


def test_singleton_can_compose_other_dependencies(container: Container):
    first = container.resolve(MyCompositeDep)
    second = container.resolve(MyCompositeDep)
    assert type(first.a) == MyBasicDep
    assert type(first.b) == MyMoreComplicatedDep
    assert first is second
