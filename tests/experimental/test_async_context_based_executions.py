from contextlib import asynccontextmanager
from typing import ContextManager, AsyncGenerator, Awaitable

import pytest

from lagom import Container, dependency_definition
from lagom.decorators import context_dependency_definition
from lagom.exceptions import InvalidDependencyDefinition
from lagom.experimental.context_based import AsyncContextContainer, AwaitableSingleton


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
@asynccontextmanager
async def _load_a_some_dep_then_clean() -> AsyncGenerator[SomeDep, None]:
    try:
        yield SomeDep()
    finally:
        SomeDep.global_clean_up_has_happened = True


@context_dependency_definition(container)
async def _load_a_some_wrapper_dep_then_clean(
    c,
) -> AsyncGenerator[SomeWrapperDep, None]:
    try:
        yield SomeWrapperDep(await c[Awaitable[SomeDep]])
    finally:
        SomeWrapperDep.global_clean_up_has_happened = True


@pytest.mark.asyncio
async def test_clean_up_of_loaded_contexts_happens_on_container_exit():
    SomeDep.global_clean_up_has_happened = False

    async with AsyncContextContainer(
        container, context_types=[SomeDep]
    ) as context_container:
        assert isinstance(await context_container[Awaitable[SomeDep]], SomeDep)
        assert not SomeDep.global_clean_up_has_happened
    assert SomeDep.global_clean_up_has_happened


@pytest.mark.asyncio
async def test_context_instances_are_not_singletons():
    async with AsyncContextContainer(
        container, context_types=[SomeDep]
    ) as context_container:
        one = context_container[Awaitable[SomeDep]]
        two = context_container[Awaitable[SomeDep]]
        assert one is not two


@pytest.mark.asyncio
async def test_context_instances_can_be_made_singletons():
    SomeDep.global_clean_up_has_happened = False
    async with AsyncContextContainer(
        container, context_types=[], context_singletons=[SomeDep]
    ) as context_container:
        one = await context_container[AwaitableSingleton[SomeDep]].get()
        two = await context_container[AwaitableSingleton[SomeDep]].get()
        assert one is two
    assert SomeDep.global_clean_up_has_happened


@pytest.mark.asyncio
async def test_context_instance_singletons_only_have_a_lifespan_of_the_with():
    SomeDep.global_clean_up_has_happened = False
    context_container = AsyncContextContainer(
        container, context_types=[], context_singletons=[SomeDep]
    )
    async with context_container as c:
        one = await c[AwaitableSingleton[SomeDep]].get()
    async with context_container as c:
        two = await c[AwaitableSingleton[SomeDep]].get()
    assert one is not two


@pytest.mark.asyncio
async def test_clean_up_of_loaded_contexts_happens_recursively_on_container_exit():
    SomeDep.global_clean_up_has_happened = False
    SomeWrapperDep.global_clean_up_has_happened = False

    async with AsyncContextContainer(
        container, context_types=[SomeDep, SomeWrapperDep]
    ) as context_container:
        await context_container[Awaitable[SomeDep]]
        assert isinstance(
            await context_container[Awaitable[SomeWrapperDep]], SomeWrapperDep
        )
        assert not SomeDep.global_clean_up_has_happened
        assert not SomeWrapperDep.global_clean_up_has_happened

    assert SomeDep.global_clean_up_has_happened
    assert SomeWrapperDep.global_clean_up_has_happened


@pytest.mark.asyncio
async def test_it_fails_if_the_dependencies_arent_defined_correctly():
    with pytest.raises(InvalidDependencyDefinition) as failure:
        async with AsyncContextContainer(
            container, context_types=[SomeNotProperlySetupDef]
        ) as context_container:
            context_container.resolve(SomeNotProperlySetupDef)
    assert f"A ContextManager[{SomeNotProperlySetupDef}] should be defined" in str(
        failure.value
    )


@pytest.mark.asyncio
async def test_it_works_with_actual_context_managers():
    fresh_container = Container(container)

    class ThingManager:
        def __enter__(self):
            return Thing("managed thing")

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    fresh_container[ContextManager[Thing]] = ThingManager  # type: ignore

    async with AsyncContextContainer(
        fresh_container, context_types=[Thing]
    ) as context_container:
        assert context_container.resolve(Thing).contents == "managed thing"


@pytest.mark.asyncio
async def test_it_works_with_actual_context_managers_as_singletons():
    fresh_container = Container(container)

    class ThingManager:
        def __enter__(self):
            return Thing("managed thing")

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    fresh_container[ContextManager[Thing]] = ThingManager  # type: ignore

    async with AsyncContextContainer(
        fresh_container, context_types=[], context_singletons=[Thing]
    ) as context_container:
        assert context_container.resolve(Thing).contents == "managed thing"


@pytest.mark.asyncio
async def test_the_container_can_be_reused():
    original = AsyncContextContainer(container, context_types=[SomeDep])
    async with original as context_container_1:
        a = await context_container_1.resolve(Awaitable[SomeDep])
    async with original as context_container_2:
        b = await context_container_2.resolve(Awaitable[SomeDep])
    assert a != b


@pytest.mark.asyncio
async def test_the_container_can_be_nested_though_this_has_no_meaning():
    original = AsyncContextContainer(container, context_types=[SomeDep])
    async with original as context_container_1:
        a = await context_container_1.resolve(Awaitable[SomeDep])
        async with context_container_1 as context_container_2:
            b = context_container_2.resolve(Awaitable[SomeDep])
    assert a != b
