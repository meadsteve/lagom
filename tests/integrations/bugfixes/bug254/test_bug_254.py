from starlette.testclient import TestClient

from tests.integrations.bugfixes.bug254 import app


def test_the_bug_is_fixed():
    client = TestClient(app)
    response = client.get("problem_route")

    assert response.content == b"A is: A result, B is: B result"


def test_it_works_as_it_did_before_the_bug_fix():
    client = TestClient(app)
    response = client.get("happy_route")

    assert response.content == b"A is: A result, B is: B result"
