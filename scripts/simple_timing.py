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


@bind_to_container(container, shared=[SomeService])
def do_work(thing: AThingIMightNeed):
    thing.do_it()


if __name__ == "__main__":
    start = time.perf_counter()
    for i in range(0, 800_00):
        do_work()
    end = time.perf_counter()
    print(f"Time taken {end - start}")

# 9.7
