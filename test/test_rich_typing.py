from typing import NewType, List

from lagom import Container

MyServiceUrl = NewType("MyServiceUrl", str)


class ApiClientOfSomeKind:
    def __init__(self, url: MyServiceUrl):
        pass


class LoadBalancePerhaps:
    def __init__(self, urls: List[MyServiceUrl]):
        pass


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
