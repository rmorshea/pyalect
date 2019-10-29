from pyalect import Dialect


def test_imports():
    class MyDialect(Dialect):

        name = "test"

        def __init__(self, dialect):
            self.dialect = dialect

        def transform_src(self, source):
            return source.replace("x", "y")

        def transform_ast(self, node):
            return node

    from .mock_package import comment_header

    # the name x has been replaced with y
    assert comment_header.y == 1
