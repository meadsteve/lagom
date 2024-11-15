"""
Extra pieces for the flask integration that aren't quite stable.
For the stable code for flask see lagom.integrations.flask
"""

from typing import List, Type, Optional, Callable, Dict

from flask.blueprints import Blueprint

from lagom.integrations.flask import FlaskIntegration
from lagom.interfaces import ExtendableContainer


class FlaskBlueprintIntegration(FlaskIntegration):
    """
    Wraps a flask blueprint and a container so that dependencies are provided to
    flask routes
    """

    blueprint: Blueprint
    _injection_map: Dict[Callable, Callable]

    def __init__(
        self,
        blueprint: Blueprint,
        container: ExtendableContainer,
        request_singletons: Optional[List[Type]] = None,
    ):
        """
        :param blueprint: The flask blueprint to provide dependency injection for
        :param request_singletons: A list of types that should be singletons for a request
        :param container: an existing container to provide dependencies
        """
        # A blueprint is not actually a flask app but we can pretend it is for this
        # integration.
        # TODO: Refactor this properly when moving out of experimental
        super().__init__(blueprint, container, request_singletons)  # type: ignore
        self.blueprint = blueprint

    def route(self, rule, **options):
        """Equivalent to the flask @route decorator
        Injectable arguments should be set by making the default value
        lagom.injectable
        """

        def _decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            if f not in self._injection_map:
                self._injection_map[f] = self._container.partial(
                    f, shared=self._request_singletons
                )
            self.blueprint.add_url_rule(
                rule, endpoint, self._injection_map[f], **options
            )
            return f

        return _decorator

    def magic_route(self, rule, **options):
        """Equivalent to the flask @route decorator
        The injection container will try and bind all arguments
        """

        def _decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            if f not in self._injection_map:
                self._injection_map[f] = self._container.magic_partial(
                    f, shared=self._request_singletons
                )
            self.blueprint.add_url_rule(
                rule, endpoint, self._injection_map[f], **options
            )
            return f

        return _decorator
