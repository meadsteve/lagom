from typing import Optional

from lagom import Container, Singleton
from lagom.interfaces import ContainerDebugInfo


class InitialDep:
    pass


class SomeOtherThing(InitialDep):
    pass


def test_container_can_list_the_types_explicitly_defined(container: Container):
    container[InitialDep] = InitialDep
    container[SomeOtherThing] = Singleton(SomeOtherThing)

    assert container.defined_types == {
        ContainerDebugInfo,
        InitialDep,
        SomeOtherThing,
        Optional[InitialDep],
        Optional[SomeOtherThing],
    }


def test_container_can_list_the_types_explicitly_defined_in_a_cloned_container(
    container: Container,
):
    container[InitialDep] = InitialDep

    child_container = container.clone()
    child_container[SomeOtherThing] = Singleton(SomeOtherThing)

    assert child_container.defined_types == {
        ContainerDebugInfo,
        InitialDep,
        SomeOtherThing,
        Optional[InitialDep],
        Optional[SomeOtherThing],
    }

    assert container.defined_types == {
        ContainerDebugInfo,
        InitialDep,
        Optional[InitialDep],
    }


def test_the_container_can_inject_its_own_overview(container: Container):
    info = container[ContainerDebugInfo]  # type: ignore
    assert hasattr(info, "defined_types")
    assert hasattr(info, "reflection_cache_overview")
    assert isinstance(info, ContainerDebugInfo)
