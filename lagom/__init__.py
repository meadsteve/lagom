"""Lagom, a type based dependency injection container"""
from .version import __version__
from .definitions import Singleton, Alias
from .container import Container
from .decorators import bind_to_container
