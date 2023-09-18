import random
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from lagom import (
    Container,
    ContextContainer,
    ExplicitContainer,
    context_dependency_definition,
    dependency_definition,
)


class Object:
    def __init__(self) -> None:
        self.id = random.randint(0, 9999)


class MySingleton(Object):
    pass


class MyContextSingleton(Object):
    def __init__(self, foo: str) -> None:
        super().__init__()
        self.foo = foo

    def close(self) -> None:
        print(f"closing {self.id}")


class MyDependency(Object):
    def __init__(self, ctx: MyContextSingleton) -> None:
        super().__init__()
        self.ctx = ctx


class MyService(Object):
    def __init__(self, dep: MyDependency) -> None:
        super().__init__()
        self.dep = dep


container = ExplicitContainer(log_undefined_deps=True)


@dependency_definition(container, singleton=True)
def _get_my_singleton() -> MySingleton:
    return MySingleton()


@dependency_definition(container)
def _get_my_service(c: Container) -> MyService:
    return MyService(c[MyDependency])


@dependency_definition(container)
def _get_my_dependency(c: Container) -> MyDependency:
    return MyDependency(c[MyContextSingleton])


@context_dependency_definition(container)
def _get_my_context_singleton() -> Iterable[MyContextSingleton]:
    cli = MyContextSingleton("bar")
    try:
        yield cli
    finally:
        cli.close()


context_container = ContextContainer(
    container, context_types=[], context_singletons=[MyContextSingleton]
)


def _example_function(num: int) -> None:
    with context_container as c:
        service1 = c[MyService]
        service2 = c[MyService]
        print(
            f"Thread {num} - MySingleton {c[MySingleton].id} - MyService {service1.id} - MyDependency {service1.dep.id} - MyContextSingleton {service1.dep.ctx.id}"
        )
        print(
            f"Thread {num} - MySingleton {c[MySingleton].id} - MyService {service2.id} - MyDependency {service2.dep.id} - MyContextSingleton {service1.dep.ctx.id}"
        )


def test_context_containers_are_thread_safe_bug_242():
    with ThreadPoolExecutor() as pool:
        f1 = pool.submit(_example_function, 1)
        f2 = pool.submit(_example_function, 2)
        f1.result()
        f2.result()
    assert True
