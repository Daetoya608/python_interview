# Тело — вложенные модели

> Перевод страницы [Body - Nested Models](https://fastapi.tiangolo.com/tutorial/body-nested-models/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

С **FastAPI** можно определять, валидировать, документировать и использовать модели произвольной глубины вложенности (благодаря Pydantic).

## Поля-списки

Атрибут можно объявить подтипом. Например, `list` Python:

```python title="body_nested_models/tutorial001_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list = []


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results
```

Так `tags` станет списком, хотя тип элементов списка не объявлен.

## Поля-списки с параметром типа

Но в Python есть специальный способ объявлять списки с внутренними типами, или «параметрами типа»:

### Объявите `list` с параметром типа

Чтобы объявить типы, у которых есть параметры типа (внутренние типы), например `list`, `dict`, `tuple`, передайте внутренний тип (типы) как «параметры типа» в квадратных скобках: `[` и `]`

```Python
my_list: list[str]
```

Это обычный стандартный синтаксис Python для объявления типов.

Используйте тот же стандартный синтаксис для атрибутов модели с внутренними типами.

Так что в нашем примере можно сделать `tags` именно «списком строк»:

```python title="body_nested_models/tutorial002_py310.py"
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []
```

## Типы-множества

Но потом мы задумываемся и понимаем, что теги не должны повторяться — скорее всего, это уникальные строки.

А в Python есть специальный тип данных для множеств уникальных элементов — `set`.

Тогда можно объявить `tags` как множество строк:

```python title="body_nested_models/tutorial003_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results
```

Теперь, даже если придёт запрос с повторяющимися данными, они будут преобразованы в множество уникальных элементов.

И при выводе этих данных, даже если в источнике были дубликаты, они будут выведены как множество уникальных элементов.

И соответствующим образом аннотированы / задокументированы.

## Вложенные модели

У каждого атрибута модели Pydantic есть тип.

Но этот тип сам может быть другой моделью Pydantic.

Так что можно объявлять глубоко вложенные JSON-«объекты» с конкретными именами атрибутов, типами и валидациями.

И всё это — с произвольной вложенностью.

### Определите подмодель

Например, можно определить модель `Image`:

```python title="body_nested_models/tutorial004_py310.py"
class Image(BaseModel):
    url: str
    name: str
```

### Используйте подмодель как тип

А затем использовать её как тип атрибута:

```python title="body_nested_models/tutorial004_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results
```

Это означает, что **FastAPI** будет ожидать тело, похожее на:

```JSON
{
    "name": "Foo",
    "description": "The pretender",
    "price": 42.0,
    "tax": 3.2,
    "tags": ["rock", "metal", "bar"],
    "image": {
        "url": "http://example.com/baz.jpg",
        "name": "The Foo live"
    }
}
```

И снова, сделав только это объявление, с **FastAPI** вы получаете:

* Поддержку редактора (автодополнение и т. д.), даже для вложенных моделей
* Преобразование данных
* Валидацию данных
* Автоматическую документацию

## Специальные типы и валидация

Помимо обычных простых типов вроде `str`, `int`, `float` и т. д., можно использовать более сложные простые типы, наследующиеся от `str`.

Чтобы увидеть все доступные варианты, загляните в [обзор типов Pydantic](https://pydantic.dev/docs/validation/latest/concepts/types/). Несколько примеров вы увидите в следующей главе.

Например, раз в модели `Image` есть поле `url`, его можно объявить как экземпляр `HttpUrl` из Pydantic вместо `str`:

```python title="body_nested_models/tutorial005_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results
```

Строка будет проверена на то, что это валидный URL, и задокументирована как таковая в JSON Schema / OpenAPI.

## Атрибуты со списками подмоделей

Модели Pydantic можно также использовать как подтипы `list`, `set` и т. д.:

```python title="body_nested_models/tutorial006_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results
```

Это будет ожидать (преобразовывать, валидировать, документировать и т. д.) JSON-тело вида:

```JSON
{
    "name": "Foo",
    "description": "The pretender",
    "price": 42.0,
    "tax": 3.2,
    "tags": [
        "rock",
        "metal",
        "bar"
    ],
    "images": [
        {
            "url": "http://example.com/baz.jpg",
            "name": "The Foo live"
        },
        {
            "url": "http://example.com/dave.jpg",
            "name": "The Baz"
        }
    ]
}
```

> **Примечание**
>
> Обратите внимание, что теперь в ключе `images` находится список объектов-изображений.

## Глубоко вложенные модели

Можно определять модели произвольной глубины вложенности:

```python title="body_nested_models/tutorial007_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer
```

> **Примечание**
>
> Обратите внимание, что у `Offer` есть список `Item`, у которых, в свою очередь, есть необязательный список `Image`.

## Тела, состоящие из списков

Если значение верхнего уровня ожидаемого JSON-тела — это JSON-`array` (`list` в Python), тип можно объявить в параметре функции так же, как в моделях Pydantic:

```Python
images: list[Image]
```

как здесь:

```python title="body_nested_models/tutorial008_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images
```

## Поддержка редактора повсюду

И поддержка редактора у вас есть повсюду.

Даже для элементов внутри списков:

<img src="https://fastapi.tiangolo.com/img/tutorial/body-nested-models/image01.png">

Такой поддержки редактора не было бы, если бы вы работали напрямую с `dict` вместо моделей Pydantic.

Но и о них беспокоиться не нужно: входящие словари преобразуются автоматически, а ваш вывод тоже автоматически преобразуется в JSON.

## Тела из произвольных `dict`

Тело можно также объявить как `dict` с ключами одного типа и значениями другого.

Так не нужно заранее знать, какие имена полей/атрибутов допустимы (как было бы в случае моделей Pydantic).

Это полезно, если вы хотите принимать ключи, которые заранее неизвестны.

---

Другой полезный случай — когда нужны ключи другого типа (например, `int`).

Именно его мы и рассмотрим.

В этом случае принимается любой `dict`, если у него ключи `int` и значения `float`:

```python title="body_nested_models/tutorial009_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights
```

> **Совет**
>
> Помните, что JSON поддерживает в качестве ключей только `str`.
>
> Но в Pydantic есть автоматическое преобразование данных.
>
> Это значит, что хотя клиенты API могут отправлять в качестве ключей только строки, если эти строки содержат целые числа, Pydantic преобразует и провалидирует их.
>
> И `dict`, который вы получите в `weights`, действительно будет иметь ключи `int` и значения `float`.

## Итоги

С **FastAPI** у вас есть максимальная гибкость, которую дают модели Pydantic, и при этом код остаётся простым, коротким и элегантным.

Но со всеми преимуществами:

* Поддержка редактора (автодополнение везде!)
* Преобразование данных (т. е. парсинг / сериализация)
* Валидация данных
* Документирование схем
* Автоматическая документация
