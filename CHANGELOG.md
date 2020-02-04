# Changelog

## 0.5.2 (2020-02-04)

### Enhancements
* Async defs are now bindable.

### Bug fixes
None

### Backwards incompatible changes
None

## 0.5.1 (2020-02-04)

### Enhancements
* The result of binding to a container will now pass `inspect.is_function`

### Bug fixes
None

### Backwards incompatible changes
None

## 0.5.0 (2020-02-04)

### Enhancements
* Singleton bool for `dependency_definition` decorator
* Invocation level singletons are now lazily loaded

### Bug fixes
None

### Backwards incompatible changes
* Invocation level singletons are now lazily loaded

## 0.4.1 (2020-02-03)

### Enhancements
* Invocation level caching for decorated functions

### Bug fixes
None

### Backwards incompatible changes
None

## 0.4.0 (2020-02-03)

### Enhancements
* Added `dependency_definition` decorator to handle log construction logic
* Error is raised if the same typed is defined twice.

### Bug fixes
* All container instances no longer share the same state.

### Backwards incompatible changes
* It's now no longer possible to overwrite existing definitions.

## 0.3.2 (2019-08-18)

### Enhancements
* Simplified decorator for partial functions that now allows 
positional argument calls.

### Bug fixes
None

### Backwards incompatible changes
None

## 0.3.1 (2019-07-10)

### Enhancements
* Better documentation and testing for partially bound functions.

### Bug fixes
None

### Backwards incompatible changes
None

## 0.3.0 (2019-07-01)

### Enhancements
* Support for generators as partially bound functions

### Bug fixes
* Fixed handling around partial functions.

### Backwards incompatible changes
None

## 0.2.0 (2019-06-06)

### Enhancements
- Arity 1 constructor functions allowed and are passed the container.

### Bug fixes
None

### Backwards incompatible changes
None