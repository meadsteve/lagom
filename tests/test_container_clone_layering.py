from lagom import Container


class Dep:
    def __init__(self, contents: str):
        self.contents = contents


class OtherDep:
    def __init__(self, dep: Dep):
        self.dep = dep


class OtherDepNeedingALambda:
    def __init__(self, dep):
        self.dep = dep


level_one = Container()
level_one[Dep] = Dep("level one")
level_one[OtherDepNeedingALambda] = lambda c: OtherDepNeedingALambda(c[Dep])

level_two = level_one.clone()
level_two[Dep] = Dep("level two")

level_three = level_two.clone()
level_three[Dep] = Dep("level three")


def test_container_invocation_level_controls_the_dep_loaded_for_reflected_constructions():
    assert level_one[OtherDep].dep.contents == "level one"
    assert level_two[OtherDep].dep.contents == "level two"
    assert level_three[OtherDep].dep.contents == "level three"


def test_container_invocation_level_is_passed_to_lambdas():
    assert level_one[OtherDepNeedingALambda].dep.contents == "level one"
    assert level_two[OtherDepNeedingALambda].dep.contents == "level two"
    assert level_three[OtherDepNeedingALambda].dep.contents == "level three"
