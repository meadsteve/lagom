#!/usr/bin/env bash
set -ex
export PIPENV_VERBOSITY=-1
pip install pipenv
pipenv install --dev
pytest test -vv --cov=lagom --cov-report=html
