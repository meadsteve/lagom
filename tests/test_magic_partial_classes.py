from lagom import Container
from lagom.decorators import magic_bind_to_container


class Foo:
    def __init__(self, name="Foo") -> None:
        self._name = name

    def greet(self) -> str:
        return f"Hello {self._name}"


container = Container()


class Bar:
    def __init__(self, not_injected: str, foo: Foo) -> None:
        self.not_injected = not_injected
        self.foo = foo

    def greet(self) -> str:
        return self.foo.greet() + self.not_injected


def test_partial_application_can_be_applied_to_class():
    bar = container.magic_partial(Bar)(not_injected="!")
    assert bar.greet() == "Hello Foo!"


def test_passed_in_arguments_are_used_over_container_generated_ones_when_positional():
    partial_bar = container.magic_partial(Bar)
    assert partial_bar("!", Foo(name="Local")).greet() == "Hello Local!"


def test_passed_in_arguments_are_used_over_container_generated_ones_when_named():
    partial_bar = container.magic_partial(Bar)
    assert (
        partial_bar(not_injected="!", foo=Foo(name="Local")).greet() == "Hello Local!"
    )
