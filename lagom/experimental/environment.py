"""
This module provides code to automatically load environment variables from the container.
It is built on top of (and requires) pydantic.

At first one or more classes representing the required environment variables are defined.
All environment variables are assumed to be all uppercase and are automatically lowercased.

class MyWebEnv(Env):
    port: str
    host: str

class DBEnv(Env):
    db_host: str
    db_password: str


@bind_to_container(c)
def some_function(env: DBEnv):
    do_something(env.db_host, env.db_password)

"""
import os
from abc import ABC

from pydantic.main import BaseModel


class Env(ABC, BaseModel):
    """
    This class implements logic to automatically load properties from ENV
    variables.
    """

    def __init__(self, **kwargs):
        if len(kwargs) == 0:
            super().__init__(
                **{key.lower(): value for (key, value) in os.environ.items()}
            )
        else:
            super().__init__(**kwargs)
