from contextlib import contextmanager
from typing import Iterator

from fastapi import FastAPI, Request

from lagom import Container, dependency_definition
from lagom.integrations.fast_api import FastApiIntegration


class Inner:
    def __init__(self, msg=None):
        self.msg = msg


class RequestInjectedSingleton:
    def __init__(self, request: Request) -> None:
        self.request = request


class Outer:
    def __init__(self, inner: Inner):
        self.inner = inner


class ContextLoaded:
    cleaned_up = False

    def __str__(self):
        return f"{self.cleaned_up}"


class UnusedDepOne:
    pass


class UnusedDepTwo:
    pass


app = FastAPI()
container = Container()
deps = FastApiIntegration(
    container,
    request_singletons=[UnusedDepOne, Inner, RequestInjectedSingleton, UnusedDepTwo],
    request_context_singletons=[ContextLoaded],
)


@dependency_definition(container)
@contextmanager
def _load_then_clean() -> Iterator[ContextLoaded]:
    try:
        yield ContextLoaded()
    finally:
        ContextLoaded.cleaned_up = True


@app.get("/")
async def read_main(outer_one=deps.depends(Outer), outer_two=deps.depends(Outer)):
    return {"outer_one": hash(outer_one.inner), "outer_two": hash(outer_two.inner)}


@app.get("/inner")
async def another_route(dep_one=deps.depends(Inner)):
    return {"data": dep_one.msg}

@app.get("/request_injected_request_singleton")
async def request_injected_request_singleton(
        dep_one=deps.depends(RequestInjectedSingleton)):
    return {"data": dep_one.request.url.path}

@app.get("/with_some_context")
async def a_route_with_context(dep_one=deps.depends(ContextLoaded)):
    return {"cleaned_up": str(dep_one)}
