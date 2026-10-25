# Классы как зависимости

> Перевод страницы [Classes as Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Прежде чем глубже погружаться в систему **внедрения зависимостей**, улучшим предыдущий пример.

## `dict` из предыдущего примера

В предыдущем примере мы возвращали `dict` из нашей зависимости («dependable»):

```python title="dependencies/tutorial001_an_py310.py"
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

Но тогда в параметре `commons` *функции операции пути* мы получаем `dict`.

А мы знаем, что редакторы не могут обеспечить много поддержки (например, автодополнения) для `dict`, потому что не знают их ключей и типов значений.

Можно сделать лучше...

## Что делает объект зависимостью

До сих пор вы видели зависимости, объявленные как функции.

Но это не единственный способ объявлять зависимости (хотя, вероятно, самый распространённый).

Ключевой фактор — зависимость должна быть «вызываемым объектом» (callable).

«**Вызываемый объект**» в Python — это всё, что Python может «вызвать», как функцию.

Так что, если у вас есть объект `something` (который может и _не_ быть функцией) и его можно «вызвать» (выполнить) так:

```Python
something()
```

или

```Python
something(some_argument, some_keyword_argument="foo")
```

то это «вызываемый объект».

## Классы как зависимости

Вы могли заметить, что для создания экземпляра класса Python используется тот же синтаксис.

Например:

```Python
class Cat:
    def __init__(self, name: str):
        self.name = name


fluffy = Cat(name="Mr Fluffy")
```

В этом случае `fluffy` — экземпляр класса `Cat`.

И чтобы создать `fluffy`, вы «вызываете» `Cat`.

Значит, класс Python — это тоже **вызываемый объект**.

Тогда в **FastAPI** класс Python можно использовать как зависимость.

На самом деле FastAPI проверяет, что это «вызываемый объект» (функция, класс или что-то ещё), и смотрит на объявленные параметры.

Если передать «вызываемый объект» как зависимость в **FastAPI**, он проанализирует параметры этого «вызываемого объекта» и обработает их так же, как параметры *функции операции пути*. Включая подзависимости.

Это относится и к вызываемым объектам вообще без параметров — так же, как и к *функциям операций пути* без параметров.

Тогда можно заменить зависимость `common_parameters` выше на класс `CommonQueryParams`:

```python title="dependencies/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/")
async def read_items(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
```

Обратите внимание на метод `__init__`, используемый для создания экземпляра класса:

```python title="dependencies/tutorial002_an_py310.py"
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit
```

...у него те же параметры, что и у нашей прежней `common_parameters`:

```python title="dependencies/tutorial001_an_py310.py"
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}
```

Именно эти параметры **FastAPI** будет использовать, чтобы «разрешить» зависимость.

В обоих случаях будут:

* Необязательный параметр запроса `q` типа `str`.
* Параметр запроса `skip` типа `int`, по умолчанию `0`.
* Параметр запроса `limit` типа `int`, по умолчанию `100`.

В обоих случаях данные будут преобразованы, провалидированы, задокументированы в схеме OpenAPI и т. д.

## Используйте его

Теперь можно объявить зависимость с помощью этого класса (см. `read_items` в примере выше).

**FastAPI** вызывает класс `CommonQueryParams`. Это создаёт «экземпляр» этого класса, и экземпляр будет передан в вашу функцию как параметр `commons`.

## Аннотация типа и `Depends`

Обратите внимание, что в коде выше мы пишем `CommonQueryParams` дважды:

**Python 3.10+**

```Python
commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]
```

**Python 3.10+ без Annotated** (по возможности предпочитайте версию с `Annotated`)

```Python
commons: CommonQueryParams = Depends(CommonQueryParams)
```

Последний `CommonQueryParams` в:

```Python
... Depends(CommonQueryParams)
```

...— это то, что **FastAPI** на самом деле использует, чтобы узнать, какова зависимость.

Именно из него FastAPI извлечёт объявленные параметры, и именно его FastAPI будет вызывать.

---

В данном случае первый `CommonQueryParams` в:

**Python 3.10+**

```Python
commons: Annotated[CommonQueryParams, ...
```

**Python 3.10+ без Annotated**

```Python
commons: CommonQueryParams ...
```

...не имеет для **FastAPI** никакого особого значения. FastAPI не будет использовать его для преобразования данных, валидации и т. д. (поскольку для этого он использует `Depends(CommonQueryParams)`).

На самом деле можно было бы написать просто:

**Python 3.10+**

```Python
commons: Annotated[Any, Depends(CommonQueryParams)]
```

**Python 3.10+ без Annotated**

```Python
commons = Depends(CommonQueryParams)
```

...как здесь:

```python title="dependencies/tutorial003_an_py310.py"
from typing import Annotated, Any

from fastapi import Depends, FastAPI

app = FastAPI()


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/")
async def read_items(commons: Annotated[Any, Depends(CommonQueryParams)]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
```

Но объявлять тип рекомендуется, потому что так редактор будет знать, что будет передано в параметр `commons`, и сможет помогать с автодополнением, проверкой типов и т. д.:

<img src="https://fastapi.tiangolo.com/img/tutorial/dependencies/image02.png">

## Сокращённая запись

Но видно, что здесь есть повторение кода — `CommonQueryParams` пишется дважды:

**Python 3.10+**

```Python
commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]
```

**Python 3.10+ без Annotated**

```Python
commons: CommonQueryParams = Depends(CommonQueryParams)
```

**FastAPI** предоставляет сокращение для таких случаев, когда зависимость — *именно* класс, который **FastAPI** будет «вызывать», чтобы создать экземпляр самого этого класса.

Для таких случаев можно сделать следующее.

Вместо:

**Python 3.10+**

```Python
commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]
```

**Python 3.10+ без Annotated**

```Python
commons: CommonQueryParams = Depends(CommonQueryParams)
```

...написать:

**Python 3.10+**

```Python
commons: Annotated[CommonQueryParams, Depends()]
```

**Python 3.10+ без Annotated**

```Python
commons: CommonQueryParams = Depends()
```

Вы объявляете зависимость как тип параметра и используете `Depends()` без параметров, вместо того чтобы *снова* писать полный класс внутри `Depends(CommonQueryParams)`.

Тогда тот же пример будет выглядеть так:

```python title="dependencies/tutorial004_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/")
async def read_items(commons: Annotated[CommonQueryParams, Depends()]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
```

...и **FastAPI** будет знать, что делать.

> **Совет**
>
> Если это кажется скорее запутанным, чем полезным, — не обращайте внимания, это вам *не нужно*.
>
> Это просто сокращение. Потому что **FastAPI** заботится о том, чтобы помочь вам минимизировать повторение кода.
