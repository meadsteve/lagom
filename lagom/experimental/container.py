from typing import Type, TypeVar

from lagom import Container
from lagom.experimental.exceptions import DependencyNotDefined

X = TypeVar("X")


class ExplicitContainer(Container):
    def resolve(
        self, dep_type: Type[X], suppress_error=False, skip_definitions=False
    ) -> X:
        if dep_type not in self.defined_types:
            if suppress_error:
                return None  # type: ignore
            raise DependencyNotDefined(
                f"{dep_type.__name__} has not been defined. "
                "In an explict container all dependencies must be defined"
            )
        return super().resolve(dep_type, suppress_error, skip_definitions)
