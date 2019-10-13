import pytest

import pyalect

from .mock_package.mock_module import MockTranspiler


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
def test_find_dialect_in_source(source):
    assert pyalect.dialect.find_dialect(source) == "test"


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
    assert pyalect.dialect.find_dialect(source) is None


def test_register_dialect_transpiler_by_name():
    name = "tests.mock_package.mock_module:MockTranspiler"
    pyalect.register("mock_dialect", name)
    transpiler = pyalect.dialect.transpiler("mock_dialect")
    assert isinstance(transpiler, MockTranspiler)


def test_deregister_dialect_transpiler_by_name(config):
    name = "tests.mock_package.mock_module:MockTranspiler"
    pyalect.register("mock_dialect", name)
    pyalect.deregister("mock_dialect", name)
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect")


def test_register_dialect_transpiler_in_memory():
    class MyTranspiler:
        def __init__(self, dialect):
            ...

        def transform_src(self, source):
            ...

        def transform_ast(self, node):
            ...

    pyalect.register("mock_dialect", MyTranspiler)
    transpiler = pyalect.dialect.transpiler("mock_dialect")
    assert isinstance(transpiler, MyTranspiler)


def test_deregister_dialect_transpiler_in_memory():
    pyalect.register("mock_dialect", MockTranspiler)
    pyalect.deregister("mock_dialect", MockTranspiler)
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect")


def test_deregister_transpiler_name_from_all():
    name = "tests.mock_package.mock_module:MockTranspiler"
    pyalect.register("mock_dialect_1", name)
    pyalect.register("mock_dialect_2", name)
    pyalect.deregister(transpiler=name)
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect_1")
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect_2")


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
    pyalect.deregister("mock_dialect", "*")
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect")
    name = "tests.mock_package.mock_module:MockTranspiler"
    pyalect.register("mock_dialect", name)
    pyalect.deregister("mock_dialect", "*")
    with pytest.raises(ValueError):
        pyalect.dialect.transpiler("mock_dialect")
