from dataclasses import dataclass
from typing import Awaitable

import pytest

from lagom import Container, dependency_definition


@dataclass
class MyComplexDep:
    some_number: int


@pytest.mark.asyncio
async def test_simple_async_component_def(container: Container):
    @dependency_definition(container)
    async def my_constructor() -> MyComplexDep:
        return MyComplexDep(some_number=5)

    assert (await container[Awaitable[MyComplexDep]]) == MyComplexDep(some_number=5)  # type: ignore
