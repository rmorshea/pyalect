import textwrap
from functools import wraps
from typing import Any, Callable, Dict, Optional

from docopt import docopt
from typing_extensions import Protocol

_ConsoleFunction = Callable[[Dict[str, Any]], None]


class _WrappedConsoleFunction(Protocol):
    def __call__(self, arguments: Optional[Dict[str, Any]] = None) -> None:
        ...


def docopt_func(
    *args: Any, **kwargs: Any
) -> Callable[[_ConsoleFunction], _WrappedConsoleFunction]:
    """Makes functions with DocOpt docstrings compatible with Sphinx styling.

    This passes the original docstring to DocOpt, but modifies ``__doc__`` of the
    function to be compatible with Sphinx.

    Parameters:
        args: forwarded to ``docopt``
        kwargs: forwarded to ``docopt``
    """

    def setup(func: _ConsoleFunction) -> _WrappedConsoleFunction:
        """Decorator for properly formatting the function's docstring"""
        if func.__doc__ is None:
            raise ValueError("No docstring for docopt function.")

        original_docstring: str = func.__doc__

        @wraps(func)
        def wrapper(arguments: Optional[Dict[str, Any]] = None) -> None:
            args_to_exec: Dict[str, Any]
            if arguments is None:
                args_to_exec = docopt(textwrap.dedent("    " + original_docstring))
            else:
                args_to_exec = arguments
            return func(args_to_exec)

        func.__doc__ = "::\n\n    " + original_docstring
        return wrapper

    return setup
