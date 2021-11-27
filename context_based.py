import logging
from contextlib import ExitStack
from typing import Collection, Union, Type, TypeVar, Optional, cast, ContextManager, Iterator, Generator

from lagom import Container

X = TypeVar("X")


class ContextContainer(Container):
    context_types: Collection[Type]
    exit_stack: Optional[ExitStack]

    def __init__(self, container: Container, context_types: Collection[Type], log_undefined_deps: Union[bool, logging.Logger] = False):
        super().__init__(container, log_undefined_deps)
        self.context_types = set(context_types)

    def resolve(
            self, dep_type: Type[X], suppress_error=False, skip_definitions=False
    ) -> X:
        if dep_type in self.context_types:
            assert self.exit_stack, "Types can only be resolved within a with"
            type_def = self.get_definition(Iterator[dep_type]) or self.get_definition(Generator[dep_type, None, None])  # type: ignore
            assert type_def, f"Either Iterator[{dep_type}] or Generator[{dep_type}, None, None] should be defined"
            context_manager = cast(ContextManager, type_def.get_instance(self))
            return self.exit_stack.enter_context(context_manager)

        return super(ContextContainer, self).resolve(dep_type, suppress_error, skip_definitions)

    def __enter__(self):
        self.exit_stack = ExitStack()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.exit_stack, "__exit__ called before __enter__"
        self.exit_stack.close()
        self.exit_stack = None
