"""
FastAPI (https://fastapi.tiangolo.com/)

"""
import typing

from fastapi import Depends
from starlette.requests import Request

from ..definitions import PlainInstance
from ..interfaces import ExtendableContainer

T = typing.TypeVar("T")


class FastApiIntegration:
    """
    Integration between a container and the FastAPI framework.
    Provides a method `Depends` which functions in the same way as
    FastApi `Depends`
    """

    _container: ExtendableContainer

    def __init__(self, container: ExtendableContainer):
        self._container = container

    def depends(self, dep_type: typing.Type[T]) -> T:
        """Returns a Depends object which FastAPI understands

        :param dep_type:
        :return:
        """

        def _resolver(request: Request):
            request_container = self._container.clone()
            request_container.define(Request, PlainInstance(request))
            return request_container.resolve(dep_type)

        return Depends(_resolver)
