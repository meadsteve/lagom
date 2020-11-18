# Testing with Lagom
Since lagom leaves most code unmodified testing can be done on the plain objects
without needing to make any changes at all.


## Using a container in tests
Once a container has been cloned definitions can be altered. This is useful if you want
to create a copy of the production setup but with certain dependencies mocked out.

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
