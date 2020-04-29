from typing import List

import pytest

from lagom import Container
from lagom.exceptions import UnresolvableType


class MyMissingDep:
    def __init__(self, _stuff: str):
        pass


class UnfulfilledDeps:
    def __init__(self, _stuff: MyMissingDep):
        pass


@pytest.mark.parametrize("dep", [str, int, float, bool])
def test_simple_objects_cannot_be_resolved(container: Container, dep):
    with pytest.raises(UnresolvableType):
        container.resolve(dep)


def test_raises_error_with_the_dep_that_couldnt_be_built(container):
    with pytest.raises(UnresolvableType):
        container.resolve(MyMissingDep)


def test_raises_error_with_the_dep_that_couldnt_be_built_at_the_top_level(container):
    with pytest.raises(UnresolvableType) as e_info:
        container.resolve(UnfulfilledDeps)
    assert (
        str(e_info.value) == "Unable to construct dependency of type UnfulfilledDeps "
        "The constructor probably has some unresolvable dependencies"
    )


def test_composite_type_failures_still_throw_sensible_errors(container):
    with pytest.raises(UnresolvableType) as e_info:
        container.resolve(List[UnfulfilledDeps])
    assert (
        str(e_info.value) == "Unable to construct dependency of type "
        "typing.List[tests.test_error_handling.UnfulfilledDeps] "
        "The constructor probably has some unresolvable dependencies"
    )
