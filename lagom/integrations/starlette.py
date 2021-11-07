"""
For use with Starlette (https://www.starlette.io/)
"""
from inspect import isclass
from typing import List, Type, Callable, Optional, Union

from starlette.routing import Route
from starlette.endpoints import HTTPEndpoint

from ..interfaces import ExtendableContainer


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
        methods: List[str] = None,
        name: str = None,
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
        methods: List[str] = None,
        name: str = None,
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

    def wrapped_endpoint_factory(
        self,
        endpoint: Union[Callable, Type[HTTPEndpoint]],
        partial_provider: Callable
    ):
        """Builds an instance of a starlette Route with endpoint callables 
        bound to the container so dependencies can be auto injected. 

        :param endpoint: 
        :param partial_provider:
        """
        si = self
        
        if not (isinstance(endpoint, type) and issubclass(endpoint, HTTPEndpoint)):
            return partial_provider(endpoint, shared=self._request_singletons)

        class HTTPEndpointProxy(HTTPEndpoint):
        
            def __init__(self, scope, receive, send):
                super().__init__(scope, receive, send)
                self.endpoint = endpoint(scope, receive, send)

            def __getattribute__(self, name: str):
                if name in (
                    "dispatch",
                    "method_not_allowed",
                    "scope",
                    "receive",
                    "send",
                ):
                    return object.__getattribute__(self, name)

                endpoint_instance = object.__getattribute__(self, "endpoint")
                endpoint_method = endpoint_instance.__getattribute__(name)

                return partial_provider(
                    endpoint_method, shared=si._request_singletons
                )

        return HTTPEndpointProxy
