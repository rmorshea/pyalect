import ast
import sys

from _pytest.assertion.rewrite import AssertionRewritingHook, rewrite_asserts

from pyalect import Dialect

_PYTEST_CONFIG = None
for finder in sys.meta_path:
    if isinstance(finder, AssertionRewritingHook):
        _PYTEST_CONFIG = finder.config


class RewritePytestAssertions(Dialect):

    name = "pytest"

    def transform_src(self, source: str) -> str:
        self.source = source
        return source

    def transform_ast(self, node: ast.AST) -> ast.AST:
        rewrite_asserts(node, self.source, self.filename, _PYTEST_CONFIG)
        return node
