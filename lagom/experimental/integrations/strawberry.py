import inspect
from typing import Set, Type, TypeVar, _GenericAlias

from strawberry.dataloader import DataLoader

from lagom import Container
from lagom.interfaces import SpecialDepDefinition, TypeResolver

X = TypeVar("X")


class StrawberryContainer(Container):
    _data_loader_types: Set[Type[DataLoader]]

    def __init__(self):
        self._data_loader_types = set()
        super().__init__()

    def define(self, dep: Type[X], resolver: TypeResolver[X]) -> SpecialDepDefinition:
        if isinstance(dep, _GenericAlias) and inspect.isclass(dep.__origin__) and issubclass(dep.__origin__, DataLoader):
            self._data_loader_types.add(dep)
        if inspect.isclass(dep) and issubclass(dep, DataLoader):
            self._data_loader_types.add(dep)
        return super().define(dep, resolver)

    def strawberry_context_container(self):
        with self.temporary_singletons(self._data_loader_types) as c:
            return c
