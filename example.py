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


class PlayerDb:
    def __init__(self, some_dsn):
        pass

    def load(self, name: str):
        # Maybe cache what we've loaded. But for how long?
        return "DATA"


class LocalCachingPlayerDb(PlayerDb):
    cache: typing.Dict

    def load(self, name: str):
        # cache what we've loaded FOR EVER
        self.cache[name] = "CACHE"
        return "DATA"


class HttpDiceClient(DiceClient):

    def __init__(self, url: DiceApiUrl, limiting: RateLimitingConfig):
        pass


class Game:
    def __init__(self, dice_roller: DiceClient):
        pass

    def make_move(self, a, b, move):
        pass


# Next we setup some definitions

container = Container()
# We need a specific url
container[DiceApiUrl] = DiceApiUrl("https://roll.diceapi.com")

# Our player DB should be reloaded each time as it caches locally
# we'll share it per request later
container[PlayerDb] = lambda: LocalCachingPlayerDb("blah blah blah")

# Wherever our code wants a DiceClient we get the http one
container[DiceClient] = HttpDiceClient


# If we wanted to build this into a web framework for example
# we can partially bind functions to the container we share the
# PlayerDB so the object can cache data locally but only for the
# lifetime of a single request
@bind_to_container(container, shared=[PlayerDb])
def handle_some_request(request: typing.Dict, game: Game, player_db: PlayerDb):
    player_one = player_db.load(request["player_one"])
    player_two = player_db.load(request["player_two"])
    game.make_move(player_one, player_two, request["move"])


# we can now call the following. the game argument will automagically
# come from the container
handle_some_request(request={"roll_dice": 5})
