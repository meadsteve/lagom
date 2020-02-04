import inspect

import pytest

from lagom import Container, bind_to_container


class Something:
    pass


def test_partial_application_can_be_applied_to_async_functions(container: Container):
    @bind_to_container(container)
    async def example_async_function(message: str) -> str:
        return message

    assert inspect.iscoroutinefunction(example_async_function)


@pytest.mark.asyncio
async def test_calling_async_partials_works_as_expected(container: Container):
    @bind_to_container(container)
    async def example_async_function(message: str) -> str:
        return message

    assert await example_async_function("test") == "test"


@pytest.mark.asyncio
async def test_calling_async_partials_works_as_expected_with_shared_too(container: Container):
    @bind_to_container(container, shared=[Something])
    async def example_async_function(message: str) -> str:
        return message

    assert await example_async_function("test") == "test"
