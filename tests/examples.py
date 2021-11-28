class SomeClass:
    pass


class SomeExtendedClass(SomeClass):
    pass


class SomeClassManager:
    def __enter__(self):
        return SomeClass()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
