#!/bin/bash
set -e

pytest --cov=pyalect --cov-config=.coveragerc
black --verbose --check .
flake8 pyalect tests
mypy pyalect --strict
sphinx-build -b html docs/source docs/build
