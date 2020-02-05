from starlette.routing import Route

from lagom import Container
from lagom.integrations.starlette import StarletteContainer


class MyDep:
    pass


class ComplexDep:
    def __init__(self, something):
        pass


def some_handler(request, dep: MyDep):
    return "ok"


def test_a_special_starlette_container_can_be_used_and_provides_routes():
    sc = StarletteContainer()
    route = sc.route("/", some_handler)
    assert isinstance(route, Route)
    assert route.endpoint({}) == "ok"


def test_the_starlette_container_can_wrap_an_existing_container(container: Container):
    container[ComplexDep] = ComplexDep("")
    sc = StarletteContainer(container)
    assert isinstance(sc[ComplexDep], ComplexDep)
