# Тело запроса

> Перевод страницы [Request Body](https://fastapi.tiangolo.com/tutorial/body/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Когда нужно отправить данные от клиента (скажем, браузера) в ваш API, их отправляют в **теле запроса** (request body).

Тело **запроса** — это данные, которые клиент отправляет в ваш API. Тело **ответа** — это данные, которые ваш API отправляет клиенту.

Ваш API почти всегда должен отправлять тело **ответа**. Но клиентам не обязательно всё время отправлять **тела запросов**: иногда они только запрашивают путь, возможно с какими-то параметрами запроса, но тело не отправляют.

Чтобы объявить тело **запроса**, используются модели [Pydantic](https://pydantic.dev/docs/) со всей их мощью и преимуществами.

> **Примечание**
>
> Чтобы отправлять данные, следует использовать один из методов: `POST` (самый распространённый), `PUT`, `DELETE` или `PATCH`.
>
> Поведение при отправке тела в запросе `GET` в спецификациях не определено, тем не менее FastAPI это поддерживает — только для очень сложных/крайних случаев.
>
> Поскольку так делать не рекомендуется, интерактивная документация на Swagger UI не будет показывать документацию тела при использовании `GET`, а промежуточные прокси могут это не поддерживать.

## Импортируйте `BaseModel` из Pydantic

Сначала нужно импортировать `BaseModel` из `pydantic`:

```python title="body/tutorial001_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


@app.post("/items/")
async def create_item(item: Item):
    return item
```

## Создайте модель данных

Затем объявите модель данных как класс, наследующийся от `BaseModel`.

Для всех атрибутов используйте стандартные типы Python:

```python title="body/tutorial001_py310.py"
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
```

Как и при объявлении параметров запроса, если у атрибута модели есть значение по умолчанию, он не обязателен. Иначе он обязателен. Используйте `None`, чтобы сделать атрибут просто необязательным.

Например, модель выше описывает JSON-«`object`» (или `dict` в Python) вроде такого:

```JSON
{
    "name": "Foo",
    "description": "An optional description",
    "price": 45.2,
    "tax": 3.5
}
```

...а поскольку `description` и `tax` необязательны (у них значение по умолчанию `None`), такой JSON-«`object`» тоже будет валидным:

```JSON
{
    "name": "Foo",
    "price": 45.2
}
```

## Объявите её как параметр

Чтобы добавить модель в *операцию пути*, объявите её так же, как объявляли параметры пути и запроса:

```python title="body/tutorial001_py310.py"
@app.post("/items/")
async def create_item(item: Item):
    return item
```

...и укажите в качестве её типа созданную модель `Item`.

## Результат

Только благодаря этому объявлению типа Python **FastAPI**:

* Прочитает тело запроса как JSON.
* Преобразует соответствующие типы (при необходимости).
* Провалидирует данные.
    * Если данные невалидны, вернёт аккуратную и понятную ошибку, указав, где именно и какие данные были неверны.
* Передаст вам полученные данные в параметре `item`.
    * Поскольку в функции вы объявили его тип как `Item`, у вас также будет вся поддержка редактора (автодополнение и т. д.) для всех атрибутов и их типов.
* Сгенерирует определения [JSON Schema](https://json-schema.org) для вашей модели; их можно использовать и в любом другом месте, если это имеет смысл для вашего проекта.
* Эти схемы станут частью сгенерированной схемы OpenAPI и будут использоваться <abbr title="User Interfaces — пользовательскими интерфейсами">UI</abbr> автоматической документации.

## Автоматическая документация

JSON Schema ваших моделей будут частью сгенерированной схемы OpenAPI и будут отображаться в интерактивной документации API:

<img src="https://fastapi.tiangolo.com/img/tutorial/body/image01.png">

А также будут использоваться в документации API внутри каждой *операции пути*, которой они нужны:

<img src="https://fastapi.tiangolo.com/img/tutorial/body/image02.png">

## Поддержка редактора

В редакторе внутри функции у вас повсюду будут подсказки типов и автодополнение (этого бы не было, если бы вы получали `dict` вместо модели Pydantic):

<img src="https://fastapi.tiangolo.com/img/tutorial/body/image03.png">

Вы также получаете проверку ошибок при некорректных операциях с типами:

<img src="https://fastapi.tiangolo.com/img/tutorial/body/image04.png">

Это не случайность — весь фреймворк построен вокруг такого дизайна.

И это было тщательно протестировано ещё на этапе проектирования, до какой-либо реализации, чтобы убедиться, что всё будет работать во всех редакторах.

Ради этого даже были внесены некоторые изменения в сам Pydantic.

Предыдущие скриншоты сделаны в [Visual Studio Code](https://code.visualstudio.com).

Но такую же поддержку вы получите в [PyCharm](https://www.jetbrains.com/pycharm/) и большинстве других редакторов Python:

<img src="https://fastapi.tiangolo.com/img/tutorial/body/image05.png">

> **Совет**
>
> Если вы используете [PyCharm](https://www.jetbrains.com/pycharm/), можно установить [плагин Pydantic для PyCharm](https://github.com/koxudaxi/pydantic-pycharm-plugin/).
>
> Он улучшает поддержку моделей Pydantic в редакторе:
>
> * автодополнение
> * проверки типов
> * рефакторинг
> * поиск
> * инспекции

## Использование модели

Внутри функции можно напрямую обращаться ко всем атрибутам объекта модели:

```python title="body/tutorial002_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
```

## Тело запроса + параметры пути

Можно одновременно объявить параметры пути и тело запроса.

**FastAPI** поймёт, что параметры функции, совпадающие с параметрами пути, нужно **брать из пути**, а параметры функции, объявленные как модели Pydantic, — **из тела запроса**.

```python title="body/tutorial003_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}
```

## Тело запроса + параметры пути + параметры запроса

Можно также объявить параметры **тела**, **пути** и **запроса** — все одновременно.

**FastAPI** распознает каждый из них и возьмёт данные из правильного места.

```python title="body/tutorial004_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result
```

Параметры функции распознаются так:

* Если параметр объявлен также в **пути**, он используется как параметр пути.
* Если параметр имеет **простой тип** (например, `int`, `float`, `str`, `bool` и т. д.), он интерпретируется как параметр **запроса**.
* Если тип параметра объявлен как **модель Pydantic**, он интерпретируется как **тело** запроса.

> **Примечание**
>
> FastAPI поймёт, что значение `q` не обязательно, благодаря значению по умолчанию `= None`.
>
> FastAPI не использует `str | None`, чтобы определить, что значение не обязательно; он поймёт это потому, что есть значение по умолчанию `= None`.
>
> Но добавление аннотаций типов позволит редактору лучше вам помогать и находить ошибки.

## Без Pydantic

Если вы не хотите использовать модели Pydantic, можно также использовать параметры **Body**. См. документацию [Тело — несколько параметров: единичные значения в теле](09-body-multiple-params.md).
