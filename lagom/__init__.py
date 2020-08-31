"""Lagom, a type based dependency injection container"""
from .version import __version__
from .definitions import Singleton, Alias
from .container import Container
from .decorators import (
    bind_to_container,
    magic_bind_to_container,
    dependency_definition,
)
from .markers import injectable
from . import integrations, environment, experimental, exceptions

__all__ = [
    "__version__",
    "Singleton",
    "Alias",
    "Container",
    "bind_to_container",
    "magic_bind_to_container",
    "dependency_definition",
    "integrations",
    "experimental",
    "exceptions",
    "environment",
    "injectable",
]
