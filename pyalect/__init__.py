__version__ = "0.1.0.dev6"
from . import importer, shims
from .config import activate, deactivate, path
from .dialect import Transpiler, deregister, register, registered

__all__ = [
    "activate",
    "deactivate",
    "deregister",
    "importer",
    "path",
    "register",
    "registered",
    "shims",
    "Transpiler",
]
