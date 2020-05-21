# Changelog

## 0.9.2 (2020-05-21)
### Enhancements
* Container has property which exposes list of defined types. 
* The experimental django integration now provides access to custom `Manager` objects.

### Bug fixes
None

### Backwards incompatible changes
None

## 0.9.1 (2020-05-21)
### Enhancements
* Experimental explict container added. Requires a definition for every dependency (implements #38)

### Bug fixes
* Extracted bare exception into the namespaced exceptions (fixes #39)

### Backwards incompatible changes
None

## 0.9.0 (2020-05-15)
### Enhancements
None

### Bug fixes
* Bound functions now take supplied arguments over container generated ones. 

### Backwards incompatible changes
* The argument order on Container.partial has changed.
* Bound functions now take supplied arguments over container generated ones.

## 0.8.0 (2020-05-13)
### Enhancements
* Optional types are now handled. If they can be built they are. If not they are omitted.
* Add experimental django integration. 

### Bug fixes
* Error messages when a generic type couldn't be built in 3.6 now contain the full type name.

### Backwards incompatible changes
None

## 0.7.1 (2020-05-05)
### Enhancements
* Added an experimental way of defining functions as injected dependencies. This may not be kept and changes will
not be considered breaking.

### Bug fixes
None

### Backwards incompatible changes
None

## 0.7.0 (2020-05-03)

### Enhancements
* Tidied up logic around singletons, aliases and constructors.
* Documentation and doc testing of more methods

### Bug fixes
None

### Backwards incompatible changes
* Subtle changes to lots of container interfaces. No "normal" code should require changes.

## 0.6.7 (2020-02-07)

### Enhancements
* Request level singletons are enabled for starlette & flask integrations.

### Bug fixes
* Fix bug that meant singleton construction couldn't reference container.

### Backwards incompatible changes
None

## 0.6.6 (2020-02-06)

### Enhancements
* Basic introspection properties are kept in bound functions

### Bug fixes
None

### Backwards incompatible changes
None

## 0.6.5 (2020-02-06)

### Enhancements
* Flask integration provided

### Bug fixes
None

### Backwards incompatible changes
None

## 0.6.4 (2020-02-04)

### Enhancements
* Added explicit support for python 3.6 (required no actual code changes)

### Bug fixes
None

### Backwards incompatible changes
None

## 0.6.3 (2020-02-04)

### Enhancements
* Provide extended container that integrates well with fastapi.

### Bug fixes
None

### Backwards incompatible changes
None

## 0.6.2 (2020-02-04)

### Enhancements
* Better error messages if a List[X] like type can't be fufilled.

### Bug fixes
None

### Backwards incompatible changes
None

## 0.6.1 (2020-02-04)

### Enhancements
* Provide extended container that integrates well with starlette.

### Bug fixes
None

### Backwards incompatible changes
None

## 0.6.0 (2020-02-04)

### Enhancements
* Expose a richer type definition when registering dependencies. This is a
design goal after all.

### Bug fixes
None

### Backwards incompatible changes
* The strong type definition *could* cause errors in existing code.

## 0.5.4 (2020-02-04)

### Enhancements
None

### Bug fixes
* Fix bug causing bound functions to resolve dependencies at definition time.

### Backwards incompatible changes
None

## 0.5.5 (2020-02-04)

### Enhancements
* Better error handling

### Bug fixes
None

### Backwards incompatible changes
None

## 0.5.3 (2020-02-04)

### Enhancements
None

### Bug fixes
* Fix async binding with invocation level singletons so that they pass iscoroutinefunction

### Backwards incompatible changes
None

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