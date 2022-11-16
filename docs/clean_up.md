# Clean up

## ContextManagers and ContextContainers

Often you will have a dependency that has some cleanup code that needs to be called after it has been used.
Lagom provides the `ContextContainer` to help with this. It takes an existing lagom container and a list of resources
that should be managed within the context.

```python
from lagom import Container, ContextContainer, context_dependency_definition, injectable, bind_to_container
from typing import Iterator
from .my_lib import SomeDep

# First a regular lagom container is defined
container = Container()

# Then we create a ContextManager for some dependency SomeDep. 
# This would be available in Lagom as container[ContextManager[SomeDep]]
@context_dependency_definition(container)
def _load_dep_then_clean() -> Iterator[SomeDep]:
    try:
        yield SomeDep()
    finally:
        print("Clean up!!")

# Next we wrap the base container in a ContextContainer and configure SomeDep to be managed
context_container = ContextContainer(container, context_types=[SomeDep])

# Then our functions can be bound to this ContextContainer
# At the end of invoking this function the cleanup code of SomeDep will be automatically called.
@bind_to_container(context_container)
def do_something(dep: SomeDep = injectable):
    print(f"I got {dep}")
```

## Only cleaning up once per invocation - context singletons
In the code above a new instance of SomeDep will be constructed each time it is referenced and a cleanup call
will be scheduled for each constructed instance. If you only want one instance per invocation shared across
all dependencies then you need to define this as a `context_singleton`. A good example of this might be a 
transaction of some kind.

```python

# Let's say we have two classes that both need an active transaction. For an invocation we probably want these
# to be the same
class A:
    def __init__(self, t: Transaction):
        pass

    
class B:
    def __init__(self, t: Transaction):
        pass

@context_dependency_definition(container)
def _get_a_transaction() -> Iterator[SomeDep]:
    transaction = Transaction()
    try:
        yield 
    finally:
        transaction.commit()

# Next we wrap the base container in a ContextContainer and configure SomeDep to be managed
context_container = ContextContainer(container, context_types=[], context_singletons=[Transaction])

# Both a and b will get the same instance of a transaction because it was configured as a singleton
# the cleanup will only happen once (per invocation).
@bind_to_container(context_container)
def do_something(a: A = injectable, b: B = injectable):
    print(f"do something")
```