# Cookbook
Common patterns and usages are documented here.

## Removing a dependency on the system clock

```python
from datetime import datetime
from typing import NewType

from lagom import Container, bind_to_container

container = Container()

Now = NewType("Now", datetime)

container[Now] = lambda: datetime.now()


@bind_to_container(container)
def month_as_a_string(now: Now):
    return now.strftime("%B")


print(month_as_a_string())


# in testing:

assert month_as_a_string(datetime(2020, 5, 12)) == "May"

```