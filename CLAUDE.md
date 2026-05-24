# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make install          # set up pipenv virtualenv with dev dependencies
make test             # run all checks: mypy, unit tests, doctest, format, doc coverage
make test_unit        # run unit tests only (excluding benchmarks)
make test_mypy        # run mypy type checking
make test_doctests    # run doctests embedded in source modules
make test_format      # check formatting with black
make format           # auto-format with black
make coverage         # generate HTML coverage report
make benchmark        # run benchmark tests
```

To run a single test file or test:
```bash
pipenv run pytest tests/path/to/test_file.py -vv
pipenv run pytest tests/path/to/test_file.py::test_name -vv
```

Doc coverage is enforced at 65%+ (via `interrogate`). New public API must have docstrings.

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
