import ast
import io
import re
import tokenize
from pathlib import Path
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Type,
    Union,
    overload,
)

DIALECT_COMMENT = re.compile(r"^# ?dialect *= *(\w+(?: *, *\w+)*)\n?$")
DIALECT_NAME = re.compile(r"^\w+$")

_REGISTERED_DIALECTS: Dict[str, Type["Dialect"]] = {}


def find_file_dialects(filename: Union[str, Path]) -> List[str]:
    """Find dialects in the source of the file at the given path.

    See :func:`find_source_dialects` for more info.
    """
    filepath = Path(filename)
    if filepath.suffix == ".py":
        file = io.FileIO(str(filepath))
        try:
            return find_source_dialects(file)
        finally:
            file.close()
    else:
        return []


def find_source_dialects(source: Union[bytes, str, io.FileIO]) -> List[str]:
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
                names = match.groups()[0].split(",")
                return list(map(str.strip, names))
    return []


class Dialect:
    """A base class for defining a dialect transpiler.

    The logic of transpiling can be roughly paraphrased as:

    .. code-block::

        import ast

        transpiler = MyDialect("my_module.py")
        source = read_file_source()
        new_source = transpiler.transform_src(source)
        tree = ast.parse(new_source)
        new_tree = transpiler.transform_ast(tree)

        exec(compile(new_tree, "my_module.py", "exec"))

    .. note::

        A transpiler instance is only used **once** per module and **shouldn't** be
        reused. This means that a :class:`Dialect` can keep state between calls to
        :meth:`Dialect.transform_src` and :meth:`Dialect.transform_ast`

    Parameters:
        filename: the name of the file being transpiled.
    """

    name: str

    def __init_subclass__(cls, name: Optional[str] = None) -> None:
        if name is not None:
            cls.name = name
        if getattr(cls, "name", None) is not None:
            register(cls)

    def __init__(self, filename: Optional[str] = None) -> None:
        self.filename = filename

    def transform_src(self, source: str) -> str:
        """Implement this method to transform a raw Python source string."""
        return source

    def transform_ast(self, node: ast.AST) -> ast.AST:
        """Implement this method to transform an :class:`~ast.AST`."""
        return node


class DialectReducer(Sequence[Dialect]):
    """A reducer for applying many dialects at once.

    It acts like a :class:`typing.Sequence`, but with the same interface
    as a :class:`Dialect` which makes it easy to work with.
    """

    def __init__(self, dialects: Iterable[Dialect]):
        self._dialects = tuple(dialects)

    @overload
    def __getitem__(self, index: int) -> Dialect:
        ...

    @overload
    def __getitem__(self, index: slice) -> "DialectReducer":
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Dialect, "DialectReducer"]:
        if isinstance(index, int):
            return self._dialects[index]
        else:
            return DialectReducer(self._dialects[index])

    def __len__(self) -> int:
        return len(self._dialects)

    def transform_src(self, source: str) -> str:
        """Transform raw Python source code using the contained dialects."""
        for d in self._dialects:
            source = d.transform_src(source)
        return source

    def transform_ast(self, node: ast.AST) -> ast.AST:
        """Transform an AST tree using the contained dialects."""
        for d in self._dialects:
            node = d.transform_ast(node)
        return node


def apply_dialects(
    source: str, names: Union[str, Iterable[str]], filename: Optional[str] = None
) -> ast.AST:
    """Utility for applying dialect transpilers to source code."""
    reducer = dialect_reducer(names, filename)
    source = reducer.transform_src(source)
    tree = reducer.transform_ast(ast.parse(source))
    return tree


def dialect_reducer(
    names: Union[str, Iterable[str]], filename: Optional[str] = None
) -> DialectReducer:
    """Get a :class:`DialectReducer`

    Examples:
        There's a couple different ways to create the reducer.

        .. code-block::

            dialect_reducer("d1")
            dialect_reducer("d1, d2, d3")
            dialect_reducer(["d1", "d2", "d3"])
    """
    return DialectReducer([dialect(n, filename) for n in _split_dialect_names(names)])


def dialect(name: str, filename: Optional[str]) -> Dialect:
    """Instantiate a dialect for use on the given file.

    Parameters:
        name: The dialect name
        filename: The name of the file the :class:`Dialect` will be used on.
    """
    if name in _REGISTERED_DIALECTS:
        return _REGISTERED_DIALECTS[name](filename)
    else:
        raise ValueError(f"Unknown dialect {name!r}")


def registered() -> Set[str]:
    """The set of dialect names already registered."""
    return set(_REGISTERED_DIALECTS)


def register(dialect: Type[Dialect]) -> Type[Dialect]:
    """Register a :class:`Dialect` so it will be applied to imported modules."""
    if not issubclass(dialect, Dialect):
        raise TypeError(f"Expected a 'Dialect' not {dialect}")
    if getattr(dialect, "name", None) is None:
        raise ValueError(f"Dialect {dialect} has no name defined")
    elif dialect.name in _REGISTERED_DIALECTS:
        msg = f"Already registered {_REGISTERED_DIALECTS[dialect.name]!r} as {dialect.name!r}"
        raise ValueError(msg)
    _REGISTERED_DIALECTS[_check_valid_dialect_name(dialect.name)] = dialect
    return dialect


def deregister(*dialects: Union[Type[Dialect], Iterable[str], str],) -> None:
    """Deregister one or more :class:`Dialect` classes.

    Parameters:
        dialects: the dialect name, or class
    """
    if not dialects:
        _REGISTERED_DIALECTS.clear()
        return None

    for dia in dialects:
        if isinstance(dia, str):
            for name in _split_dialect_names(dia):
                try:
                    del _REGISTERED_DIALECTS[name]
                except KeyError:
                    raise ValueError(f"No dialect {name!r} to deregister")
        elif isinstance(dia, type) and issubclass(dia, Dialect):
            if (
                getattr(dia, "name", None) is not None
                and _REGISTERED_DIALECTS[dia.name] == dia
            ):
                del _REGISTERED_DIALECTS[dia.name]
            else:
                raise ValueError(f"{dia} is not registered.")
        else:
            raise TypeError(f"Expected a string, or Dialect subclass, not {dia}")


def _split_dialect_names(dialects: Union[str, Iterable[str]]) -> Iterator[str]:
    if not isinstance(dialects, str):
        dialect_iter = dialects
    else:
        dialect_iter = list(map(str.strip, dialects.split(",")))
    for dia in dialect_iter:
        yield _check_valid_dialect_name(dia)


def _check_valid_dialect_name(name: str) -> str:
    if not DIALECT_NAME.match(name):
        raise ValueError(f"Invalid dialect name {name!r}")
    return name
