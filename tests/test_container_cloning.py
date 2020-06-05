from lagom import Container, Singleton


class InitialDep:
    pass


class SomeMockForTesting(InitialDep):
    pass


class SomeOtherMockForTesting(InitialDep):
    pass


def test_container_can_be_cloned_and_maintains_separate_deps(container: Container):
    new_container = container.clone()
    new_container.define(InitialDep, lambda: SomeMockForTesting())

    assert isinstance(new_container[InitialDep], SomeMockForTesting)
    assert isinstance(container[InitialDep], InitialDep)


def test_a_cloned_container_can_have_deps_overwritten(container: Container):
    container.define(InitialDep, lambda: SomeMockForTesting())
    new_container = container.clone()
    new_container.define(InitialDep, lambda: SomeOtherMockForTesting())

    assert isinstance(new_container[InitialDep], SomeOtherMockForTesting)


def test_a_clone_shares_the_parents_singleton_instances(container: Container):
    container.define(InitialDep, Singleton(InitialDep))
    new_container = container.clone()

    assert id(container[InitialDep]) == id(new_container[InitialDep])


def test_overwriting_a_singleton_creates_a_new_one(container: Container):
    container.define(InitialDep, Singleton(InitialDep))
    new_container = container.clone()
    new_container.define(InitialDep, Singleton(InitialDep))

    assert id(container[InitialDep]) != id(new_container[InitialDep])
