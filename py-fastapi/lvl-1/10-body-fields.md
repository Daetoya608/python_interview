# Тело — поля

> Перевод страницы [Body - Fields](https://fastapi.tiangolo.com/tutorial/body-fields/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Так же как с помощью `Query`, `Path` и `Body` можно объявлять дополнительную валидацию и метаданные в параметрах *функции операции пути*, внутри моделей Pydantic валидацию и метаданные можно объявлять с помощью `Field` из Pydantic.

## Импортируйте `Field`

Сначала его нужно импортировать:

```python title="body_fields/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results
```

> **Внимание**
>
> Обратите внимание, что `Field` импортируется напрямую из `pydantic`, а не из `fastapi`, как все остальные (`Query`, `Path`, `Body` и т. д.).

## Объявите атрибуты модели

Затем `Field` можно использовать с атрибутами модели:

```python title="body_fields/tutorial001_an_py310.py"
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
```

`Field` работает так же, как `Query`, `Path` и `Body`, у него все те же параметры и т. д.

> **Примечание | Технические подробности**
>
> На самом деле `Query`, `Path` и другие, которые вы увидите дальше, создают объекты подклассов общего класса `Param`, который сам является подклассом класса `FieldInfo` из Pydantic.
>
> И `Field` из Pydantic тоже возвращает экземпляр `FieldInfo`.
>
> `Body` также напрямую возвращает объекты подкласса `FieldInfo`. Есть и другие, которые вы увидите позже, — подклассы класса `Body`.
>
> Помните, что когда вы импортируете `Query`, `Path` и другие из `fastapi`, на самом деле это функции, возвращающие специальные классы.

> **Совет**
>
> Обратите внимание, что каждый атрибут модели с типом, значением по умолчанию и `Field` имеет ту же структуру, что и параметр *функции операции пути*, только с `Field` вместо `Path`, `Query` и `Body`.

## Добавьте дополнительную информацию

Дополнительную информацию можно объявить через `json_schema_extra` в `Field`, `Query`, `Body` и т. д. Она будет включена в сгенерированную JSON Schema.

Подробнее о добавлении дополнительной информации вы узнаете позже в документации, когда будете учиться объявлять примеры.

> **Внимание**
>
> Дополнительные ключи, переданные в `json_schema_extra`, также окажутся в итоговой схеме OpenAPI вашего приложения.
> Поскольку эти ключи не обязательно являются частью спецификации OpenAPI, некоторые инструменты OpenAPI, например [валидатор OpenAPI](https://validator.swagger.io/), могут не работать с вашей сгенерированной схемой.

## Итоги

`Field` из Pydantic можно использовать для объявления дополнительных валидаций и метаданных атрибутов модели.

Можно также использовать `json_schema_extra`, чтобы передать дополнительные метаданные JSON Schema.
