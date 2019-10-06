#!/bin/bash
set -e

pytest --cov=pyalect --cov-config=.coveragerc
black --verbose --check .
flake8 src/py
mypy pyalect --config-file=mypy.ini