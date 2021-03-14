# Moving to explicit definitions

The auto-wiring feature of lagom is intended to enable rapid
development of your application in the early stages of development without
having to worry about lagom too much. Once your app has stabilised a little
more you can switch to using more explicit definitions. This makes it clearer
what actually gets loaded and provides a speed boost.

## What do I need to define?
Lagom can be configured to write a log entry every time it uses reflection
to figure out how to build a class.

```python
from lagom import Container
# You can also pass an existing logger instead of setting True
container = Container(log_undefined_deps=True)
```

now in your log output you should see a warning like this for each
dependency that didn't have an explicit definition:

```
Undefined dependency. Using reflection for SomeClass
```

## Setting the definitions

Work through each dependency listed in the logger above and define how
it is constructed. Details on how to do this can be found in the
[getting started section](index.md#defining-construction) but it will look something like
this:

```python
from lagom import Singleton

container[SomeClass] = lambda c: SomeClass(thing=c[AnotherDependency])
container[AnotherDependency] = Singleton(lambda c: AnotherDependency("Some Config"))
```

In this example everything is a lambda so no actual construction will occur
until an object is needed.

## Enforcing definitions
If you want to disable the reflection based construction entirely a
special container called `ExplicitContainer` is provided. This has
the same interface as `Container` but a `DependencyNotDefined` exception
will be raised if construction of an unknown class is requested.