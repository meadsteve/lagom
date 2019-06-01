# Lagom - Dependency injection container
[![Build Status](https://travis-ci.org/meadsteve/lagom.svg?branch=master)](https://travis-ci.org/meadsteve/lagom)
## Usage
Everything in Lagom is based on types. To create an object
you pass the type to the container:
```python
container = Container()
some_thing = container[SomeClass]
```

### Defining a singleton
```python
container[SomeExpensiveToCreateClass] = SomeExpensiveToCreateClass("up", "left")
```
alternatively if you want to defer construction until it's needed:
```python
container[SomeExpensiveToCreateClass] = Singleton(SomeExpensiveToCreateClass)
```


### Defining a type that gets recreated every time
```python
container[SomeClass] = lambda: SomeClass("down", "spiral")
```

### Alias a concrete instance to an ABC
```python
container[SomeAbc] = ConcreteClass
```
## Example
```python
from abc import ABC
from dataclasses import dataclass

from lagom import Container

#--------------------------------------------------------------
# Here is an example of some classes your application may be built from


@dataclass
class DiceApiUrl:
    url: str


class RateLimitingConfig:
    pass


class DiceClient(ABC):
    pass


class HttpDiceClient(DiceClient):

    def __init__(self, url: DiceApiUrl, limiting: RateLimitingConfig):
        pass


class Game:
    def __init__(self, dice_roller: DiceClient):
        pass

#--------------------------------------------------------------
# Next we setup some definitions

container = Container()
# We need a specific url
container[DiceApiUrl] = DiceApiUrl("https://roll.diceapi.com")
# Wherever our code wants a DiceClient we get the http one
container[DiceClient] = HttpDiceClient

#--------------------------------------------------------------
# Now the container can build the game object

game = container[Game]

```