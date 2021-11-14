import pytest

from starlette.routing import Route, WebSocketRoute
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from lagom import injectable
from lagom.integrations.starlette import StarletteIntegration


class MyDep:
    pass


class ComplexDep:
    def __init__(self, something):
        pass


def some_handler(request, dep: MyDep = injectable):
    return "ok"


def two_dep_handler(request, dep_one: MyDep = injectable, dep_two: MyDep = injectable):
    return "singleton" if dep_one is dep_two else "new instances"


async def some_async_handler(request, dep: MyDep = injectable):
    return "ok"


async def some_websocket_handler(session, dep: MyDep = injectable):
    await session.accept()
    await session.send_text("ok")
    await session.close()


class SomeEndpointHandler(HTTPEndpoint):
    async def get(self, request, dep: MyDep = injectable):
        return PlainTextResponse("ok")


class SomeWebSocketHandler(WebSocketEndpoint):
    encoding = "text"

    async def on_connect(self, websocket, dep: MyDep = injectable):
        await websocket.accept()
        await websocket.send_text("connected")

    async def on_receive(self, websocket, data, dep: MyDep = injectable):
        await websocket.send_text("received")

    async def on_disconnect(self, websocket, close_code, dep: MyDep = injectable):
        pass


def test_a_special_starlette_container_can_be_used_and_provides_routes(container):
    sc = StarletteIntegration(container)
    route = sc.route("/", some_handler)
    assert isinstance(route, Route)
    assert route.endpoint({}) == "ok"


def test_the_starlette_container_can_define_request_level_singletons(container):
    sc = StarletteIntegration(container, request_singletons=[MyDep])
    route = sc.route("/two", two_dep_handler)
    assert route.endpoint({}) == "singleton"


@pytest.mark.asyncio
async def test_the_starlette_container_handles_async_handlers(container):
    sc = StarletteIntegration(container, request_singletons=[MyDep])

    route = sc.route("/", some_async_handler)

    assert isinstance(route, Route)
    assert await route.endpoint({}) == "ok"


@pytest.mark.asyncio
async def test_the_starlette_container_can_handle_endpoint_classes(container):
    sc = StarletteIntegration(container)
    route = sc.route("/", SomeEndpointHandler)
    assert isinstance(route, Route)

    client = TestClient(route)
    response = client.get("/")

    assert response.status_code == 200
    assert response.text == "ok"


def test_starlette_container_can_handle_websocket_funcs(container):
    sc = StarletteIntegration(container)
    route = sc.ws_route("/", some_websocket_handler)

    assert isinstance(route, WebSocketRoute)

    client = TestClient(route)

    with client.websocket_connect("/") as session:
        text = session.receive_text()
        assert text == "ok"


def test_starlette_container_can_handle_websocket_endpoints(container):
    sc = StarletteIntegration(container)
    route = sc.ws_route("/", SomeWebSocketHandler)

    assert isinstance(route, WebSocketRoute)

    client = TestClient(route)

    with client.websocket_connect("/") as session:
        connect_msg = session.receive_text()
        assert connect_msg == "connected"

        session.send_text("hello")
        receive_msg = session.receive_text()

        assert receive_msg == "received"
