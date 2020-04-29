from dataclasses import dataclass

from fastapi.params import Depends

from lagom.integrations.fast_api import FastApiContainer


@dataclass
class ComplexDep:
    something: str


def test_the_fast_api_container_can_return_a_fastapi_dependency():
    fac = FastApiContainer()
    fac[ComplexDep] = ComplexDep("testing")
    dependency_injection = fac.depends(ComplexDep)
    assert isinstance(dependency_injection, Depends)
    assert dependency_injection.dependency() == ComplexDep("testing")  # type: ignore
