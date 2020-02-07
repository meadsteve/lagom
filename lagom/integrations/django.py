import types
from typing import TypeVar, Generic, List, Type, Optional

from django.db.models import Manager, Model
from django.views import View

from lagom import Container

M = TypeVar("M", bound=Model)


class DjangoModel(Generic[M]):
    model: Type[M]
    objects: Manager

    def __init__(self, model: Type[M]):
        self.model = model
        self.objects = model.objects  # type: ignore

    def new(self, **kwargs) -> M:
        return self.model(**kwargs)


class DjangoContainer(Container):
    def __init__(
        self, models: Optional[List[Type[Model]]] = None, container: Container = None
    ):
        super().__init__(container)
        for model in models or []:
            self[DjangoModel[model]] = lambda: DjangoModel(model)  # type: ignore

    def view(self, view):
        if isinstance(view, types.FunctionType):
            # Plain old function can be bound to the container
            return self.partial(view)
        if issubclass(view, View):
            # For django class based view each method needs to be bound
            # to the container
            self._bind_view_methods_to_container(view)
            return view.as_view()
        raise SyntaxError(f"Container doesn't know how to handle type {type(view)}")

    def _bind_view_methods_to_container(self, view):
        for method in View.http_method_names:
            if hasattr(view, method):
                setattr(view, method, self.partial(getattr(view, method)))
