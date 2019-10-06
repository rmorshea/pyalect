__version__ = "0.1.0.dev0"
from .dialect import Transpiler, register, deregister
from .importer import activate, deactivate
from .config import path
from . import shims
