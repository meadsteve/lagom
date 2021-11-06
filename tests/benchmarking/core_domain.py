class SomeOtherThingAsAsingleton:
    def work(self):
        return 1


class SomeService:
    def __init__(self, other: SomeOtherThingAsAsingleton):
        self.other = other

    def do_it(self):
        return self.other.work()


class AThingIMightNeed:
    service: SomeService

    def __init__(self, service: SomeService):
        self.service = service

    def do_it(self):
        return self.service.do_it()
