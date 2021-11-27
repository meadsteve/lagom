from contextlib import contextmanager
from typing import Iterator

from context_based import ContextContainer
from lagom import Container, dependency_definition


class SomeDep:
    global_clean_up_has_happened = False


container = Container()


@dependency_definition(container)
@contextmanager
def _load_a_some_dep_then_clean(c) -> Iterator[SomeDep]:
    try:
        yield SomeDep()
    finally:
        SomeDep.global_clean_up_has_happened = True


def test_clean_up_of_loaded_contexts_happens_on_container_exit():
    SomeDep.global_clean_up_has_happened = False

    with ContextContainer(container, context_types=[SomeDep]) as context_container:
        assert isinstance(context_container[SomeDep], SomeDep)
        assert not SomeDep.global_clean_up_has_happened
    assert SomeDep.global_clean_up_has_happened
