import pytest

from lagom import Container, ExplicitContainer


@pytest.fixture(scope="function")
def container():
    return Container()


@pytest.fixture(scope="function")
def explicit_container():
    return ExplicitContainer()
