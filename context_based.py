import logging
from contextlib import ExitStack
from typing import Collection, Union, Type, TypeVar, Optional, cast, ContextManager, Iterator, Generator

from lagom import Container
from lagom.definitions import ConstructionWithContainer
from lagom.exceptions import InvalidDependencyDefinition
from lagom.interfaces import ReadableContainer, SpecialDepDefinition

X = TypeVar("X")


class ContextContainer(Container):
    exit_stack: Optional[ExitStack]

    def __init__(self, container: Container, context_types: Collection[Type], log_undefined_deps: Union[bool, logging.Logger] = False):
        super().__init__(container, log_undefined_deps)
        for dep_type in set(context_types):
            self._define_context_type(dep_type)

    def __enter__(self):
        self.exit_stack = ExitStack()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.exit_stack, "__exit__ called before __enter__"
        self.exit_stack.close()
        self.exit_stack = None

    def _define_context_type(self, dep_type: Type):
        type_def = self.get_definition(Iterator[dep_type]) or self.get_definition(Generator[dep_type, None, None])  # type: ignore
        if type_def is None:
            raise InvalidDependencyDefinition(f"Either Iterator[{dep_type}] or Generator[{dep_type}, None, None] should be defined")
        self.define(dep_type, ConstructionWithContainer(lambda c: self._context_resolver(c, type_def)))  # type: ignore

    def _context_resolver(self, c: ReadableContainer, type_def: SpecialDepDefinition):
        """
        Takes an existing definition which must be a context manager. Returns
        the value of the context manager from __enter__ and then places the
        __exit__ in this container's exit stack
        """
        assert self.exit_stack, "Types can only be resolved within a with"
        context_manager = cast(ContextManager, type_def.get_instance(c))
        return self.exit_stack.enter_context(context_manager)
