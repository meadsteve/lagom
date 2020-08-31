import pytest

from lagom import Container, bind_to_container, injectable


class MyDep:
    value: str

    def __init__(self, value="testing"):
        self.value = value


container = Container()


@bind_to_container(container)
def example_function(message: str, resolved: MyDep = injectable) -> str:
    return resolved.value + message


@bind_to_container(container)
async def async_example_function(message: str, resolved: MyDep = injectable) -> str:
    return resolved.value + message


def test_functions_decorated_get_the_correct_argument():
    assert example_function(message=" world") == "testing world"


def test_injected_arguments_can_over_overridden():
    assert example_function(message=" world", resolved=MyDep("set")) == "set world"


@pytest.mark.asyncio
async def test_async_functions_decorated_get_the_correct_argument():
    assert await async_example_function(message=" world") == "testing world"
