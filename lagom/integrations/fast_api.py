"""
FastAPI (https://fastapi.tiangolo.com/)

"""
from typing import TypeVar, Optional, Type, List

from fastapi import Depends
from starlette.requests import Request

from ..definitions import PlainInstance
from ..interfaces import ExtendableContainer, ReadableContainer
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
