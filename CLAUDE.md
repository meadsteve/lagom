# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Always use the `make` targets below rather than constructing bespoke `pipenv run …` or `python -m …` invocations. Default to `make test` for verification rather than chaining individual `make test_*` targets — `make test` already runs mypy, unit tests, doctests, formatting check and doc coverage in one go.

```bash
make install          # set up pipenv virtualenv with dev dependencies
make setup_pipenv     # install / upgrade pipenv itself — run this first if `make install` fails
make test             # full verification: mypy, unit tests, doctests, format, doc coverage
make test_unit        # unit tests only (excluding benchmarks)
make test_mypy        # mypy type checking
make test_doctests    # doctests embedded in source modules
make test_format      # check formatting with black
make format           # auto-format with black
make coverage         # HTML coverage report
make benchmark        # benchmark tests
```

To run a single test file or test:
```bash
pipenv run pytest tests/path/to/test_file.py -vv
pipenv run pytest tests/path/to/test_file.py::test_name -vv
```

Doc coverage is enforced at 65%+ (via `interrogate`) over the **whole project**, so the headroom above 65% is small. Adding a new module, class, or public method without docstrings will silently eat that buffer and break `make test`. Add docstrings in the same commit as the new code.

### When something is broken, fix the root cause — don't work around it

If a `make` target fails or a tool misbehaves, **read the Makefile end-to-end first** — there's often a sibling target that fixes the failure mode (e.g. `make setup_pipenv` for a broken pipenv). Then **stop and ask the user before bypassing the failing tool**. Do not silently swap in equivalent commands (`python -m pytest` instead of `make test_unit`, `pip install` instead of `pipenv install`, hardcoded venv paths, custom shell pipelines). Diagnose the failure, then propose the real fix in the project — usually a Makefile edit, dependency bump, or pinned version — and only proceed once the user has approved. Workarounds hide problems and force the user to re-approve unfamiliar commands every session; root-cause fixes stick.

Common gotcha: if `make install` fails with `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'`, the system `pipenv` is too old for Python 3.12 — run `make setup_pipenv` to upgrade it (the Makefile pins the right version), then retry `make install`. This is the fix, not a workaround.

### Keep CHANGELOG.md current

Any user-visible change (new feature, behaviour change, bug fix, perf improvement, breaking change) gets an entry under the `## Unreleased` section of `CHANGELOG.md` in the same change-set. Use the existing section headings (`### Enhancements`, `### Bug Fixes`, `### Backwards incompatible changes`). If there is no `## Unreleased` section yet, add one above the latest released version. Pure refactors, docs-only edits, and test-only changes do not need an entry.

### Branch hygiene before push

Before marking a PR ready (or pushing a branch you expect to be reviewed), check for `WIP`, `HACKING`, `fixup`, or `remove some junk` style commits and squash them into the logical change they belong to. Reviewers shouldn't have to read scaffolding commits. If you see a string of these on a branch you're handed, flag it to the user and offer to clean up the history before doing further work.

### Benchmarking workflow

`make benchmark` runs `pytest-benchmark` against `tests/benchmarking/`. To validate a perf-oriented change, save a baseline on `master` and compare:

```bash
git checkout master && pipenv run pytest tests -m "benchmarking" --benchmark-save=master
git checkout <branch> && pipenv run pytest tests -m "benchmarking" --benchmark-compare=0001
```

Saved runs live in `.benchmarks/`. `--benchmark-compare-fail=mean:50%` in the `make benchmark` target already fails the run on a 50% regression — use that flag locally too if you want CI-style guard rails.

## Architecture

Lagom is a **type-based dependency injection container**. The core idea: everything is resolved by Python type, not by name or string magic. No domain code should be aware of lagom — it's only wired up at the composition root.

### Public API

Semver applies only to symbols exported in `lagom.__all__` (`lagom/__init__.py`). Everything else is internal. `lagom.experimental` is explicitly **not** semver-stable — it's a staging area before things graduate to the main API.

### Core resolution flow

1. `Container.resolve` (also callable via `container[SomeType]`) is the entry point.
2. First checks `_registered_types` (explicit definitions), walking up to `_parent_definitions` (another container) if not found.
3. If nothing is registered, falls back to **reflection build**: inspects `__init__` type hints via `CachingReflector` (`lagom/util/reflection.py`) and recursively resolves sub-dependencies.
4. Primitive types (`str`, `int`, `float`, etc.) in `UNRESOLVABLE_TYPES` are never auto-wired.

### Key types and where they live

| Concept | Location |
|---|---|
| Interfaces/ABCs | `lagom/interfaces.py` — `ReadableContainer`, `WriteableContainer`, `SpecialDepDefinition`, `TypeResolver` |
| Main containers | `lagom/container.py` — `Container` (auto-wiring), `ExplicitContainer` (must define everything) |
| Context-managed deps | `lagom/context_based.py` — `ContextContainer` (uses Python context managers for dependency lifecycle) |
| Dependency definitions | `lagom/definitions.py` — `Singleton`, `Alias`, `PlainInstance`, `ConstructionWithContainer`, async/yield variants |
| Decorators | `lagom/decorators.py` — `bind_to_container`, `magic_bind_to_container`, `dependency_definition` |
| Framework integrations | `lagom/integrations/` — FastAPI, Flask, Starlette |
| Experimental integrations | `lagom/experimental/integrations/` — Click, Django, Flask |

### Definition normalisation

`definitions.normalise()` is the central dispatch that converts a `TypeResolver` (which can be a class, lambda, instance, coroutine function, or `SpecialDepDefinition`) into a concrete `SpecialDepDefinition`. The arity of callables (0 or 1 argument) determines whether a container is passed in at resolution time.

### Container cloning and singletons

`Container.clone()` creates a child container that inherits parent definitions via `_parent_definitions`. `temporary_singletons()` and `ContextContainer` both use cloning to create per-invocation scopes without mutating the shared container. `SingletonWrapper` uses a `threading.Lock` for thread safety.

### Compilation

`lagom/compilaton.py` (note: intentional typo in filename — search for "compilaton" not "compilation") provides `mypyc_attr`, imported from `mypy_extensions` and falling back to a no-op decorator when that package is not installed. Classes decorated with `@mypyc_attr(allow_interpreted_subclasses=True)` can still be subclassed in interpreted code.

### Design constraints

- No domain code should import or reference lagom types.
- Type hints drive all resolution — if `__init__` lacks type hints, lagom can't auto-wire.
- `injectable` marker (`lagom/markers.py`) is used in `partial()` to mark arguments for injection without requiring they be the only args.
- `magic_partial()` infers all injectable args from type hints; `partial()` only injects args marked with `injectable`.
