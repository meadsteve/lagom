from contextlib import contextmanager
from typing import Iterator, Generator

import pytest

from context_based import ContextContainer
from lagom import Container, dependency_definition
from lagom.exceptions import InvalidDependencyDefinition


class SomeDep:
    global_clean_up_has_happened = False


class SomeWrapperDep:
    global_clean_up_has_happened = False

    def __init__(self, dep: SomeDep):
        pass


class SomeNotProperlySetupDef:
    pass


container = Container()


@dependency_definition(container)
@contextmanager
def _load_a_some_dep_then_clean() -> Generator[SomeDep, None, None]:
    try:
        yield SomeDep()
    finally:
        SomeDep.global_clean_up_has_happened = True


@dependency_definition(container)
@contextmanager
def _load_a_some_wrapper_dep_then_clean(c) -> Iterator[SomeWrapperDep]:
    try:
        yield SomeWrapperDep(c[SomeDep])
    finally:
        SomeWrapperDep.global_clean_up_has_happened = True


def test_clean_up_of_loaded_contexts_happens_on_container_exit():
    SomeDep.global_clean_up_has_happened = False

    with ContextContainer(container, context_types=[SomeDep]) as context_container:
        assert isinstance(context_container[SomeDep], SomeDep)
        assert not SomeDep.global_clean_up_has_happened
    assert SomeDep.global_clean_up_has_happened


def test_clean_up_of_loaded_contexts_happens_recursively_on_container_exit():
    SomeDep.global_clean_up_has_happened = False
    SomeWrapperDep.global_clean_up_has_happened = False

    with ContextContainer(
        container, context_types=[SomeDep, SomeWrapperDep]
    ) as context_container:
        assert isinstance(context_container[SomeWrapperDep], SomeWrapperDep)
        assert not SomeDep.global_clean_up_has_happened
        assert not SomeWrapperDep.global_clean_up_has_happened

    assert SomeDep.global_clean_up_has_happened
    assert SomeWrapperDep.global_clean_up_has_happened


def test_it_fails_if_the_dependencies_arent_defined_correctly():
    with pytest.raises(InvalidDependencyDefinition) as failure:
        with ContextContainer(
            container, context_types=[SomeNotProperlySetupDef]
        ) as context_container:
            context_container.resolve(SomeNotProperlySetupDef)
    assert "Either Iterator" in str(failure.value)
    assert "or Generator" in str(failure.value)
    assert "should be defined" in str(failure.value)
