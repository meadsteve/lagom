from lagom import Container, ExplicitContainer


def test_container_is_okay():
    class Faketainer(Container):
        pass

    assert isinstance(Faketainer(), Container)


def test_explicit_container_is_okay():
    class Faketainer(ExplicitContainer):
        pass

    assert isinstance(Faketainer(), Container)
