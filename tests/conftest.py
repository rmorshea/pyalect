import pytest
from IPython import get_ipython, start_ipython
from IPython.terminal.interactiveshell import TerminalInteractiveShell

from pyalect.dialect import _REGISTERED_DIALECTS


@pytest.fixture(autouse=True)
def dialects():
    yield
    _REGISTERED_DIALECTS.clear()


@pytest.fixture(scope="session")
def ipython():
    TerminalInteractiveShell.interact = lambda *a, **kw: None
    start_ipython([])
    return get_ipython()
