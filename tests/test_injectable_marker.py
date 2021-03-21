from copy import deepcopy

import pytest

from lagom import injectable
from lagom.exceptions import InjectableNotResolved


def test_injectable_is_falsy():
    assert not injectable


def test_trying_to_reference_a_property_on_injectable_raises_an_error():
    with pytest.raises(InjectableNotResolved):
        injectable.some_value  # type: ignore


def test_trying_to_call_things_on_injectable_raises_an_error():
    with pytest.raises(InjectableNotResolved):
        injectable.do_thing()  # type: ignore


def test_cloning_injectable_is_the_same_injectable():
    assert injectable is deepcopy(injectable)
