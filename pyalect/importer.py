import ast
import io
import os
import re
import imp
import sys
import marshal
import inspect
import tokenize
from uuid import uuid1
from importlib import import_module
from importlib.abc import MetaPathFinder, FileLoader
from importlib.util import spec_from_file_location
from typing import Union, Optional
from types import CodeType

from . import dialect, config


def activate():
    config.write({"active": True})


def deactivate():
    config.write({"active": False})


class PyalectLoader(FileLoader):
    def get_byte_source(self, fullname: str) -> bytes:
        with open(self.get_filename(fullname), "rb") as f:
            return f.read()

    def get_source(self, fullname: str) -> bytes:
        byte_source = self.get_byte_source(fullname)
        encoding, _ = tokenize.detect_encoding(io.BytesIO(byte_source).readline)
        newline_decoder = io.IncrementalNewlineDecoder(None, True)
        return newline_decoder.decode(byte_source.decode(encoding))

    def get_dialect(self, fullname: str) -> Optional[str]:
        """Find dialect comment before the first non-continuation newline."""
        return dialect.find(self.get_byte_source(fullname))

    def get_code(self, fullname: str) -> CodeType:
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
    def find_spec(self, fullname, path, target=None):
        if path in (None, ""):
            path = [os.getcwd()]  # top level import
        if "." in fullname:
            parents, name = fullname.rsplit(".", 1)
        else:
            name = fullname

        for entry in path:
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
