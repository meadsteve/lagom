from typing import TypeVar

INTROSPECTION_ATTRS = (
    "__module__",
    "__name__",
    "__qualname__",
    "__doc__",
    "__annotations__",
)

T = TypeVar("T")


def decorated_wrapper(wrapped: T, original) -> T:
    for attr in INTROSPECTION_ATTRS:
        if hasattr(original, attr):
            setattr(wrapped, attr, getattr(original, attr))
    return wrapped
