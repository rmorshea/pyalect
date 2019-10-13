import pytest

import pyalect
from pyalect.dialect import _IN_MEMORY_DIALECTS as IN_MEMORY_DIALECTS


@pytest.fixture(autouse=True)
def config():
    yield pyalect.config.read
    pyalect.config.delete()
    IN_MEMORY_DIALECTS.clear()
