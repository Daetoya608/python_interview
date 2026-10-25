# Параметры запроса и валидация строк

> Перевод страницы [Query Parameters and String Validations](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

**FastAPI** позволяет объявлять для параметров дополнительную информацию и валидацию.

Возьмём в качестве примера такое приложение:

```python title="query_params_str_validations/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/")
async def read_items(q: str | None = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

Параметр запроса `q` имеет тип `str | None`, то есть это `str`, но он может быть и `None`; и действительно, значение по умолчанию — `None`, так что FastAPI поймёт, что параметр не обязателен.

> **Примечание**
>
> FastAPI поймёт, что значение `q` не обязательно, благодаря значению по умолчанию `= None`.
>
> А `str | None` позволит редактору лучше вам помогать и находить ошибки.

## Дополнительная валидация

Мы сделаем так, чтобы, хотя `q` и необязателен, всякий раз, когда он передан, **его длина не превышала 50 символов**.

### Импортируйте `Query` и `Annotated`

Для этого сначала импортируйте:

* `Query` из `fastapi`
* `Annotated` из `typing`

```python title="query_params_str_validations/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
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

## Используйте `Annotated` в типе параметра `q`

Помните, я говорил раньше во [Введении в типы Python](https://fastapi.tiangolo.com/python-types/#type-hints-with-metadata-annotations), что `Annotated` можно использовать для добавления метаданных к параметрам?

Пора применить это в FastAPI. 🚀

У нас была такая аннотация типа:

```Python
q: str | None = None
```

Мы обернём её в `Annotated`, и получится:

```Python
q: Annotated[str | None] = None
```

Обе версии означают одно и то же: `q` — это параметр, который может быть `str` или `None`, и по умолчанию он равен `None`.

А теперь — к самому интересному. 🎉

## Добавьте `Query` в `Annotated` параметра `q`

Теперь, когда у нас есть `Annotated`, куда можно поместить дополнительную информацию (в данном случае — дополнительную валидацию), добавьте внутрь `Annotated` объект `Query` и задайте параметр `max_length` равным `50`:

```python title="query_params_str_validations/tutorial002_an_py310.py"
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

Обратите внимание, что значение по умолчанию по-прежнему `None`, так что параметр всё ещё необязателен.

Но теперь, поместив `Query(max_length=50)` внутрь `Annotated`, мы сообщаем FastAPI, что хотим **дополнительную валидацию** этого значения — максимум 50 символов. 😎

> **Совет**
>
> Здесь мы используем `Query()`, потому что это **параметр запроса**. Позже мы увидим и другие — `Path()`, `Body()`, `Header()` и `Cookie()`, — которые принимают те же аргументы, что и `Query()`.

Теперь FastAPI будет:

* **Валидировать** данные, проверяя, что максимальная длина — 50 символов
* Показывать клиенту **понятную ошибку**, если данные невалидны
* **Документировать** параметр в *операции пути* схемы OpenAPI (так что он появится в **интерфейсе автоматической документации**)

## Альтернатива (устаревшая): `Query` как значение по умолчанию

Предыдущие версии FastAPI (до <dfn title="до 2023-03">0.95.0</dfn>) требовали использовать `Query` как значение по умолчанию параметра, а не помещать его в `Annotated`. Велика вероятность, что вы будете встречать такой код, поэтому я его объясню.

> **Совет**
>
> В новом коде и везде, где возможно, используйте `Annotated`, как описано выше. У него множество преимуществ (объяснены ниже) и никаких недостатков. 🍰

Вот как можно использовать `Query()` в качестве значения по умолчанию параметра функции, задав параметр `max_length` равным 50:

```python title="query_params_str_validations/tutorial002_py310.py"
from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: str | None = Query(default=None, max_length=50)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

Поскольку в этом случае (без `Annotated`) нам приходится заменить значение по умолчанию `None` в функции на `Query()`, теперь значение по умолчанию нужно задавать параметром `Query(default=None)` — он служит той же цели определения значения по умолчанию (по крайней мере для FastAPI).

Итак:

```Python
q: str | None = Query(default=None)
```

...делает параметр необязательным со значением по умолчанию `None`, так же как:

```Python
q: str | None = None
```

Но версия с `Query` явно объявляет его как параметр запроса.

Затем в `Query` можно передать дополнительные параметры. В данном случае — параметр `max_length`, который применяется к строкам:

```Python
q: str | None = Query(default=None, max_length=50)
```

Это провалидирует данные, покажет понятную ошибку, если данные невалидны, и задокументирует параметр в *операции пути* схемы OpenAPI.

### `Query` как значение по умолчанию или в `Annotated`

Помните, что при использовании `Query` внутри `Annotated` нельзя использовать параметр `default` у `Query`.

Вместо этого используйте настоящее значение по умолчанию параметра функции. Иначе возникнет противоречие.

Например, так нельзя:

```Python
q: Annotated[str, Query(default="rick")] = "morty"
```

...потому что непонятно, каким должно быть значение по умолчанию: `"rick"` или `"morty"`.

Поэтому следует писать (предпочтительно):

```Python
q: Annotated[str, Query()] = "rick"
```

...а в старых кодовых базах вы встретите:

```Python
q: str = Query(default="rick")
```

### Преимущества `Annotated`

**Рекомендуется использовать `Annotated`** вместо значения по умолчанию в параметрах функции — это **лучше** по нескольким причинам. 🤓

**Значение по умолчанию** **параметра функции** — это **настоящее значение по умолчанию**, что в целом более интуитивно для Python. 😌

Ту же функцию можно **вызвать** в **других местах** без FastAPI, и она **будет работать как ожидается**. Если есть **обязательный** параметр (без значения по умолчанию), **редактор** сообщит об ошибке, и **Python** тоже пожалуется, если запустить функцию без обязательного параметра.

Если вы не используете `Annotated`, а применяете **(устаревший) стиль со значением по умолчанию**, то при вызове этой функции без FastAPI в **других местах** нужно **помнить**, что аргументы надо передать, чтобы она работала правильно, иначе значения окажутся не такими, как вы ожидаете (например, `QueryInfo` или что-то подобное вместо `str`). И ни редактор, ни Python при запуске функции не пожалуются — ошибка возникнет только тогда, когда сломаются операции внутри.

Поскольку у `Annotated` может быть больше одной аннотации метаданных, ту же функцию теперь можно использовать даже с другими инструментами, например [Typer](https://typer.tiangolo.com/). 🚀

## Добавьте больше валидаций

Можно также добавить параметр `min_length`:

```python title="query_params_str_validations/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

## Добавьте регулярные выражения

Можно задать `pattern` — <dfn title="Регулярное выражение (regex, regexp) — последовательность символов, задающая шаблон поиска в строках.">регулярное выражение</dfn>, которому должен соответствовать параметр:

```python title="query_params_str_validations/tutorial004_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")
    ] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

Этот конкретный шаблон регулярного выражения проверяет, что полученное значение параметра:

* `^`: начинается со следующих символов, перед ними ничего нет.
* `fixedquery`: имеет точное значение `fixedquery`.
* `$`: на этом заканчивается, после `fixedquery` больше нет символов.

Если вы теряетесь во всех этих идеях **«регулярных выражений»**, не переживайте. Для многих это сложная тема. Многое можно сделать и без них.

Теперь вы знаете, что, когда они понадобятся, их можно использовать в **FastAPI**.

## Значения по умолчанию

Конечно, можно использовать значения по умолчанию, отличные от `None`.

Допустим, вы хотите объявить параметр запроса `q` с `min_length` равным `3` и значением по умолчанию `"fixedquery"`:

```python title="query_params_str_validations/tutorial005_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[str, Query(min_length=3)] = "fixedquery"):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

> **Примечание**
>
> Наличие значения по умолчанию любого типа, включая `None`, делает параметр необязательным.

## Обязательные параметры

Когда не нужно объявлять дополнительные валидации или метаданные, параметр запроса `q` можно сделать обязательным, просто не объявляя значение по умолчанию:

```Python
q: str
```

вместо:

```Python
q: str | None = None
```

Но сейчас мы объявляем его с `Query`, например так:

```Python
q: Annotated[str | None, Query(min_length=3)] = None
```

Поэтому, если при использовании `Query` нужно сделать значение обязательным, можно просто не объявлять значение по умолчанию:

```python title="query_params_str_validations/tutorial006_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[str, Query(min_length=3)]):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

### Обязательные параметры и `None`

Тип `str | None` допускает `None` как значение Python, но не делает параметр запроса необязательным. Без значения по умолчанию параметр по-прежнему обязателен:

```python title="query_params_str_validations/tutorial006c_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(min_length=3)]):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

Значения параметров запроса приходят как строки, и у них нет встроенного представления `None`. Передача `?q=None` или `?q=null` отправляет строки `"None"` и `"null"` соответственно. Передача `?q=` отправляет пустую строку, которая в этом примере не проходит валидацию `min_length=3`.

Чтобы клиенты могли не передавать `q` и использовать `None` в качестве его значения, задайте значение по умолчанию `None`:

```Python
q: Annotated[str | None, Query(min_length=3)] = None
```

В отличие от параметров запроса, тела запросов в JSON могут содержать явное значение `null`.

## Список параметров запроса / несколько значений

Когда вы явно объявляете параметр запроса через `Query`, можно также указать, что он принимает список значений, иначе говоря — несколько значений.

Например, чтобы объявить параметр запроса `q`, который может встречаться в URL несколько раз, можно написать:

```python title="query_params_str_validations/tutorial011_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[list[str] | None, Query()] = None):
    query_items = {"q": q}
    return query_items
```

Тогда при URL вида:

```
http://localhost:8000/items/?q=foo&q=bar
```

вы получите несколько значений *параметра запроса* `q` (`foo` и `bar`) в виде `list` Python внутри *функции операции пути*, в *параметре функции* `q`.

Поэтому ответ на этот URL будет таким:

```JSON
{
  "q": [
    "foo",
    "bar"
  ]
}
```

> **Совет**
>
> Чтобы объявить параметр запроса с типом `list`, как в примере выше, нужно явно использовать `Query`, иначе он будет интерпретирован как тело запроса.

Интерактивная документация API соответственно обновится, чтобы позволять несколько значений:

<img src="https://fastapi.tiangolo.com/img/tutorial/query-params-str-validations/image02.png">

### Список параметров запроса / несколько значений со значениями по умолчанию

Можно также задать `list` значений по умолчанию на случай, если ничего не передано:

```python title="query_params_str_validations/tutorial012_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[list[str], Query()] = ["foo", "bar"]):
    query_items = {"q": q}
    return query_items
```

Если перейти по:

```
http://localhost:8000/items/
```

значением `q` по умолчанию будет `["foo", "bar"]`, и ответ будет таким:

```JSON
{
  "q": [
    "foo",
    "bar"
  ]
}
```

#### Просто `list`

Можно также использовать `list` напрямую вместо `list[str]`:

```python title="query_params_str_validations/tutorial013_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[list, Query()] = []):
    query_items = {"q": q}
    return query_items
```

> **Примечание**
>
> Учтите, что в этом случае FastAPI не будет проверять содержимое списка.
>
> Например, `list[int]` проверил бы (и задокументировал), что содержимое списка — целые числа. А просто `list` — нет.

## Объявите больше метаданных

Можно добавить больше информации о параметре.

Эта информация будет включена в сгенерированный OpenAPI и использована интерфейсами документации и внешними инструментами.

> **Примечание**
>
> Учтите, что разные инструменты могут поддерживать OpenAPI в разной степени.
>
> Некоторые из них пока могут не показывать всю объявленную дополнительную информацию, хотя в большинстве случаев недостающая возможность уже запланирована к разработке.

Можно добавить `title`:

```python title="query_params_str_validations/tutorial007_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(
    q: Annotated[str | None, Query(title="Query string", min_length=3)] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

И `description`:

```python title="query_params_str_validations/tutorial008_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
        ),
    ] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

## Псевдонимы параметров

Представьте, что вы хотите, чтобы параметр назывался `item-query`.

Как здесь:

```
http://127.0.0.1:8000/items/?item-query=foobaritems
```

Но `item-query` — недопустимое имя переменной в Python.

Ближайший вариант — `item_query`.

А вам всё равно нужно, чтобы он назывался именно `item-query`...

Тогда можно объявить `alias` (псевдоним), и именно он будет использоваться для поиска значения параметра:

```python title="query_params_str_validations/tutorial009_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(alias="item-query")] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

## Пометка параметров как устаревших

Теперь допустим, что этот параметр вам больше не нравится.

Его придётся оставить на какое-то время, потому что им пользуются клиенты, но вы хотите, чтобы документация явно показывала его как <dfn title="устаревший, использовать не рекомендуется">deprecated</dfn>.

Тогда передайте в `Query` параметр `deprecated=True`:

```python title="query_params_str_validations/tutorial010_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
    ] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

Документация покажет это так:

<img src="https://fastapi.tiangolo.com/img/tutorial/query-params-str-validations/image01.png">

## Исключение параметров из OpenAPI

Чтобы исключить параметр запроса из сгенерированной схемы OpenAPI (а значит, и из систем автоматической документации), задайте параметр `include_in_schema` у `Query` равным `False`:

```python title="query_params_str_validations/tutorial014_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(
    hidden_query: Annotated[str | None, Query(include_in_schema=False)] = None,
):
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not found"}
```

## Пользовательская валидация

Бывают случаи, когда нужна **пользовательская валидация**, которую нельзя сделать с помощью показанных выше параметров.

В таких случаях можно использовать **пользовательскую функцию-валидатор**, которая применяется после обычной валидации (например, после проверки, что значение — `str`).

Этого можно добиться с помощью [`AfterValidator` из Pydantic](https://pydantic.dev/docs/validation/latest/concepts/validators/#field-after-validator) внутри `Annotated`.

> **Совет**
>
> В Pydantic есть также [`BeforeValidator`](https://pydantic.dev/docs/validation/latest/concepts/validators/#field-before-validator) и другие. 🤓

Например, этот пользовательский валидатор проверяет, что ID элемента начинается с `isbn-` для номера книги <abbr title="International Standard Book Number — Международный стандартный книжный номер">ISBN</abbr> или с `imdb-` для ID фильма в URL <abbr title="Internet Movie Database: сайт с информацией о фильмах">IMDB</abbr>:

```python title="query_params_str_validations/tutorial015_an_py310.py"
import random
from typing import Annotated

