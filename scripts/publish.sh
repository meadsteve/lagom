#!/usr/bin/env bash

set -ex

version=$(pipenv run python lagom/version.py)

git fetch --tags

if git tag --list | grep "v$version";
then
    echo "Version already released"
else
    git rev-parse HEAD > lagom/githash.txt
    pipenv run flit publish
    git tag -a "v$version" -m "v$version"
    git push origin "v$version"
fi