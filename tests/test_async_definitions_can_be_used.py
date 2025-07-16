from dataclasses import dataclass
from typing import Awaitable

import pytest

from lagom import Container, dependency_definition, Singleton
from lagom.exceptions import TypeOnlyAvailableAsAwaitable


@dataclass
class MyComplexDep:
    some_number: int

    @classmethod
    async def asyc_loader(cls):
        return cls(10)


@pytest.mark.asyncio
async def test_simple_async_component_def(container: Container):
    @dependency_definition(container)
    async def my_constructor() -> MyComplexDep:
        return MyComplexDep(some_number=5)

    assert (await container[Awaitable[MyComplexDep]]) == MyComplexDep(some_number=5)  # type: ignore


@pytest.mark.asyncio
async def test_alternative_way_of_defining_an_async_dep(container: Container):
    container[Awaitable[MyComplexDep]] = MyComplexDep.asyc_loader  # type: ignore

    assert (await container[Awaitable[MyComplexDep]]) == MyComplexDep(some_number=10)  # type: ignore


@pytest.mark.asyncio
async def test_async_singleton_do_not_raise_runtime_error(container: Container):
    container[Awaitable[MyComplexDep]] = Singleton(MyComplexDep.asyc_loader)  # type: ignore[type-abstract]

    assert (await container[Awaitable[MyComplexDep]]) == MyComplexDep(some_number=10)  # type: ignore[type-abstract]
    assert (await container[Awaitable[MyComplexDep]]) == MyComplexDep(some_number=10)  # type: ignore[type-abstract]


@pytest.mark.asyncio
async def test_simple_async_singleton_do_not_raise_runtime_error(container: Container):
    @dependency_definition(container, singleton=True)
    async def my_constructor() -> MyComplexDep:
        return MyComplexDep(some_number=10)

    assert (await container[Awaitable[MyComplexDep]]) == MyComplexDep(some_number=10)  # type: ignore[type-abstract]
    assert (await container[Awaitable[MyComplexDep]]) == MyComplexDep(some_number=10)  # type: ignore[type-abstract]


@pytest.mark.asyncio
async def test_defining_an_async_dep_provides_a_helpful_error_if_you_forget_awaitable(
    container: Container,
):
    container[Awaitable[MyComplexDep]] = MyComplexDep.asyc_loader  # type: ignore

    with pytest.raises(TypeOnlyAvailableAsAwaitable):
        assert container[MyComplexDep]


@pytest.mark.asyncio
async def test_a_sync_and_async_version_can_be_defined(
    container: Container,
):
    container[MyComplexDep] = lambda: MyComplexDep(5)
    container[Awaitable[MyComplexDep]] = MyComplexDep.asyc_loader  # type: ignore

    assert container[MyComplexDep]
    assert container[Awaitable[MyComplexDep]]  # type: ignore
