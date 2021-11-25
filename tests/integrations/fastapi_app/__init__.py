from fastapi import FastAPI

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
