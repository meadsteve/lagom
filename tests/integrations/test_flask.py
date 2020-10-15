from flask import Flask, Response

from lagom import injectable
from lagom.integrations.flask import FlaskContainer


class ComplexDep:
    def __init__(self, message):
        self.message = message


def test_flask_container_provides_a_route_decorator():
    app = Flask(__name__)
    container = FlaskContainer(app)
    container[ComplexDep] = ComplexDep("hello from dep")

    @container.route("/")
    def _some_handler(dep: ComplexDep = injectable):
        return dep.message

    with app.test_client() as client:
        resp: Response = client.get("/")
        assert resp.get_data(as_text=True) == "hello from dep"


def test_the_route_decorator_can_have_request_level_singletons():
    app = Flask(__name__)
    container = FlaskContainer(app, request_singletons=[ComplexDep])
    container[ComplexDep] = lambda: ComplexDep("hello from dep")

    @container.route("/")
    def _some_handler(
        dep_one: ComplexDep = injectable, dep_two: ComplexDep = injectable
    ):
        return "singleton" if dep_one is dep_two else "nope"

    with app.test_client() as client:
        resp: Response = client.get("/")
        assert resp.get_data(as_text=True) == "singleton"
