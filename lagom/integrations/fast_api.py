"""
FastAPI (https://fastapi.tiangolo.com/)

"""
from contextlib import contextmanager
from typing import TypeVar, Optional, Type, List, Iterator

from fastapi import Depends
from starlette.requests import Request

from ..definitions import PlainInstance
from ..interfaces import ExtendableContainer, ReadableContainer, WriteableContainer
from ..updaters import update_container_singletons

T = TypeVar("T")


class FastApiIntegration:
    """
    Integration between a container and the FastAPI framework.
    Provides a method `Depends` which functions in the same way as
    FastApi `Depends`
    """

    _container: ExtendableContainer

    def __init__(
        self,
        container: ExtendableContainer,
        request_singletons: Optional[List[Type]] = None,
    ):
        self._container = container
        self._request_singletons = request_singletons or []

    def depends(self, dep_type: Type[T]) -> T:
        """Returns a Depends object which FastAPI understands

        :param dep_type:
        :return:
        """

        def _resolver(request: Request):
            request_container = self._container_from_request(request)
            return request_container.resolve(dep_type)

        return Depends(_resolver)

    @contextmanager
    def override_for_test(self) -> Iterator[WriteableContainer]:
        """
        Returns a ContextManager that returns an editiable container
        that will temporaily alter the dependency injection resolution
        of all dependencies bound to this container.

            client = TestClient(app)
            with deps.override_for_test() as test_container:
                # FooService is an external API so mock it during test
                test_container[FooService] = Mock(FooService)
                response = client.get("/")
            assert response.status_code == 200

        :return:
        """
        original = self._container
        new_container_for_test = self._container.clone()
        self._container = new_container_for_test  # type: ignore
        try:
            yield new_container_for_test
        finally:
            self._container = original

    def _container_from_request(self, request: Request) -> ReadableContainer:
        """
        We use the state of the request object to store a single instance of the
        container. Request level singletons can then be defined on this container.
        We only need to construct it once per request.
        :param request:
        :return:
        """
        if (
            not hasattr(request.state, "lagom_request_container")
            or not request.state.lagom_request_container
        ):
            request_container = update_container_singletons(
                self._container, self._request_singletons
            )
            request_container.define(Request, PlainInstance(request))
            request.state.lagom_request_container = request_container

        return request.state.lagom_request_container
