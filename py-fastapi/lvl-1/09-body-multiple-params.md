# Тело — несколько параметров

> Перевод страницы [Body - Multiple Parameters](https://fastapi.tiangolo.com/tutorial/body-multiple-params/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Теперь, когда мы разобрались с `Path` и `Query`, рассмотрим более продвинутые способы объявления тела запроса.

## Смешивание параметров `Path`, `Query` и тела

Во-первых, конечно, можно свободно смешивать объявления параметров `Path`, `Query` и тела запроса, и **FastAPI** поймёт, что делать.

Можно также объявлять параметры тела необязательными, задав значение по умолчанию `None`:

```python title="body_multiple_params/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str | None = None,
    item: Item | None = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results
```

> **Примечание**
>
> Обратите внимание, что в этом случае `item`, который берётся из тела, необязателен, так как у него значение по умолчанию `None`.

## Несколько параметров тела

В предыдущем примере *операции пути* ожидали JSON-тело с атрибутами `Item`, например:

```JSON
{
    "name": "Foo",
    "description": "The pretender",
    "price": 42.0,
    "tax": 3.2
}
```

Но можно объявить и несколько параметров тела, например `item` и `user`:

```python title="body_multiple_params/tutorial002_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results
```

В этом случае **FastAPI** заметит, что в функции больше одного параметра тела (два параметра являются моделями Pydantic).

Поэтому он использует имена параметров как ключи (имена полей) в теле и будет ожидать тело вида:

```JSON
{
    "item": {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    },
    "user": {
        "username": "dave",
        "full_name": "Dave Grohl"
    }
}
```

> **Примечание**
>
> Обратите внимание: хотя `item` объявлен так же, как раньше, теперь ожидается, что он будет внутри тела под ключом `item`.

**FastAPI** автоматически преобразует данные из запроса, так что параметр `item` получит своё содержимое, и то же самое для `user`.

Он выполнит валидацию составных данных и задокументирует их соответствующим образом в схеме OpenAPI и автоматической документации.

## Единичные значения в теле

Так же как есть `Query` и `Path` для определения дополнительных данных параметров запроса и пути, **FastAPI** предоставляет аналогичный `Body`.

Например, расширяя предыдущую модель, вы можете решить, что в том же теле, помимо `item` и `user`, нужен ещё ключ `importance`.

Если объявить его как есть, то, поскольку это единичное значение, **FastAPI** решит, что это параметр запроса.

Но можно указать **FastAPI** считать его ещё одним ключом тела с помощью `Body`:

```python title="body_multiple_params/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


@app.put("/items/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: Annotated[int, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results
```

В этом случае **FastAPI** будет ожидать тело вида:

```JSON
{
    "item": {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    },
    "user": {
        "username": "dave",
        "full_name": "Dave Grohl"
    },
    "importance": 5
}
```

И опять же он преобразует типы данных, провалидирует, задокументирует и т. д.

## Несколько параметров тела и параметры запроса

Конечно, при необходимости можно объявлять и дополнительные параметры запроса — в дополнение к любым параметрам тела.

Поскольку по умолчанию единичные значения интерпретируются как параметры запроса, явно добавлять `Query` не нужно, можно просто написать:

```Python
q: str | None = None
```

Например:

```python title="body_multiple_params/tutorial004_an_py310.py"
from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None,
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results
```

> **Примечание**
>
> У `Body` есть все те же дополнительные параметры валидации и метаданных, что и у `Query`, `Path` и других, которые вы увидите позже.

## Встраивание единственного параметра тела

Допустим, у вас есть только один параметр тела `item` — модель Pydantic `Item`.

По умолчанию **FastAPI** будет ожидать непосредственно её тело.

Но если вы хотите, чтобы он ожидал JSON с ключом `item`, а внутри него — содержимое модели, как это происходит при объявлении дополнительных параметров тела, можно использовать специальный параметр `embed` у `Body`:

```Python
item: Annotated[Item, Body(embed=True)]
```

как здесь:

```python title="body_multiple_params/tutorial005_an_py310.py"
from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results
```

В этом случае **FastAPI** будет ожидать тело вида:

```JSON
{
    "item": {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    }
}
```

вместо:

```JSON
{
    "name": "Foo",
    "description": "The pretender",
    "price": 42.0,
    "tax": 3.2
}
```

## Итоги

В *функцию операции пути* можно добавить несколько параметров тела, хотя у запроса может быть только одно тело.

**FastAPI** с этим справится: передаст в функцию правильные данные, а также провалидирует и задокументирует правильную схему в *операции пути*.

Можно также объявлять единичные значения, которые будут приниматься как часть тела.

И можно указать **FastAPI** встроить тело в ключ, даже если объявлен всего один параметр.
