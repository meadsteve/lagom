import pytest

from lagom import Container
from lagom.experimental.integrations.django import DjangoModel, DjangoIntegration
from tests.experimental.integrations.conftest import FakeDjangoModel, FakeDjangoManager


def test_django_models_can_be_created(django_integration: DjangoIntegration):
    models = django_integration._container.resolve(DjangoModel[FakeDjangoModel])
    new_model_instance = models.new(first=1, second=2)
    assert isinstance(new_model_instance, FakeDjangoModel)
    assert new_model_instance.data == {"first": 1, "second": 2}


def test_django_models_can_be_managed(django_integration: DjangoIntegration):
    models = django_integration._container.resolve(DjangoModel[FakeDjangoModel])
    assert isinstance(models.objects, FakeDjangoManager)


def test_django_models_can_be_managed_via_a_custom_manager(
    django_integration: DjangoIntegration,
):
    models = django_integration._container.resolve(DjangoModel[FakeDjangoModel])
    assert isinstance(models.managers.custom_manager, FakeDjangoManager)


def test_trying_to_load_a_non_existent_manager_throws_a_sensible_error(
    django_integration: DjangoIntegration,
):
    models = django_integration._container.resolve(DjangoModel[FakeDjangoModel])
    with pytest.raises(KeyError):
        models.managers.lol.all()
