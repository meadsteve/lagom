from .container import Container


def bind_to_container(container: Container):
    def decorator(func):
        return container.partial(func)

    return decorator
