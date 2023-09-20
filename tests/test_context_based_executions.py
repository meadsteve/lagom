from contextlib import contextmanager
from typing import Iterator, Generator, ContextManager

import pytest

from lagom import (
    Container,
    dependency_definition,
    ContextContainer,
    injectable,
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


container = Container()


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

    with ContextContainer(
        container, context_types=[SomeDep]
    ).clone() as context_container:
        assert isinstance(context_container[SomeDep], SomeDep)
        assert not SomeDep.global_clean_up_has_happened
    assert SomeDep.global_clean_up_has_happened


def test_context_instances_are_not_singletons():
    with ContextContainer(
        container, context_types=[SomeDep]
    ).clone() as context_container:
        one = context_container[SomeDep]
        two = context_container[SomeDep]
        assert one is not two


def test_context_instances_can_be_made_singletons():
    SomeDep.global_clean_up_has_happened = False
    with ContextContainer(
        container, context_types=[], context_singletons=[SomeDep]
    ).clone() as context_container:
        one = context_container[SomeDep]
        two = context_container[SomeDep]
        assert one is two
    assert SomeDep.global_clean_up_has_happened


def test_context_instance_singletons_only_have_a_lifespan_of_the_with():
    SomeDep.global_clean_up_has_happened = False
    context_container = ContextContainer(
        container, context_types=[], context_singletons=[SomeDep]
    )
    with context_container.clone() as c:
        one = c[SomeDep]
    with context_container.clone() as c:
        two = c[SomeDep]
    assert one is not two


def test_clean_up_of_loaded_contexts_happens_recursively_on_container_exit():
    SomeDep.global_clean_up_has_happened = False
    SomeWrapperDep.global_clean_up_has_happened = False

    with ContextContainer(
        container, context_types=[SomeDep, SomeWrapperDep]
    ).clone() as context_container:
        assert isinstance(context_container[SomeWrapperDep], SomeWrapperDep)
        assert not SomeDep.global_clean_up_has_happened
        assert not SomeWrapperDep.global_clean_up_has_happened

    assert SomeDep.global_clean_up_has_happened
    assert SomeWrapperDep.global_clean_up_has_happened


def test_it_fails_if_the_dependencies_arent_defined_correctly():
    with pytest.raises(InvalidDependencyDefinition) as failure:
        with ContextContainer(
            container, context_types=[SomeNotProperlySetupDef]
        ).clone() as context_container:
            context_container.resolve(SomeNotProperlySetupDef)
    assert f"A ContextManager[{SomeNotProperlySetupDef}] should be defined" in str(
        failure.value
    )


def test_it_works_with_actual_context_managers():
    class ThingManager:
        def __enter__(self):
            return Thing("managed thing")

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    container[ContextManager[Thing]] = ThingManager  # type: ignore

    with ContextContainer(
        container, context_types=[Thing]
    ).clone() as context_container:
        assert context_container.resolve(Thing).contents == "managed thing"


def test_the_container_can_be_reused():
    original = ContextContainer(container, context_types=[SomeDep])
    with original.clone() as context_container_1:
        a = context_container_1.resolve(SomeDep)
    with original.clone() as context_container_2:
        b = context_container_2.resolve(SomeDep)
    assert a != b


def test_a_partial_function_cleans_up_the_loaded_contexts_after_execution():
    SomeDep.global_clean_up_has_happened = False
    context_container = ContextContainer(container, context_types=[SomeDep])

    def _some_func(dep: SomeDep = injectable):
        return dep

    wrapped_func = context_container.partial(_some_func)

    assert isinstance(wrapped_func(), SomeDep)
    assert SomeDep.global_clean_up_has_happened


def test_a_magic_partial_function_cleans_up_the_loaded_contexts_after_execution():
    SomeDep.global_clean_up_has_happened = False
    context_container = ContextContainer(container, context_types=[SomeDep])

    def _some_func(dep: SomeDep):
        return dep

    wrapped_func = context_container.magic_partial(_some_func)

    assert isinstance(wrapped_func(), SomeDep)
    assert SomeDep.global_clean_up_has_happened
