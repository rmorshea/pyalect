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
    pyalect register <transpiler> as <dialect> [--force]:
        Save a transpiler to be applied to modules with the given dialect header.
        The <transpiler> should be of the form `dotted.path.to:TranspilerClass`.
    pyalect deregister (<dialect> | <transpiler> as <dialect>):
        Remove a transpiler from the dialect registery. Providing just the <dialect>
        will remove any transpiler that's registered to it. Providing a <transpiler>
        will remove is from the given <dialect>, however if <dialect> is "*" it will
        be deregistered from dialects.
    pyalect show config:
        Prints the configuration file path and current state.
    pyalect delete config:
        Deletes the config file. This should be done prior to uninstalling Pyalect.
"""
import sys
import json
from typing import Dict, Any, Iterable

from docopt import docopt

import pyalect
from . import config, dialect
from .errors import UsageError


def main() -> None:
    arguments = docopt(__doc__, version=pyalect.__version__)
    try:
        for output in execute(arguments):
            print(output)
    except UsageError as error:
        print(error)
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
    text = str(value).title()
    return text + "\n" + ("-" * len(text))


if __name__ == "__main__":
    main()
