"""
For use with Starlette (https://www.starlette.io/)
"""

from typing import List, Type, Callable, Optional, Union

from starlette.routing import Route, WebSocketRoute
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint

from ..interfaces import ExtendableContainer

OVERRIDE_HTTP_METHODS = {
    "get",
    "head",
    "post",
    "put",
    "delete",
    "connect",
    "options",
    "trace",
    "patch",
}

OVERRIDE_WEBSOCKET_METHODS = {"on_connect", "on_receive", "on_disconnect"}


class StarletteIntegration:
    """
    Wraps a container and a route method for use in the Starlette framework
    """

    _request_singletons: List[Type]
    _container: ExtendableContainer

    def __init__(
        self,
        container: ExtendableContainer,
        request_singletons: Optional[List[Type]] = None,
    ):
        """
        :param request_singletons: List of types that will be singletons for a request
        :param container:
        """
        self._request_singletons = request_singletons or []
        self._container = container

    def route(
        self,
        path: str,
        endpoint: Callable,
        *,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> Route:
        """Returns an instance of a starlette Route
        The callable endpoint is bound to the container so dependencies can be
        injected. All other arguments are passed on to starlette.
        :param path:
        :param endpoint:
        :param methods:
        :param name:
        :param include_in_schema:
        :return:
        """
        wrapped = self.wrapped_endpoint_factory(endpoint, self._container.partial)

        return Route(
            path,
            wrapped,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )

    def magic_route(
        self,
        path: str,
        endpoint: Callable,
        *,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> Route:
        """Returns an instance of a starlette Route
        The callable endpoint is bound to the container so dependencies can be
        auto injected. All other arguments are passed on to starlette.
        :param path:
        :param endpoint:
        :param methods:
        :param name:
        :param include_in_schema:
        :return:
        """
        wrapped = self.wrapped_endpoint_factory(endpoint, self._container.magic_partial)

        return Route(
            path,
            wrapped,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )

    def ws_route(
        self,
        path: str,
        endpoint: Callable,
        *,
        name: Optional[str] = None,
    ) -> WebSocketRoute:
        """Returns an instance of a starlette WebSocketRoute
        The callable endpoint is bound to the container so dependencies can be
        injected. All other arguments are passed on to starlette.
        :param path:
        :param endpoint:
        :param name:
        :return:
        """
        wrapped = self.wrapped_endpoint_factory(endpoint, self._container.partial)

        return WebSocketRoute(path, wrapped, name=name)

    def ws_magic_route(
        self,
        path: str,
        endpoint: Callable,
        *,
        name: Optional[str] = None,
    ) -> WebSocketRoute:
        """Returns an instance of a starlette WebSocketRoute
        The callable endpoint is bound to the container so dependencies can be
        auto injected. All other arguments are passed on to starlette.
        :param path:
        :param endpoint:
        :param name:
        :return:
        """
        wrapped = self.wrapped_endpoint_factory(endpoint, self._container.magic_partial)

        return WebSocketRoute(path, wrapped, name=name)

    def wrapped_endpoint_factory(
        self, endpoint: Union[Callable, Type[HTTPEndpoint]], partial_provider: Callable
    ):
        """Builds an instance of a starlette Route with endpoint callables
        bound to the container so dependencies can be auto injected.

        :param endpoint:
        :param partial_provider:
        """
        if not isinstance(endpoint, type):
            return partial_provider(endpoint, shared=self._request_singletons)

        if issubclass(endpoint, HTTPEndpoint):
            return self.create_http_endpoint_proxy(
                endpoint, partial_provider, self._request_singletons
            )

        if issubclass(endpoint, WebSocketEndpoint):
            return self.create_websocket_endpoint_proxy(
                endpoint, partial_provider, self._request_singletons
            )

    @staticmethod
    def create_http_endpoint_proxy(
        endpoint_cls: Type[HTTPEndpoint],
        partial_provider: Callable,
        request_singletons: List[Type],
    ) -> Type[HTTPEndpoint]:
        """Create a subclass of Starlette's HTTPEndpoint which injects dependencies
        into HTTP-method-named methods on the user's `endpoint_cls` subclass of HTTPEndpoint

        :param endpoint_cls:
        :param partial_provider:
        :param request_singletons:
        """

        class HTTPEndpointProxy(HTTPEndpoint):
            def __init__(self, scope, receive, send):
                super().__init__(scope, receive, send)
                self.endpoint = endpoint_cls(scope, receive, send)

            def __getattribute__(self, name: str):
                if name in OVERRIDE_HTTP_METHODS:
                    endpoint_instance = object.__getattribute__(self, "endpoint")
                    endpoint_method = getattr(endpoint_instance, name)

                    return partial_provider(endpoint_method, shared=request_singletons)

                return object.__getattribute__(self, name)

        return HTTPEndpointProxy

    @staticmethod
    def create_websocket_endpoint_proxy(
        endpoint_cls: Type[WebSocketEndpoint],
        partial_provider: Callable,
        request_singletons: List[Type],
    ) -> Type[WebSocketEndpoint]:
        """Create a subclass of Starlette's WebSocketEndpoint which injects dependencies
        into relevant methods on the user's `endpoint_cls` subclass of WebSocketEndpoint

        :param endpoint_cls:
        :param partial_provider:
        :param request_singletons:
        """

        class WebSocketEndpointProxy(WebSocketEndpoint):
            def __init__(self, scope, receive, send):
                super().__init__(scope, receive, send)
                self.endpoint = endpoint_cls(scope, receive, send)

            def __getattribute__(self, name: str):
                if name in OVERRIDE_WEBSOCKET_METHODS:
                    endpoint_instance = object.__getattribute__(self, "endpoint")
                    endpoint_method = getattr(endpoint_instance, name)

                    return partial_provider(endpoint_method, shared=request_singletons)

                return object.__getattribute__(self, name)

        return WebSocketEndpointProxy
