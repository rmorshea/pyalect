"""Pyalect

Custom language dialect management for Python

Usage:
  pyalect (activate | deactivate)
  pyalect register <transpiler> as <dialect> [--force]
  pyalect deregister (<dialect> | <transpiler> [as <dialect])
  pyalect config (show | path)
"""
import json

from docopt import docopt

import pyalect
from . import config, dialect, importer
from .errors import UsageError


def main():
    arguments = docopt(__doc__, version=pyalect.__version__)
    try:
        for output in execute(arguments):
            print(output)
    except UsageError as error:
        print(error)


def execute(arguments):
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
