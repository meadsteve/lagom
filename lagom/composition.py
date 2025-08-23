from itertools import chain
from typing import TypeVar, Type, Optional, Set, Tuple, Collection, Sequence

from .container import Container
from .interfaces import DefinitionsSource, SpecialDepDefinition

X = TypeVar("X")


def compose(*args: DefinitionsSource) -> Container:
    combined_sources = _SourceList(*args)
    _assert_unique_dependencies(args)

    return Container(container=combined_sources)


class _SourceList(DefinitionsSource):
    """
    Combines multiple `DefinitionsSource`s which are accessed in order
    """

    sources: Collection[DefinitionsSource]

    def __init__(self, *args: DefinitionsSource):
        self.sources = args

    def get_definition(self, dep_type: Type[X]) -> Optional[SpecialDepDefinition[X]]:
        """
        For a supplied type returns the definition of how to build that type.
        If unknown None is returned
        :param dep_type:
        """
        for source in self.sources:
            definition = source.get_definition(dep_type)
            if definition is not None:
                return definition
        return None

    @property
    def defined_types(self) -> Set[Type]:
        """
        The list of types that have been explicitly defined
        :return:
        """
        return set(chain.from_iterable(s.defined_types for s in self.sources))


def _assert_unique_dependencies(definition_sources: Sequence[DefinitionsSource]):
    for first in range(0, len(definition_sources)):
        for second in range(first + 1, len(definition_sources)):
            for dep in definition_sources[first].defined_types:
                if (
                    dep.__name__ != "ContainerDebugInfo"
                    and dep in definition_sources[second].defined_types
                ):
                    raise ValueError(f"Dep {dep} defined in {first} and {second}")
