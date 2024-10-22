import io
import sys
import tokenize
import types
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec, SourceFileLoader
from importlib.util import spec_from_file_location
from pathlib import Path
from types import CodeType
from typing import Dict, List, Optional, Sequence, Union

from .dialect import apply_dialects, find_file_dialects
from .errors import DialectError, reraise_dialect_error


def decode_source(source_bytes: bytes) -> str:
    """Copied from importlib._bootstrap_external"""
    source_bytes_readline = io.BytesIO(source_bytes).readline
    encoding = tokenize.detect_encoding(source_bytes_readline)
    newline_decoder = io.IncrementalNewlineDecoder(None, True)
    return newline_decoder.decode(source_bytes.decode(encoding[0]))


class PyalectLoader(SourceFileLoader):
    """Import loader for Pyalect."""

    def __init__(self, dialects: List[str], fullname: str, filename: str):
        super().__init__(fullname, filename)
        self.dialects = dialects

    def source_to_code(  # type: ignore
        self, data: Union[bytes, str], path: str = "<string>"
    ) -> CodeType:
        if isinstance(data, bytes):
            source = decode_source(data)
        else:
            source = data
        try:
            ast_tree = apply_dialects(source, self.dialects, path)
        except DialectError:
            reraise_dialect_error()
        code: CodeType = compile(ast_tree, path, "exec")
        return code


class PyalectFinder(MetaPathFinder):
    """Determine whether to load modules with a :class:`PyalectLoader`.

    This class is registered to :data:`sys.meta_path`.
    """

    def __init__(self) -> None:
        self._specs: Dict[str, ModuleSpec] = {}

    def invalidate_caches(self) -> None:
        self._specs.clear()

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[Union[bytes, str]]],
        target: Optional[types.ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        if fullname in self._specs:
            return self._specs[fullname]

        known_path: List[Path]
        if path is None:
            known_path = [Path.cwd()]  # top level import
        else:
            str_paths = (p if isinstance(p, str) else p.decode() for p in path)
            known_path = list(map(Path, str_paths))

        if "." in fullname:
            name = fullname.rsplit(".", 1)[1]
        else:
            name = fullname

        for entry in known_path:
            submodule_locations: Optional[List[str]]
            if (entry / name).is_dir():
                filename = entry / name / "__init__.py"
                submodule_locations = [str(entry / name)]
            else:
                filename = entry / (name + ".py")
                submodule_locations = None

            if not filename.exists():
                continue

            dialects = find_file_dialects(filename)

            if not dialects:
                continue

            spec = self._specs[fullname] = spec_from_file_location(
                fullname,
                filename,
                loader=PyalectLoader(dialects, fullname, str(filename)),
                submodule_search_locations=submodule_locations,
            )
            return spec

        # we don't know how to import this
        return None


sys.meta_path.insert(0, PyalectFinder())
