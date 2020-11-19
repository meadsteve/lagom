from starlette.routing import Route

from lagom import Container, injectable
from lagom.integrations.starlette import StarletteIntegration


class MyDep:
    pass


class ComplexDep:
    def __init__(self, something):
        pass


def some_handler(request, dep: MyDep = injectable):
    return "ok"


def two_dep_handler(request, dep_one: MyDep = injectable, dep_two: MyDep = injectable):
    return "singleton" if dep_one is dep_two else "new instances"


def test_a_special_starlette_container_can_be_used_and_provides_routes(container):
    sc = StarletteIntegration(container)
    route = sc.route("/", some_handler)
    assert isinstance(route, Route)
    assert route.endpoint({}) == "ok"


def test_the_starlette_container_can_define_request_level_singletons(container):
    sc = StarletteIntegration(container, request_singletons=[MyDep])
    route = sc.route("/two", two_dep_handler)
    assert route.endpoint({}) == "singleton"
