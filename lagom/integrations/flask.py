from typing import Type, List, Optional

from flask import Flask

from lagom import Container


class FlaskContainer(Container):
    flask_app: Flask
    _request_singletons: List[Type]

    def __init__(
        self,
        app: Flask,
        request_singletons: Optional[List[Type]] = None,
        container=None,
    ):
        self.flask_app = app
        self._request_singletons = request_singletons or []
        super().__init__(container)

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", None)
            injected_func = self.partial(f, shared=self._request_singletons)
            self.flask_app.add_url_rule(rule, endpoint, injected_func, **options)
            return f

        return decorator
