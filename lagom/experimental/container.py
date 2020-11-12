from typing import Type, TypeVar

from .. import Container, Alias, Singleton
from .exceptions import DependencyNotDefined
from ..exceptions import InvalidDependencyDefinition

X = TypeVar("X")


class ExplicitContainer(Container):
    def resolve(
        self, dep_type: Type[X], suppress_error=False, skip_definitions=False
    ) -> X:
        try:
            type_to_build = self._registered_types[dep_type]
        except KeyError as key_error:
            if suppress_error:
                return None  # type: ignore
            raise DependencyNotDefined(
                f"{dep_type.__name__} has not been defined. "
                f"In an explict container all dependencies must be defined"
            ) from key_error
        return type_to_build.get_instance(self)

    def define(self, dep, resolver):
        definition = super().define(dep, resolver)
        if isinstance(definition, Alias):
            raise InvalidDependencyDefinition(
                "Aliases are not valid in an explicit container"
            )
        if isinstance(definition, Singleton) and isinstance(
            definition.singleton_type, Alias
        ):
            raise InvalidDependencyDefinition(
                "Aliases are not valid inside singletons in an explicit container"
            )
        return definition
