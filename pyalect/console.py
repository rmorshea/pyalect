import json
import sys
import textwrap
from functools import wraps
from typing import Any, Callable, Dict, Iterable, Optional

from docopt import docopt
from typing_extensions import Protocol

import pyalect

from . import config, dialect
from .errors import UsageError

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
        def wrapper(argv: Optional[str] = None) -> None:
            arguments = docopt(
                textwrap.dedent("    " + original_docstring),
                argv,
                version=pyalect.__version__,
            )
            return func(arguments)

        func.__doc__ = "::\n\n    " + original_docstring
        return wrapper

    return setup


@docopt_func(version=pyalect.__version__)
def main(arguments: Dict[str, Any]) -> None:
    """Pyalect

    Custom language dialect management for Python

    Usage:
        pyalect (activate | deactivate)
        pyalect register <transpiler> as <dialect> [--force]
        pyalect deregister (<dialect> | <transpiler> from <dialect>)
        pyalect (show | delete) config

    Descriptions:
        pyalect activate:
            The current Python interpreter will now automatically apply registered
            transpilers to imported module with a `# dialect=...` comment header.
        pyalect deactivate:
            The current Python interpreter will no longer apply registered transpilers
            to import modules
        pyalect register:
            Save a transpiler to be applied to modules with the given dialect header.
            The <transpiler> should be of the form `dotted.path.to:TranspilerClass`.
        pyalect deregister:
            Remove a transpiler from the dialect registery. Providing just the <dialect>
            will remove any transpiler that's registered to it. Providing a <transpiler>
            will remove is from the given <dialect>, however if <dialect> is "*" it will
            be deregistered from dialects.
        pyalect show config:
            Prints the configuration file path and current state.
        pyalect delete config:
            Deleting the configuration file will also effectively deactivate Pyalect.
    """
    try:
        for output in execute(arguments):
            print(output)
    except UsageError as error:
        print(error, file=sys.stderr)
        sys.exit(1)


def execute(arguments: Dict[str, Any]) -> Iterable[Any]:
    if arguments["config"]:
        path = config.path()
        if not path.exists():
            yield "No configuration file exists"
        elif arguments["show"]:
            yield _title("path")
            yield path
            yield "\n" + _title("configuration")
            yield json.dumps(config.read(), indent=4, sort_keys=True)
        elif arguments["delete"]:
            config.delete()
    elif arguments["activate"]:
        config.activate()
    elif arguments["deactivate"]:
        config.deactivate()
    if arguments["register"]:
        dialect.register(
            arguments["<dialect>"], arguments["<transpiler>"], arguments["--force"]
        )
    elif arguments["deregister"]:
        dialect.deregister(arguments["<dialect>"], arguments["<transpiler>"])


def _title(value: Any) -> str:
    return f"--- {str(value).upper()} ---"


if __name__ == "__main__":
    main()
