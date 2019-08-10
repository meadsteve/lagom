import functools

from .container import Container


def bind_to_container(container: Container):
    def decorator(func):
        @functools.wraps(func)
        def bound_function(**kwargs):
            return container.partial(func, keys_to_skip=kwargs.keys())(**kwargs)

        return bound_function

    return decorator
