"""
Classes representing specific ways of representing dependencies
"""
import inspect
from threading import Lock
from typing import Union, Type, Optional, Callable, TypeVar, NoReturn, Iterator

from .exceptions import (
    InvalidDependencyDefinition,
    TypeResolutionBlocked,
)
from .interfaces import SpecialDepDefinition, ReadableContainer, TypeResolver
from .util.functional import arity

X = TypeVar("X")


class ConstructionWithoutContainer(SpecialDepDefinition[X]):
    """Wraps a callable for constructing a type"""

    def __init__(self, constructor: Callable[[], X]):
        self.constructor = constructor

    def get_instance(self, container: ReadableContainer) -> X:
        resolver = self.constructor
        return resolver()


class ConstructionWithContainer(SpecialDepDefinition[X]):
    """Wraps a callable for constructing a type"""

    def __init__(self, constructor: Callable[[ReadableContainer], X]):
        self.constructor = constructor

    def get_instance(self, container: ReadableContainer) -> X:
        resolver = self.constructor
        return resolver(container)


class YieldWithoutContainer(SpecialDepDefinition[X]):
    """Wraps a callable for constructing a type"""

    def __init__(self, constructor: Callable[[], Iterator[X]]):
        self.constructor = constructor

    def get_instance(self, container: ReadableContainer) -> X:
        resolver = self.constructor
        return next(resolver())


class YieldWithContainer(SpecialDepDefinition[X]):
    """Wraps a generator for constructing a type"""

    def __init__(self, constructor: Callable[[ReadableContainer], Iterator[X]]):
        self.constructor = constructor

    def get_instance(self, container: ReadableContainer) -> X:
        resolver = self.constructor
        return next(resolver(container))


def construction(
    resolver: Callable,
) -> Union[ConstructionWithContainer, ConstructionWithoutContainer]:
    """
    Takes a generator and returns a type definition
    :param reflector:
    :param resolver:
    :return:
    """
    func_arity = arity(resolver)
    if func_arity == 0:
        return ConstructionWithoutContainer(resolver)
    if func_arity == 1:
        return ConstructionWithContainer(resolver)
    raise InvalidDependencyDefinition(f"Arity {func_arity} functions are not supported")


def yielding_construction(
    resolver: Callable,
) -> Union[YieldWithContainer, YieldWithoutContainer]:
    """
    Takes a generator and returns a type definition
    :param reflector:
    :param resolver:
    :return:
    """
    func_arity = arity(resolver)
    if func_arity == 0:
        return YieldWithoutContainer(resolver)
    if func_arity == 1:
        return YieldWithContainer(resolver)
    raise InvalidDependencyDefinition(
        f"Arity {func_arity} generators are not supported"
    )


class Alias(SpecialDepDefinition[X]):
    """When one class is asked for the other should be returned"""

    alias_type: Type[X]
    skip_definitions: bool

    def __init__(self, alias_type, skip_definitions=False):
        self.alias_type = alias_type
        self.skip_definitions = skip_definitions

    def get_instance(self, container: ReadableContainer) -> X:
        return container.resolve(
            self.alias_type, skip_definitions=self.skip_definitions
        )

    def __copy__(self):
        return Alias(self.alias_type, self.skip_definitions)


class SingletonWrapper(SpecialDepDefinition[X]):
    """Builds only once then saves the built instance"""

    singleton_type: SpecialDepDefinition
    _instance: Optional[X]
    _thread_lock: Lock

    def __init__(self, def_to_wrap: SpecialDepDefinition):
        self.singleton_type = def_to_wrap
        self._instance = None
        self._thread_lock = Lock()

    def get_instance(self, container: ReadableContainer) -> X:
        if self._has_instance:
            return self._instance  # type: ignore
        return self._load_instance(container)

    @property
    def _has_instance(self) -> bool:
        return self._instance is not None

    def _load_instance(self, container):
        try:
            self._thread_lock.acquire()
            if self._has_instance:
                return self._instance
            self._instance = self.singleton_type.get_instance(container)
            return self._instance
        finally:
            self._thread_lock.release()


class Singleton(SingletonWrapper[X]):
    """Builds only once then saves the built instance"""

    def __init__(self, singleton_type: TypeResolver):
        super().__init__(normalise(singleton_type, skip_alias_definitions=True))


class PlainInstance(SpecialDepDefinition[X]):
    """Wraps an actual object that should just be returned"""

    value: X

    def __init__(self, value):
        self.value = value

    def get_instance(self, _) -> X:
        return self.value


class UnresolvableTypeDefinition(SpecialDepDefinition[NoReturn]):
    """
    Used to represent a type that should not be built by the container
    """

    _msg_or_exception: Union[str, Exception]

    def __init__(self, msg_or_exception: Union[str, Exception]):
        self._msg_or_exception = msg_or_exception

    def get_instance(self, container: ReadableContainer) -> NoReturn:
        if isinstance(self._msg_or_exception, Exception):
            raise self._msg_or_exception
        else:
            raise TypeResolutionBlocked(self._msg_or_exception)


def normalise(
    resolver: TypeResolver, skip_alias_definitions=False
) -> SpecialDepDefinition:
    """
    :param resolver:
    :param skip_alias_definitions if an alias is loaded should futher definitions be skipped
    :return:
    """
    if isinstance(resolver, SpecialDepDefinition):
        return resolver
    elif inspect.isfunction(resolver):
        return construction(resolver)  # type: ignore
    elif inspect.iscoroutinefunction(resolver):
        return construction(resolver)  # type: ignore
    elif inspect.isclass(resolver):
        return Alias(resolver, skip_alias_definitions)
    else:
        return PlainInstance(resolver)
