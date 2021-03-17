# Experimental Lagom Features
Lagom provides a module with code which is not yet ready for a stable release.
This code can be considered beta. It works and is tested but the interface
may change based on feedback after usage. 

## Django container
### Overview
The django integration is designed assuming there will be one container per
django app. So the starting point is a new file `dependency_config.py` alongside
your existing `views.py` and `urls.py`.

```python
# dependency_config.py
# a per app dep injection container

container = Container()
container[SomeService] = SomeService("connection details etc")

dependencies = DjangoIntegration(container)
```

and then in `views.py`:

```python
from .dependency_config import dependencies


@dependencies.bind_view
def index(request, dep: SomeService):
    return HttpResponse(f"service says: {dep.get_message()}")

# Or if you prefer class based views

@dependencies.bind_view
class CBVexample(View):
    def get(self, request, dep: SomeService):
        return HttpResponse(f"service says: {dep.get_message()}")
```

These views can then be used as normal in the url definitions:

```python
from django.urls import path

from . import views


urlpatterns = [
    path('function_view', views.index, name='func_view'),
    path('class_based', views.CBVexample.as_view(), name='cbv'),
]
```

### Django models
Django models are usually referenced statically. Some extra code is provided to
make these injectable instead.

When defining the container, list all the models that should be available via the container:

```python
# dependency_config.py
# a per app dep injection container
from .models import Question

container = Container()

dependencies = DjangoIntegration(container, models=[Question])
```

Now in the views you can use:

```python
from django.http import HttpResponse
from django.utils import timezone
from lagom.experimental.integrations.django import DjangoModel

from .dependency_config import dependencies
from .models import Question


@dependencies.bind_view
def new_question(request, questions: DjangoModel[Question]):
    new_question = questions.new(question_text="What's next?", pub_date=timezone.now())
    new_question.save()
    return HttpResponse(f"new question created")


@dependencies.bind_view
def question_count(request, questions: DjangoModel[Question]):
    count = questions.objects.all().count()
    return HttpResponse(f"{count} questions are in the DB")
```

in these examples `questions.objects` is the same as calling `Question.objects`
and `questions.new()` is the same as `Question()`. The benefit now though is the
view function has no global state dependency. We can call the view functions directly 
in tests passing in whatever we want to `questions`. This enables the dependency on 
the DB to be switched out without any monkey patching at all.

### Django settings
A class `DjangoSettings` is provided. When bound to the container
this will automatically get injected with the settings of your app.

```python
# settings.py
SECRET_MSG = "hello world"

# views.py
@dependencies.bind_view
def show_secret_message(request, settings: DjangoSettings = injectable):
    return HttpResponse(f"your secret message is: {settings.SECRET_MSG}")
```

### Injecting Request
If any argument type hints on `HttpRequest` then the django
object for the current request will be injected.

```python
# some_services.py
class DataStoreForRequest:
    def __init__(self, request: HttpRequest, db: SomeDb):
        # Now we can use anything generic we want from the request
        pass

# views.py
@dependencies.bind_view
def question_count(request, store: DataStoreForRequest = injectable):
    # The `store` here was constructed with the correct request object
    return HttpResponse(f"Done")
```

## Click
An integration layer is provided which wraps click's decorators and
wraps the function with lagom injection.

```python
container = Container()
cli = ClickIntegration(container)


@cli.command()
@cli.argument("name")
def call_the_thing(input, service: SomeServiceClass = injectable):
    service.do_thing(input)
```

to enable testing without monkey patching the integration 
ends the `Command` class to retain a reference to the function
as `plain_function`:

```python
def test_something():
    mock_service = mock.create_autospec(SomeServiceClass)
    call_the_thing.plain_function("something", mock_io)
    mock_service.do_thing.assert_called_once_with("something")
```

in addition, for testing echoed output a `ClickIO` class
is automatically made available:

```python
@cli.command()
@cli.argument("name")
def hello(name, io: ClickIO = injectable):
    io.echo(f"Hello {name}")
```