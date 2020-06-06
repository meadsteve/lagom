from ..exceptions import LagomException


class DependencyNotDefined(ValueError, LagomException):
    """The type must be explicitly defined in the container"""

    pass
