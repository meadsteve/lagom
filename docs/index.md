# Lagom - Dependency injection container

## What
Lagom is a dependency injection container designed to give you "just enough"
help with building your dependencies. The intention is that almost
all of your code doesn't know about or rely on lagom. Lagom will
only be involved at the top level to pull everything together.

### Features
 * Fully based on types. Strong integration with mypy.
 * Minimal changes to existing code.
 * Integration with a few common web frameworks.
 * Support for async python.
 * Thread-safe at runtime

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
In a lot of web frameworks you'll have a function responsible for handling requests.
This is a point where lagom can be integrated. A decorator is provided that wraps
a function and uses reflection to inject any arguments from the supplied container.

In this example the database will be built automatically by lagom:

```python
@magic_bind_to_container(container)
def handle_some_request(request, database: DB):
    # Do something in the database with this request
    pass
```

### Bind only explicit arguments to the container
The `magic_bind_to_container` above will try and construct any argument that isn't provided. If you
want to be explicit and restrict what lagom injects then an `injectable` marker is provided. Setting
a default value of `injectable` tells lagom to inject this value if it's not provided by the caller.

```python
from lagom import injectable

@bind_to_container(container)
def handle_some_request(request: typing.Dict, profile: ProfileLoader = injectable, user_avatar: AvatarLoader = injectable):
    # do something to the game
    pass
```
In this example lagom will only try and inject the `profile` and `user_avatar` arguments.


### Invocation level caching
If for the life time of a function (maybe a web request) you want a certain class to act as a temporary singleton then
lagom has the concept of `shared` dependencies. When binding a function to a container a list of classes is provided. 
Each of these classes will only be constructed once per function invocation.

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

### Defining an async loaded type
Lagom fully supports async python. If an async def is used to define a dependency then it
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
