"""
Defines the per-invocation injection context used by bound functions to
resolve their dependencies against a fresh (cloned or updated) container.
"""

from typing import Optional, Callable

from .interfaces import ReadableContainer, ExtendableContainer


class TemporaryInjectionContext:
    """
    Context Manager wrapper around a container which applies the supplied function on
    __enter__
    """

    _base_container: ExtendableContainer
    _update_function: Optional[Callable[[ReadableContainer], ReadableContainer]] = None

    def __init__(
        self,
        container: ExtendableContainer,
        update_function: Optional[
            Callable[[ReadableContainer], ReadableContainer]
        ] = None,
    ):
        """Capture the base container and an optional per-enter update function."""
        self._base_container = container
        self._update_function = update_function
        if update_function is not None:
            self._build_temporary_container = lambda: update_function(
                self._base_container
            )
        else:
            self._build_temporary_container = lambda: self._base_container.clone()

    def __enter__(self) -> ReadableContainer:
        return self._build_temporary_container()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def rebind(self, new_container):
        """Return a copy of this context bound to a different base container."""
        return TemporaryInjectionContext(new_container, self._update_function)
