import inspect

from .container import Container


def bind_to_container(container: Container):
    def decorator(func):
        return container.partial(func)

    return decorator


def dependency_definition(container: Container):
    def decorator(func):
        try:
            arg_spec = inspect.getfullargspec(func)
            return_type = arg_spec.annotations["return"]
        except KeyError:
            raise SyntaxError("Function used as a definition must have a return type")
        container.define(return_type, func)
        return func

    return decorator
