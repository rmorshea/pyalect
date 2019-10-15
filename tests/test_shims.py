import ast

import pyalect


def test_simple_dialect(ipython):
    capture = []

    class MockTranspiler:
        def __init__(self, dialect):
            capture.append(dialect)

        def transform_src(self, source):
            capture.append(source)
            return source

        def transform_ast(self, node):
            capture.append(node)
            return node

    pyalect.register("test", MockTranspiler)

    ipython.run_cell(
        """
    %%dialect test

    x = 1
    """
    )

    assert capture[:2] == ["test", "\nx = 1\n\n"]
    assert len(capture) == 3
    assert ast.dump(capture[2]) == ast.dump(ast.parse("x = 1"))
