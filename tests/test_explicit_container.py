from typing import Optional

import pytest

from lagom import Container, Singleton, ExplicitContainer
from lagom.exceptions import InvalidDependencyDefinition, DependencyNotDefined


class SomethingToBuild:
    pass


class SomethingBiggerToBuild:
    def __init__(self, inner: SomethingToBuild):
        pass


def test_dependencies_must_be_explicitly_defined(explicit_container: Container):
    with pytest.raises(DependencyNotDefined) as e_info:
        explicit_container.resolve(SomethingToBuild)

    assert (
        str(e_info.value)
        == "SomethingToBuild has not been defined. In an explict container all dependencies must be defined"
    )


def test_the_error_suppression_flag_is_honoured(explicit_container: Container):
    assert explicit_container.resolve(SomethingToBuild, suppress_error=True) is None


def test_an_can_build_with_basic_lambdas(explicit_container: Container):
    explicit_container[SomethingToBuild] = lambda: SomethingToBuild()

    built_object = explicit_container.resolve(SomethingToBuild)
    assert isinstance(built_object, SomethingToBuild)


def test_aliases_arent_valid_as_they_require_reflection(explicit_container: Container):

    with pytest.raises(InvalidDependencyDefinition) as e_info:
        explicit_container[SomethingBiggerToBuild] = SomethingBiggerToBuild

    assert str(e_info.value) == "Aliases are not valid in an explicit container"


def test_singletons_with_aliases_arent_valid_as_they_require_reflection(
    explicit_container: Container,
):

    with pytest.raises(InvalidDependencyDefinition) as e_info:
        explicit_container[SomethingBiggerToBuild] = Singleton(SomethingBiggerToBuild)

    assert (
        str(e_info.value)
        == "Aliases are not valid inside singletons in an explicit container"
    )


def test_the_inner_dependencies_dont_have_to_be_defined_in_the_container(
    explicit_container: Container,
):
    explicit_container[SomethingBiggerToBuild] = lambda: SomethingBiggerToBuild(
        SomethingToBuild()
    )

    built_object = explicit_container.resolve(SomethingBiggerToBuild)
    assert isinstance(built_object, SomethingBiggerToBuild)

    # We still can't build the inner object directly
    assert explicit_container.resolve(SomethingToBuild, suppress_error=True) is None


def test_optional_deps_can_be_injected_if_they_can_be_built(
    explicit_container: Container,
):
    explicit_container[SomethingToBuild] = lambda: SomethingToBuild()

    built_object = explicit_container.resolve(Optional[SomethingToBuild])  # type: ignore
    assert isinstance(built_object, SomethingToBuild)


def test_the_clone_of_an_explicit_container_is_also_an_explicit_container(
    explicit_container: Container,
):
    clone = explicit_container.clone()
    assert isinstance(clone, ExplicitContainer)
