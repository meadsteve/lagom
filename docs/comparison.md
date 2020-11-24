# Comparison to other frameworks

Here is how Lagom compares to other frameworks on a few key issues that
lagom focuses on. The primary goal of Lagom was to provide type based 
auto wiring. 

| Framework                                                               | Supports name based auto wiring | Supports type based auto wiring | Supports Async | Avoids alteration of domain code | Exports useful types |
|-------------------------------------------------------------------------|---------------------------------|---------------------------------|----------------|----------------------------------|----------------------|
| Lagom                                                                   |                                 | ✔                               | ✔              | ✔                                | ✔                    |
| [Pinject](https://github.com/google/pinject)                            | ✔                               |                                 |                | ✔                                |                      |
| [Injector](https://github.com/alecthomas/injector)                      |                                 |                                 |                | (✔) requires subtle alteration   | ✔                    |
| [Dependency Injector](https://python-dependency-injector.ets-labs.org/) |                                 |                                 | ✔              | ✔                                | ✔                    |

## Points of comparison

### Supports name based auto wiring
Does the framework support automatic injection of dependencies base on name.
For example if pinject sees an argument called some_dep and a class SomeDep it
will automatically inject it.

### Supports type based auto wiring
Does the framework support automatic injection of dependencies based on type.
For example if a constructor needs an instance of MyDep can one be automatically
constructed without configuration.

### Supports Async
Does it work with async defs.

### Avoids alteration of domain code
Can code be configured either automatically or configured externally without
apply special decorators or makers to class constructors.

### Exports useful types
Do the functions of the framework export type information useable by mypy.

## Contributions
This list is incomplete. Corrections and clarifications are more than welcome.