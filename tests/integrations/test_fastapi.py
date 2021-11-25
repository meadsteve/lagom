from dataclasses import dataclass

import pytest
from fastapi.params import Depends
from starlette.testclient import TestClient

from lagom import Container
from lagom.integrations.fast_api import FastApiIntegration
from .fastapi_app import app, deps, Inner


@dataclass
class ComplexDep:
    something: str


class _FakeRequestState:
    lagom_request_container = None


class _FakeRequest:
    def __init__(self):
        self.state = _FakeRequestState()


def test_the_fast_api_container_can_return_a_fastapi_dependency(container: Container):
    container[ComplexDep] = ComplexDep("testing")

    deps = FastApiIntegration(container)
    dependency_injection = deps.depends(ComplexDep)
    assert isinstance(dependency_injection, Depends)

    # The fast api dependency injection would supply a real request
    fake_request = _FakeRequest()
    assert dependency_injection.dependency(fake_request) == ComplexDep("testing")  # type: ignore


def test_request_singletons_are_the_same_within_a_request_context():
    client = TestClient(app)
    response = client.get("/")
    data = response.json()
    assert data["outer_one"] == data["outer_two"]


def test_request_singletons_are_different_for_new_requests():
    client = TestClient(app)
    data_one = client.get("/").json()
    data_two = client.get("/").json()

    assert data_one["outer_one"] != data_two["outer_one"]


def test_deps_can_be_overridden_during_test():
    client = TestClient(app)
    with deps.override_for_test() as c:
        c[Inner] = Inner("test_message")
        call_under_test = client.get("/inner").json()
    call_after_test = client.get("/inner").json()

    assert call_under_test["data"] == "test_message"
    assert call_after_test["data"] != "test_message"


@pytest.fixture
def fixture_fake_deps():
    with deps.override_for_test() as test_container:
        test_container[Inner] = Inner("fixture_deps")
        yield test_container


def test_overriding_with_fixtures_works(fixture_fake_deps):
    client = TestClient(app)
    resp = client.get("/inner").json()
    assert resp["data"] == "fixture_deps"


def test_deps_can_be_overridden_during_test_multiple_times():
    client = TestClient(app)
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
