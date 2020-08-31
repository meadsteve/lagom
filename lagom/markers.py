from typing import Any


class Injectable:
    """
    This class is looked for when analysing function signatures for arguments to
    injected
    """

    pass


# singleton object used to indicate that an argument should be injected
injectable: Any = Injectable()
