from importlib import import_module

import pytest

import pyalect


@pytest.mark.parametrize(
    "module_name", ["comment_header", "file_extension", "file_extension_dot_py"]
)
def test_imports(module_name):
    @pyalect.register("test")
    class MyTranspiler:
        def __init__(self, dialect):
            self.dialect = dialect

        def transform_src(self, source):
            return source.replace("x", "y")

        def transform_ast(self, node):
            return node

    package = __name__.rsplit(".", 1)[0] + ".mock_package"
    module = import_module(module_name, package)

    # the name x has been replaced with y
    assert module.y == 1
