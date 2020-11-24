# Lagom - Dependency injection container

## What
Lagom is a dependency injection container designed to give you "just enough"
help with building your dependencies. The intention is that almost
all of your code doesn't know about or rely on lagom. Lagom will
only be involved at the top level to pull everything together.

## Installation
```bash
pip install lagom
# or: 
# pipenv install lagom
# poetry add lagom
```
## Usage
Everything in Lagom is based on types. To create an object
you pass the type to the container:
```python
container = Container()
some_thing = container[SomeClass]
```

Most of the time Lagom doesn't need to be told how to build your classes. If 
the `__init__` method has type hints then lagom will use these to inject
the correct dependencies. The following will work without any special configuration:

```python
class MyDataSource:
    pass
    
class SomeClass:
   def __init__(datasource: MyDataSource)
      pass

container = Container()
some_thing = container[SomeClass] # An instance of SomeClass will be built with an instance of MyDataSource provided
```


### Defining how to build a type if can't be inferred automatically
If lagom can't infer (or you don't want it to) how to build a type you can instruct
the container how to do this.

```python
container[SomeClass] = lambda: SomeClass("down", "spiral")
```

if the type needs things from the container the lambda can take a
single argument which is the container:
```python
container[SomeClass] = lambda c: SomeClass(c[SomeOtherDep], "spinning")
```

if your construction logic is longer than would fit in a lambda a
function can also be bound to the container:
```python
@dependency_definition(container)
def my_constructor() -> MyComplexDep:
    # Really long
    # stuff goes here
    return MyComplexDep(some_number=5)
```

### Defining a singleton
You may have dependencies that you don't want to be built every time. Any
dependency can be configured as a singleton without changing the class at 
all.

```python
container[SomeClasssToLoadOnce] = SomeClasssToLoadOnce("up", "left")
```
alternatively if you want to defer construction until it's needed:

```python
container[SomeClasssToLoadOnce] = Singleton(SomeClasssToLoadOnce)
```

### Alias a concrete instance to an ABC
If your classes are written to depened on an ABC or an interface but at runtime
you want to configure a specific concrete class lagom supports definitions of aliases:

```python
container[SomeAbc] = ConcreteClass
```

### Partially bind a function
Apply a function decorator to any function.
```python
@magic_bind_to_container(container)
def handle_some_request(request: typing.Dict, game: Game):
    # do something to the game
    pass
```

This function can now be called omitting any arguments 
that the container knows how to build.
```python
# we can now call the following. the game argument will automagically
# come from the container
handle_some_request(request={"roll_dice": 5})
```


### Invocation level caching
Suppose you have a function and you want all the dependencies
to share an instance of an object then you can define invocation
level shared dependencies.

```python

class ProfileLoader:
    def __init__(self, loader: DataLoader):
        pass

class AvatarLoader:
    def __init__(self, loader: DataLoader):
        pass

@magic_bind_to_container(container, shared=[DataLoader])
def handle_some_request(request: typing.Dict, profile: ProfileLoader, user_avatar: AvatarLoader):
    # do something to the game
    pass
```

now each invocation of handle_some_request will get the same instance
of loader so this class can cache values for the invocation lifetime.


### Bind only explicit arguments to the container
Instead of the magic binding described earlier an explicit decorator is 
provided:
```python
@bind_to_container(container)
def handle_some_request(request: typing.Dict, profile: ProfileLoader = injectable, user_avatar: AvatarLoader = injectable):
    # do something to the game
    pass
```
In this example lagom will only try and inject the `profile` and `user_avatar` arguments.

### Alternative to decorator
The above example can also be used without a decorator if you want
to keep the pure unaltered function available for testing.

```python
def handle_some_request(request: typing.Dict, game: Game):
    pass

# This new function can be bound to a route or used wherever
# need
func_with_injection = container.magic_partial(handle_some_request)
```


### Defining an async loaded type
Lagom supports async python. If an async def is used to define a dependency then it
will be available as `Awaitable[TheDependency]`

```python
@dependency_definition(container)
async def my_constructor() -> MyComplexDep:
    # await some stuff or any other async things
    return MyComplexDep(some_number=5)

my_thing = await container[Awaitable[MyComplexDep]]

```

### Loading environment variables (requires pydantic to be installed)

This module provides code to automatically load environment variables from the container.
It is built on top of (and requires) pydantic.

At first one or more classes representing the required environment variables are defined.
All environment variables are assumed to be all uppercase and are automatically lowercased.
```python
class MyWebEnv(Env):
    port: str
    host: str

class DBEnv(Env):
    db_host: str
    db_password: str
```

Now that these env classes are defined they can be injected
as usual:
```python
@magic_bind_to_container(c)
def some_function(env: DBEnv):
    do_something(env.db_host, env.db_password)
```

For testing a manual constructed Env class can be passed in.
At runtime the class will be populated automatically from
the environment.
