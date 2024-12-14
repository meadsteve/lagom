from typing import Iterator

import pytest

from lagom import (
    Singleton,
    Container,
    context_container,
    magic_bind_to_container,
    ExplicitContainer,
    bind_to_container,
    injectable,
    context_dependency_definition,
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
        for _ in range(10):
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
        for _ in range(10):
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
        for _ in range(10):
            do_work()
        return True

    assert benchmark(do_pretend_work)


@pytest.mark.benchmarking
def test_context_partials(benchmark):
    container = Container()
    container[SomeOtherThingAsAsingleton] = Singleton(SomeOtherThingAsAsingleton)

    @context_dependency_definition(container)
    def _load_dep_then_clean(c) -> Iterator[SomeService]:
        try:
            yield SomeService(c[SomeOtherThingAsAsingleton])
        finally:
            pass

    @bind_to_container(
        context_container(container, context_types=[SomeService]), shared=[SomeService]
    )
    def do_work(thing: AThingIMightNeed = injectable):
        thing.do_it()

    def do_pretend_work():
        for _ in range(10):
            do_work()
        return True

    assert benchmark(do_pretend_work)
