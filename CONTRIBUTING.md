# Developing/Contributing

(Taken from: https://lagom-di.readthedocs.io/en/latest/development_of_lagom/)

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

As of version 2 performance is not considered as part of the public interface. The library
added a compilation step which for some platforms gives a speed boost. This may need to be taken away in 
the future to keep the library maintainable. The build process has benchmark tests to help manage the perfomance
in pure python even though this is not part of the public interface.

The `lagom.experimental` module is an exception and does not follow semver. This is a place
for new code to be released. The public interface of this code may change
before it settles down and gets moved out of the experimental module.

## Design Goals
1. Everything should be done by type. No reliance on names/magic strings.
2. The API should expose sensible typing (for use in pycharm/mypy).
3. All domain code should remain unaware of lagom. No special decorators. (Note: This doesn't include the places where lagom is integrated)
4. Usage of the container should encourage code to be testable without monkey patching.
5. Usage of the container should remove the need to depend on global state.
6. Usage of the container should encourage code to embrace type hints and static analysis.
7. Embrace modern python features (3.7 at the time of creation)
