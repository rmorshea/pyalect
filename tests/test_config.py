from distutils.sysconfig import get_python_lib
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

import pyalect


def test_activate_deactivate():
    pyalect.activate()
    assert pyalect.config.read()["active"]
    pyalect.deactivate()
    assert not pyalect.config.read()["active"]


def test_path():
    expected = Path(get_python_lib()) / "pyalect.pth"
    assert expected == pyalect.config.path()


@pytest.mark.parametrize(
    "value",
    [
        {"version": "1.0.0", "active": True, "dialects": {}},
        {"version": "1.0.0", "active": False, "dialects": {}},
        {
            "version": "1.0.0",
            "active": True,
            "dialects": {"my_dialect": "path.to:Transpiler"},
        },
        {
            "version": "1.0.0",
            "active": True,
            "dialects": {
                "my_dialect_1": "path.to:Transpiler1",
                "my_dialect_2": "path.to:Transpiler2",
            },
        },
    ],
)
def test_valid_schema():
    assert pyalect.config.read() == {}


def test_activate_deactivate(config):
    pyalect.activate()
    assert config()["active"]
    pyalect.deactivate()
    assert not config()["active"]


def test_path():
    expected = Path(get_python_lib()) / "pyalect.pth"
    assert expected == pyalect.config.path()


@pytest.mark.parametrize(
    "value",
    [
        {"version": "1.0.0", "active": True, "dialects": {}},
        {"version": "1.0.0", "active": False, "dialects": {}},
        {
            "version": "1.0.0",
            "active": True,
            "dialects": {"my_dialect": "path.to:Transpiler"},
        },
        {
            "version": "1.0.0",
            "active": True,
            "dialects": {
                "my_dialect_1": "path.to:Transpiler1",
                "my_dialect_2": "path.to:Transpiler2",
            },
        },
    ],
)
def test_valid_schema(value):
    pyalect.config.validate_config(value)


@pytest.mark.parametrize(
    "value",
    [
        {
            # missing required fields
        },
        {
            "version": "1.0.0",
            # missing required fields
        },
        {
            "version": "1.0.0",
            "active": True,
            # missing required fields
        },
        {"version": None, "active": True, "dialects": {}},  # bad value
        {"version": "1.0.0", "active": None, "dialects": {}},  # bad value
        {"version": "1.0.0", "active": True, "dialects": None},  # bad value
        {"version": "1.0.0", "active": True, "dialects": {"!@#": "bad.dialect:Name"}},
        {
            "version": "1.0.0",
            "active": True,
            "dialects": {"bad_transpiler_name": "#$*"},
        },
        {
            "version": "1.0.0",
            "active": True,
            "dialects": {"bad_transpiler_name": "missing.colon"},
        },
    ],
)
def test_valid_schema(value):
    with pytest.raises(ValidationError):
        pyalect.config.validate_config(value)
