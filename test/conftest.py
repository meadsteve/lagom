import pytest

from lagom import Container


@pytest.fixture(scope="function")
def container():
    c = Container()
    return c
