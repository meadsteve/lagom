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


**Limitation warning** This integration currently doesn't support invocation level singletons like the other frameworks do. If you
need this feature you may want to use either the `bind_to_container` or `magic_bind_to_container` decorators instead.

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

## [Django](https://www.djangoproject.com/)
A django integration is currently under beta in the experimental module.
See documentation here: [Django Integration Docs](experimental.md#django-container)
