# Framework Integrations
In addition to the binding decorators lagom provides a number of integrations to
popular web frameworks.

## [Starlette](https://www.starlette.io/)
To make integration with starlette simpler a special container is provided
that can generate starlette routes.

Starlette endpoints are defined in the normal way. Any extra arguments are
then provided by the container:
```python
async def homepage(request, db: DBConnection = injectable):
    user = db.fetch_data_for_user(request.user)
    return PlainTextResponse(f"Hello {user.name}")


container = StarletteContainer()
container[DBConnection] = DB("DSN_CONNECTION_GOES_HERE")


routes = [
    # This function takes the same arguments as starlette.routing.Route
    container.route("/", endpoint=homepage),
]

app = Starlette(routes=routes)
```

## [FastAPI](https://fastapi.tiangolo.com/)
FastAPI already provides a method for dependency injection however
if you'd like to use lagom instead a special container is provided.

Calling the method `.depends` will provide a dependency in the format
that FastAPI expects:

```python
container = FastApiContainer()
container[DBConnection] = DB("DSN_CONNECTION_GOES_HERE")

app = FastAPI()

@app.get("/")
async def homepage(request, db = container.depends(DBConnection)):
    user = db.fetch_data_for_user(request.user)
    return PlainTextResponse(f"Hello {user.name}")

```

## [Flask API](https://www.flaskapi.org/)
A special container is provided for flask. It takes the flask app
then provides a wrapped `route` decorator to use:

```python
app = Flask(__name__)
container = FlaskContainer(app)
container[Database] = Singleton(lambda: Database("connection details"))


@container.route("/save_it/<string:thing_to_save>", methods=['POST'])
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
