from contextlib import contextmanager
from typing import Iterator, Generator, ContextManager

import pytest

from lagom import Container, dependency_definition
from lagom.context_based import ContextContainer
from lagom.exceptions import InvalidDependencyDefinition


class SomeDep:
    global_clean_up_has_happened = False


class SomeWrapperDep:
    global_clean_up_has_happened = False

    def __init__(self, dep: SomeDep):
        pass


class SomeNotProperlySetupDef:
    pass


class Thing:
    contents: str

    def __init__(self, contents: str):
        self.contents = contents


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


def test_context_instances_are_not_singletons():
    with ContextContainer(container, context_types=[SomeDep]) as context_container:
        one = context_container[SomeDep]
        two = context_container[SomeDep]
        assert one is not two


def test_context_instances_can_be_made_singletons():
    SomeDep.global_clean_up_has_happened = False
    with ContextContainer(
        container, context_types=[], context_singletons=[SomeDep]
    ) as context_container:
        one = context_container[SomeDep]
        two = context_container[SomeDep]
        assert one is two
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
    assert f"A ContextManager[{str(SomeNotProperlySetupDef)}] should be defined" in str(
        failure.value
    )


def test_it_works_with_actual_context_managers():
    class ThingManager:
        def __enter__(self):
            return Thing("managed thing")

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    container[ContextManager[Thing]] = ThingManager  # type: ignore

    with ContextContainer(container, context_types=[Thing]) as context_container:
        assert context_container.resolve(Thing).contents == "managed thing"
