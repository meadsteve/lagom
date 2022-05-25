from lagom import Container
from lagom.updaters import update_container_singletons


class ThingOne:
    pass


class ThingTwo:
    pass


class ThingThree:
    pass


c = Container()


def test_a_new_container_can_be_made_with_singletons():
    singleton_container = update_container_singletons(c, [ThingOne])
    assert singleton_container[ThingOne] is singleton_container[ThingOne]
    assert isinstance(singleton_container[ThingOne], ThingOne)


def test_a_new_container_can_be_made_with_many_types_as_singletons():
    singleton_container = update_container_singletons(c, [ThingOne, ThingTwo, ThingThree])
    assert isinstance(singleton_container[ThingOne], ThingOne)
    assert isinstance(singleton_container[ThingTwo], ThingTwo)
    assert isinstance(singleton_container[ThingThree], ThingThree)

