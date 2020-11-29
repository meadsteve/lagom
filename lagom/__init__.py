"""Lagom, a type based dependency injection container"""
from .version import __version__
from .debug import get_build_info
from .definitions import Singleton, Alias
from .container import Container, ExplicitContainer
from .decorators import (
    bind_to_container,
    magic_bind_to_container,
    dependency_definition,
)
from .markers import injectable

__all__ = [
    "__version__",
    "get_build_info",
    "Singleton",
    "Alias",
    "Container",
    "ExplicitContainer",
    "bind_to_container",
    "magic_bind_to_container",
    "dependency_definition",
    "integrations",
    "experimental",
    "exceptions",
    "environment",
    "injectable",
]
