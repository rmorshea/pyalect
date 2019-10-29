import ast

from pyalect.dialect import apply_dialects


def test_pytest_transpiler():
    import pyalect.builtins.pytest  # noqa

    source = "f = lambda : [1, 2, 3]\nassert f() == [1, 2]"
    tree = apply_dialects(source, "pytest")
    # Hard to assert exactly what the difference will be if Pytest
    # updates. Main thing is to test that it's being modified.
    assert ast.dump(ast.parse(source)) != ast.dump(tree)
