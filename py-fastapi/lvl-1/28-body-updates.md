# Тело — обновления

> Перевод страницы [Body - Updates](https://fastapi.tiangolo.com/tutorial/body-updates/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

## Обновление с заменой через `PUT`

Для обновления элемента можно использовать операцию [HTTP `PUT`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PUT).

С помощью `jsonable_encoder` можно преобразовать входные данные в данные, которые можно хранить как JSON (например, в NoSQL-базе данных). Например, преобразовать `datetime` в `str`.

```python title="body_updates/tutorial001_py310.py"
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    return items[item_id]


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded
```

`PUT` используется для получения данных, которые должны заменить существующие данные.

### Предупреждение о замене

Это значит, что если вы хотите обновить элемент `bar` через `PUT` с телом:

```Python
{
    "name": "Barz",
    "price": 3,
    "description": None,
}
```

то, поскольку в нём нет уже сохранённого атрибута `"tax": 20.2`, входная модель возьмёт значение по умолчанию `"tax": 10.5`.

И данные будут сохранены с этим «новым» `tax`, равным `10.5`.

## Частичные обновления через `PATCH`

Можно также использовать операцию [HTTP `PATCH`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PATCH), чтобы *частично* обновлять данные.

Это значит, что можно отправить только те данные, которые нужно обновить, оставив остальное без изменений.

> **Примечание**
>
> `PATCH` используют и знают реже, чем `PUT`.
>
> И многие команды используют только `PUT`, даже для частичных обновлений.
>
> Вы **вольны** использовать их как угодно, **FastAPI** не накладывает никаких ограничений.
>
> Но это руководство показывает, примерно как их задумано использовать.

### Использование параметра `exclude_unset` из Pydantic

Если вы хотите получать частичные обновления, очень полезно использовать параметр `exclude_unset` в методе `.model_dump()` модели Pydantic.

Например, `item.model_dump(exclude_unset=True)`.

Это сгенерирует `dict` только с теми данными, которые были заданы при создании модели `item`, исключив значения по умолчанию.

Затем с его помощью можно получить `dict` только с заданными данными (отправленными в запросе), опустив значения по умолчанию:

```python title="body_updates/tutorial002_py310.py"
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    return items[item_id]


@app.patch("/items/{item_id}")
async def update_item(item_id: str, item: Item) -> Item:
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.model_dump(exclude_unset=True)
    updated_item = stored_item_model.model_copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item
```

### Использование параметра `update` из Pydantic

Теперь можно создать копию существующей модели с помощью `.model_copy()` и передать параметр `update` со словарём (`dict`), содержащим данные для обновления.

Например, `stored_item_model.model_copy(update=update_data)` (см. пример выше).

### Итоги по частичным обновлениям

Итак, чтобы применить частичные обновления, нужно:

* (При желании) использовать `PATCH` вместо `PUT`.
* Получить сохранённые данные.
* Поместить эти данные в модель Pydantic.
* Сгенерировать `dict` без значений по умолчанию из входной модели (с помощью `exclude_unset`).
    * Так вы обновите только значения, реально заданные пользователем, а не перезапишете уже сохранённые значения значениями по умолчанию из модели.
* Создать копию сохранённой модели, обновив её атрибуты полученными частичными обновлениями (с помощью параметра `update`).
* Преобразовать скопированную модель во что-то, что можно сохранить в БД (например, с помощью `jsonable_encoder`).
    * Это похоже на повторное использование метода модели `.model_dump()`, но гарантирует (и выполняет) преобразование значений в типы данных, которые можно преобразовать в JSON, например `datetime` в `str`.
* Сохранить данные в БД.
* Вернуть обновлённую модель.

> **Совет**
>
> На самом деле тот же приём можно использовать и с операцией HTTP `PUT`.
>
> Но в примере здесь используется `PATCH`, потому что он создан для таких случаев.

> **Примечание**
>
> Обратите внимание, что входная модель всё равно валидируется.
>
> Поэтому, если вы хотите получать частичные обновления, в которых могут отсутствовать все атрибуты, нужна модель, в которой все атрибуты помечены как необязательные (со значениями по умолчанию или `None`).
>
> Чтобы отличать модели со всеми необязательными значениями для **обновлений** от моделей с обязательными значениями для **создания**, можно использовать идеи, описанные в разделе [Дополнительные модели](19-extra-models.md).
