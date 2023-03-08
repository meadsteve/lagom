import inspect
import logging
from asyncio import Lock
from contextlib import AsyncExitStack
from copy import copy
from functools import wraps
from typing import (
    Optional,
    Type,
    TypeVar,
    Awaitable,
    Generic,
    Collection,
    Union,
    ContextManager,
    AsyncContextManager,
    Iterator,
    Generator,
    AsyncGenerator,
    Callable,
    List,
    Dict,
)

from lagom.container import Container
from lagom.definitions import Alias, ConstructionWithContainer, SingletonWrapper
from lagom.exceptions import InvalidDependencyDefinition, MissingFeature
from lagom.experimental.definitions import AsyncConstructionWithContainer
from lagom.interfaces import (
    ReadableContainer,
    SpecialDepDefinition,
    CallTimeContainerUpdate,
    ContainerBoundFunction,
)

T = TypeVar("T")
X = TypeVar("X")


class AwaitableSingleton(Generic[T]):
    instance: Optional[T]
    constructor: ConstructionWithContainer[Awaitable[T]]
    container: Container
    _lock: Lock

    def __init__(self, constructor: ConstructionWithContainer, container: Container):
        self.instance = None
        self.constructor = constructor  # type: ignore
        self.container = container
        self._lock = Lock()

    async def get(self) -> T:
        if not self.instance:
            async with self._lock:
                if not self.instance:
                    self.instance = await self.constructor.get_instance(self.container)
        return self.instance


class _AsyncContextBoundFunction(ContainerBoundFunction[X]):
    """
    Represents an instance of a function bound to an async context container
    """

    async_context_container: "AsyncContextContainer"
    partially_bound_function: ContainerBoundFunction

    __slots__ = (
        "async_context_container",
        "partially_bound_function",
        "__dict__"
    )

    def __init__(
        self,
        async_context_container: "AsyncContextContainer",
        partially_bound_function: ContainerBoundFunction,
    ):
        self.async_context_container = async_context_container
        self.partially_bound_function = partially_bound_function

    def __call__(self, *args, **kwargs) -> X:
        return self.__async_call__(*args, **kwargs)

    async def __async_call__(self, *args, **kwargs):
        async with self.async_context_container as c:
            return await self.partially_bound_function.rebind(c)(*args, **kwargs)

    def rebind(self, container: ReadableContainer) -> "ContainerBoundFunction[X]":
        return wraps(self.partially_bound_function)(
            _AsyncContextBoundFunction(
                self.async_context_container,
                self.partially_bound_function.rebind(container),
            )
        )

    def __getattribute__(self, item):
        if item == "__dict__":
            return {}
        return super().__getattribute__(item)


