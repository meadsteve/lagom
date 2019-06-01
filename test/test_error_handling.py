import pytest

from lagom import Container
from lagom.exceptions import UnresolvableType


class MyMissingDep:
    def __init__(self, _stuff: str):
        pass


class UnfulfilledDeps:
    def __init__(self, _stuff: MyMissingDep):
        pass


@pytest.fixture
def container():
    c = Container()
    return c


@pytest.mark.parametrize("dep", [str, int, float, bool])
def test_simple_objects_cannot_be_resolved(container: Container, dep):
    with pytest.raises(UnresolvableType):
        container.resolve(dep)


def test_raises_error_with_the_dep_that_couldnt_be_built(container):
    with pytest.raises(UnresolvableType) as e_info:
        container.resolve(UnfulfilledDeps)
    assert str(e_info.value) == "Cannot construct type UnfulfilledDeps"
