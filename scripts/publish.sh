#!/usr/bin/env bash

set -ex

# First check for any issues that need to be resolved before releasing
blocking_issues=$(curl 'https://api.github.com/repos/meadsteve/lagom/issues?labels=release_blocker'|jq length)

if [[ "$blocking_issues" -gt 0 ]]; then
  echo "There are $blocking_issues issues that must be fixed before release."
  exit 1
fi

# Next check that we've not already released this version
version=$(pipenv run python lagom/version.py)

git fetch --tags

if git tag --list | grep "$version\$";
then
    echo "Version already released"
    exit 2
else
    git rev-parse HEAD > lagom/githash.txt
    pipenv run flit publish
    git tag -a "$version" -m "$version"
    git push origin "$version"
    exit 0
fi