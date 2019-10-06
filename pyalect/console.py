"""Pyalect

Custom language dialect management for Python

Usage:
    pyalect (activate | deactivate)
    pyalect register <transpiler> as <dialect> [--force]
    pyalect deregister (<dialect> | <transpiler> as <dialect>)
    pyalect config (show | path)

Descriptions:
    pyalect activate:
        The current Python interpreter will now automatically apply registered
        transpilers to imported module with a `# dialect=...` comment header.
    pyalect deactivate:
        The current Python interpreter will no longer apply registered transpilers
        to import modules
    pyalect register <transpiler> as <dialect> [--force]:
        Save a transpiler to be applied to modules with the given dialect header.
        The <transpiler> should follow one of the following forms:
        - package.module.submodule
        - package.module.submodule:attribute
    pyalect deregister (<dialect> | <transpiler> as <dialect>):
        Remove a transpiler from the dialect registery. Providing just the <dialect>
        will remove any transpiler that's registered to it. Providing a <transpiler>
        will remove is from the given <dialect>, however if <dialect> is "*" it will
        be deregistered from dialects.
    pyalect config show:
        Prints the current configuration to the console
    pyalect config path:
        Prints the configuration files's path to the console
"""
import sys
import json
from typing import Dict, Any, Iterable

from docopt import docopt

import pyalect
from . import config, dialect, importer
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
        if arguments["show"]:
            yield json.dumps(config.read(), indent=4, sort_keys=True)
        elif arguments["path"]:
            yield config.path()
    elif arguments["activate"]:
        importer.activate()
    elif arguments["deactivate"]:
        importer.deactivate()
    if arguments["register"]:
        dialect.register(
            arguments["<dialect>"], arguments["<transpiler>"], arguments["--force"]
        )
    elif arguments["deregister"]:
        dialect.deregister(arguments["<dialect>"], arguments["<transpiler>"])


if __name__ == "__main__":
    main()
