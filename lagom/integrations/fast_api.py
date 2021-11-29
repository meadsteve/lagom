"""
FastAPI (https://fastapi.tiangolo.com/)

"""
from contextlib import contextmanager
from typing import TypeVar, Optional, Type, List, Iterator

from fastapi import Depends
from starlette.requests import Request

from ..context_based import ContextContainer
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
        request_context_singletons: Optional[List[Type]] = None,
    ):
        self._container = container
        self._request_singletons = request_singletons or []
        self._request_context_singletons = request_context_singletons or []

    def depends(self, dep_type: Type[T]) -> T:
        """Returns a Depends object which FastAPI understands

        :param dep_type:
        :return:
        """

        def _container_from_request(request: Request) -> Iterator[ReadableContainer]:
            """
            We use the state of the request object to store a single instance of the
            container. Request level singletons can then be defined on this container.
            We only need to construct it once per request. This container is also
            wrapped in a ContextContainer which is yielded to fastapi and can call
            the __exit__ methods of any context managers used constructing objects
            during the requests lifetime.
            """
            if (
                not hasattr(request.state, "lagom_request_container")
                or not request.state.lagom_request_container
            ):
                request.state.lagom_request_container = self._build_container(request)
                with request.state.lagom_request_container:
                    yield request.state.lagom_request_container
            else:
                # No need to "with" as it's already been done once and this
                # will handle the exit
                yield request.state.lagom_request_container

        def _resolver(
            container: ExtendableContainer = Depends(_container_from_request),
        ):
            return container.resolve(dep_type)

        return Depends(_resolver)

    @contextmanager
    def override_for_test(self) -> Iterator[WriteableContainer]:
        """
        Returns a ContextManager that returns an editiable container
        that will temporarily alter the dependency injection resolution
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

    def _build_container(self, request: Request) -> ContextContainer:
        request_container = update_container_singletons(
            self._container, self._request_singletons
        )
        request_container.define(Request, PlainInstance(request))
        return ContextContainer(
            request_container,
            context_types=[],
            context_singletons=self._request_context_singletons,
        )
