"""
Exceptions raised by the library
"""
import inspect
import typing
from abc import ABC
from typing import Type


class LagomException(Exception, ABC):
    """All exceptions in this library are instances of a LagomException"""

    pass


class InjectableNotResolved(RuntimeError, LagomException):
    """
    An instance of injectable was consumed in some user code.
    This should not occur as lagom should have replaced the injectable
    with an object. This likely means the function wasn't bound to
    an injection container.
    """

    pass


class InvalidDependencyDefinition(ValueError, LagomException):
    """The provided construction logic is not valid"""

    pass


class ClassesCannotBeDecorated(SyntaxError, LagomException):
    """Decorating classes is not supported by lagom"""

    dep_type: str

    def __init__(self):
        super().__init__(
            "Decorating classes is not supported by lagom. \n"
            "Alternative is to create a factory method and use that: \n"
            "factory_func = container.partial(ClassName)"
        )


class MissingReturnType(SyntaxError, LagomException):
    """The function provided doesnt type hint a return"""

    pass


class DuplicateDefinition(ValueError, LagomException):
    """The type has already been defined somewhere else"""

    pass


class UnableToInvokeBoundFunction(TypeError, LagomException):
    """A function bound to the container could not be invoked"""

    unresolvable_deps: typing.List[Type]

    def __init__(self, msg, unresolvable_deps):
        self.unresolvable_deps = unresolvable_deps
        unresolvable_string_list = ",".join(d.__name__ for d in unresolvable_deps)
        super().__init__(
            f"{msg}. The container could not construct the following types: {unresolvable_string_list}"
        )


class UnresolvableType(ValueError, LagomException):
    """The type cannot be constructed"""

    dep_type: str

    def __init__(self, dep_type: Type):
        """

        :param dep_type: The type that could not be constructed
        """
        self.dep_type = _dep_type_as_string(dep_type)
        if inspect.isabstract(dep_type):
            super().__init__(
                f"Unable to construct Abstract type {self.dep_type}."
                "Try defining an alias or a concrete class to construct"
            )
        else:
            super().__init__(
                f"Unable to construct dependency of type {self.dep_type} "
                "The constructor probably has some unresolvable dependencies"
            )


class TypeResolutionBlocked(UnresolvableType):
    """The type was explicitly blocked by configuration"""

    def __init__(self, msg: str):
        super(ValueError, self).__init__(msg)


class RecursiveDefinitionError(SyntaxError, LagomException):
    """Whilst trying to resolve the type python exceeded the recursion depth"""

    dep_type: Type

    def __init__(self, dep_type: Type):
        """
        :param dep_type: The type that could not be constructed
        """
        self.dep_type = dep_type

        super().__init__(
            f"When trying to build dependency of type '{_dep_type_as_string(dep_type)}' python hit a recursion limit. "
            "This could indicate a circular definition somewhere."
        )


class DependencyNotDefined(ValueError, LagomException):
    """The type must be explicitly defined in the container"""

    dep_type: Type

    def __init__(self, dep_type: Type):
        """
        :param dep_type: The type that was not defined
        """
        self.dep_type = dep_type
        super().__init__(
            f"{_dep_type_as_string(dep_type)} has not been defined. "
            f"In an explict container all dependencies must be defined"
        )


def _dep_type_as_string(dep_type: Type):
    # This first check makes 3.6 behave the same as 3.7 and later
    if hasattr(typing, "GenericMeta") and isinstance(dep_type, typing.GenericMeta):  # type: ignore
        return str(dep_type)
    elif hasattr(typing, "get_origin") and typing.get_origin(dep_type) is not None:
        # repr() gives a more sensible output in version 3.10 for List[X] and others like this
        return repr(dep_type)
    elif hasattr(dep_type, "__name__"):
        return dep_type.__name__

    return str(dep_type)
