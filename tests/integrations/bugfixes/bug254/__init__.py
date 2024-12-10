from typing import Iterator

from fastapi import FastAPI
from lagom import Container, context_dependency_definition
from lagom.integrations.fast_api import FastApiIntegration
from starlette.responses import PlainTextResponse


class ServiceA:
    def __init__(self, value: str):
        if not value == "correctly constructed":
            raise ValueError("Service A not correctly constructed!")

    def method_a(self):
        return "A result"


class ServiceB:
    def method_b(self):
        return "B result"


container = Container()


@context_dependency_definition(container)
def my_constructor() -> Iterator[ServiceA]:
    try:
        yield ServiceA("correctly constructed")
    finally:
        pass


deps = FastApiIntegration(container, request_context_singletons=[ServiceA])

app = FastAPI()


@app.get("/problem_route")
async def problem_route(
    service_b=deps.depends(ServiceB), service_a=deps.depends(ServiceA)
):  # there are other injections before A, DOESN'T WORK
    a = service_a.method_a()
    b = service_b.method_b()
    return PlainTextResponse(f"A is: {a}, B is: {b}")


@app.get("/happy_route")
async def happy_route(
    service_a=deps.depends(ServiceA), service_b=deps.depends(ServiceB)
):
    a = service_a.method_a()
    b = service_b.method_b()
    return PlainTextResponse(f"A is: {a}, B is: {b}")
