"""
Flask API (https://www.flaskapi.org/)
"""
from typing import Type, List, Optional

from flask import Flask

from lagom import Container


class FlaskContainer(Container):
    """
    Wraps a flask app so that the container dependencies are provided to
    flask routes
    """

    flask_app: Flask
    _request_singletons: List[Type]

    def __init__(
        self,
        app: Flask,
        request_singletons: Optional[List[Type]] = None,
        container=None,
    ):
        """

        :param app: The flask app to provide dependency injection for
        :param request_singletons: A list of types that should be singletons for a request
        :param container: an existing container to clone
        """
        self.flask_app = app
        self._request_singletons = request_singletons or []
        super().__init__(container)

    def route(self, rule, **options):
        """Equivalent to the flask @route decorator
        """

        def _decorator(f):
            endpoint = options.pop("endpoint", None)
            injected_func = self.partial(f, shared=self._request_singletons)
            self.flask_app.add_url_rule(rule, endpoint, injected_func, **options)
            return f

        return _decorator
