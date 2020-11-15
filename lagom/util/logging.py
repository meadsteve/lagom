""" Help with logging within lagom
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    class NullLogger(Logger):
        """
        The NullLogger should type exactly as a regular logger
        """

        def __init__(self):
            pass


else:

    class NullLogger:
        """
        Implements the contract of a logger but does nothing
        """

        def debug(self, msg, *args, **kwargs):
            pass

        def info(self, msg, *args, **kwargs):
            pass

        def warning(self, msg, *args, **kwargs):
            pass

        def error(self, msg, *args, **kwargs):
            pass

        def exception(self, msg, *args, exc_info=True, **kwargs):
            pass

        def critical(self, msg, *args, **kwargs):
            pass
