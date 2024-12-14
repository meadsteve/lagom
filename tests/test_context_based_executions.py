from contextlib import contextmanager
from typing import Iterator, Generator, ContextManager

import pytest

import lagom
from lagom import (
    Container,
    dependency_definition,
    context_container,
)
from lagom.decorators import context_dependency_definition
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


class ThingManager:
    def __enter__(self):
        return Thing("managed thing")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


container = Container()


container[ContextManager[Thing]] = ThingManager  # type: ignore


@dependency_definition(container)
@contextmanager
def _load_a_some_dep_then_clean() -> Generator[SomeDep, None, None]:
    try:
        yield SomeDep()
    finally:
        SomeDep.global_clean_up_has_happened = True


@context_dependency_definition(container)
def _load_a_some_wrapper_dep_then_clean(c) -> Iterator[SomeWrapperDep]:
    try:
        yield SomeWrapperDep(c[SomeDep])
    finally:
        SomeWrapperDep.global_clean_up_has_happened = True


def test_clean_up_of_loaded_contexts_happens_on_container_exit():
    SomeDep.global_clean_up_has_happened = False

    with context_container(container, context_types=[SomeDep]) as c:
        assert isinstance(c[SomeDep], SomeDep)
        assert not SomeDep.global_clean_up_has_happened
    assert SomeDep.global_clean_up_has_happened


def test_context_instances_are_not_singletons():
    with context_container(container, context_types=[SomeDep]) as c:
        one = c[SomeDep]
        two = c[SomeDep]
        assert one is not two


def test_context_instances_can_be_made_singletons():
    SomeDep.global_clean_up_has_happened = False
    with context_container(
        container, context_types=[], context_singletons=[SomeDep]
    ) as c:
        one = c[SomeDep]
        two = c[SomeDep]
        assert one is two
    assert SomeDep.global_clean_up_has_happened


def test_context_instance_singletons_only_have_a_lifespan_of_the_with():
    SomeDep.global_clean_up_has_happened = False
    with context_container(
        container, context_types=[], context_singletons=[SomeDep]
    ) as c:
        one = c[SomeDep]
    with context_container(
        container, context_types=[], context_singletons=[SomeDep]
    ) as c:
        two = c[SomeDep]
    assert one is not two


def test_clean_up_of_loaded_contexts_happens_recursively_on_container_exit():
    SomeDep.global_clean_up_has_happened = False
    SomeWrapperDep.global_clean_up_has_happened = False

    with context_container(container, context_types=[SomeDep, SomeWrapperDep]) as c:
        assert isinstance(c[SomeWrapperDep], SomeWrapperDep)
        assert not SomeDep.global_clean_up_has_happened
        assert not SomeWrapperDep.global_clean_up_has_happened

    assert SomeDep.global_clean_up_has_happened
    assert SomeWrapperDep.global_clean_up_has_happened


def test_it_fails_if_the_dependencies_arent_defined_correctly():
    with pytest.raises(InvalidDependencyDefinition) as failure:
        with context_container(container, context_types=[SomeNotProperlySetupDef]) as c:
            c.resolve(SomeNotProperlySetupDef)
    assert f"A ContextManager[{SomeNotProperlySetupDef}] should be defined" in str(
        failure.value
    )


def test_it_works_with_actual_context_managers():
    with context_container(container, context_types=[Thing]) as c:
        assert c.resolve(Thing).contents == "managed thing"


def test_it_works_with_bind_to_container():

    @lagom.bind_to_container(context_container(container, context_types=[Thing]))
    def _get_thing_contents(thing: Thing = lagom.injectable):
        return thing.contents

    assert _get_thing_contents() == "managed thing"
    assert _get_thing_contents() == "managed thing"


def test_it_works_with_magic_bind_to_container():
    @lagom.magic_bind_to_container(context_container(container, context_types=[Thing]))
    def _get_thing_contents(thing: Thing):
        return thing.contents

    assert _get_thing_contents() == "managed thing"
    assert _get_thing_contents() == "managed thing"


def test_the_container_can_not_be_reused():
    original = context_container(container, context_types=[SomeDep])
    with original as context_container_1:
        pass

    with pytest.raises(Exception):
        with original as context_container_2:
            pass
