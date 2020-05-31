from lagom import Container, Singleton, bind_to_container
import time


class SomeService:
    def do_it(self):
        pass


class AThingIMightNeed:
    service: SomeService

    def __init__(self, service: SomeService):
        self.service = service

    def do_it(self):
        self.service.do_it()


container = Container()
container[SomeService] = Singleton(SomeService)


@bind_to_container(container)
def do_work(thing: AThingIMightNeed):
    thing.do_it()


if __name__ == "__main__":
    start = time.perf_counter()
    for i in range(0, 100_000):
        do_work()
    end = time.perf_counter()
    print(f"Time taken {end - start}")

# 3.5875363860000107
