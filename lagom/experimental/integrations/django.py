"""
Django integration.

Usage:


```
#views.py

from .dependency_config import container


@container.bind_view
def index(request, dep: SomeDep, questions: DjangoModel[Question]):
    new_question = questions.new(question_text="What's next?", pub_date=timezone.now())
    new_question.save()
    return HttpResponse(f"plain old function: {dep.message} with {questions.objects.all().count()} questions")


@container.bind_view
class CBVexample(View):
    def get(self, request, dep: SomeDep):
        return HttpResponse(f"Class based: {dep.message}")

```

```
# dependency_config.py
# a per app dep injection container

# Lists all models that should be available
container = DjangoContainer(models=[Question], request_singletons= [SomeCache])
container[SomeService] = SomeService("connection details etc")
```

"""
import types
from typing import TypeVar, Generic, List, Type, Optional

from django.db.models import Manager, Model
from django.views import View

from ..container import Container

M = TypeVar("M", bound=Model)


class _Managers(Generic[M]):
    """
    Wraps around a django model and provides access to the class properties.
    The intention is that all the Manager objects can be accessed via this.
    """

    def __init__(self, model: Type[M]):
        self.model = model

    def __getattr__(self, item) -> Manager:
        if not hasattr(self.model, item):
            raise KeyError(
                f"Django model {self.model.__name__} does not define a property {item}"
            )
        return getattr(self.model, item)


class DjangoModel(Generic[M]):
    """Wrapper around a django model for injection hinting
    Usage:
        container = DjangoContainer(models=[Question])

        @bind_to_container(container)
        def load_first_question(questions: DjangoModel[Question]):
            return questions.objects.first()

    """

    model: Type[M]
    managers: _Managers[M]

    def __init__(self, model: Type[M]):
        """

        :param model: The django model class
        """
        self.model = model
        self.managers = _Managers(self.model)

    @property
    def objects(self) -> Manager:
        """ Equivalent to MyModel.objects

        :return:
        """
        return self.managers.objects

    def new(self, **kwargs) -> M:
        """ Equivalent to MyModel(**kwargs)

        :param kwargs:
        :return:
        """
        return self.model(**kwargs)


class DjangoContainer(Container):
    """
    Same behaviour as the basic container bug provides a view method which
    should be used as a decorator to wrap views. Once wrapped
    the view can reference dependencies which will be auto-wired.
    """

    _request_singletons: List[Type]

    def __init__(
        self,
        models: Optional[List[Type[Model]]] = None,
        request_singletons: Optional[List[Type]] = None,
        container: Container = None,
    ):
        """
        :param models: List of models which should be available for injection
        :param request_singletons:
        :param container:
        """
        super().__init__(container)
        self._request_singletons = request_singletons or []
        for model in models or []:
            self.define(DjangoModel[model], DjangoModel(model))  # type: ignore

    def bind_view(self, view):
        """
        Takes either a plain function view or a class based view
        binds it to the container then returns something that can
        be used in a django url definition
        :param view:
        :return:
        """
        if isinstance(view, types.FunctionType):
            # Plain old function can be bound to the container
            return self.partial(view, shared=self._request_singletons)
        return self._bind_view_methods_to_container(view)

    def _bind_view_methods_to_container(self, view):
        for method in View.http_method_names:
            if hasattr(view, method):
                setattr(
                    view,
                    method,
                    self.partial(
                        getattr(view, method), shared=self._request_singletons
                    ),
                )
        return view
