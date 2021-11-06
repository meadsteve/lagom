import pytest

from lagom import Singleton, Container, magic_bind_to_container
from .core_domain import SomeOtherThingAsAsingleton, SomeService, AThingIMightNeed


@pytest.mark.benchmarking
def test_magic(benchmark):
    container = Container()
    container[SomeOtherThingAsAsingleton] = Singleton(SomeOtherThingAsAsingleton)

    @magic_bind_to_container(container, shared=[SomeService])
    def do_work(thing: AThingIMightNeed):
        thing.do_it()

    def do_pretend_work():
        for _ in range(3000):
            do_work()
        return True

    assert benchmark(do_pretend_work)
