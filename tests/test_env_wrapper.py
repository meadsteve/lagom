from typing import Optional, ClassVar

from lagom import Container
from lagom.environment import Env


class MyEnv(Env):
    example_value: Optional[str]


class MyEnvWithPrefix(Env):
    PREFIX: ClassVar = "APPNAME"
    example_value: str


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
