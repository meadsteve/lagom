# Lagom - Dependency injection container
[![](https://img.shields.io/pypi/pyversions/lagom.svg)](https://pypi.org/pypi/lagom/)
[![Build Status](https://travis-ci.org/meadsteve/lagom.svg?branch=master)](https://travis-ci.org/meadsteve/lagom)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/meadsteve/lagom/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/meadsteve/lagom/?branch=master)
[![Code Coverage](https://scrutinizer-ci.com/g/meadsteve/lagom/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/meadsteve/lagom/?branch=master)
![PyPI](https://img.shields.io/pypi/v/lagom.svg?style=plastic)
[![Downloads](https://pepy.tech/badge/lagom/month)](https://pepy.tech/project/lagom/month)

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

## Developing/Contributing
Contributions and PRS are welcome. For any large changes please open
an issue to discuss first. All PRs should pass the tests, type checking
and styling. To get development setup locally:
```bash
make install # sets up the pipenv virtualenv
```
then 
```bash
make format # To format the code
make test # To make sure the build will pass
```

### Versioning - Semver
This library follows semver as closely as possible (mistakes may occur).
The public interface is considered to be everything in `lagom.__all__`. Anything
else is considered an internal implementation detail.

The `lagom.experimental` module is an exception to this. This is a place
for new code to be released. The public interface of this code may change
before it settles down and gets moved out of the experimental module.

### Design Goals
* The API should expose sensible typing (for use in pycharm/mypy)
* Everything should be done by type. No reliance on names.
* All domain code should remain unmodified. No special decorators.
* Usage of the container should encourage code to be testable without monkey patching.
* Usage of the container should remove the need to depend on global state.
* Embrace modern python features (3.7 at the time of creation)
