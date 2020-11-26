from typing import Optional

from lagom import Container, Singleton


class InitialDep:
    pass


class SomeOtherThing(InitialDep):
    pass


def test_container_can_list_the_types_explicitly_defined(container: Container):
    container[InitialDep] = InitialDep
    container[SomeOtherThing] = Singleton(SomeOtherThing)

    assert container.defined_types == {
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
        InitialDep,
        SomeOtherThing,
        Optional[InitialDep],
        Optional[SomeOtherThing],
    }

    assert container.defined_types == {
        InitialDep,
        Optional[InitialDep],
    }
