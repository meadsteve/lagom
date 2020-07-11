# Cookbook
Common patterns and usages are documented here.

## Removing a dependency on the system clock

```python
from datetime import datetime
from typing import NewType

from lagom import Container, magic_bind_to_container

container = Container()

Now = NewType("Now", datetime)

container[Now] = lambda: datetime.now()


@magic_bind_to_container(container)
def month_as_a_string(now: Now):
    return now.strftime("%B")


print(month_as_a_string())


# in testing:

assert month_as_a_string(datetime(2020, 5, 12)) == "May"

```

## Hiding executor details from functions

```python
import asyncio
import concurrent
from concurrent.futures.thread import ThreadPoolExecutor
from typing import NewType

from lagom import Container, magic_bind_to_container

container = Container()

IOBoundExecutor = NewType("IOBoundExecutor", ThreadPoolExecutor)

MAX_WORKERS = 8 # Or twice CPU count or whatever
container[IOBoundExecutor] = lambda : ThreadPoolExecutor(max_workers=MAX_WORKERS)


# This function now doesn't need to know details of the
# system it's running on (CPU count). All it needs to know
# is if the task is IO bound or not.
@magic_bind_to_container(container)
async def do_some_work(io_bound_executor: IOBoundExecutor):
    with io_bound_executor as executor:
        futures = {executor.submit(process_message, n) for n in range(0, 20)}
        completed_futures = concurrent.futures.wait(futures)
    print([f.result() for f in completed_futures.done])

def process_message(number):
    # Pretend we did some io bound work
    return f"hej {number}"

asyncio.run(do_some_work())
```