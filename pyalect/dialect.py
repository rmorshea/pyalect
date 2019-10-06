import io
import ast
import re
import inspect
import tokenize
from importlib import import_module
from typing import Any, Optional, Union
from typing_extensions import Protocol, runtime_checkable

from . import config
from .errors import UsageError


_TEMP_DIALECTS = {}

DIALECT_NAME = re.compile(r"^[\w\.]+$")
DIALECT_COMMENT = re.compile(r"^# ?dialect ?= ?(.+)\n?$")
TRANSPILER_NAME = re.compile(r"^[\w\.]+(\:[\w\.]+)?$")


def find(source: Union[bytes, str]) -> Optional[str]:
    """Find dialect comment before the first non-continuation newline."""
    if isinstance(source, str):
        buffer = io.BytesIO(source.encode())
    else:
        buffer = io.BytesIO(source)
    for token in tokenize.tokenize(buffer.readline):
        if token.type == tokenize.NEWLINE:
            break
        if token.type == tokenize.COMMENT:
            match = DIALECT_COMMENT.match(token.string)
            if match is not None:
                name = match.groups()[0]
                if DIALECT_NAME.match(name):
                    return name
    return None


def is_transpiler(value: Any) -> bool:
    if inspect.isclass(value):
        return issubclass(value, Transpiler)
    else:
        return isinstance(value, Transpiler)


@runtime_checkable
class Transpiler(Protocol):
    def transform_src(self, source: str) -> str:
        return source

    def transform_ast(self, node: ast.AST) -> ast.AST:
        return node


def import_transpiler(name: str) -> Transpiler:
    module_name, _, from_name = name.partition(":")
    module = import_module(module_name)
    if from_name:
        try:
            transpiler = getattr(module, from_name)
        except AttributeError:
            raise ImportError(f"Cannot import {from_name!r} from {module_name!r}")
    else:
        transpiler = module
    if isinstance(transpiler, Transpiler):
        return transpiler
    elif inspect.isclass(transpiler) and issubclass(transpiler, Transpiler):
        return transpiler()  # type: ignore
    else:
        raise ImportError(f"{transpiler!r} is not a valid transpiler")


def transpiler(dialect: str) -> Transpiler:
    cfg_dialects = config.read()["dialects"]
    if dialect not in cfg_dialects:
        raise ImportError(f"Unknown dialect {dialect!r}")
    else:
        transpiler_name = cfg_dialects[dialect]
        return import_transpiler(transpiler_name)


def register(dialect: str, transpiler: Union[Transpiler, str], force: bool) -> None:
    if not DIALECT_NAME.match(dialect):
        raise UsageError(f"invalid dialect name {dialect!r}")
    cfg = config.read()
    cfg_dialects = cfg["dialects"]
    if dialect in cfg_dialects and not force:
        existing = cfg_dialects[dialect]
        raise UsageError(f"already registered {existing!r} as {dialect!r}")
    elif isinstance(transpiler, str):
        try:
            import_transpiler(transpiler)
        except ImportError as error:
            raise UsageError(error)
        if not TRANSPILER_NAME.match(transpiler):
            raise UsageError(f"invalid transpiler name {transpiler!r}")
        cfg_dialects[dialect] = transpiler
        config.write(cfg)
    elif is_transpiler(transpiler):
        _TEMP_DIALECTS[dialect] = transpiler
    else:
        raise TypeError(f"Invalid transpiler {transpiler!r} for dialect {dialect!r}")


def deregister(
    dialect: Optional[str], transpiler: Union[Transpiler, str, None]
) -> None:
    if dialect is not None and not DIALECT_NAME.match(dialect):
        raise UsageError(f"invalid dialect name {dialect!r}")

    if is_transpiler(transpiler):
        _deregister_temp(dialect, transpiler)  # type: ignore
        return None

    if transpiler is not None and not TRANSPILER_NAME.match(transpiler):  # type: ignore
        raise UsageError(f"invalid transpiler name {transpiler!r}")
    if not (transpiler or dialect):
        raise UsageError("No transpiler or dialect to deregister")

    cfg = config.read()
    cfg_dialects = cfg["dialects"]
    if dialect is not None and transpiler != "*":
        if dialect not in cfg_dialects:
            raise UsageError(f"No dialect {dialect!r} to deregister")
        elif transpiler != cfg_dialects[dialect]:
            msg = f"{transpiler!r} is not the transpiler for dialect {dialect!r}"
            raise UsageError(msg)
        else:
            del cfg_dialects[dialect]
    elif dialect is not None:
        cfg_dialects.pop(dialect, None)
    else:
        for d, t in list(cfg_dialects.items()):
            if t == transpiler:
                del cfg_dialects[dialect]

    config.write(cfg)


def _deregister_temp(dialect: str, transpiler: Transpiler) -> None:
    if dialect is None:
        for d, t in _TEMP_DIALECTS.items():
            if t == transpiler:
                del _TEMP_DIALECTS[d]
    elif dialect not in _TEMP_DIALECTS:
        raise UsageError(f"No dialect {dialect!r} to deregister")
    elif _TEMP_DIALECTS[dialect] != transpiler:
        msg = f"{transpiler!r} is not the transpiler for dialect {dialect!r}"
        raise UsageError(msg)
    else:
        del _TEMP_DIALECTS[dialect]
