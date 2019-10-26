import pyalect


def test_imports():
    @pyalect.register("test")
    class MyTranspiler:
        def __init__(self, dialect):
            self.dialect = dialect

        def transform_src(self, source):
            return source.replace("x", "y")

        def transform_ast(self, node):
            return node

    from .mock_package import comment_header

    # the name x has been replaced with y
    assert comment_header.y == 1
