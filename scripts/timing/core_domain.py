class SomeOtherThingAsAsingleton:
    pass


class SomeService:
    def __init__(self, other: SomeOtherThingAsAsingleton):
        pass

    def do_it(self):
        pass


class AThingIMightNeed:
    service: SomeService

    def __init__(self, service: SomeService):
        self.service = service

    def do_it(self):
        self.service.do_it()