import json
import sys
from typing import Any, Dict, Iterable

import pyalect

from . import config, dialect
from .errors import UsageError
from .utils import docopt_func


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
            Should be done prior to uninstalling Pyalect. This has the effect of
            deactivating Pyalect and clearing the configuration state.
    """
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
