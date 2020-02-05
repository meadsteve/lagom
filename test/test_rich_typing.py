from typing import NewType

from lagom import Container

MyServiceUrl = NewType("MyServiceUrl", str)


class ApiClientOfSomeKind:
    def __init__(self, url: MyServiceUrl):
        pass


def test_newtype_works_well_with_the_container(container: Container):
    container[MyServiceUrl] = MyServiceUrl("https://roll.diceapi.com")
    api_client = container[ApiClientOfSomeKind]
    assert isinstance(api_client, ApiClientOfSomeKind)
