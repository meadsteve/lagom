import functools
import logging
from contextlib import ExitStack, contextmanager
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
from lagom.exceptions import InvalidDependencyDefinition, ContextReuseError
from lagom.interfaces import (
    ReadableContainer,
    SpecialDepDefinition,
    CallTimeContainerUpdate,
)

X = TypeVar("X")


def context_container(
    container: Container,
    context_types: Collection[Type],
    context_singletons: Collection[Type] = tuple(),
) -> "_ContextContainer":
    return _ContextContainer(container, context_types, context_singletons)


class _ContextContainer:
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
    >>> with context_container(c, context_types=[SomeClass]) as c:
    ...     c[SomeClass]
    <tests.examples.SomeClass object at ...>
    """

    exit_stack: ExitStack
    _container: Container
    _context_types: Collection[Type]
    _context_singletons: Collection[Type]
    _used: bool

    def __init__(
        self,
        container: Container,
        context_types: Collection[Type],
        context_singletons: Collection[Type] = tuple(),
    ):
        self._container = container
        self._context_types = context_types
        self.exit_stack = ExitStack()
        self._used = False
        self._context_singletons = context_singletons

    def clone(self) -> "_ContextContainer":
        if self._used:
            raise ContextReuseError()
        return self.__class__(
            self._container, self._context_types, self._context_singletons
        )

    def partial(
        self,
        func: Callable[..., X],
        shared: Optional[List[Type]] = None,
    ) -> Callable[..., X]:

        @functools.wraps(func)
        def _f(*args, **kwargs):
            with self.clone() as c:
                return c.partial(func, shared)(*args, **kwargs)

        return _f

    def magic_partial(
        self,
        func: Callable[..., X],
        shared: Optional[List[Type]] = None,
    ) -> Callable[..., X]:

        @functools.wraps(func)
        def _f(*args, **kwargs):
            with self.clone() as c:
                return c.magic_partial(func, shared)(*args, **kwargs)

        return _f

    def __enter__(self):
        if self._used:
            raise ContextReuseError()
        self._used = True
        in_context = self._container.clone()
        for dep_type in set(self._context_types):
            in_context[dep_type] = self._context_type_def(dep_type)
        for dep_type in set(self._context_singletons):
            in_context[dep_type] = self._singleton_type_def(dep_type)

        return in_context

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_stack.close()

    def _context_type_def(self, dep_type: Type):
        type_def = self._container.get_definition(ContextManager[dep_type]) or self._container.get_definition(Iterator[dep_type]) or self._container.get_definition(Generator[dep_type, None, None])  # type: ignore
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
