import inspect
from typing import Set, Type, TypeVar, _GenericAlias, MutableMapping

from strawberry.dataloader import DataLoader
from strawberry.types import Info

from lagom import Container, injectable
from lagom.interfaces import SpecialDepDefinition, TypeResolver, ReadableContainer

X = TypeVar("X")


CONTEXT_KEY = "__lagom__.dependencies"


class LagomNotAddedToStrawberryError(RuntimeError):
    pass


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

    def hook_into_context(self, context: MutableMapping):
        context[CONTEXT_KEY] = self.strawberry_context_container()

    def attach_field(container_self, field_func):
        # TODO: I'm a bit copy pasted. dry me up. Maybe?
        spec = container_self._get_spec_without_self(field_func)
        keys_to_bind = (
            key for (key, arg) in spec.defaults.items() if arg is injectable
        )
        keys_and_types = [(key, spec.annotations[key]) for key in keys_to_bind]

        def _wrapper(self, info: Info):
            if not info.context or CONTEXT_KEY not in info.context:
                raise LagomNotAddedToStrawberryError("The context needs to be updated with container.hook_into_context")
            req_container: ReadableContainer = info.context[CONTEXT_KEY]
            kwargs = {key: req_container.resolve(dep_type) for (key, dep_type) in keys_and_types}
            return field_func(self, **kwargs)
        _wrapper.__annotations__['return'] = field_func.__annotations__['return']
        return _wrapper
