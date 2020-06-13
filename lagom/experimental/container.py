from typing import Type, TypeVar, Set

from .. import Container
from .exceptions import DependencyNotDefined

X = TypeVar("X")


class ExplicitContainer(Container):
    def _resolve(
        self,
        dep_type: Type[X],
        suppress_error=False,
        skip_definitions=False,
        types_to_skip: Set[Type] = None,
    ):
        if dep_type not in self.defined_types:
            if suppress_error:
                return None  # type: ignore
            raise DependencyNotDefined(
                f"{dep_type.__name__} has not been defined. "
                "In an explict container all dependencies must be defined"
            )
        return super()._resolve(
            dep_type, suppress_error, skip_definitions, types_to_skip
        )
