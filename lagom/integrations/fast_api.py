import typing

from fastapi import Depends

from .. import Container

T = typing.TypeVar("T")


class FastApiContainer(Container):
    def depends(self, dep_type: typing.Type[T]) -> T:
        return Depends(lambda: self.resolve(dep_type))
