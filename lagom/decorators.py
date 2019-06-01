import functools

from .container import Container


def bind_to_container(container: Container):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return container.partial(func)(*args, **kwargs)

        return wrapper

    return decorator
