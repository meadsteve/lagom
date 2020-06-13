from lagom import Container


class AThing:
    def __init__(self):
        pass


class AnotherThing:
    def __init__(self, thing: AThing):
        pass


def test_initially_nothing_has_been_reflected(container: Container):
    assert container.reflection_cache_overview == {}


def test_all_reflection_used_is_described(container: Container):
    container.resolve(AnotherThing)
    assert container.reflection_cache_overview == {
        "AnotherThing.__init__": "(?, AThing)",
        "AThing.__init__": "(?)",
    }
