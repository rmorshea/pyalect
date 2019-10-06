#!/bin/bash
set -e

pytest --cov=htm_pyx --cov-config=.coveragerc
black --verbose --check .
flake8 src/py
mypy htm_pyx --config-file=mypy.ini
