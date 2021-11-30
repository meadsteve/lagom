"""Lagom, a type based dependency injection container"""
from .container import Container, ExplicitContainer
from .context_based import ContextContainer
from .debug import get_build_info
from .decorators import (
    bind_to_container,
    magic_bind_to_container,
    dependency_definition,
    context_dependency_definition,
)
from .definitions import Singleton, Alias, UnresolvableTypeDefinition
from .markers import injectable
from .util.functional import FunctionCollection
from .version import __version__

__all__ = [
    "__version__",
    "get_build_info",
    "Singleton",
    "Alias",
    "UnresolvableTypeDefinition",
    "Container",
    "ExplicitContainer",
    "FunctionCollection",
    "bind_to_container",
    "magic_bind_to_container",
    "dependency_definition",
    "context_dependency_definition",
    "integrations",
    "experimental",
    "exceptions",
    "environment",
    "injectable",
    "ContextContainer",
]
