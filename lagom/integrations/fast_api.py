"""
FastAPI (https://fastapi.tiangolo.com/)

"""
import typing

from fastapi import Depends

from ..interfaces import ReadableContainer

T = typing.TypeVar("T")


class FastApiIntegration:
    """
    Integration between a container and the FastAPI framework.
    Provides a method `Depends` which functions in the same way as
    FastApi `Depends`
    """

    _container: ReadableContainer

    def __init__(self, container: ReadableContainer):
        self._container = container

    def depends(self, dep_type: typing.Type[T]) -> T:
        """Returns a Depends object which FastAPI understands

        :param dep_type:
        :return:
        """
        return Depends(lambda: self._container.resolve(dep_type))
