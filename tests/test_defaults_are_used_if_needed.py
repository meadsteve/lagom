from lagom import Container


class DepWithMultipleDefaults:
    a_string: str
    a_bool: bool

    def __init__(self, a_string: str = "hello", a_bool: bool = True):
        self.a_string = a_string
        self.a_bool = a_bool


def test_defaults_are_used_if_needed(container: Container):
    resolved = container.resolve(DepWithMultipleDefaults)
    assert resolved.a_string == "hello"
    assert resolved.a_bool is True