from fastapi import FastAPI
from pydantic import AfterValidator

app = FastAPI()

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


@app.get("/items/")
async def read_items(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}
```

> **Примечание**
>
> Это доступно в Pydantic версии 2 и выше. 😎

> **Совет**
>
> Если нужна валидация, требующая обращения к какому-либо **внешнему компоненту**, например к базе данных или другому API, вместо этого следует использовать **зависимости FastAPI** — вы узнаете о них позже.
>
> Эти пользовательские валидаторы предназначены для того, что можно проверить, используя **только** **те же данные**, что пришли в запросе.

### Разбор этого кода

Главное — просто использовать **`AfterValidator` с функцией внутри `Annotated`**. Эту часть можно смело пропустить. 🤸

---

Но если вам интересен этот конкретный пример кода и вы ещё не заскучали, вот несколько дополнительных подробностей.

#### Строка с `value.startswith()`

Заметили? Метод строки `value.startswith()` может принимать кортеж и проверит каждое значение в нём:

```python title="query_params_str_validations/tutorial015_an_py310.py"
def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id
```

#### Случайный элемент

С помощью `data.items()` мы получаем <dfn title="Нечто, по чему можно пройти циклом for, например list, set и т. д.">итерируемый объект</dfn> с кортежами, содержащими ключ и значение каждого элемента словаря.

Мы преобразуем этот итерируемый объект в настоящий `list` с помощью `list(data.items())`.

Затем с помощью `random.choice()` получаем **случайное значение** из списка — кортеж `(id, name)`. Это будет что-то вроде `("imdb-tt0371724", "The Hitchhiker's Guide to the Galaxy")`.

Потом мы **присваиваем эти два значения** кортежа переменным `id` и `name`.

Так что, если пользователь не передал ID элемента, он всё равно получит случайную рекомендацию.

...и всё это в **одной простой строке**. 🤯 Разве можно не любить Python? 🐍

```python title="query_params_str_validations/tutorial015_an_py310.py"
@app.get("/items/")
async def read_items(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}
```

## Итоги

Для параметров можно объявлять дополнительные валидации и метаданные.

Общие валидации и метаданные:

* `alias`
* `title`
* `description`
* `deprecated`

Валидации, специфичные для строк:

* `min_length`
* `max_length`
* `pattern`

Пользовательские валидации с помощью `AfterValidator`.

В этих примерах вы видели, как объявлять валидации для значений `str`.

В следующих главах вы узнаете, как объявлять валидации для других типов, например чисел.
