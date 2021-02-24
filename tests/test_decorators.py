import pytest

from lagom import Container, bind_to_container, magic_bind_to_container
from lagom.exceptions import ClassesCannotBeDecorated

container = Container()


@bind_to_container(container)
def _do_something():
    """
    The doc string
    :return:
    """
    pass


@magic_bind_to_container(container)
def _do_something_magic():
    """
    The magic doc string
    :return:
    """
    pass


def test_doc_strings_are_preserved():
    assert _do_something.__doc__
    assert _do_something_magic.__doc__
    assert "The doc string" in _do_something.__doc__
    assert "The magic doc string" in _do_something_magic.__doc__


def test_classes_can_not_be_decorated():
    with pytest.raises(ClassesCannotBeDecorated):

        @bind_to_container(container)
        class TestThisThing:
            pass


def test_classes_can_not_be_magic_decorated():
    with pytest.raises(ClassesCannotBeDecorated):

        @magic_bind_to_container(container)
        class TestThisOtherThing:
            pass
