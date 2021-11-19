from lagom import Container


class SomeDep:
    pass


def test_temporary_singletons_work(container: Container):

    with container.temporary_singletons([SomeDep]) as container_with_singletons:
        # The original container is unaltered and the dep isn't a singleton
        assert container[SomeDep] is not container[SomeDep]
        # The temporary container has the singletons defined
        assert container_with_singletons[SomeDep] is container_with_singletons[SomeDep]


def test_temporary_singletons_dont_effect_the_base_container(container: Container):

    with container.temporary_singletons([SomeDep]) as container_with_singletons:
        the_singleton = container_with_singletons[SomeDep]
    assert container[SomeDep] is not the_singleton
