from flask import Flask, Response
from lagom.integrations.flask import FlaskContainer


class ComplexDep:
    def __init__(self, message):
        self.message = message


def test_flask_container_provides_a_route_decorator():
    app = Flask(__name__)
    container = FlaskContainer(app)
    container[ComplexDep] = ComplexDep("hello from dep")

    @container.route("/")
    def _some_handler(dep: ComplexDep):
        return dep.message

    with app.test_client() as client:
        resp: Response = client.get("/")
        assert resp.get_data(as_text=True) == "hello from dep"
