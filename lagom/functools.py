"""
Exports some modified versions of functions from functools
"""

from functools import wraps as functools_wraps, WRAPPER_UPDATES


def wraps(wrapped):
    """
    This has the same functionality as single arity functools.wraps but deals with the case
    where the wrapping object may not have __dict__
    """

    def _wrapper(wrapping):
        return functools_wraps(
            wrapped,
            updated=WRAPPER_UPDATES if hasattr(wrapping, "__dict__") else tuple(),
        )(wrapping)

    return _wrapper
