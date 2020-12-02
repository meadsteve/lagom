# Lagom - Dependency injection container
[![](https://img.shields.io/pypi/pyversions/lagom.svg)](https://pypi.org/pypi/lagom/)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/meadsteve/lagom/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/meadsteve/lagom/?branch=master)
[![Code Coverage](https://scrutinizer-ci.com/g/meadsteve/lagom/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/meadsteve/lagom/?branch=master)
![PyPI](https://img.shields.io/pypi/v/lagom.svg?style=plastic)
[![Downloads](https://pepy.tech/badge/lagom/month)](https://pepy.tech/project/lagom/)

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
 
You can see a [comparison to other frameworks here](./docs/comparison.md)

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

### Singletons
You can tell the container that something should be a singleton:
```python
container[SomeExpensiveToCreateClass] = SomeExpensiveToCreateClass("up", "left")
```

### Explicit build instructions when required
You can explicitly tell the container how to construct something by giving it a function:

```python
container[SomeClass] = lambda: SomeClass("down", "spiral")
```

All of this is done without modifying any of your classes. This is one of the design goals of
lagom. 

### Hooks in to existing systems
A decorator is provided to hook top level functions into the container.

```python
@bind_to_container(container)
def handle_move_post_request(request: typing.Dict, game: Game = lagom.injectable):
    # do something to the game
    return Response()
```

(There's also a few common framework integrations [provided here](https://lagom-di.readthedocs.io/en/latest/framework_integrations/))

[Full docs here here](https://lagom-di.readthedocs.io/en/latest/)

## Contributing

Contributions are very welcome. [Please see instructions here](docs/development_of_lagom.md)
