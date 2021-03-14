from typing import List, Type

from lagom.definitions import SingletonWrapper, ConstructionWithoutContainer
from lagom.interfaces import ExtendableContainer, WriteableContainer


def update_container_singletons(container: ExtendableContainer, singletons: List[Type]):
    new_container = container.clone()
    for dep in singletons:
        new_container[dep] = SingletonWrapper(
            ConstructionWithoutContainer(lambda: container.resolve(dep))
        )
    return new_container
