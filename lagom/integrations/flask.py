"""
Flask API (https://www.flaskapi.org/)
"""
from typing import Type, List, Optional, Any, Dict, Callable

from flask import Flask, request

from ..definitions import ConstructionWithoutContainer
from ..interfaces import ExtendableContainer, WriteableContainer


class _Request:
    pass


# Exposing a type to be flask's request
# for now it's an any type but later this could be better.
Request: Any = _Request


class FlaskIntegration:
    """
    Wraps a flask app and a container so that dependencies are provided to
    flask routes
    """

    flask_app: Flask
    _container: WriteableContainer
    _request_singletons: List[Type]
    _injection_map: Dict[Callable, Callable]

    def __init__(
        self,
        app: Flask,
        container: ExtendableContainer,
        request_singletons: Optional[List[Type]] = None,
    ):
        """

        :param app: The flask app to provide dependency injection for
        :param request_singletons: A list of types that should be singletons for a request
        :param container: an existing container to provide dependencies
        """
        self.flask_app = app
        self._container = container.clone()
        self._container[Request] = ConstructionWithoutContainer(lambda: request)
        self._request_singletons = request_singletons or []
        self._injection_map = {}

    def route(self, rule, **options):
        """Equivalent to the flask @route decorator
        Injectable arguments should be set by making the default value
        lagom.injectable
        """

        def _decorator(f):
            endpoint = options.pop("endpoint", None)
            if f not in self._injection_map:
                self._injection_map[f] = self._container.partial(
                    f, shared=self._request_singletons
                )
            self.flask_app.add_url_rule(
                rule, endpoint, self._injection_map[f], **options
            )
            return f

        return _decorator

    def magic_route(self, rule, **options):
        """Equivalent to the flask @route decorator
        The injection container will try and bind all arguments
        """

        def _decorator(f):
            endpoint = options.pop("endpoint", None)
            if f not in self._injection_map:
                self._injection_map[f] = self._container.magic_partial(
                    f, shared=self._request_singletons
                )
            self.flask_app.add_url_rule(
                rule, endpoint, self._injection_map[f], **options
            )
            return f

        return _decorator
