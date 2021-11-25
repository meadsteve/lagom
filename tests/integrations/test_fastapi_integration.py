from fastapi import FastAPI
from fastapi.testclient import TestClient

from lagom import Container
from lagom.integrations.fast_api import FastApiIntegration


class Inner:
    def __init__(self, msg=None):
        self.msg = msg


class Outer:
    def __init__(self, inner: Inner):
        self.inner = inner


app = FastAPI()
container = Container()
deps = FastApiIntegration(container, request_singletons=[Inner])


@app.get("/")
async def read_main(outer_one=deps.depends(Outer), outer_two=deps.depends(Outer)):
    return {"outer_one": hash(outer_one.inner), "outer_two": hash(outer_two.inner)}


@app.get("/inner")
async def another_route(dep_one=deps.depends(Inner)):
    return {"data": dep_one.msg}


client = TestClient(app)


def test_request_singletons_are_the_same_within_a_request_context():
    response = client.get("/")
    data = response.json()
    assert data["outer_one"] == data["outer_two"]


def test_request_singletons_are_different_for_new_requests():
    data_one = client.get("/").json()
    data_two = client.get("/").json()

    assert data_one["outer_one"] != data_two["outer_one"]


def test_deps_can_be_overridden_during_test():
    with deps.override_for_test() as c:
        c[Inner] = Inner("test_message")
        call_under_test = client.get("/inner").json()
    call_after_test = client.get("/inner").json()

    assert call_under_test["data"] == "test_message"
    assert call_after_test["data"] != "test_message"


def test_deps_can_be_overridden_during_test_mutiple_times():
    with deps.override_for_test() as c1:
        with deps.override_for_test() as c2:
            c1[Inner] = Inner("first_level")
            c2[Inner] = Inner("second_level")
            second = client.get("/inner").json()
        first = client.get("/inner").json()
    outer = client.get("/inner").json()

    assert outer["data"] is None
    assert first["data"] == "first_level"
    assert second["data"] == "second_level"
