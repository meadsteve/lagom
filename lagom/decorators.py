import inspect
from typing import List, Type

from .container import Container
from .util.reflection import RETURN_ANNOTATION


def bind_to_container(container: Container, shared: List[Type] = None):
    def decorator(func):
        return container.partial(func, shared=shared)

    return decorator


def dependency_definition(container: Container):
    def decorator(func):
        try:
            arg_spec = inspect.getfullargspec(func)
            return_type = arg_spec.annotations[RETURN_ANNOTATION]
        except KeyError:
            raise SyntaxError("Function used as a definition must have a return type")
        container.define(return_type, func)
        return func

    return decorator
