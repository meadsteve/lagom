from lagom import Container, Singleton, magic_bind_to_container, injectable, bind_to_container
import time


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


container = Container()
container[SomeOtherThingAsAsingleton] = Singleton(SomeOtherThingAsAsingleton)


@bind_to_container(container, shared=[SomeService])
def do_work(thing: AThingIMightNeed = injectable):
    thing.do_it()


if __name__ == "__main__":
    start = time.perf_counter()
    for _ in range(1_600_00):
        #do_work(AThingIMightNeed(SomeService()))
        do_work()
    end = time.perf_counter()
    print(f"Time taken {end - start}")

# 4.1
