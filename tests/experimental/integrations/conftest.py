from typing import Any

import pytest

from lagom.experimental.integrations.django import DjangoContainer


class FakeDjangoManager:
    pass


class FakeDjangoModel:
    data: Any
    objects = FakeDjangoManager()
    custom_manager = FakeDjangoManager()

    def __init__(self, **kwargs):
        self.data = kwargs


@pytest.fixture(scope="function")
def django_container():
    return DjangoContainer(models=[FakeDjangoModel])  # type: ignore
