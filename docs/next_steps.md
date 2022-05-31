# Next Steps

## Multiple versions of a dependency
It is very likely that at some point you will have multiple instances of a single type, and you'll 
want to control which instance is used when constructing a resource.

Take for example the case of a database. Let's say we have a primary read/write DB and a read replica. 
Both used the `Database` class. Let's also assume we have a `QueryService` which needs the read replica
as a dependency and a `DataWriter` class which needs the primary DB.

```python
class Database:
    pass

class QueryService:
    def __init(self, db: Database):
        pass

class DataWriter:
    def __init(self, db: Database):
        pass
```

There are two main ways of dealing with this in lagom.

### Explicit Definitions
The first is using [explicit definitions](./explicit_definitions.md). In this case we would 
tell the container explicitly how to build each class and which database it needs.

```python
from lagom import Container
container = Container()

container[QueryService] = lambda: QueryService(Database("read-replica-connection-string"))
container[DataWriter] = lambda: DataWriter(Database("primary-connection-string"))
```

This is the simplest and requires the least addition and change to the codebase.

### Subtyping

The second approach to this situation is using subclasses.

```python
# Both these classes will behave exactly the same as Database, but we can now 
# indicate which type we need.
class PrimaryDb(Database):
    pass

class ReadReplica(Database):
    pass

# Then configure them (they could be singletons or use any other lagom definitions)
container[ReadReplica] = lambda: ReadReplica("read-replica-connection-string")
container[PrimaryDb] = lambda: PrimaryDb("primary-connection-string")

# The domain code then needs altering to hint which type of database 
class QueryService:
    def __init(self, db: ReadReplica):
        pass

class DataWriter:
    def __init(self, db: PrimaryDb):
        pass
```

Although this requires extra code and encourages the creation of some extra classes it also communicates
a lot more information. It's explicit and standard python. There's no magic string based logic specific to lagom.
IDEs and other tooling can automatically find every dependency which requires the primary database using
normal static analysis.