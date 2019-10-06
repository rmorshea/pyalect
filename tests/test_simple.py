import pyalect


def test_activate_deactivate():
    pyalect.activate()
    assert pyalect.config.read()["active"]
    pyalect.deactivate()
    assert not pyalect.config.read()["active"]
