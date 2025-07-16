"""
Integration layer for Click https://click.palletsprojects.com/
"""

from typing import Optional, List, Type, Callable

from click import utils, decorators
from click.core import Command

from lagom.interfaces import ExtendableContainer, WriteableContainer


class DecoratedCommand(Command):
    """
    Virtual class which is returned by the lagom wrapped click command
    decorator
    """

    plain_function: Callable


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
    Integration between a container and click. The ClickIntegration
    instance provides all the same decorators and functions as click.
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

    def command(
        self, name=None, cls=None, **attrs
    ) -> Callable[[Callable], DecoratedCommand]:
        """
        Proxies click.command but binds the function to lagom
        so that any arguments with lagom.injectable as a default will
        be injected by the container
        :param name:
        :param cls:
        :param attrs:
        :return:
        """

        def _decorator(f):
            bound_f = self._container.partial(f, shared=self._execution_singletons)
            command = decorators.command(name, cls, **attrs)(bound_f)
            setattr(command, "plain_function", bound_f)
            return command

        return _decorator

    @staticmethod
    def option(*param_decls, **attrs):
        """
        Proxies click.option
        :param param_decls:
        :param attrs:
        :return:
        """
        return decorators.option(*param_decls, **attrs)

    @staticmethod
    def argument(*param_decls, **attrs):
        """
        Proxies click.argument
        :param param_decls:
        :param attrs:
        :return:
        """
        return decorators.argument(*param_decls, **attrs)

    def __getattr__(self, item):
        # Any method not explicitly code just gets passed to click
        import click

        return getattr(click, item)
