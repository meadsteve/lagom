import logging

from lagom import Container


class AThing:
    pass


def test_it_writes_a_warning_every_time_reflection_is_used(caplog):
    c = Container(log_undefined_deps=True)
    with caplog.at_level(logging.INFO):
        _something = c[AThing]

    assert len(caplog.records) == 1
    assert (
        caplog.records[0].message
        == "Undefined dependency. Using reflection for <class 'tests.test_undefinied_dep_logging.AThing'>"
    )
    assert caplog.records[0].undefined_dependency == AThing


def test_by_default_it_doesnt_log(caplog):
    c = Container()
    with caplog.at_level(logging.INFO):
        _something = c[AThing]
    assert len(caplog.records) == 0
