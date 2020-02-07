from typing import List, Type, Callable, Optional

from starlette.routing import Route

from .. import Container


class StarletteContainer(Container):
    _request_singletons: List[Type]

    def __init__(self, request_singletons: Optional[List[Type]] = None, container=None):
        self._request_singletons = request_singletons or []
        super().__init__(container)

    def route(
        self,
        path: str,
        endpoint: Callable,
        *,
        methods: List[str] = None,
        name: str = None,
        include_in_schema: bool = True,
    ) -> Route:
        wrapped_endpoint = self.partial(endpoint, shared=self._request_singletons)
        return Route(
            path,
            wrapped_endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )
