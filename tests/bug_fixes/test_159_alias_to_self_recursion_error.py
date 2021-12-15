# https://github.com/meadsteve/lagom/issues/159
import abc

from lagom import Container


class AbstractFoo(abc.ABC):
    pass


class Foo(AbstractFoo):
    pass


def test_it_now_works():
    container = Container()
    container[AbstractFoo] = Foo

    # This is/was the root cause of the issue
    container[Foo] = Foo

    assert isinstance(container[AbstractFoo], Foo)
