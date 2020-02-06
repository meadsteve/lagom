from flask import Flask

from lagom import Container


class FlaskContainer(Container):
    flask_app: Flask

    def __init__(self, app: Flask, container=None):
        self.flask_app = app
        super().__init__(container)

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", None)
            injected_func = self.partial(f)
            self.flask_app.add_url_rule(rule, endpoint, injected_func, **options)
            return f

        return decorator
