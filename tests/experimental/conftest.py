import pytest

from lagom.experimental.container import ExplicitContainer


@pytest.fixture(scope="function")
def explicit_container():
    return ExplicitContainer()
