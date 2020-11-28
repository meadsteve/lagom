from typing import Any

import pytest

from lagom import Container
from lagom.experimental.integrations.django import DjangoIntegration


class FakeDjangoManager:
    pass


class FakeDjangoModel:
    data: Any
    objects = FakeDjangoManager()
    custom_manager = FakeDjangoManager()

    def __init__(self, **kwargs):
        self.data = kwargs


@pytest.fixture(scope="function")
def django_integration():
    return DjangoIntegration(Container(), models=[FakeDjangoModel])
