import pytest

from lagom import Container, compose


class A:
    def __init__(self, something: str):
        pass


class B:
    def __init__(self, something: str):
        pass


class C:
    def __init__(self, something: str):
        pass


container_a = Container()
container_a[A] = lambda: A("hello")

container_b = Container()
container_b[B] = lambda: B("world")

container_c = Container()
container_c[C] = lambda: C("!!!!")


def test_two_containers_can_be_composed_together_and_all_dependencies_resolved():
    composed_container = compose(container_a, container_b)

    assert composed_container[A]
    assert composed_container[B]


def test_the_composed_container_can_list_all_defined_deps():
    composed_container = compose(container_a, container_b)

    assert A in composed_container.defined_types
    assert B in composed_container.defined_types


def test_composed_container_definitions_cannot_overlap():
    with pytest.raises(ValueError):
        compose(container_a, container_a)


def test_the_result_of_a_composition_can_be_composed():
    composed_container = compose(container_a, container_b)
    next_composed_container = compose(composed_container, container_c)

    assert A in next_composed_container.defined_types
    assert B in next_composed_container.defined_types
    assert C in next_composed_container.defined_types
    assert C not in composed_container.defined_types
