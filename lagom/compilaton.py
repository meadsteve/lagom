"""
This module wraps mypy_extensions functions so that code can run without mypy_extension installed or with it installed.

It is generally only required to have it installed when compiling the code using mypc
"""

try:
    from mypy_extensions import mypyc_attr
except:

    def mypyc_attr(*attrs, **kwattrs):  # type: ignore
        """
        Fake version of mypyc_attr from the mypy_extensions library that does nothing
        """
        return lambda x: x
