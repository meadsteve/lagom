from abc import ABC
from dataclasses import dataclass

import typing

from lagom import Container, bind_to_container


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


# Next we setup some definitions

container = Container()
# We need a specific url
container[DiceApiUrl] = DiceApiUrl("https://roll.diceapi.com")
# Wherever our code wants a DiceClient we get the http one
container[DiceClient] = HttpDiceClient

# Now the container can build the game object

game = container[Game]

# If we wanted to build this into a web framework for example
# we can partially bind functions to the container


@bind_to_container(container)
def handle_some_request(request: typing.Dict, game: Game):
    # do something to the game
    pass


# we can now call the following. the game argument will automagically
# come from the container
handle_some_request(request={"roll_dice": 5})
