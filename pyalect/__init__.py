__version__ = "0.1.0.dev2"
from . import importer, shims
from .config import activate, deactivate, path
from .dialect import Transpiler, deregister, register

__all__ = [
    "activate",
    "deactivate",
    "deregister",
    "importer",
    "path",
    "register",
    "shims",
    "Transpiler",
]
