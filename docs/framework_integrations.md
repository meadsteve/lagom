# Framework Integrations
In addition to the binding decorators lagom provides a number of integrations to
popular web frameworks.

## [Starlette](https://www.starlette.io/)
To make integration with starlette simpler an integration is provided
that can generate starlette routes.

Starlette endpoints are defined in the normal way. Any extra arguments are
then provided by the container:
```python
async def homepage(request, db: DBConnection = injectable):
    user = db.fetch_data_for_user(request.user)
    return PlainTextResponse(f"Hello {user.name}")


container = Container()
container[DBConnection] = DB("DSN_CONNECTION_GOES_HERE")

with_deps = StarletteIntegration(container) 

routes = [
    # This function takes the same arguments as starlette.routing.Route
    with_deps.route("/", endpoint=homepage),
]

app = Starlette(routes=routes)
```

## [FastAPI](https://fastapi.tiangolo.com/)
FastAPI already provides a method for dependency injection however
if you'd like to use lagom instead an integration is provided.

Calling the method `.depends` will provide a dependency in the format
that FastAPI expects:

```python
container = Container()
container[DBConnection] = DB("DSN_CONNECTION_GOES_HERE")

app = FastAPI()
deps = FastApiIntegration(container)

@app.get("/")
async def homepage(request, db = deps.depends(DBConnection)):
    user = db.fetch_data_for_user(request.user)
    return PlainTextResponse(f"Hello {user.name}")

```

### Access the request
The fast api automatically binds the active request to the container.
This enables the following definitions:

```python
from starlette.requests import Request

class SomeExtendedRequest:
    def __init(self, req: Request, db: Database):
        pass
```

Each time SomeExtendedRequest is created the correct `Request`
object will be passed in.

### Swapping for mocks when using the test client
Lagom encourages testing with dependencies manually passed to the code under test. 
However, when testing using the test client dependencies will be constructed using
the lagom container. For this reason you may want to swap out certain dependencies.
The fastapi integration has a method `override_for_test` which returns a ContextManager
that can temporarily edit the dependency injection container.

```python
def test_something():
    client = TestClient(app)
    with deps.override_for_test() as test_container:
        # FooService is an external API so mock it during test
        test_container[FooService] = Mock(FooService)
        response = client.get("/")
        
    assert response.status_code == 200
```

### Request level singletons
When constructing the integration a list of types can be passed
for request level singletons. Each of these types will only be constructed
once per request:

```python
deps = FastApiIntegration(container, request_singletons=[SomeClass])
```

### Request level singletons - with clean up
In addition to the request level singletons it's also possible to define types that
are a singleton over the lifetime of the request and call some clean up code once
the request has been handled. This is implemented using regular python context managers.

When setting up the integration a list of types using context managers can be provided.

```python
deps = FastApiIntegration(container, request_context_singletons=[SomeClass])
```

When a dependency of type `SomeClass` is required lagom looks for `ContextManager[SomeClass]`.

This can be defined in the container in two ways. Either with a generator and the context
manager decorator:

```python
@context_dependency_definition(container)
def my_constructor() -> Iterator[SomeResource]:
    try:
        yield SomeResource()
    finally:
        # TODO: do some tidy up now the request has finished
        pass
```

Or alternatively if a `ContextManager` already exists for the class this can be used:

```python
class SomeResourceManager:
    def __enter__(self):
        return SomeResource()
    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: do some tidy up now the request has finished
        pass

container[ContextManager[SomeResource]] = SomeResourceManager
```

## [Flask API](https://www.flaskapi.org/)
An integration is provided for flask. It takes the flask app
and a container then provides a wrapped `route` decorator to use:

```python
app = Flask(__name__)
container[Database] = Singleton(lambda: Database("connection details"))

app_with_deps = FlaskIntegration(app, container)

@app_with_deps.route("/save_it/<string:thing_to_save>", methods=['POST'])
def save_to_db(thing_to_save, db: Database = injectable):
    db.save(thing_to_save)
    return 'saved'

```
(taken from https://github.com/meadsteve/lagom-flask-example/)

The decorator leaves the original function unaltered so it can be
used directly in tests.

### Flask Blueprints
Experimental support is provided for flask blueprints.
See documentation here: [Flask blueprint Docs](experimental.md#flask-blueprints)


## [Django](https://www.djangoproject.com/)
A django integration is currently under beta in the experimental module.
See documentation here: [Django Integration Docs](experimental.md#django-container)

## [Click](https://click.palletsprojects.com/)
A click integration is currently under beta in the experimental module.
See documentation here: [Click Integration Docs]()(experimental.md#click)
