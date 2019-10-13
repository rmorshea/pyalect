#!/bin/bash
set -e

pytest --cov=pyalect --cov-config=.coveragerc
black --verbose --check .
flake8 src/py
mypy pyalect --strict
sphinx-build -b html docs/source docs/build
