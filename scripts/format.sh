#!/usr/bin/env bash
set -ex
export PIPENV_VERBOSITY=-1

pipenv run black test lagom