# Настройка операции пути

> Перевод страницы [Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-operation-configuration/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Есть несколько параметров, которые можно передать в *декоратор операции пути*, чтобы настроить её.

> **Внимание**
>
> Обратите внимание, что эти параметры передаются непосредственно в *декоратор операции пути*, а не в *функцию операции пути*.

## Код статуса ответа

Можно задать (HTTP) `status_code`, который будет использоваться в ответе *операции пути*.

Можно передать код напрямую как `int`, например `404`.

Но если вы не помните, для чего какой числовой код, можно использовать константы-сокращения из `status`:

```python title="path_operation_configuration/tutorial001_py310.py"
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item) -> Item:
    return item
```

Этот код статуса будет использован в ответе и добавлен в схему OpenAPI.

> **Примечание | Технические подробности**
>
> Можно также использовать `from starlette import status`.
>
> **FastAPI** предоставляет тот же `starlette.status` в виде `fastapi.status` просто для удобства разработчика. Но он берётся напрямую из Starlette.

## Теги

К *операции пути* можно добавить теги: передайте параметр `tags` со списком (`list`) строк `str` (обычно всего одна `str`):

```python title="path_operation_configuration/tutorial002_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


@app.post("/items/", tags=["items"])
async def create_item(item: Item) -> Item:
    return item


@app.get("/items/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]


@app.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "johndoe"}]
```

Они будут добавлены в схему OpenAPI и использованы интерфейсами автоматической документации:

<img src="https://fastapi.tiangolo.com/img/tutorial/path-operation-configuration/image01.png">

### Теги с Enum

В большом приложении у вас может накопиться **много тегов**, и вы захотите быть уверены, что для связанных *операций пути* всегда используется **один и тот же тег**.

В таких случаях может иметь смысл хранить теги в `Enum`.

**FastAPI** поддерживает это так же, как обычные строки:

```python title="path_operation_configuration/tutorial002b_py310.py"
from enum import Enum

from fastapi import FastAPI

app = FastAPI()


class Tags(Enum):
    items = "items"
    users = "users"


@app.get("/items/", tags=[Tags.items])
async def get_items():
    return ["Portal gun", "Plumbus"]


@app.get("/users/", tags=[Tags.users])
async def read_users():
    return ["Rick", "Morty"]
```

## Краткое описание и описание

Можно добавить `summary` (краткое описание) и `description` (описание):

```python title="path_operation_configuration/tutorial003_py310.py"
@app.post(
    "/items/",
    summary="Create an item",
    description="Create an item with all the information, name, description, price, tax and a set of unique tags",
)
async def create_item(item: Item) -> Item:
    return item
```

## Описание из docstring

Поскольку описания обычно длинные и занимают несколько строк, описание *операции пути* можно объявить в <dfn title="многострочная строка — первое выражение внутри функции (не присвоенное никакой переменной), используемое для документации">docstring</dfn> функции, и **FastAPI** прочитает его оттуда.

В docstring можно писать на [Markdown](https://ru.wikipedia.org/wiki/Markdown) — он будет интерпретирован и правильно отображён (с учётом отступов docstring).

```python title="path_operation_configuration/tutorial004_py310.py"
@app.post("/items/", summary="Create an item")
async def create_item(item: Item) -> Item:
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item
```

Оно будет использоваться в интерактивной документации:

<img src="https://fastapi.tiangolo.com/img/tutorial/path-operation-configuration/image02.png">

## Описание ответа

Описание ответа можно указать с помощью параметра `response_description`:

```python title="path_operation_configuration/tutorial005_py310.py"
@app.post(
    "/items/",
    summary="Create an item",
    response_description="The created item",
)
async def create_item(item: Item) -> Item:
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item
```

> **Примечание**
>
> Обратите внимание, что `response_description` относится именно к ответу, а `description` — к *операции пути* в целом.

> **Совет**
>
> OpenAPI требует, чтобы у каждой *операции пути* было описание ответа.
>
> Поэтому, если вы его не укажете, **FastAPI** автоматически сгенерирует описание «Successful response».

<img src="https://fastapi.tiangolo.com/img/tutorial/path-operation-configuration/image03.png">

## Пометка *операции пути* как устаревшей

Если нужно пометить *операцию пути* как <dfn title="устаревшая, использовать не рекомендуется">deprecated</dfn>, но не удалять её, передайте параметр `deprecated`:

```python title="path_operation_configuration/tutorial006_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]


@app.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "johndoe"}]


@app.get("/elements/", tags=["items"], deprecated=True)
async def read_elements():
    return [{"item_id": "Foo"}]
```

В интерактивной документации она будет чётко помечена как устаревшая:

<img src="https://fastapi.tiangolo.com/img/tutorial/path-operation-configuration/image04.png">

Посмотрите, как выглядят устаревшие и неустаревшие *операции пути*:

<img src="https://fastapi.tiangolo.com/img/tutorial/path-operation-configuration/image05.png">

## Итоги

*Операции пути* легко настраивать и добавлять к ним метаданные, передавая параметры в *декораторы операций пути*.
