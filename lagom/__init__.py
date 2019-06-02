"""Lagom, a type based dependency injection container"""

__version__ = "0.1.0"

from .definitions import Singleton, Construction, Alias
from .container import Container
from .decorators import bind_to_container
