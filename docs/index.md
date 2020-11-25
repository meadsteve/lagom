# Lagom - Dependency injection container

## What
Lagom is a dependency injection container designed to give you "just enough"
help with building your dependencies. The intention is that almost
all of your code doesn't know about or rely on lagom. Lagom will
only be involved at the top level to pull everything together.

### Features
 * Typed based auto wiring with zero configuration.
 * Fully based on types. Strong integration with mypy.
 * Minimal changes to existing code.
 * Integration with a few common web frameworks.
 * Support for async python.
 * Thread-safe at runtime
 
You can see a [comparison to other frameworks here](./comparison.md)

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

### Auto-wiring (with zero configuraton)
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

and later if you extend your class no changes are needed to lagom:

```python
class SomeClass:
   def __init__(datasource: MyDataSource, service: SomeFeatureProvider)
      pass

# Note the following code is unchaged
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
container[SomeClassToLoadOnce] = SomeClassToLoadOnce("up", "left")
```
alternatively if you want to defer construction until it's needed:

```python
container[SomeClassToLoadOnce] = Singleton(SomeClassToLoadOnce)
```

### Alias a concrete instance to an ABC
If your classes are written to depend on an ABC or an interface but at runtime
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

**Prerequisites** Using this feature requires [pydantic](https://github.com/samuelcolvin/pydantic/) to be installed

The first step is to create one or more classes that describe the environment variables your application depends on.
Lower case property names automatically map on to an uppercase environment variable of the same name.

```python
class MyWebEnv(Env):
    port: str # maps to environment variable PORT 
    host: str # maps to environment variable HOST

class DBEnv(Env):
    db_host: str# maps to environment variable DB_HOST
    db_password: str# maps to environment variable DB_PASSWORD
```
Now any function or class requiring configuration can type hint on these classes and get the values from the envionment injected in:
```python
# Example usage:
#    DB_HOST=localhost DB_PASSWORD=secret python myscript.py

c = Container()

@magic_bind_to_container(c)
def main(env: DBEnv):
    print(f"Config supplied: {env.db_host}, {env.db_password}")

if __name__ == "__main__":
   main()
```

For test purposes these classes can be created with explicitly set values:
```python
test_db_env = DBEnv(db_host="fake", db_password="skip")
```
