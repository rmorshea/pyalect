import ast
import io
import os
import sys
import tokenize
import types
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec, SourceFileLoader
from importlib.util import spec_from_file_location
from types import CodeType
from typing import Dict, List, Optional, Sequence, Union

from . import dialect


def decode_source(source_bytes: bytes) -> str:
    """Copied from importlib._bootstrap_external"""
    source_bytes_readline = io.BytesIO(source_bytes).readline
    encoding = tokenize.detect_encoding(source_bytes_readline)
    newline_decoder = io.IncrementalNewlineDecoder(None, True)
    return newline_decoder.decode(source_bytes.decode(encoding[0]))


class PyalectLoader(SourceFileLoader):
    """Import loader for Pyalect."""

    @staticmethod
    def source_to_code(data: Union[bytes, str], path: str = "<string>") -> CodeType:
        dialect_name = dialect.find_dialect(data)
        code: CodeType
        if dialect_name is not None:
            transpiler = dialect.transpiler(dialect_name)
            if isinstance(data, bytes):
                source = decode_source(data)
            else:
                source = data
            trans_source = transpiler.transform_src(source)
            tree = ast.parse(trans_source)
            trans_tree = transpiler.transform_ast(tree)
            code = compile(trans_tree, path, "exec")
        else:
            code = compile(data, path, "exec")
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

        if path is None:
            known_path = [os.getcwd()]  # top level import
        else:
            known_path = [p if isinstance(p, str) else p.decode() for p in path]
        if "." in fullname:
            parents, name = fullname.rsplit(".", 1)
        else:
            name = fullname

        for entry in known_path:
            submodule_locations: Optional[List[str]]
            if os.path.isdir(os.path.join(entry, name)):
                # this module has child modules
                filename = os.path.join(entry, name, "__init__.py")
                submodule_locations = [os.path.join(entry, name)]
            else:
                filename = os.path.join(entry, name + ".py")
                submodule_locations = None

            if not os.path.exists(filename):
                continue

            loader = PyalectLoader(fullname, filename)
            if dialect.find_dialect(loader.get_data(filename)) is None:
                # no dialect defined
                return None

            spec = spec_from_file_location(
                fullname,
                filename,
                loader=loader,
                submodule_search_locations=submodule_locations,
            )
            self._specs[fullname] = spec
            return spec

        # we don't know how to import this
        return None


sys.meta_path.insert(0, PyalectFinder())
