# Параметры пути и валидация чисел

> Перевод страницы [Path Parameters and Numeric Validations](https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Так же как с помощью `Query` можно объявлять дополнительные валидации и метаданные для параметров запроса, с помощью `Path` можно объявлять такие же валидации и метаданные для параметров пути.

## Импортируйте `Path`

Сначала импортируйте `Path` из `fastapi`, а также импортируйте `Annotated`:

```python title="path_params_numeric_validations/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

> **Примечание**
>
> Поддержка `Annotated` появилась в FastAPI (и он начал рекомендовать её) в версии 0.95.0.
>
> В более старой версии при попытке использовать `Annotated` вы получите ошибки.
>
> Перед использованием `Annotated` убедитесь, что вы [обновили FastAPI](https://fastapi.tiangolo.com/deployment/versions/#upgrading-the-fastapi-versions) как минимум до 0.95.1.

## Объявите метаданные

Можно объявлять все те же параметры, что и для `Query`.

Например, чтобы объявить метаданные `title` для параметра пути `item_id`, можно написать:

```python title="path_params_numeric_validations/tutorial001_an_py310.py"
    item_id: Annotated[int, Path(title="The ID of the item to get")],
```

> **Примечание**
>
> Параметр пути всегда обязателен, потому что он должен быть частью пути URL. Добавление `None` к его типу не делает его необязательным. Параметр, объявленный через `Path`, не может иметь значения по умолчанию.

## Упорядочивайте параметры как вам нужно

> **Совет**
>
> Если вы используете `Annotated`, это, вероятно, не так важно и не так нужно.

Допустим, вы хотите объявить параметр запроса `q` как обязательный `str`.

И больше ничего для этого параметра объявлять не нужно, так что `Query` вам, по сути, не нужен.

Но для параметра пути `item_id` всё же нужно использовать `Path`. И по какой-то причине вы не хотите использовать `Annotated`.

Python будет ругаться, если поставить значение со «значением по умолчанию» перед значением, у которого его нет.

Но их можно переставить и поставить первым значение без значения по умолчанию (параметр запроса `q`).

Для **FastAPI** это неважно. Он определяет параметры по их именам, типам и объявлениям значений по умолчанию (`Query`, `Path` и т. д.), порядок его не волнует.

Так что функцию можно объявить так:

```python title="path_params_numeric_validations/tutorial002_py310.py"
from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(q: str, item_id: int = Path(title="The ID of the item to get")):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

Но помните: если использовать `Annotated`, этой проблемы не будет — это не важно, поскольку вы не используете значения по умолчанию параметров функции для `Query()` или `Path()`.

```python title="path_params_numeric_validations/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    q: str, item_id: Annotated[int, Path(title="The ID of the item to get")]
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

## Упорядочивайте параметры как вам нужно: хитрости

> **Совет**
>
> Если вы используете `Annotated`, это, вероятно, не так важно и не так нужно.

Вот **небольшая хитрость**, которая может пригодиться, хотя нужна она нечасто.

Если вы хотите:

* объявить параметр запроса `q` без `Query` и без какого-либо значения по умолчанию
* объявить параметр пути `item_id` через `Path`
* расположить их в другом порядке
* не использовать `Annotated`

...в Python для этого есть небольшой специальный синтаксис.

Передайте `*` первым параметром функции.

Python ничего не делает с этой `*`, но будет знать, что все следующие параметры должны передаваться как именованные аргументы (пары «ключ-значение»), также известные как <abbr title="От: K-ey W-ord Arg-uments — именованные аргументы"><code>kwargs</code></abbr>. Даже если у них нет значения по умолчанию.

```python title="path_params_numeric_validations/tutorial003_py310.py"
from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(*, item_id: int = Path(title="The ID of the item to get"), q: str):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

### Лучше с `Annotated`

Помните: если использовать `Annotated`, то, поскольку вы не используете значения по умолчанию параметров функции, этой проблемы не будет, и `*`, скорее всего, не понадобится.

```python title="path_params_numeric_validations/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")], q: str
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

## Валидация чисел: больше или равно

С помощью `Query` и `Path` (и других, которые вы увидите позже) можно объявлять ограничения на числа.

Здесь с `ge=1` значение `item_id` должно быть целым числом «больше или равным» (`g`reater than or `e`qual) `1`.

```python title="path_params_numeric_validations/tutorial004_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)], q: str
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

## Валидация чисел: больше и меньше или равно

То же самое относится к:

* `gt`: больше (`g`reater `t`han)
* `le`: меньше или равно (`l`ess than or `e`qual)

```python title="path_params_numeric_validations/tutorial005_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
    q: str,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

## Валидация чисел: float, больше и меньше

Валидация чисел работает и для значений `float`.

Здесь становится важно иметь возможность объявить <abbr title="больше"><code>gt</code></abbr>, а не только <abbr title="больше или равно"><code>ge</code></abbr>. С его помощью можно потребовать, например, чтобы значение было больше `0`, даже если оно меньше `1`.

Так что `0.5` будет допустимым значением. А `0.0` или `0` — нет.

То же самое для <abbr title="меньше"><code>lt</code></abbr>.

```python title="path_params_numeric_validations/tutorial006_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    *,
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str,
    size: Annotated[float, Query(gt=0, lt=10.5)],
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results
```

## Итоги

С помощью `Query`, `Path` (и других, которые вы ещё не видели) можно объявлять метаданные и валидацию строк так же, как в разделе [Параметры запроса и валидация строк](06-query-params-str-validations.md).

А также можно объявлять валидацию чисел:

* `gt`: больше (`g`reater `t`han)
* `ge`: больше или равно (`g`reater than or `e`qual)
* `lt`: меньше (`l`ess `t`han)
* `le`: меньше или равно (`l`ess than or `e`qual)

> **Примечание**
>
> `Query`, `Path` и другие классы, которые вы увидите позже, — подклассы общего класса `Param`.
>
> У всех них одинаковые параметры для дополнительной валидации и метаданных, которые вы уже видели.

> **Примечание | Технические подробности**
>
> Когда вы импортируете `Query`, `Path` и другие из `fastapi`, на самом деле это функции.
>
> При вызове они возвращают экземпляры классов с тем же именем.
>
> То есть вы импортируете `Query` — функцию. А когда вызываете её, она возвращает экземпляр класса, который тоже называется `Query`.
>
> Эти функции существуют (вместо прямого использования классов) для того, чтобы редактор не помечал ошибки, связанные с их типами.
>
> Так вы можете пользоваться обычным редактором и инструментами разработки, не добавляя специальных настроек, чтобы игнорировать такие ошибки.
