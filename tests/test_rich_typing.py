from typing import NewType, List

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

from lagom import Container

MyServiceUrl = NewType("MyServiceUrl", str)


class ApiClientOfSomeKind:
    def __init__(self, url: MyServiceUrl):
        pass


class LoadBalancePerhaps:
    def __init__(self, urls: List[MyServiceUrl]):
        pass


class BakerProtocol(Protocol):
    def bake(self) -> str:
        pass


class Bakery:
    def __init__(self, baker: BakerProtocol):
        pass


class CrumpetBaker:
    def bake(self) -> str:
        return "crumpets"


def test_newtype_works_well_with_the_container(container: Container):
    container[MyServiceUrl] = MyServiceUrl("https://roll.diceapi.com")
    api_client = container[ApiClientOfSomeKind]
    assert isinstance(api_client, ApiClientOfSomeKind)


def test_lists_of_newtype_work_well_with_the_container(container: Container):
    container[List[MyServiceUrl]] = [
        MyServiceUrl("https://roll.diceapi.com"),
        MyServiceUrl("https://lol.diceapi.com"),
    ]
    load_balancer = container[LoadBalancePerhaps]
    assert isinstance(load_balancer, LoadBalancePerhaps)


def test_protocols_work_well_with_the_container(container: Container):
    # TODO: update contracts so this type ignore can be removed
    container[BakerProtocol] = CrumpetBaker  # type: ignore
    bakery = container[Bakery]
    assert isinstance(bakery, Bakery)
