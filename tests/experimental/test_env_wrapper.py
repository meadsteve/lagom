from typing import Optional

from lagom import Container
from lagom.experimental.environment import Env


class MyEnv(Env):
    example_value: Optional[str]


def test_env_can_be_loaded(container: Container):
    assert isinstance(container.resolve(MyEnv), MyEnv)


def test_defined_env_variables_are_loaded_automatically(
    monkeypatch, container: Container
):
    monkeypatch.setenv("EXAMPLE_VALUE", "from the environment")
    env = container.resolve(MyEnv)
    assert env.example_value == "from the environment"
