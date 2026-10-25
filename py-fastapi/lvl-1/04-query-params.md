# Параметры запроса

> Перевод страницы [Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Если объявить другие параметры функции, которые не являются частью параметров пути, они автоматически интерпретируются как параметры «запроса» (query).

```python title="query_params/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

Запрос (query) — это набор пар «ключ-значение», которые идут после `?` в URL и разделяются символами `&`.

Например, в URL:

```
http://127.0.0.1:8000/items/?skip=0&limit=10
```

...параметры запроса такие:

* `skip`: со значением `0`
* `limit`: со значением `10`

Поскольку они являются частью URL, это «естественным образом» строки.

Но когда вы объявляете их с типами Python (в примере выше — как `int`), они преобразуются в этот тип и проверяются на соответствие ему.

К параметрам запроса применяются все те же процессы, что и к параметрам пути:

* Поддержка редактора (разумеется)
* <dfn title="преобразование строки, пришедшей в HTTP-запросе, в данные Python">«Парсинг»</dfn> данных
* Валидация данных
* Автоматическая документация

## Значения по умолчанию

Поскольку параметры запроса не являются фиксированной частью пути, они могут быть необязательными и иметь значения по умолчанию.

В примере выше у них значения по умолчанию `skip=0` и `limit=10`.

Поэтому переход по URL:

```
http://127.0.0.1:8000/items/
```

будет тем же самым, что и переход по:

```
http://127.0.0.1:8000/items/?skip=0&limit=10
```

Но если перейти, например, по:

```
http://127.0.0.1:8000/items/?skip=20
```

значения параметров в вашей функции будут такими:

* `skip=20`: потому что вы указали его в URL
* `limit=10`: потому что это значение по умолчанию

## Необязательные параметры

Точно так же можно объявить необязательные параметры запроса, задав им значение по умолчанию `None`:

```python title="query_params/tutorial002_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

В этом случае параметр функции `q` будет необязательным и по умолчанию будет равен `None`.

> **Совет**
>
> Обратите также внимание, что **FastAPI** достаточно умён, чтобы понять, что `item_id` — это параметр пути, а `q` — нет, а значит, это параметр запроса.

## Преобразование типов параметров запроса

Можно также объявлять тип `bool`, и значения будут преобразованы:

```python title="query_params/tutorial003_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
```

В этом случае, если перейти по:

```
http://127.0.0.1:8000/items/foo?short=1
```

или

```
http://127.0.0.1:8000/items/foo?short=True
```

или

```
http://127.0.0.1:8000/items/foo?short=true
```

или

```
http://127.0.0.1:8000/items/foo?short=on
```

или

```
http://127.0.0.1:8000/items/foo?short=yes
```

или любому другому варианту регистра (всё заглавными, первая буква заглавная и т. д.), ваша функция получит параметр `short` со значением `bool`, равным `True`.

Значения вроде `0`, `false`, `off` и `no` (включая варианты регистра) преобразуются в `False`.

Если `short` не передан, **FastAPI** использует значение по умолчанию, в этом примере — `False`.

Пустое значение (`?short=`) или нераспознанное значение (например, `?short=maybe`) приводит к ошибке валидации `422`.

## Несколько параметров пути и запроса

Можно одновременно объявлять несколько параметров пути и параметров запроса — **FastAPI** знает, какой из них какой.

И объявлять их в каком-то определённом порядке не нужно.

Они будут распознаны по имени:

```python title="query_params/tutorial004_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
```

## Обязательные параметры запроса

Когда вы объявляете значение по умолчанию для параметров, не являющихся параметрами пути (пока мы видели только параметры запроса), такой параметр становится необязательным.

Если не нужно задавать конкретное значение, а нужно просто сделать параметр необязательным, задайте значение по умолчанию `None`.

А если параметр запроса нужно сделать обязательным, просто не объявляйте для него значение по умолчанию:

```python title="query_params/tutorial005_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item
```

Здесь параметр запроса `needy` — обязательный параметр запроса типа `str`.

Если открыть в браузере URL вида:

```
http://127.0.0.1:8000/items/foo-item
```

...не добавив обязательный параметр `needy`, вы увидите ошибку вроде:

```JSON
{
  "detail": [
    {
      "type": "missing",
      "loc": [
        "query",
        "needy"
      ],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

Поскольку `needy` — обязательный параметр, его нужно указать в URL:

```
http://127.0.0.1:8000/items/foo-item?needy=sooooneedy
```

...и это сработает:

```JSON
{
    "item_id": "foo-item",
    "needy": "sooooneedy"
}
```

И, конечно, можно сделать одни параметры обязательными, другие — со значением по умолчанию, а третьи — полностью необязательными:

```python title="query_params/tutorial006_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item
```

В этом случае есть 3 параметра запроса:

* `needy` — обязательный `str`.
* `skip` — `int` со значением по умолчанию `0`.
* `limit` — необязательный `int`.

> **Совет**
>
> `Enum` можно использовать точно так же, как с [параметрами пути](03-path-params.md).
