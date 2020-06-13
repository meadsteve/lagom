.PHONY: setup setup_pipenv install update test test_mypy test_unit test_format test_doctests test_cookbook_docs test_package_safety publish mutate format enforce_docs
PIPENV_VERBOSITY=-1

setup: setup_pipenv install

setup_pipenv:
	pip install pipenv

install:
	pipenv install --dev --skip-lock

update:
	pipenv update --dev
	pipenv clean
	pipenv run  pip list --outdated

test: test_mypy test_unit enforce_docs test_doctests test_cookbook_docs test_format test_package_safety

test_mypy:
	pipenv run mypy --config-file mypy.ini

test_unit:
	pipenv run pytest tests -vv

test_format:
	pipenv run black --check tests lagom

test_doctests:
	pipenv run  pytest --doctest-modules lagom

test_cookbook_docs:
	PYTHONPATH=./lagom pipenv run python -m pytest docs -vv

test_package_safety:
	pip freeze | safety check --stdin

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
	pipenv run interrogate --ignore-semiprivate --ignore-magic --ignore-private --fail-under 70 -vv lagom