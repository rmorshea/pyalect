import ast

import pytest

import pyalect


class MockTranspiler:
    def __init__(self, dialect):
        self.dialect = dialect

    def transform_src(self, source):
        self.source = source
        return source

    def transform_ast(self, node):
        self.node = node
        return node


@pytest.mark.parametrize(
    "source",
    [
        "# dialect=test",
        "#dialect=test",
        "\n\n\n# dialect=test",
        "# coding=utf-8\n# dialect=test",
        "\n# coding=utf-8\n\n# dialect=test",
        "# coding=utf-8\n\n# other comment\n\n# dialect=test",
    ],
)
def test_module_dialect_in_source(source):
    assert pyalect.dialect.module_dialect(source) == "test"


@pytest.mark.parametrize(
    "source",
    [
        "",
        "\n\n\n",
        "'a docstring'\n# dialect=test",
        "\n# coding=utf-8\n'a docstring'\n# dialect=test",
    ],
)
def test_no_dialect_found_in_source(source):
    assert pyalect.dialect.module_dialect(source) is None


def test_module_dialect_uses_str_or_bytes():
    pyalect.dialect.module_dialect("")
    pyalect.dialect.module_dialect(b"")
    with pytest.raises(TypeError):
        pyalect.dialect.module_dialect(None)


def test_default_transpiler_does_not_modify():
    class MyTranspiler(pyalect.dialect.Transpiler):
        pass

    trsp = MyTranspiler("test")
    src = "# dialect=test\nx = 1"
    assert trsp.transform_src(src) == src
    assert ast.dump(trsp.transform_ast(ast.parse(src))) == ast.dump(ast.parse(src))


def test_register_dialect_transpiler():
    class MyTranspiler:
        def __init__(self, dialect):
            ...

        def transform_src(self, source):
            ...

        def transform_ast(self, node):
            ...

    pyalect.register("mock_dialect", MyTranspiler)
    assert pyalect.registered() == {"mock_dialect"}
    transpiler = pyalect.dialect.transpiler("mock_dialect")
    assert isinstance(transpiler, MyTranspiler)


def test_deregister_dialect_transpiler():
    pyalect.register("mock_dialect", MockTranspiler)
    assert pyalect.registered() == {"mock_dialect"}
    pyalect.deregister("mock_dialect", MockTranspiler)
    assert pyalect.registered() == set()
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect")


def test_deregister_transpiler_class_from_all():
    pyalect.register("mock_dialect_1", MockTranspiler)
    pyalect.register("mock_dialect_2", MockTranspiler)
    pyalect.deregister(transpiler=MockTranspiler)
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect_1")
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect_2")


def test_deregister_any_from_dialect():
    pyalect.register("mock_dialect", MockTranspiler)
    pyalect.deregister("mock_dialect")
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect")


def test_reject_registering_bad_dialect_name():
    with pytest.raises(ValueError, match=r"invalid dialect name .*"):
        pyalect.register("#>%&*", MockTranspiler)


def test_already_registered_error():
    pyalect.register("mock_dialect", MockTranspiler)
    with pytest.raises(ValueError, match=r"already registered.*"):
        pyalect.register("mock_dialect", MockTranspiler)


def test_register_bad_transpiler_type():
    with pytest.raises(ValueError, match=r"Expected a Transpiler, not 'bad-value'"):
        pyalect.register("test", "bad-value")

    with pytest.raises(ValueError, match=r"Expected a Transpiler, not .*"):

        @pyalect.register("test")
        class MissingTransformSource:
            def transform_ast(self, node):
                ...

    with pytest.raises(ValueError, match=r"Expected a Transpiler, not .*"):

        @pyalect.register("test")
        class MissingTransformAst:
            def transform_src(self, source):
                ...
