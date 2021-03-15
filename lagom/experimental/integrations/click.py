from typing import Optional, List, Type

from click import utils, decorators

from lagom.interfaces import ExtendableContainer, WriteableContainer


class ClickIO:
    """
    Provides an injectable hint for click IO if needed.
    """
    @staticmethod
    def echo(message=None, file=None, nl=True, err=False, color=None):
        utils.echo(message, file, nl, err, color)

    def __getattr__(self, item):
        import click
        return getattr(click, item)


class ClickIntegration:
    """
    Integration between a container and the FastAPI framework.
    Provides a method `Depends` which functions in the same way as
    FastApi `Depends`
    """

    _container: WriteableContainer

    def __init__(
        self,
        container: ExtendableContainer,
        execution_singletons: Optional[List[Type]] = None,
    ):
        self._container = container.clone()
        self._container[ClickIO] = ClickIO()
        self._execution_singletons = execution_singletons or []

    def command(self, name=None, cls=None, **attrs):
        def _decorator(f):
            bound_f = self._container.partial(f, shared=self._execution_singletons)
            return decorators.command(name, cls, **attrs)(bound_f)

        return _decorator

    @staticmethod
    def option(*param_decls, **attrs):
        return decorators.option(*param_decls, **attrs)

    def __getattr__(self, item):
        # Any method not explicitly code just gets passed to click
        import click
        return getattr(click, item)
