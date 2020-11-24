# Developing/Contributing

Contributions and PRS are welcome. For any large changes please open
an issue to discuss first. All PRs should pass the tests, type checking
and styling. To get development setup locally:
```bash
make install # sets up the pipenv virtualenv
```
then 
```bash
make format # To format the code
make test # To make sure the build will pass
```

## Versioning - Semver
This library follows semver as closely as possible (mistakes may occur).
The public interface is considered to be everything in `lagom.__all__`. Anything
else is considered an internal implementation detail.

The `lagom.experimental` module is an exception to this. This is a place
for new code to be released. The public interface of this code may change
before it settles down and gets moved out of the experimental module.

## Design Goals
* The API should expose sensible typing (for use in pycharm/mypy)
* Everything should be done by type. No reliance on names.
* All domain code should remain unmodified. No special decorators.
* Usage of the container should encourage code to be testable without monkey patching.
* Usage of the container should remove the need to depend on global state.
* Embrace modern python features (3.7 at the time of creation)
