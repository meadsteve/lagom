from fastapi import FastAPI
from fastapi.testclient import TestClient

from lagom import Container
from lagom.integrations.fast_api import FastApiIntegration


class Inner:
    pass


class Outer:
    def __init__(self, inner: Inner):
        self.inner = inner


app = FastAPI()
container = Container()
deps = FastApiIntegration(container, request_singletons=[Inner])


@app.get("/")
async def read_main(outer_one=deps.depends(Outer), outer_two=deps.depends(Outer)):
    return {"outer_one": hash(outer_one.inner), "outer_two": hash(outer_two.inner)}


client = TestClient(app)


def test_request_singletons_are_the_same_within_a_request_context():
    response = client.get("/")
    data = response.json()
    assert data["outer_one"] == data["outer_two"]


def test_request_singletons_are_different_for_new_requests():
    data_one = client.get("/").json()
    data_two = client.get("/").json()

    assert data_one["outer_one"] != data_two["outer_one"]
