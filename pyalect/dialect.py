import ast
import io
import tokenize
from importlib import import_module
from typing import Dict, Optional, Set, Type, Union

from typing_extensions import Protocol, runtime_checkable

from . import config
from .errors import UsageError
from .patterns import DIALECT_COMMENT, DIALECT_NAME, TRANSPILER_NAME

_IN_MEMORY_DIALECTS: Dict[str, Type["Transpiler"]] = {}


def registered() -> Set[str]:
    return set(config.read()["dialects"]).union(_IN_MEMORY_DIALECTS)


def find_dialect(source: Union[bytes, str, io.FileIO]) -> Optional[str]:
    """Extract dialect from comment headers in module source code.

    The comment should be of the form ``# dialect=my_dialect`` and must be before
    the first non-continuation newline.

    Examples:
        .. code-block::

            # dialect=my_dialect

        .. code-block::

            # coding=utf-8
            # dialect=my_dialect
            '''docstring'''
    """
    buffer: Union[io.FileIO, io.BytesIO]
    if isinstance(source, io.FileIO):
        buffer = source
    elif isinstance(source, str):
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


@runtime_checkable
class Transpiler(Protocol):
    """A base class for defining a dialect transpiler.

    .. note::

        A transpiler instance is only used once per module and shouldn't be reused.

    The logic of transpiling can be roughly paraphrased as:

    .. code-block::

        import ast

        transpiler = MyTranspiler()
        source = read_file_source()
        new_source = transpiler.transform_src(source)
        tree = ast.parse(new_source)
        new_tree = transpiler.transform_ast(tree)

        exec(compile(new_tree, "my_module.py", "exec"))

    Parameters:
        dialect: the name of the dialect being transpiled.
    """

    def __init__(self, dialect: str) -> None:
        ...

    def transform_src(self, source: str) -> str:
        """Implement this method to transform a raw Python source string."""
        return source

    def transform_ast(self, node: ast.AST) -> ast.AST:
        """Implement this method to transform an :class:`~ast.AST`."""
        return node


def import_transpiler_class(name: str) -> Type[Transpiler]:
    if not TRANSPILER_NAME.match(name):
        raise ValueError(f"Invalid transpiler name {name!r}")
    module_name, attr_name = name.split(":", 1)

    module = import_module(module_name)
    try:
        transpiler_cls: Type[Transpiler] = getattr(module, attr_name)
    except AttributeError:
        raise ImportError(f"Cannot import {attr_name!r} from {module_name!r}")

    if isinstance(transpiler_cls, type) and issubclass(transpiler_cls, Transpiler):
        return transpiler_cls
    else:
        raise TypeError(f"{transpiler!r} is not a valid transpiler")


def transpiler(dialect: str) -> Transpiler:
    """Retrieve the transpiler for the given dialect."""
    cfg_dialects = config.read()["dialects"]
    if dialect in _IN_MEMORY_DIALECTS:
        return _IN_MEMORY_DIALECTS[dialect](dialect)
    elif dialect in cfg_dialects:
        cls = import_transpiler_class(cfg_dialects[dialect])
        return cls(dialect)
    else:
        raise ValueError(f"Unknown dialect {dialect!r}")


def register(
    dialect: str, transpiler: Union[Type[Transpiler], str], force: bool = True
) -> None:
    """Register a transpiler for the given dialect.

    This transpiler can be retrieved later via :func:`transpiler`.

    Parameters:
        dialect:
            The name of a dialect
        transpiler:
            If given as a string, it should be of the form
            ``dotted.path.to.TranspilerClass``. Otherwise it
            should be a ``Transpiler`` subclass.
    """
    if not DIALECT_NAME.match(dialect):
        raise UsageError(f"invalid dialect name {dialect!r}")

    cfg = config.read()
    cfg_dialects = cfg["dialects"]
    if (dialect in cfg_dialects or dialect in _IN_MEMORY_DIALECTS) and not force:
        raise UsageError(f"already registered {cfg_dialects[dialect]!r} as {dialect!r}")

    if isinstance(transpiler, str):
        if not TRANSPILER_NAME.match(transpiler):
            raise UsageError(f"invalid transpiler name {transpiler!r}")
        cfg_dialects[dialect] = transpiler
        config.write(cfg)
    elif isinstance(transpiler, type) and issubclass(transpiler, Transpiler):
        _IN_MEMORY_DIALECTS[dialect] = transpiler
    else:
        raise ValueError(f"Expected a string or Transpiler, not {transpiler!r}")


def deregister(
    dialect: str = "*", transpiler: Union[Type[Transpiler], str] = "*"
) -> None:
    """Deregister a transpiler from a given dialect.

    Parameters:
        dialect:
            The name of a dialect or ``"*"`` to delete a given ``transpiler``
            from all dialects.
        transpiler:
            If ``"*"`` then any transpiler for the given ``dialect`` will
            be removed. If given as a string, it should be of the form
            ``dotted.path.to.TranspilerClass``. Otherwise it should be a
            ``Transpiler`` subclass.
    """
    if dialect != "*" and not DIALECT_NAME.match(dialect):
        raise UsageError(f"invalid dialect name {dialect!r}")

    if isinstance(transpiler, str):
        if transpiler != "*" and not TRANSPILER_NAME.match(transpiler):
            raise UsageError(f"invalid transpiler name {transpiler!r}")
    elif isinstance(transpiler, type):
        if not issubclass(transpiler, Transpiler):
            raise ValueError(f"{transpiler} is not a Transpiler")
    else:
        raise ValueError(f"Expected a string or Transpiler, not {transpiler!r}")

    cfg = config.read()
    cfg_dialects = cfg["dialects"]

    if dialect == "*" and transpiler == "*":
        cfg_dialects.clear()
        _IN_MEMORY_DIALECTS.clear()
    elif dialect == "*":
        for d, t in list(cfg_dialects.items()):
            if t == transpiler:
                del cfg_dialects[d]
        for d, t in list(_IN_MEMORY_DIALECTS.items()):
            if t == transpiler:
                del _IN_MEMORY_DIALECTS[d]
    elif transpiler == "*":
        _IN_MEMORY_DIALECTS.pop(dialect, None)
        cfg_dialects.pop(dialect, None)
    else:
        if dialect in cfg_dialects:
            if transpiler != cfg_dialects[dialect]:
                msg = f"{transpiler!r} is not the transpiler for dialect {dialect!r}"
                raise UsageError(msg)
            else:
                del cfg_dialects[dialect]
        elif dialect in _IN_MEMORY_DIALECTS:
            if transpiler != _IN_MEMORY_DIALECTS[dialect]:
                msg = f"{transpiler!r} is not the transpiler for dialect {dialect!r}"
                raise UsageError(msg)
            else:
                del _IN_MEMORY_DIALECTS[dialect]
        else:
            raise UsageError(f"no dialect {dialect!r} to deregister")
    config.write(cfg)


def _deregister_temp(dialect: Optional[str], transpiler: Type[Transpiler]) -> None:
    if dialect is None:
        for d, t in _IN_MEMORY_DIALECTS.items():
            if t == transpiler:
                del _IN_MEMORY_DIALECTS[d]
    elif dialect not in _IN_MEMORY_DIALECTS:
        raise UsageError(f"no dialect {dialect!r} to deregister")
    elif _IN_MEMORY_DIALECTS[dialect] != transpiler:
        msg = f"{transpiler!r} is not the transpiler for dialect {dialect!r}"
        raise UsageError(msg)
    else:
        del _IN_MEMORY_DIALECTS[dialect]
