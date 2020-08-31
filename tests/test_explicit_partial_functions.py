from lagom import Container, bind_to_container, injectable


class MyDep:
    value: str

    def __init__(self, value="testing"):
        self.value = value


container = Container()


@bind_to_container(container)
def example_function(message: str, resolved: MyDep = injectable) -> str:
    return resolved.value + message


def test_functions_decorated_get_the_correct_argument():
    assert example_function(message=" world") == "testing world"
