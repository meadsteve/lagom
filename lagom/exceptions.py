from typing import Type


class InvalidDependencyDefinition(ValueError):
    pass


class DuplicateDefinition(ValueError):
    pass


class UnresolvableType(ValueError):
    dep_type: str

    def __init__(self, dep_type: Type):
        self.dep_type = (
            dep_type.__name__ if hasattr(dep_type, "__name__") else str(dep_type)
        )
        super().__init__(
            f"Unable to construct dependency of type {self.dep_type} "
            "The constructor probably has some unresolvable dependencies"
        )
