try:
    from mypy_extensions import mypyc_attr
except:

    def mypyc_attr(*attrs, **kwattrs):  # type: ignore
        return lambda x: x
