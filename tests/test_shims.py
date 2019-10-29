import ast

from pyalect import Dialect


def test_simple_dialect(ipython):
    capture = []

    class MockDialect(Dialect):

        name = "test"

        def __init__(self, filename):
            capture.append(filename)

        def transform_src(self, source):
            capture.append(source)
            return source

        def transform_ast(self, node):
            capture.append(node)
            return node

    ipython.run_cell(
        """
    %%dialect test

    x = 1
    """
    )

    assert capture[:2] == [None, "\nx = 1\n\n"]
    assert len(capture) == 3
    assert ast.dump(capture[2]) == ast.dump(ast.parse("x = 1"))
