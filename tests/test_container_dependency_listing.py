import pytest

from lagom import Construction, Container, Singleton
from lagom.exceptions import DuplicateDefinition


class InitialDep:
    pass


class SomeOtherThing(InitialDep):
    pass


def test_container_can_list_the_types_explicitly_defined(container: Container):
    container[InitialDep] = InitialDep
    container[SomeOtherThing] = Singleton(SomeOtherThing)

    assert container.defined_types == {InitialDep, SomeOtherThing}
