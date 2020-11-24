# Testing with Lagom
Since lagom leaves most code unmodified testing can be done on the plain objects
without needing to make any changes at all. One of the goals of lagom is
to enable this style of testing and avoid any patching.

For example the following class:
````python
class UserPremiumService:
    
    # The DB here will be injected by lagom at runtime. But we don't need to modify this
    # class at at all to allow this.
    def __init__(self, db: DB):
        pass

    def upgrade_user_to_premium(self, user):
        pass
````

this can be tested like this:

```python
def test_user_can_be_made_premium():
    mock_db = MockDBOfSomeKind()
    service = UserPremiumService(mock_db)
    test_user = SomeUser()

    service.make_user_premium(test_user)

    assert_mock_db_has_premium_user(mock_db, test_user)
```

Your tests now have no dependency on global state, patching or lagom itself.

## Using a container in tests
Although the testing style above is the goal of lagom you may want some tests
with a copy of the production setup but with certain key dependencies mocked out.
Once a container has been cloned definitions can be altered.

Taking container from the [example here](full_example.md) we can create a fixture
like this which patches out how communication works:

```python
def container_fixture():
    from my_app.prod_container import container
    test_container = container.clone() # Cloning enables overwriting deps
    test_container[DiceClient] = StubbedResponseClient()
    return test_container
```

and then it can be used like this:
```python
def test_something(container_fixture: Container):
    container_fixture[DiceClient] = FakeDice(always_roll=6)
    game_to_test = container_fixture[Game]
    # TODO: act & assert on something
```
