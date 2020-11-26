# Lagom - Dependency injection container
[![](https://img.shields.io/pypi/pyversions/lagom.svg)](https://pypi.org/pypi/lagom/)
[![Build Status](https://travis-ci.org/meadsteve/lagom.svg?branch=master)](https://travis-ci.org/meadsteve/lagom)
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

You can tell the container that something should be a singleton:
```python
container[SomeExpensiveToCreateClass] = SomeExpensiveToCreateClass("up", "left")
```

You can explicitly tell the container how to construct something by giving it a function:

```python
container[SomeClass] = lambda: SomeClass("down", "spiral")
```

All of this is done without modifying any of your classes. This is one of the design goals of
lagom. 

A decorator is provided to hook top level functions into the container.

```python
@bind_to_container(container)
def handle_move_post_request(request: typing.Dict, game: Game = lagom.injectable):
    # do something to the game
    return Response()
```


[Full docs here here](https://lagom-di.readthedocs.io/en/stable/)

## Contributing

Contributions are very welcome. [Please see instructions here](docs/development_of_lagom.md)
