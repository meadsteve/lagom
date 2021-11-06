import pytest

from lagom import (
    Singleton,
    Container,
    magic_bind_to_container,
    ExplicitContainer,
    bind_to_container,
    injectable,
)
from .core_domain import SomeOtherThingAsAsingleton, SomeService, AThingIMightNeed


@pytest.mark.benchmarking
def test_magic(benchmark):
    container = Container()
    container[SomeOtherThingAsAsingleton] = Singleton(SomeOtherThingAsAsingleton)

    @magic_bind_to_container(container, shared=[SomeService])
    def do_work(thing: AThingIMightNeed):
        thing.do_it()

    def do_pretend_work():
        for _ in range(1000):
            do_work()
        return True

    assert benchmark(do_pretend_work)


@pytest.mark.benchmarking
def test_plain(benchmark):
    container = Container()
    container[SomeOtherThingAsAsingleton] = Singleton(SomeOtherThingAsAsingleton)

    @bind_to_container(container, shared=[SomeService])
    def do_work(thing: AThingIMightNeed = injectable):
        thing.do_it()

    def do_pretend_work():
        for _ in range(1000):
            do_work()
        return True

    assert benchmark(do_pretend_work)


@pytest.mark.benchmarking
def test_optimised(benchmark):
    container = ExplicitContainer()
    container[SomeOtherThingAsAsingleton] = SomeOtherThingAsAsingleton()
    container[SomeService] = lambda c: SomeService(c[SomeOtherThingAsAsingleton])
    container[AThingIMightNeed] = lambda c: AThingIMightNeed(c[SomeService])

    @bind_to_container(container, shared=[SomeService])
    def do_work(thing: AThingIMightNeed = injectable):
        thing.do_it()

    def do_pretend_work():
        for _ in range(1000):
            do_work()
        return True

    assert benchmark(do_pretend_work)
