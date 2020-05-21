import pytest

from lagom import Container
from lagom.experimental.exceptions import DependencyNotDefined


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


def test_an_alias_counts_as_definition(explicit_container: Container):
    explicit_container[SomethingToBuild] = SomethingToBuild

    built_object = explicit_container.resolve(SomethingToBuild)
    assert isinstance(built_object, SomethingToBuild)


def test_the_explicit_rule_applies_to_inner_objects_too(explicit_container: Container):
    explicit_container[SomethingBiggerToBuild] = SomethingBiggerToBuild

    with pytest.raises(DependencyNotDefined) as e_info:
        explicit_container.resolve(SomethingBiggerToBuild)

    assert (
        str(e_info.value)
        == "SomethingToBuild has not been defined. In an explict container all dependencies must be defined"
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
