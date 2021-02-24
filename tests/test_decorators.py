from lagom import Container, bind_to_container, magic_bind_to_container

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
    assert "The doc string" in _do_something.__doc__
    assert "The magic doc string" in _do_something_magic.__doc__
