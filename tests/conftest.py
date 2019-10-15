import pytest
from IPython import get_ipython, start_ipython
from IPython.terminal.interactiveshell import TerminalInteractiveShell

import pyalect
from pyalect.dialect import _IN_MEMORY_DIALECTS as IN_MEMORY_DIALECTS


@pytest.fixture(autouse=True)
def config():
    yield pyalect.config.read
    pyalect.config.delete()
    IN_MEMORY_DIALECTS.clear()


@pytest.fixture(scope="session")
def ipython():
    TerminalInteractiveShell.interact = lambda *a, **kw: None
    start_ipython([])
    return get_ipython()
