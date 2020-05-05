from lagom.definitions import X
from lagom.interfaces import SpecialDepDefinition, ReadableContainer


class PlainFunction(SpecialDepDefinition[X]):
    """Preserves a function without any dep injection performed on it"""

    callable_func: X

    def __init__(self, callable_func: X):
        """

        """
        self.callable_func = callable_func

    def get_instance(self, _container: ReadableContainer) -> X:
        return self.callable_func
