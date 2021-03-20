from typing import Any

from lagom.exceptions import InjectableNotResolved


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

    def __getattr__(self, item: str):
        """
        injectable should never have it's attributes referenced or a method call.
        This normally indicates that the default injectable value hasn't been
        handled by lagom - which is likely a function missing a bind decorator.
        """
        # Ignore dunder methods as it's likely some decorator magic and
        # it doesn't really help to raise an exception then.
        if item.startswith("__") and item.endswith("__"):
            return None
        raise InjectableNotResolved(
            f"Cannot get {item} on injectable. Make sure the function was bound to a container instance"
        )


# singleton object used to indicate that an argument should be injected
injectable: Any = Injectable()
