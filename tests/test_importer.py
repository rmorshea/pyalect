import pyalect


def test_import_mock_module():
    @pyalect.register("test")
    class MyTranspiler:
        def __init__(self, dialect):
            self.dialect = dialect

        def transform_src(self, source):
            return source.replace("x", "y")

        def transform_ast(self, node):
            return node

    from . import mock_module

    assert mock_module.y == 1
