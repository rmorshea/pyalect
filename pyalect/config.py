import json
import os
from copy import deepcopy
from distutils.sysconfig import get_python_lib
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema

import pyalect

from .patterns import DIALECT_NAME, TRANSPILER_NAME

_HERE = Path(__file__).parent
_CONFIG: Optional[Dict[str, Any]] = None
_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "active": {"type": "boolean"},
        "dialects": {
            "type": "object",
            "patternProperties": {
                DIALECT_NAME.pattern: {
                    "type": "string",
                    "pattern": TRANSPILER_NAME.pattern,
                }
            },
            "additionalProperties": False,
        },
    },
    "required": ["version", "active", "dialects"],
}


def validate_config(config: Dict[str, Any]) -> None:
    jsonschema.validate(config, schema=_SCHEMA)


def activate() -> None:
    write({"active": True}, read())


def deactivate() -> None:
    write({"active": False}, read())


def path() -> Path:
    """Path to ``.pth`` file.

    Depending on platform the path will be located in one
    of several directories. See :mod:`site` for more info.
    """
    return Path(get_python_lib()) / "pyalect.pth"


def read() -> Dict[str, Any]:
    """Read config file from :func:`path`."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _read_file()
    new: Dict[str, Any] = deepcopy(_CONFIG)
    validate_config(new)
    return new


def write(*new: Dict[str, Any]) -> None:
    """Write config file to :func:`path`"""
    global _CONFIG
    cfg = _merge({}, *new)
    validate_config(cfg)
    _CONFIG = cfg  # only assign after validation
    _write_file(_CONFIG)


def delete() -> bool:
    """Delete config file from :func:`path`."""
    global _CONFIG
    if _CONFIG is not None:
        _CONFIG = None
    if path().exists():
        os.remove(path())
        return True
    else:
        return False


def _read_file() -> Dict[str, Any]:
    default = {"version": pyalect.__version__, "dialects": {}, "active": False}
    if not path().exists():
        return default
    else:
        with open(path()) as pth:
            for line in pth:
                if line.startswith("#"):
                    cfg: Dict[str, Any] = json.loads(line[1:])
                    return cfg
        return default


def _write_file(config: Dict[str, Any]) -> None:
    lines = []
    if config["active"]:
        # only import pyalect if active
        with open(_HERE / "pth.embed") as pth_src:
            lines.append("import os; exec(%r)" % pth_src.read())
    serialized = json.dumps(config)
    lines.append(f"# {serialized}")
    with open(path(), "w+") as pth:
        pth.write("\n".join(lines))
    return None


def _merge(target: Dict[str, Any], *sources: Dict[str, Any]) -> Dict[str, Any]:
    for src in reversed(sources):
        for key, v_src in src.items():
            if key not in target:
                target[key] = v_src
                continue
            v_tgt = target[key]
            if isinstance(v_tgt, dict) and isinstance(v_src, dict):
                _merge(v_tgt, v_src)
            else:
                target[key] = v_src
    return target
