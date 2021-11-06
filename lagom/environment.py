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
from typing import ClassVar, Optional

from .exceptions import MissingEnvVariable, InvalidEnvironmentVariables

try:
    from pydantic.main import BaseModel, ValidationError
except ImportError as error:
    raise ImportError(
        "Using Env requires pydantic to be installed. Try `pip install lagom[env]`"
    ) from error


class Env(ABC, BaseModel):
    """
    This class implements logic to automatically load properties from ENV
    variables.
    """

    PREFIX: ClassVar[Optional[str]] = None

    def __init__(self, **kwargs):
        """
        For normal usage no arguments should be supplied to the constructor.
        When this happens all required variables will be loaded from the Environment.
        For testing you may want to create an instance with variables explicitly set
        in the constructor.

        :param kwargs:
        """
        try:
            if len(kwargs) == 0:
                prefix = self._prefix()
                envs = os.environ.items()
                super().__init__(
                    **{
                        key.replace(prefix, "").lower(): value
                        for (key, value) in envs
                        if key.startswith(prefix)
                    }
                )
            else:
                super().__init__(**kwargs)
        except ValidationError as validation_error:
            missing_field_errors = [
                e
                for e in validation_error.errors()
                if e["type"] == "value_error.missing"
            ]
            if missing_field_errors:
                env_names = self._env_names_from_pydantic_errors(missing_field_errors)
                raise MissingEnvVariable(env_names) from validation_error
            other_field_errors = [
                e
                for e in validation_error.errors()
                if e["type"] != "value_error.missing"
            ]
            env_names = self._env_names_from_pydantic_errors(other_field_errors)
            raise InvalidEnvironmentVariables(
                env_names, str(validation_error)
            ) from validation_error

    def _env_names_from_pydantic_errors(self, missing_field_errors):
        return [
            f"{self._prefix()}{pyd_error['loc'][0]}".upper()
            for pyd_error in missing_field_errors
        ]

    def _prefix(self):
        prefix = f"{self.PREFIX}_" if self.PREFIX else ""
        return prefix
