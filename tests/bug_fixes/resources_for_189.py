from lagom import Container, injectable, bind_to_container


class SomeDep:
    pass


container = Container()


@bind_to_container(container)
def a_bound_function(dep: SomeDep = injectable):
    return "ok"


@bind_to_container(container)
async def an_async_bound_function(dep: SomeDep = injectable):
    return "ok"
