__version__ = "0.1.0"
from . import importer, shims
from .dialect import Dialect, apply_dialects, deregister, register, registered
from .errors import DialectError

__all__ = [
    "apply_dialects",
    "deregister",
    "DialectError",
    "importer",
    "register",
    "registered",
    "shims",
    "Dialect",
]
