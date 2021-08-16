from lagom import Container, injectable


class Foo:
    def __init__(self, name="Foo") -> None:
        self._name = name

    def greet(self) -> str:
        return f"Hello {self._name}"


container = Container()


class Bar:
    def __init__(self, not_injected: str, foo: Foo = injectable) -> None:
        self.not_injected = not_injected
        self.foo = foo

    def greet(self) -> str:
        return self.foo.greet() + self.not_injected


class MethodBasedBar:
    def greet(self, message: str, foo: Foo = injectable) -> str:
        return foo.greet() + message


def test_partial_application_can_be_applied_to_class():
    bar = container.partial(Bar)(not_injected="!")
    assert bar.greet() == "Hello Foo!"


def test_passed_in_arguments_are_used_over_container_generated_ones_when_positional():
    partial_bar = container.partial(Bar)
    assert partial_bar("!", Foo(name="Local")).greet() == "Hello Local!"


def test_passed_in_arguments_are_used_over_container_generated_ones_when_named():
    partial_bar = container.partial(Bar)
    assert (
        partial_bar(not_injected="!", foo=Foo(name="Local")).greet() == "Hello Local!"
    )


def test_partial_application_can_be_applied_to_instance_method():
    bar = MethodBasedBar()
    partial = container.partial(bar.greet)
    assert partial(", hello?") == "Hello Foo, hello?"
