from typing import Any


class Injectable:
    """
    This class is looked for when analysing function signatures for arguments to
    injected
    """

    def __bool__(self):
        """
        If this is used in an if statement it should be falsy as it indicates the dependency
        has not been injected.
        :return:
        """
        return False

    def __copy__(self):
        """
        Much like highlander there can be only one. Injectable
        is a singleton.
        :return:
        """
        return self

    def __deepcopy__(self, memodict=None):
        """
        Much like highlander there can be only one. Injectable
        is a singleton.
        :return:
        """
        return self


# singleton object used to indicate that an argument should be injected
injectable: Any = Injectable()
