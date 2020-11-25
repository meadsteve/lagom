import cProfile

from lagom import Singleton, bind_to_container, ExplicitContainer, injectable

from scripts.timing.core_domain import SomeOtherThingAsAsingleton, SomeService, AThingIMightNeed

container = ExplicitContainer()
container[SomeOtherThingAsAsingleton] = SomeOtherThingAsAsingleton()
container[SomeService] = lambda c: SomeService(c[SomeOtherThingAsAsingleton])
container[AThingIMightNeed] = lambda c: AThingIMightNeed(c[SomeService])


@bind_to_container(container, shared=[SomeService])
def do_work(thing: AThingIMightNeed=injectable):
    thing.do_it()


def run_test():
    for _ in range(1_600_00):
        do_work()


if __name__ == "__main__":
    cProfile.run("run_test()")

