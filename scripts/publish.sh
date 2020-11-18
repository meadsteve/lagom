#!/usr/bin/env bash

set -ex

version=$(pipenv run python lagom/version.py)

git fetch --tags

if git tag --list | grep "$version";
then
    echo "Version already released"
else
    git rev-parse HEAD > lagom/githash.txt
    pipenv run flit publish
    git tag -a "$version" -m "$version"
    git push origin "$version"
fi