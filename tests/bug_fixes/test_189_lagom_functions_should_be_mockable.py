from unittest import mock
from unittest.mock import Mock

import pytest


async def _fake_async(_):
    return "mocked"


@mock.patch("tests.bug_fixes.resources_for_189.a_bound_function", lambda _: "mocked")
def test_a_bound_function_can_be_mocked():
    from tests.bug_fixes.resources_for_189 import a_bound_function
    from tests.test_context_based_executions import SomeDep

    assert a_bound_function(SomeDep()) == "mocked"


@mock.patch("tests.bug_fixes.resources_for_189.an_async_bound_function", _fake_async)
@pytest.mark.asyncio
async def test_an_async_bound_function_can_be_mocked():
    from tests.bug_fixes.resources_for_189 import an_async_bound_function
    from tests.test_context_based_executions import SomeDep

    assert await an_async_bound_function(SomeDep()) == "mocked"


@pytest.mark.asyncio
async def test_autospec_for_async_bound_function():
    from tests.bug_fixes.resources_for_189 import an_async_bound_function

    mock = Mock(spec=an_async_bound_function)
    assert mock
