import os
import json
from pathlib import Path
from copy import deepcopy
from distutils.sysconfig import get_python_lib
from typing import Dict, Optional, Any

import pyalect


_CONFIG: Optional[Dict[str, Any]] = None


def path():
    return Path(get_python_lib()) / "pyalect.pth"


def read() -> Dict[str, Any]:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _read_file()
    return deepcopy(_CONFIG)


def write(new: Dict[str, Any], old: Optional[Dict[str, Any]] = None) -> None:
    global _CONFIG
    if old is None:
        old = read()
    _CONFIG = _merge(old, new)
    _write_file(_CONFIG)


def delete() -> bool:
    if path().exists():
        os.path.remove(path())
        return True
    else:
        return False


def _read_file():
    if not path().exists():
        return {"version": pyalect.__version__, "dialects": {}, "active": False}
    else:
        with open(path()) as pth:
            for line in pth:
                if line.startswith("#"):
                    return json.loads(line[1:])
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
            merge(v_tgt, v_src)
        else:
            target[key] = v_src
    return target
