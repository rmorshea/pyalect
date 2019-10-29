__version__ = "0.1.0.dev8"
from . import importer, shims
from .dialect import Dialect, deregister, register, registered

__all__ = ["deregister", "importer", "register", "registered", "shims", "Dialect"]
