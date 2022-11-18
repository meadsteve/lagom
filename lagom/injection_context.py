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
        self._base_container = container
        self._update_function = update_function
        if self._update_function:
            self._build_temporary_container = lambda: self._update_function(
                self._base_container
            )
        else:
            self._build_temporary_container = lambda: self._base_container.clone()

    def __enter__(self) -> ReadableContainer:
        return self._build_temporary_container()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def rebound_to(self, new_container):
        return TemporaryInjectionContext(new_container, self._update_function)
