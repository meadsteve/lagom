from lagom import Container, injectable
from lagom.decorators import bind_to_container


class Foo:
    def __init__(self, name="Foo") -> None:
        self._name = name

    def greet(self) -> str:
        return f"Hello {self._name}"


container = Container()


@bind_to_container(container)
class Bar:
    def __init__(self, not_injected: str, foo: Foo = injectable) -> None:
        self.not_injected = not_injected
        self.foo = foo

    def greet(self) -> str:
        return self.foo.greet() + self.not_injected


class Baz:
    def __init__(self, not_injected: str, foo: Foo = injectable) -> None:
        self.not_injected = not_injected
        self.foo = foo

    def greet(self) -> str:
        return self.foo.greet() + self.not_injected


def test_partial_application_can_be_applied_to_class():
    baz = container.partial(Baz)(not_injected="!")
    assert baz.greet() == "Hello Foo!"


def test_passed_in_arguments_are_used_over_container_generated_ones_when_positional():
    partial_baz = container.partial(Baz)
    assert partial_baz("!", Foo(name="Local")).greet() == "Hello Local!"


def test_passed_in_arguments_are_used_over_container_generated_ones_when_named():
    partial_baz = container.partial(Baz)
    assert partial_baz(not_injected="!", foo=Foo(name="Local")).greet() == "Hello Local!"


def test_a_decorator_can_be_used_to_bind_as_well():
    bar = Bar(not_injected="!!!")
    assert bar.greet() == "Hello Foo!!!"
