"""
FastAPI (https://fastapi.tiangolo.com/)

"""
import typing

from fastapi import Depends

from .. import Container

T = typing.TypeVar("T")


class FastApiContainer(Container):
    """
    Basic container plus a depends method which is drop in compatible with
    FastApi `Depends`
    """

    def depends(self, dep_type: typing.Type[T]) -> T:
        """Returns a Depends object which FastAPI understands

        :param dep_type:
        :return:
        """
        return Depends(lambda: self.resolve(dep_type))
