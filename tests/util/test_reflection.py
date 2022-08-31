from typing import Awaitable

from lagom.util.reflection import remove_awaitable_type


def test_awaitables_can_have_their_inner_type_revealed():
    assert remove_awaitable_type(Awaitable[int]) == int


def test_non_awaitables_dont_error_if_asked_about_awaitability():
    assert remove_awaitable_type(int) is None
