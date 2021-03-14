from dataclasses import dataclass

from fastapi.params import Depends

from lagom import Container
from lagom.integrations.fast_api import FastApiIntegration


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
