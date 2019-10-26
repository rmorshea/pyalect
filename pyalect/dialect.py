import ast
import io
import re
import tokenize
from pathlib import Path
from typing import Callable, Dict, Optional, Set, Type, Union, overload

from typing_extensions import Protocol, runtime_checkable

DIALECT_COMMENT = re.compile(r"^# ?dialect ?= ?(.+)\n?$")
DIALECT_NAME = re.compile(r"^[\w\-]+$")

_DIALECTS: Dict[str, Type["Transpiler"]] = {}


def file_dialect(filename: Union[str, Path]) -> Optional[str]:
    filepath = Path(filename)
    if not filepath.suffix:
        return None
    elif filepath.suffix == ".py":
        return module_dialect(io.FileIO(str(filepath)))
    else:
        return None


def module_dialect(source: Union[bytes, str, io.FileIO]) -> Optional[str]:
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
    elif isinstance(source, bytes):
        buffer = io.BytesIO(source)
    else:
        raise TypeError(f"Expected bytes, str, or FileIO not {source!r}")
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


def transpiler(dialect: str) -> Transpiler:
    """Retrieve the transpiler for the given dialect."""
    if dialect in _DIALECTS:
        return _DIALECTS[dialect](dialect)
    else:
        raise ValueError(f"Unknown dialect {dialect!r}")


_RegisterDeco = Callable[[Type[Transpiler]], Type[Transpiler]]


def registered() -> Set[str]:
    """The set of dialects already registered."""
    return set(_DIALECTS)


@overload
def register(dialect: str, transpiler: Type[Transpiler]) -> None:
    ...


@overload
def register(dialect: str, transpiler: None = None) -> _RegisterDeco:
    ...


def register(
    dialect: str, transpiler: Union[None, Type[Transpiler]] = None
) -> Optional[_RegisterDeco]:
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
        raise ValueError(f"invalid dialect name {dialect!r}")

    if dialect in _DIALECTS:
        raise ValueError(f"already registered {_DIALECTS[dialect]!r} as {dialect!r}")

    def setup(transpiler: Type[Transpiler]) -> Type[Transpiler]:
        if isinstance(transpiler, type) and issubclass(transpiler, Transpiler):
            _DIALECTS[dialect] = transpiler
        else:
            raise ValueError(f"Expected a Transpiler, not {transpiler!r}")
        return transpiler

    if transpiler is not None:
        setup(transpiler)
        return None
    else:
        return setup


def deregister(
    dialect: str = "*", transpiler: Optional[Type[Transpiler]] = None
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
        raise ValueError(f"invalid dialect name {dialect!r}")

    if isinstance(transpiler, type):
        if not issubclass(transpiler, Transpiler):
            raise ValueError(f"{transpiler} is not a Transpiler")
    elif transpiler is not None:
        raise ValueError(f"Expected a Transpiler, not {transpiler!r}")

    if dialect == "*" and transpiler is None:
        _DIALECTS.clear()
    elif dialect == "*":
        for d, t in list(_DIALECTS.items()):
            if t == transpiler:
                del _DIALECTS[d]
    elif transpiler is None:
        _DIALECTS.pop(dialect, None)
    else:
        if dialect in _DIALECTS:
            if transpiler != _DIALECTS[dialect]:
                msg = f"{transpiler!r} is not the transpiler for dialect {dialect!r}"
                raise ValueError(msg)
            else:
                del _DIALECTS[dialect]
        else:
            raise ValueError(f"no dialect {dialect!r} to deregister")
