import typing

from starlette.routing import Route as StarletteRoute

from .. import Container


class Route(StarletteRoute):
    def __init__(
        self,
        container: Container,
        path: str,
        endpoint: typing.Callable,
        *,
        methods: typing.List[str] = None,
        name: str = None,
        include_in_schema: bool = True,
    ):
        wrapped_endpoint = container.partial(endpoint)
        super().__init__(
            path,
            wrapped_endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )


class StarletteContainer(Container):
    def route(
        self,
        path: str,
        endpoint: typing.Callable,
        *,
        methods: typing.List[str] = None,
        name: str = None,
        include_in_schema: bool = True,
    ) -> Route:
        return Route(
            self,
            path,
            endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )
