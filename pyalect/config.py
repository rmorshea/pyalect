import os
import json
from pathlib import Path
from copy import deepcopy
from distutils.sysconfig import get_python_lib
from typing import Dict, Optional, Any

import pyalect


_CONFIG: Optional[Dict[str, Any]] = None


def activate() -> None:
    write({"active": True})


def deactivate() -> None:
    write({"active": False})


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
    return new


def write(new: Dict[str, Any], old: Optional[Dict[str, Any]] = None) -> None:
    """Write config file to :func:`path`"""
    global _CONFIG
    if old is None:
        old = read()
    _CONFIG = _merge(old, new)
    _write_file(_CONFIG)


def delete() -> bool:
    """Delete config file from :func:`path`."""
    if path().exists():
        os.remove(path())
        return True
    else:
        return False


def _read_file() -> Dict[str, Any]:
    if not path().exists():
        return {"version": pyalect.__version__, "dialects": {}, "active": False}
    else:
        with open(path()) as pth:
            for line in pth:
                if line.startswith("#"):
                    cfg: Dict[str, Any] = json.loads(line[1:])
                    return cfg
        return {}


def _write_file(config: Dict[str, Any]) -> None:
    lines = []
    if config["active"]:
        # only import pyalect if active
        lines.append("import pyalect")
    serialized = json.dumps(config)
    lines.append(f"# {serialized}")
    with open(path(), "w+") as pth:
        pth.write("\n".join(lines))
    return None


def _merge(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    for key, v_src in source.items():
        if key not in target:
            target[key] = v_src
            continue
        v_tgt = target[key]
        if isinstance(v_tgt, dict) and isinstance(v_src, dict):
            _merge(v_tgt, v_src)
        else:
            target[key] = v_src
    return target
