.PHONY: setup setup_pipenv install test test_mypy test_unit test_format test_doctests publish mutate format enforce_docs
PIPENV_VERBOSITY=-1

setup: setup_pipenv install

setup_pipenv:
	pip install pipenv

install:
	pipenv install --dev

test: test_mypy test_unit enforce_docs test_doctests test_format

test_mypy:
	pipenv run mypy --ignore-missing-imports --strict-optional --check-untyped-defs tests lagom

test_unit:
	pipenv run python -m hammett -x

test_format:
	pipenv run black --check tests lagom

test_doctests:
	pipenv run  pytest --doctest-modules lagom

publish:
	./scripts/publish.sh

mutate:
	pipenv run mutmut run
	pipenv run mutmut html
	xdg-open ./html/index.html

coverage:
	pipenv run pytest tests -vv --cov=lagom --cov-report=html

format:
	pipenv run black tests lagom

enforce_docs:
	pipenv run interrogate --ignore-semiprivate --ignore-magic --ignore-private --fail-under 75 -vv lagom