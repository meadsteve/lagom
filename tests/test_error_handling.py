import io
import typing
from typing import List

import pytest

from lagom import Container
from lagom.exceptions import UnresolvableType, RecursiveDefinitionError


class MyMissingDep:
    def __init__(self, _stuff: str):
        pass


class UnfulfilledDeps:
    def __init__(self, _stuff: MyMissingDep):
        pass


@pytest.mark.parametrize("dep", [str, int, float, bool, bytes, bytearray])
def test_simple_objects_cannot_be_resolved(container: Container, dep):
    with pytest.raises(UnresolvableType):
        container.resolve(dep)


@pytest.mark.parametrize(
    "dep",
    [
        io.BytesIO,
        io.FileIO,
        io.IOBase,
        io.RawIOBase,
        io.TextIOBase,
        io.BufferedIOBase,
        io.BufferedRandom,
        io.BufferedReader,
        io.BufferedRWPair,
        io.BufferedWriter,
        typing.IO,
        typing.TextIO,
        typing.BinaryIO,
    ],
)
def test_generic_io_cant_be_resolved(container: Container, dep):
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


class A:
    def __init__(self, b: "B"):
        pass


class B:
    def __init__(self, a: "A"):
        pass


@pytest.mark.skip(
    reason="This behaviour is a nice to have but is execution env dependent"
)
def test_circular_imports_raise_a_clear_error(container):
    with pytest.raises(RecursiveDefinitionError) as e_info:
        container.resolve(A)
    err_string = str(e_info.value)
    assert "When trying to build dependency of type " in err_string
    assert "This could indicate a circular definition somewhere." in err_string
