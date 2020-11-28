import pytest

from lagom import injectable
from lagom.exceptions import InjectableMarkerConsumed


def test_injectable_is_falsy():
    assert not injectable


def test_calling_a_method_on_it_raises_an_error():
    with pytest.raises(InjectableMarkerConsumed):
        injectable.commit()


def test_trying_to_get_a_property_on_it_returns_an_error():
    with pytest.raises(InjectableMarkerConsumed):
        injectable.active
