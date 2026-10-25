# Объявление примеров данных запроса

> Перевод страницы [Declare Request Example Data](https://fastapi.tiangolo.com/tutorial/schema-extra-example/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Можно объявлять примеры данных, которые может получать ваше приложение.

Вот несколько способов это сделать.

## Дополнительные данные JSON Schema в моделях Pydantic

Для модели Pydantic можно объявить `examples`, которые будут добавлены в сгенерированную JSON Schema.

```python title="schema_extra_example/tutorial001_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results
```

Эта дополнительная информация будет добавлена как есть в выходную **JSON Schema** этой модели и будет использоваться в документации API.

Можно использовать атрибут `model_config`, который принимает `dict`, как описано в [документации Pydantic: Configuration](https://pydantic.dev/docs/validation/latest/api/pydantic/config/).

В `"json_schema_extra"` можно передать `dict` с любыми дополнительными данными, которые вы хотите видеть в сгенерированной JSON Schema, включая `examples`.

> **Совет**
>
> Тот же приём можно использовать, чтобы расширить JSON Schema и добавить собственную дополнительную информацию.
>
> Например, с его помощью можно добавить метаданные для пользовательского интерфейса фронтенда и т. д.

> **Примечание**
>
> В OpenAPI 3.1.0 (используется начиная с FastAPI 0.99.0) добавлена поддержка `examples`, которое является частью стандарта **JSON Schema**.
>
> До этого поддерживалось только ключевое слово `example` с единственным примером. OpenAPI 3.1.0 по-прежнему его поддерживает, но оно устарело и не является частью стандарта JSON Schema. Поэтому рекомендуется перейти с `example` на `examples`. 🤓
>
> Подробнее можно прочитать в конце этой страницы.

## Дополнительные аргументы `Field`

При использовании `Field()` с моделями Pydantic можно также объявить дополнительные `examples`:

```python title="schema_extra_example/tutorial002_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(default=None, examples=["A very nice Item"])
    price: float = Field(examples=[35.4])
    tax: float | None = Field(default=None, examples=[3.2])


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results
```

## `examples` в JSON Schema — OpenAPI

При использовании любого из:

* `Path()`
* `Query()`
* `Header()`
* `Cookie()`
* `Body()`
* `Form()`
* `File()`

можно также объявить группу `examples` с дополнительной информацией, которая будет добавлена в их **JSON Schema** внутри **OpenAPI**.

### `Body` с `examples`

Здесь мы передаём `examples`, содержащий один пример данных, ожидаемых в `Body()`:

```python title="schema_extra_example/tutorial003_an_py310.py"
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
async def update_item(
    item_id: int,
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results
```

### Пример в интерфейсе документации

При любом из способов выше в `/docs` это будет выглядеть так:

<img src="https://fastapi.tiangolo.com/img/tutorial/body-fields/image01.png">

### `Body` с несколькими `examples`

Конечно, можно передать и несколько `examples`:

```python title="schema_extra_example/tutorial004_an_py310.py"
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
async def update_item(
    *,
    item_id: int,
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
                {
                    "name": "Bar",
                    "price": "35.4",
                },
                {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results
```

В этом случае примеры станут частью внутренней **JSON Schema** для этих данных тела.

Тем не менее на <dfn title="2023-08-26">момент написания</dfn> Swagger UI — инструмент, отвечающий за отображение интерфейса документации, — не поддерживает показ нескольких примеров для данных в **JSON Schema**. Но ниже описан обходной путь.

### `examples`, специфичные для OpenAPI

Ещё до того, как **JSON Schema** стала поддерживать `examples`, в OpenAPI было другое поле, тоже называвшееся `examples`.

Это **специфичное для OpenAPI** поле `examples` находится в другом разделе спецификации OpenAPI. Оно идёт в **подробностях каждой *операции пути***, а не внутри каждой JSON Schema.

И Swagger UI уже давно поддерживает именно это поле `examples`. Поэтому его можно использовать, чтобы **показывать** разные **примеры в интерфейсе документации**.

Это специфичное для OpenAPI поле `examples` имеет форму `dict` с **несколькими примерами** (а не `list`), каждый из которых содержит дополнительную информацию, которая тоже будет добавлена в **OpenAPI**.

Оно находится не внутри каждой JSON Schema, содержащейся в OpenAPI, а снаружи — непосредственно в *операции пути*.

### Использование параметра `openapi_examples`

Специфичные для OpenAPI `examples` в FastAPI можно объявить с помощью параметра `openapi_examples` для:

* `Path()`
* `Query()`
* `Header()`
* `Cookie()`
* `Body()`
* `Form()`
* `File()`

Ключи `dict` идентифицируют каждый пример, а каждое значение — это ещё один `dict`.

Каждый отдельный `dict` примера в `examples` может содержать:

* `summary`: краткое описание примера.
* `description`: длинное описание, которое может содержать текст в Markdown.
* `value`: собственно показываемый пример, например `dict`.
* `externalValue`: альтернатива `value` — URL, указывающий на пример. Правда, его могут поддерживать не так много инструментов, как `value`.

Использовать это можно так:

```python title="schema_extra_example/tutorial005_an_py310.py"
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
async def update_item(
    *,
    item_id: int,
    item: Annotated[
        Item,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results
```

### Примеры OpenAPI в интерфейсе документации

С `openapi_examples`, добавленным в `Body()`, страница `/docs` будет выглядеть так:

<img src="https://fastapi.tiangolo.com/img/tutorial/body-fields/image02.png">

## Технические подробности

> **Совет**
>
> Если вы уже используете **FastAPI** версии **0.99.0 или выше**, эти подробности, скорее всего, можно **пропустить**.
>
> Они больше актуальны для старых версий, до появления OpenAPI 3.1.0.
>
> Можете считать это кратким **уроком истории** OpenAPI и JSON Schema. 🤓

> **Внимание**
>
> Это очень технические подробности о стандартах **JSON Schema** и **OpenAPI**.
>
> Если идеи выше у вас уже работают, этого может быть достаточно, и эти подробности вам, скорее всего, не нужны — смело пропускайте их.

До OpenAPI 3.1.0 в OpenAPI использовалась более старая и модифицированная версия **JSON Schema**.

В JSON Schema не было `examples`, поэтому OpenAPI добавил собственное поле `example` в свою модифицированную версию.

OpenAPI также добавил поля `example` и `examples` в другие части спецификации:

* [`Parameter Object` (в спецификации)](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#parameter-object), который использовался следующими функциями FastAPI:
    * `Path()`
    * `Query()`
    * `Header()`
    * `Cookie()`
* [`Request Body Object`, в поле `content`, в `Media Type Object` (в спецификации)](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#media-type-object), который использовался следующими функциями FastAPI:
    * `Body()`
    * `File()`
    * `Form()`

> **Примечание**
>
> Этот старый специфичный для OpenAPI параметр `examples` начиная с FastAPI `0.103.0` называется `openapi_examples`.

### Поле `examples` в JSON Schema

Но затем в новой версии спецификации JSON Schema появилось поле [`examples`](https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.9.5).

А затем новый OpenAPI 3.1.0 был основан на последней версии (JSON Schema 2020-12), которая включала это новое поле `examples`.

И теперь это новое поле `examples` имеет приоритет над старым единичным (и нестандартным) полем `example`, которое теперь устарело.

Новое поле `examples` в JSON Schema — это **просто `list`** примеров, а не словарь с дополнительными метаданными, как в других местах OpenAPI (описанных выше).

> **Примечание**
>
> Даже после выхода OpenAPI 3.1.0 с этой новой, более простой интеграцией с JSON Schema какое-то время Swagger UI — инструмент, обеспечивающий автоматическую документацию, — не поддерживал OpenAPI 3.1.0 (поддерживает начиная с версии 5.0.0 🎉).
>
> Из-за этого версии FastAPI до 0.99.0 всё ещё использовали версии OpenAPI ниже 3.1.0.

### `examples` в Pydantic и FastAPI

Когда вы добавляете `examples` внутрь модели Pydantic с помощью `schema_extra` или `Field(examples=["something"])`, этот пример добавляется в **JSON Schema** этой модели Pydantic.

А **JSON Schema** модели Pydantic включается в **OpenAPI** вашего API и затем используется в интерфейсе документации.

В версиях FastAPI до 0.99.0 (0.99.0 и выше используют более новый OpenAPI 3.1.0), когда вы использовали `example` или `examples` с любыми другими утилитами (`Query()`, `Body()` и т. д.), эти примеры не добавлялись в JSON Schema, описывающую данные (даже в собственную версию JSON Schema от OpenAPI), — они добавлялись непосредственно в объявление *операции пути* в OpenAPI (вне частей OpenAPI, использующих JSON Schema).

Но теперь, когда FastAPI 0.99.0 и выше использует OpenAPI 3.1.0, основанный на JSON Schema 2020-12, и Swagger UI 5.0.0 и выше, всё стало более согласованным, и примеры включаются в JSON Schema.

### Swagger UI и специфичные для OpenAPI `examples`

Поскольку Swagger UI не поддерживал несколько примеров JSON Schema (на 2023-08-26), у пользователей не было способа показать несколько примеров в документации.

Чтобы решить эту проблему, в FastAPI `0.103.0` **добавили поддержку** объявления того же старого **специфичного для OpenAPI** поля `examples` с помощью нового параметра `openapi_examples`. 🤓

### Итоги

Я раньше говорил, что не очень люблю историю... а теперь посмотрите на меня — даю уроки «технической истории». 😅

Короче говоря, **обновитесь до FastAPI 0.99.0 или выше** — и всё станет гораздо **проще, согласованнее и интуитивнее**, и знать все эти исторические подробности не придётся. 😎
