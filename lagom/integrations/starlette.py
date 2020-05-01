"""
For use with Starlette (https://www.starlette.io/)
"""
from typing import List, Type, Callable, Optional

from starlette.routing import Route

from .. import Container


class StarletteContainer(Container):
    """
    Basic container plus a route method for use in the Starlette framework
    """

    _request_singletons: List[Type]

    def __init__(self, request_singletons: Optional[List[Type]] = None, container=None):
        """
        :param request_singletons: List of types that will be singletons for a request
        :param container:
        """
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
        """Returns an instance of a starlette Route
        The callable endpoint is bound to the cotainer so dependencies can be
        auto-injected. All other arguments are passed on to starlette.
        :param path:
        :param endpoint:
        :param methods:
        :param name:
        :param include_in_schema:
        :return:
        """
        wrapped_endpoint = self.partial(endpoint, shared=self._request_singletons)
        return Route(
            path,
            wrapped_endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )
