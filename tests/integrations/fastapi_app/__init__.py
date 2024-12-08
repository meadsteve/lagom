from contextlib import contextmanager
from typing import Iterator, ClassVar

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

    cleaned: ClassVar[list["ContextLoaded"]] = []

    def __init__(self):
        self.cleaned_up = False

    def clean_up(self):
        self.__class__.cleaned.append(self)
        self.cleaned_up = True

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
    var = ContextLoaded()
    try:
        yield var
    finally:
        var.clean_up()


@app.get("/")
async def read_main(outer_one=deps.depends(Outer), outer_two=deps.depends(Outer)):
    return {"outer_one": hash(outer_one.inner), "outer_two": hash(outer_two.inner)}


@app.get("/inner")
async def another_route(dep_one=deps.depends(Inner)):
    return {"data": dep_one.msg}


@app.get("/request_injected_request_singleton")
async def request_injected_request_singleton(
    dep_one=deps.depends(RequestInjectedSingleton),
):
    return {"data": dep_one.request.url.path}


@app.get("/with_some_context")
async def a_route_with_context(dep_one=deps.depends(ContextLoaded)):
    return {"cleaned_up": str(dep_one)}


@app.get("/with_double_context")
async def a_route_with_two_contexts(
    dep_one=deps.depends(ContextLoaded), dep_two=deps.depends(ContextLoaded)
):
    return {"one": str(dep_one), "two": str(dep_two)}
