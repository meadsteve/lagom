#!/usr/bin/env bash

pipenv run mutmut run
pipenv run mutmut html
xdg-open ./html/index.html