class AsyncContextContainer(Container):
    async_exit_stack: Optional[AsyncExitStack] = None
    _context_types: Collection[Type]
    _context_singletons: Collection[Type]
    _root_context: bool = True

    def __init__(
        self,
        container: Container,
        context_types: Collection[Type],
        context_singletons: Collection[Type] = tuple(),
        log_undefined_deps: Union[bool, logging.Logger] = False,
    ):
        super().__init__(container, log_undefined_deps)
        self._context_types = set(context_types)
        self._context_singletons = set(context_singletons)

    def clone(self) -> "AsyncContextContainer":
        """returns a copy of the container
        :return:
        """
        return AsyncContextContainer(
            self,
            context_types=self._context_types,
            context_singletons=self._context_singletons,
            log_undefined_deps=self._undefined_logger,
        )

    async def __aenter__(self):
        if not self.async_exit_stack and self._root_context:
            self.async_exit_stack = AsyncExitStack()

        if self.async_exit_stack and self._root_context:
            # All actual context definitions happen on a clone so that there's isolation between invocations
            in_context = self.clone()
            in_context.async_exit_stack = AsyncExitStack()
            in_context._root_context = False

            for dep_type in self._context_types:
                managed_dep = self._context_type_def(dep_type)
                key = Awaitable[dep_type] if isinstance(managed_dep, AsyncConstructionWithContainer) else dep_type  # type: ignore
                in_context[key] = managed_dep  # type: ignore
            for dep_type in self._context_singletons:
                managed_singleton = self._singleton_type_def(dep_type)
                key = AwaitableSingleton[dep_type] if isinstance(managed_singleton, AwaitableSingleton) else dep_type  # type: ignore
                in_context[key] = managed_singleton  # type: ignore

            # The parent context manager keeps track of the inner clone
            await self.async_exit_stack.enter_async_context(in_context)
            return in_context
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.async_exit_stack:
            await self.async_exit_stack.aclose()
            self.async_exit_stack = None

    def partial(
        self,
        func: Callable[..., X],
        shared: Optional[List[Type]] = None,
        container_updater: Optional[CallTimeContainerUpdate] = None,
    ) -> ContainerBoundFunction[X]:
        if not inspect.iscoroutinefunction(func):
            raise MissingFeature(
                "AsyncContextManager currently can only deal with async functions"
            )
        base_partial = super(AsyncContextContainer, self).partial(
            func, shared, container_updater
        )

        return wraps(base_partial)(_AsyncContextBoundFunction(self, base_partial))

    def magic_partial(
        self,
        func: Callable[..., X],
        shared: Optional[List[Type]] = None,
        keys_to_skip: Optional[List[str]] = None,
        skip_pos_up_to: int = 0,
        container_updater: Optional[CallTimeContainerUpdate] = None,
    ) -> ContainerBoundFunction[X]:
        if not inspect.iscoroutinefunction(func):
            raise MissingFeature(
                "AsyncContextManager currently can only deal with async functions"
            )
        base_partial = super(AsyncContextContainer, self).magic_partial(
            func, shared, keys_to_skip, skip_pos_up_to, container_updater
        )

        return wraps(base_partial)(_AsyncContextBoundFunction(self, base_partial))

    def _context_type_def(self, dep_type: Type):
        type_def = self.get_definition(ContextManager[dep_type]) or self.get_definition(Iterator[dep_type]) or self.get_definition(Generator[dep_type, None, None]) or self.get_definition(AsyncGenerator[dep_type, None]) or self.get_definition(AsyncContextManager[dep_type])  # type: ignore
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
        if self.get_definition(AsyncGenerator[dep_type, None]) or self.get_definition(AsyncContextManager[dep_type]):  # type: ignore
            return AsyncConstructionWithContainer(lambda c: self._async_context_resolver(c, type_def))  # type: ignore
        return ConstructionWithContainer(lambda c: self._context_resolver(c, type_def))  # type: ignore

    def _context_resolver(self, c: ReadableContainer, type_def: SpecialDepDefinition):
        """
        Takes an existing definition which must be a context manager. Returns
        the value of the context manager from __enter__ and then places the
        __exit__ in this container's exit stack
        """
        assert self.async_exit_stack, "Types can only be resolved within an async with"
        context_manager = type_def.get_instance(c)
        return self.async_exit_stack.enter_context(context_manager)

    def _async_context_resolver(
        self, c: ReadableContainer, type_def: SpecialDepDefinition
    ):
        """
        Takes an existing definition which must be a context manager. Returns
        the value of the context manager from __aenter__ and then places the
        __aexit__ in this container's exit stack
        """
        assert self.async_exit_stack, "Types can only be resolved within an async with"
        context_manager = type_def.get_instance(c)
        return self.async_exit_stack.enter_async_context(context_manager)

    def _singleton_type_def(self, dep_type: Type):
        """
        The same as context_type_def but acts as a singleton within this container
        """
        type_def = self._context_type_def(dep_type)
        if isinstance(type_def, AsyncConstructionWithContainer):
            return AwaitableSingleton(type_def, self)
        return SingletonWrapper(type_def)
