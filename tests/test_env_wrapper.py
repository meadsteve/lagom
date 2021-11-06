from typing import Optional, ClassVar

import pytest

from lagom import Container
from lagom.environment import Env
from lagom.exceptions import MissingEnvVariable, InvalidEnvironmentVariables


class MyEnv(Env):
    example_value: Optional[str]


class MyEnvWithPrefix(Env):
    PREFIX: ClassVar[str] = "APPNAME"
    example_value: str


class MyEnvNeedsANumberAndAString(Env):
    a_string: str
    a_number: int


def test_env_can_be_loaded(container: Container):
    assert isinstance(container.resolve(MyEnv), MyEnv)


def test_defined_env_variables_are_loaded_automatically(
    monkeypatch, container: Container
):
    monkeypatch.setenv("EXAMPLE_VALUE", "from the environment")
    env = container.resolve(MyEnv)
    assert env.example_value == "from the environment"


def test_envs_can_have_a_prefix(monkeypatch, container: Container):
    monkeypatch.setenv("APPNAME_EXAMPLE_VALUE", "from the environment with a prefix")
    env = container.resolve(MyEnvWithPrefix)
    assert env.example_value == "from the environment with a prefix"


def test_errors_are_nice_if_the_env_variable_isnt_set(container: Container):
    with pytest.raises(MissingEnvVariable) as error:
        container.resolve(MyEnvWithPrefix)
    assert (
        str(error.value)
        == "Expected environment variables not found: APPNAME_EXAMPLE_VALUE"
    )


def test_all_missing_variable_names_are_listed(container: Container):
    with pytest.raises(MissingEnvVariable) as error:
        container.resolve(MyEnvNeedsANumberAndAString)
    error_message = str(error.value)
    assert "A_STRING" in error_message
    assert "A_NUMBER" in error_message


def test_wrong_types_are_handled(monkeypatch, container: Container):
    monkeypatch.setenv("A_STRING", "correctly-a-string")
    monkeypatch.setenv("A_NUMBER", "false")
    with pytest.raises(InvalidEnvironmentVariables) as error:
        container.resolve(MyEnvNeedsANumberAndAString)
    assert "Unable to load environment variables: A_NUMBER" in str(error.value)
