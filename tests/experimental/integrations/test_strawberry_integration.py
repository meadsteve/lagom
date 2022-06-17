from typing import TypeVar, List, Any, Dict

import pytest
import strawberry
from strawberry.asgi import GraphQL
from strawberry.dataloader import DataLoader

from lagom import injectable
from lagom.experimental.integrations.strawberry import StrawberryContainer

container = StrawberryContainer()

T = TypeVar("T")


class AuthorLoader(DataLoader[int, "Author"]):
    def __init__(self):
        super().__init__(self.get_authors)

    async def get_authors(self, ids) -> List["Author"]:
        return [lookup_author(id) for id in ids]


@strawberry.type
class Author:
    name: str
    author_id: int


@strawberry.type
class Book:
    title: str
    author_id: int

    @strawberry.field
    @container.attach_field
    async def author(self, loader: "AuthorLoader" = injectable) -> Author:
        return await loader.load(self.author_id)


authors = [
    Author(author_id=1, name="F. Scott Fitzgerald"),
    Author(author_id=2, name="Frank Herbert"),
]

books = [
    Book(
        title="The Great Gatsby",
        author_id=1,
    ),
    Book(
        title="Dune",
        author_id=2,
    ),
    Book(
        title="Children of Dune",
        author_id=2,
    ),
]


def lookup_author(id: int):
    for author in authors:
        if author.author_id == id:
            return author
    raise Exception("Author not found")


def get_books():
    return books


class MyGraphQL(GraphQL):
    async def get_context(self, *args, **kwargs) -> Any:
        context: Dict = {}
        container.hook_into_context(context)
        return context


@strawberry.type
class Query:
    books: List[Book] = strawberry.field(resolver=get_books)


@pytest.mark.asyncio
async def test_the_data_gets_built_correctly():
    query = """
        query TestQuery {
          books {
            author {
              name
            }
            title
          }
        }
    """

    app = MyGraphQL(strawberry.Schema(query=Query))

    result = await app.schema.execute(query, context_value=await app.get_context())

    assert result.errors is None
    assert result.data
    assert result.data["books"] == [
        {"author": {"name": "F. Scott Fitzgerald"}, "title": "The Great Gatsby"},
        {"author": {"name": "Frank Herbert"}, "title": "Dune"},
        {"author": {"name": "Frank Herbert"}, "title": "Children of Dune"},
    ]
