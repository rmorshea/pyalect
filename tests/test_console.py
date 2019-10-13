import json

import pytest

from pyalect.console import main
from pyalect.dialect import transpiler

from .mock_package.mock_module import MockTranspiler


def test_activate_deactivate(config):
    main("activate")
    assert config()["active"] is True
    main("deactivate")
    assert config()["active"] is False


def test_register():
    name = "tests.mock_package.mock_module:MockTranspiler"
    main(f"register {name} as test")
    assert isinstance(transpiler("test"), MockTranspiler)


def test_deregister():
    name = "tests.mock_package.mock_module:MockTranspiler"
    main(f"register {name} as test")
    main(f"deregister {name} from test")
    with pytest.raises(ValueError):
        transpiler("test")


def test_show_config(config, capsys):
    main("activate")
    main("show config")
    captured = capsys.readouterr()
    output = json.loads(captured.out.split("--- CONFIGURATION ---")[1])
    assert output == config()
