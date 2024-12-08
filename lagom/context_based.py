import logging
from contextlib import ExitStack
from copy import copy
from typing import (
    Collection,
    Union,
    Type,
    TypeVar,
    Optional,
    cast,
    ContextManager,
    Iterator,
    Generator,
    Callable,
    List,
)

from lagom import Container
from lagom.compilaton import mypyc_attr
from lagom.definitions import ConstructionWithContainer, SingletonWrapper, Alias
from lagom.exceptions import InvalidDependencyDefinition
from lagom.interfaces import (
    ReadableContainer,
    SpecialDepDefinition,
    CallTimeContainerUpdate,
)

X = TypeVar("X")


@mypyc_attr(allow_interpreted_subclasses=True)
class ContextContainer(Container):
    """
    Wraps a regular container but is a ContextManager for use within a `with`.

    >>> from tests.examples import SomeClass, SomeClassManager
    >>> from lagom import Container
    >>> from typing import ContextManager
    >>>
    >>> # The regular container
    >>> c = Container()
    >>>
    >>> # register a context manager for SomeClass
    >>> c[ContextManager[SomeClass]] = SomeClassManager
    >>>
    >>> context_c = ContextContainer(c, context_types=[SomeClass])
    >>> with context_c as c:
    ...     c[SomeClass]
    <tests.examples.SomeClass object at ...>
    """

    exit_stack: Optional[ExitStack] = None
    _context_types: Collection[Type]
    _context_singletons: Collection[Type]

    def __init__(
        self,
        container: Container,
        context_types: Collection[Type],
        context_singletons: Collection[Type] = tuple(),
        log_undefined_deps: Union[bool, logging.Logger] = False,
    ):
        self._context_types = context_types
        self._context_singletons = context_singletons
        super().__init__(container, log_undefined_deps)

    def clone(self) -> "ContextContainer":
        """returns a copy of the container
        :return:
        """
        return ContextContainer(
            self,
            context_types=self._context_types,
            context_singletons=self._context_singletons,
            log_undefined_deps=self._undefined_logger,
        )

    def __copy__(self):
        return self.clone()

    def __enter__(self):
        if not self.exit_stack:
            # All actual context definitions happen on a clone so that there's isolation between invocations
            in_context = self.clone()
            for dep_type in set(self._context_types):
                in_context[dep_type] = self._context_type_def(dep_type)
            for dep_type in set(self._context_singletons):
                in_context[dep_type] = self._singleton_type_def(dep_type)
            in_context.exit_stack = ExitStack()

            # The parent context manager keeps track of the inner clone
            self.exit_stack = ExitStack()
            self.exit_stack.enter_context(in_context)
            return in_context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.exit_stack:
            self.exit_stack.close()
            self.exit_stack = None

    def partial(
        self,
        func: Callable[..., X],
        shared: Optional[List[Type]] = None,
        container_updater: Optional[CallTimeContainerUpdate] = None,
    ) -> Callable[..., X]:
        def _with_context(*args, **kwargs):
            with self as c:
                # TODO: Try and move this partial outside the function as this is expensive
                base_partial = super(ContextContainer, c).partial(
                    func, shared, container_updater
                )
                return base_partial(*args, **kwargs)

        return _with_context

    def magic_partial(
        self,
        func: Callable[..., X],
        shared: Optional[List[Type]] = None,
        keys_to_skip: Optional[List[str]] = None,
        skip_pos_up_to: int = 0,
        container_updater: Optional[CallTimeContainerUpdate] = None,
    ) -> Callable[..., X]:
        def _with_context(*args, **kwargs):
            with self as c:
                # TODO: Try and move this partial outside the function as this is expensive
                base_partial = super(ContextContainer, c).magic_partial(
                    func, shared, keys_to_skip, skip_pos_up_to, container_updater
                )
                return base_partial(*args, **kwargs)

        return _with_context

    def _context_type_def(self, dep_type: Type):
        type_def = self.get_definition(ContextManager[dep_type]) or self.get_definition(Iterator[dep_type]) or self.get_definition(Generator[dep_type, None, None])  # type: ignore
        if type_def is None:
            raise InvalidDependencyDefinition(
                f"A ContextManager[{dep_type}] should be defined. "
                f"This could be an Iterator[{dep_type}] or Generator[{dep_type}, None, None] "
                f"with the @contextmanager decorator"
            )
        if isinstance(type_def, Alias):
            # Without this we create a definition that points to
            # itself.
            type_def = copy(type_def)
            type_def.skip_definitions = True
        return ConstructionWithContainer(lambda c: self._context_resolver(c, type_def))  # type: ignore

    def _singleton_type_def(self, dep_type: Type):
        """
        The same as context_type_def but acts as a singleton within this container
        """
        return SingletonWrapper(self._context_type_def(dep_type))

    def _context_resolver(self, c: ReadableContainer, type_def: SpecialDepDefinition):
        """
        Takes an existing definition which must be a context manager. Returns
        the value of the context manager from __enter__ and then places the
        __exit__ in this container's exit stack
        """
        assert self.exit_stack, "Types can only be resolved within a with"
        context_manager = cast(ContextManager, type_def.get_instance(c))
        return self.exit_stack.enter_context(context_manager)
