import re
import traceback

from pyalect import Dialect, DialectError


def test_imports():
    class MyDialect(Dialect):

        name = "test"

        def transform_src(self, source):
            return source.replace("x", "y")

        def transform_ast(self, node):
            return node

    from .mock_package import comment_header

    # the name x has been replaced with y
    assert comment_header.y == 1


_tb_template = r""".*
  File ".*?/mock_package/empty.py", line 1, in source_to_code
    # dialect=test_dialect
pyalect.errors.DialectError: error_message
"""


def test_raise_dialect_error_on_import():
    class MyDialect(Dialect):

        name = "test_dialect"

        def transform_src(self, source):
            raise DialectError("error_message", self.filename, 1)

    try:
        from .mock_package import empty  # noqa
    except Exception:
        assert bool(re.match(_tb_template, traceback.format_exc(), re.DOTALL))
    else:
        assert False, f"Did not raise {DialectError}"
