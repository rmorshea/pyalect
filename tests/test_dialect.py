import ast
from pathlib import Path

import pytest

import pyalect
from pyalect.dialect import (
    Dialect,
    dialect_reducer,
    find_file_dialects,
    find_source_dialects,
)


class MockDialect(Dialect):
    def __init__(self, filename=None):
        self.filename = filename

    def transform_src(self, source):
        self.source = source
        return source

    def transform_ast(self, node):
        self.node = node
        return node


def make_dialect(name):
    return type(name.title(), (MockDialect,), {"name": name})


@pytest.mark.parametrize(
    "source, expected",
    [
        ("# dialect=test", ["test"]),
        ("# dialect   =test", ["test"]),
        ("# dialect=    test", ["test"]),
        ("# dialect   =    test", ["test"]),
        ("#dialect=test", ["test"]),
        ("\n\n\n# dialect=test", ["test"]),
        ("# coding=utf-8\n# dialect=test", ["test"]),
        ("\n# coding=utf-8\n\n# dialect=test", ["test"]),
        ("# coding=utf-8\n\n# other comment\n\n# dialect=test", ["test"]),
        ("# dialect=test1,test2", ["test1", "test2"]),
        ("# dialect=test1,   test2", ["test1", "test2"]),
        ("# dialect=     test1,test2", ["test1", "test2"]),
        ("# dialect    =   test1,test2", ["test1", "test2"]),
        ("# dialect    =   test1,    test2", ["test1", "test2"]),
        ("# dialect    =   test1    ,    test2", ["test1", "test2"]),
        ("# dialect = test1, test2, test3", ["test1", "test2", "test3"]),
    ],
)
def test_dialects_in_source(source, expected):
    assert find_source_dialects(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        "",
        "\n\n\n",
        "'a docstring'\n# dialect=test",
        "\n# coding=utf-8\n'a docstring'\n# dialect=test",
        "# dialect=test1 test2",
    ],
)
def test_no_dialect_found_in_source(source):
    assert find_source_dialects(source) == []


def test_file_has_no_dialect():
    no_dialect_file = Path(__file__).parents[0] / "mock_package" / "no_dialect"
    assert find_file_dialects(no_dialect_file) == []


def test_module_dialect_uses_str_or_bytes():
    pyalect.dialect.find_source_dialects("")
    pyalect.dialect.find_source_dialects(b"")
    with pytest.raises(TypeError):
        find_source_dialects(None)


def test_default_transpiler_does_not_modify():
    class MyDialect(Dialect):
        name = "test"

    trsp = MyDialect()
    src = "# dialect=test\nx = 1"
    assert trsp.transform_src(src) == src
    assert ast.dump(trsp.transform_ast(ast.parse(src))) == ast.dump(ast.parse(src))


def test_register_dialect_transpiler():
    class MyDialect(Dialect):

        name = "mock_dialect"

        def transform_src(self, source):
            ...

        def transform_ast(self, node):
            ...

    assert pyalect.registered() == {"mock_dialect"}
    dialect = dialect_reducer("mock_dialect")[0]
    assert isinstance(dialect, MyDialect)


def test_register_dialect_via_name_keyword():
    class MyDialect(Dialect, name="mock_dialect"):
        def transform_src(self, source):
            ...

        def transform_ast(self, node):
            ...

    assert pyalect.registered() == {"mock_dialect"}
    dialect = dialect_reducer("mock_dialect")[0]
    assert isinstance(dialect, MyDialect)


def test_deregister_dialect_transpiler():
    class MockDialect1(Dialect):
        name = "test1"

    class MockDialect2(Dialect):
        name = "test2"

    class MockDialect3(Dialect):
        name = "test3"

    pyalect.deregister("test1", "test2", "test3")

    with pytest.raises(ValueError):
        dialect_reducer("test1")
    with pytest.raises(ValueError):
        dialect_reducer("test2")
    with pytest.raises(ValueError):
        dialect_reducer("test3")


def test_deregister_transpiler_class_from_all():
    class MockDialect1(Dialect):
        name = "test1"

    class MockDialect2(Dialect):
        name = "test2"

    class MockDialect3(Dialect):
        name = "test3"

    pyalect.deregister()

    with pytest.raises(ValueError):
        dialect_reducer("test1")
    with pytest.raises(ValueError):
        dialect_reducer("test2")
    with pytest.raises(ValueError):
        dialect_reducer("test3")


def test_deregister_any_from_dialect():
    class MockDialect(Dialect):
        name = "test"

    pyalect.deregister(MockDialect)
    with pytest.raises(ValueError):
        dialect_reducer("test")


def test_reject_registering_bad_dialect_name():
    with pytest.raises(ValueError, match=r"Invalid dialect name .*"):

        class MockDialect(Dialect):
            name = "#$%^&"


def test_already_registered_error():
    class MockDialect1(Dialect):
        name = "test"

    with pytest.raises(ValueError, match=r"Already registered.*"):

        class MockDialect2(Dialect):
            name = "test"


def test_transpiler_reduction_as_sequence():
    transpilers = [MockDialect("x"), MockDialect("y"), MockDialect("z")]
    reduction = pyalect.dialect.DialectReducer(transpilers)
    assert len(reduction) == 3
    assert reduction[0].filename == "x"
    assert [d.filename for d in reduction[1:]] == ["y", "z"]


def test_bad_dialect_name():
    with pytest.raises(ValueError):

        class MyDialect(Dialect, name="&^%^&*"):
            pass


def test_bad_dialect_type():
    with pytest.raises(TypeError):

        @pyalect.register
        class NotADialect:
            pass


def test_register_dialect_without_name():
    with pytest.raises(ValueError):

        @pyalect.register
        class NotADialect(Dialect):
            pass


def test_deregister_non_existant_dialect():
    with pytest.raises(ValueError):
        pyalect.deregister("no_dialect")
    with pytest.raises(ValueError):
        pyalect.deregister(MockDialect)


def test_deregister_bad_value():
    with pytest.raises(TypeError):
        pyalect.deregister(None)


def test_dialect_reducer_from_list_of_names():
    dialects = [make_dialect("x"), make_dialect("y"), make_dialect("z")]
    reducer = pyalect.dialect.dialect_reducer(["x", "y", "z"])
    for dia, cls in zip(reducer, dialects):
        assert isinstance(dia, cls)
