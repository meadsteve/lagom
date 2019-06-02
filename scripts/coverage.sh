#!/usr/bin/env bash
set -ex
export PIPENV_VERBOSITY=-1
pytest test -vv --cov=lagom --cov-report=html
