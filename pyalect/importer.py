import ast
import io
import os
import sys
import tokenize
from importlib.abc import MetaPathFinder, FileLoader
from importlib.util import spec_from_file_location
from importlib.machinery import ModuleSpec
from typing import Union, Optional, Any, Sequence, List
import types

from . import dialect, config


def activate() -> None:
    config.write({"active": True})


def deactivate() -> None:
    config.write({"active": False})


class PyalectLoader(FileLoader):
    def get_byte_source(self, fullname: str) -> bytes:
        with open(self.get_filename(fullname), "rb") as f:
            return f.read()

    def get_source(self, fullname: str) -> str:
        byte_source = self.get_byte_source(fullname)
        encoding, _ = tokenize.detect_encoding(io.BytesIO(byte_source).readline)
        # see: https://github.com/python/typeshed/pull/3311
        newline_decoder = io.IncrementalNewlineDecoder(None, True)  # type: ignore
        # see: https://github.com/python/typeshed/pull/3312
        return newline_decoder.decode(byte_source.decode(encoding))  # type: ignore

    def get_dialect(self, fullname: str) -> Optional[str]:
        """Find dialect comment before the first non-continuation newline."""
        return dialect.find(self.get_byte_source(fullname))

    def get_code(self, fullname: str) -> Any:
        source = self.get_source(fullname)
        filename = self.get_filename(fullname)
        dialect_name = self.get_dialect(fullname)
        if dialect_name is not None:
            transpiler = dialect.transpiler(dialect_name)
            trans_source = transpiler.transform_src(source)
            tree = ast.parse(trans_source)
            trans_tree = transpiler.transform_ast(tree)
            return compile(trans_tree, filename, "exec")
        else:
            return compile(source, filename, "exec")


class PyalectFinder(MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[Union[bytes, str]]],
        target: Optional[types.ModuleType] = None,
    ) -> Optional[ModuleSpec]:
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
            if not loader.get_dialect(fullname):
                # no dialect defined
                return None

            return spec_from_file_location(
                fullname,
                filename,
                loader=loader,
                submodule_search_locations=submodule_locations,
            )

        # we don't know how to import this
        return None


sys.meta_path.insert(0, PyalectFinder())