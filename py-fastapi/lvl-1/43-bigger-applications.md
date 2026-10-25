# Большие приложения — несколько файлов

> Перевод страницы [Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Если вы создаёте приложение или веб-API, редко получается уместить всё в одном файле.

**FastAPI** предоставляет удобный инструмент для структурирования приложения с сохранением всей гибкости.

> **Примечание**
>
> Если вы пришли из Flask, это эквивалент Blueprints во Flask.

## Пример структуры файлов

Допустим, у вас такая структура файлов:

```
.
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   └── routers
│   │   ├── __init__.py
│   │   ├── items.py
│   │   └── users.py
│   └── internal
│       ├── __init__.py
│       └── admin.py
```

> **Совет**
>
> Здесь несколько файлов `__init__.py`: по одному в каждой директории или поддиректории.
>
> Именно это позволяет импортировать код из одного файла в другой.
>
> Например, в `app/main.py` может быть такая строка:
>
> ```
> from app.routers import items
> ```

* Директория `app` содержит всё. В ней есть пустой файл `app/__init__.py`, поэтому это «пакет Python» (набор «модулей Python»): `app`.
* В ней есть файл `app/main.py`. Поскольку он находится внутри пакета Python (директории с файлом `__init__.py`), это «модуль» этого пакета: `app.main`.
* Есть также файл `app/dependencies.py` — как и `app/main.py`, это «модуль»: `app.dependencies`.
* Есть поддиректория `app/routers/` с ещё одним файлом `__init__.py`, так что это «подпакет Python»: `app.routers`.
* Файл `app/routers/items.py` находится внутри пакета `app/routers/`, значит, это подмодуль: `app.routers.items`.
* То же с `app/routers/users.py` — это ещё один подмодуль: `app.routers.users`.
* Есть также поддиректория `app/internal/` с ещё одним файлом `__init__.py`, так что это ещё один «подпакет Python»: `app.internal`.
* А файл `app/internal/admin.py` — ещё один подмодуль: `app.internal.admin`.

<img src="https://fastapi.tiangolo.com/img/tutorial/bigger-applications/package.drawio.svg">

Та же структура файлов с комментариями:

```bash
.
├── app                  # "app" — пакет Python
│   ├── __init__.py      # этот файл делает "app" «пакетом Python»
│   ├── main.py          # модуль "main", например import app.main
│   ├── dependencies.py  # модуль "dependencies", например import app.dependencies
│   └── routers          # "routers" — «подпакет Python»
│   │   ├── __init__.py  # делает "routers" «подпакетом Python»
│   │   ├── items.py     # подмодуль "items", например import app.routers.items
│   │   └── users.py     # подмодуль "users", например import app.routers.users
│   └── internal         # "internal" — «подпакет Python»
│       ├── __init__.py  # делает "internal" «подпакетом Python»
│       └── admin.py     # подмодуль "admin", например import app.internal.admin
```

## `APIRouter`

Допустим, файл, отвечающий только за пользователей, — это подмодуль `/app/routers/users.py`.

Вы хотите держать *операции пути*, относящиеся к пользователям, отдельно от остального кода, чтобы всё было организованно.

Но это по-прежнему часть того же приложения/веб-API **FastAPI** (часть того же «пакета Python»).

Создать *операции пути* для этого модуля можно с помощью `APIRouter`.

### Импортируйте `APIRouter`

Его импортируют и создают «экземпляр» так же, как с классом `FastAPI`:

```python title="app/routers/users.py"
from fastapi import APIRouter

router = APIRouter()
```

### *Операции пути* с `APIRouter`

А затем с его помощью объявляют *операции пути*.

Используйте его так же, как использовали бы класс `FastAPI`:

```python title="app/routers/users.py"
from fastapi import APIRouter

router = APIRouter()


@router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users/me", tags=["users"])
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/users/{username}", tags=["users"])
async def read_user(username: str):
    return {"username": username}
```

`APIRouter` можно считать классом «мини-`FastAPI`».

Поддерживаются все те же опции.

Все те же `parameters`, `responses`, `dependencies`, `tags` и т. д.

> **Совет**
>
> В этом примере переменная называется `router`, но назвать её можно как угодно.

Мы подключим этот `APIRouter` к основному приложению `FastAPI`, но сначала посмотрим на зависимости и ещё один `APIRouter`.

## Зависимости

Видно, что нам понадобятся зависимости, используемые в нескольких местах приложения.

Поэтому поместим их в собственный модуль `dependencies` (`app/dependencies.py`).

Сейчас мы используем простую зависимость, чтобы читать собственный заголовок `X-Token`:

```python title="app/dependencies.py"
from typing import Annotated

from fastapi import Header, HTTPException


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")
```

> **Совет**
>
> Чтобы упростить пример, мы используем придуманный заголовок.
>
> Но в реальных случаях лучших результатов можно добиться с помощью встроенных [утилит безопасности](35-security.md).

## Ещё один модуль с `APIRouter`

Допустим, в модуле `app/routers/items.py` у вас также есть эндпоинты для работы с «элементами» (items) приложения.

У вас есть *операции пути* для:

* `/items/`
* `/items/{item_id}`

Структура та же, что и в `app/routers/users.py`.

Но мы хотим поступить умнее и немного упростить код.

Мы знаем, что у всех *операций пути* в этом модуле одинаковые:

* `prefix` пути: `/items`.
* `tags`: (всего один тег: `items`).
* Дополнительные `responses`.
* `dependencies`: всем им нужна созданная нами зависимость `X-Token`.

Поэтому, вместо того чтобы добавлять всё это в каждую *операцию пути*, можно добавить это в `APIRouter`.

```python title="app/routers/items.py"
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_token_header

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/")
async def read_items():
    return fake_items_db


@router.get("/{item_id}")
async def read_item(item_id: str):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"name": fake_items_db[item_id]["name"], "item_id": item_id}


@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=403, detail="You can only update the item: plumbus"
        )
    return {"item_id": item_id, "name": "The great Plumbus"}
```

Поскольку путь каждой *операции пути* должен начинаться с `/`, как здесь:

```Python
@router.get("/{item_id}")
async def read_item(item_id: str): ...
```

...префикс не должен заканчиваться на `/`.

Так что префикс в данном случае — `/items`.

Можно также добавить список `tags` и дополнительные `responses`, которые будут применяться ко всем *операциям пути*, включённым в этот роутер.

И можно добавить список `dependencies`, которые будут добавлены ко всем *операциям пути* роутера и будут выполняться/разрешаться для каждого запроса к ним.

> **Совет**
>
> Обратите внимание: как и в случае с [зависимостями в *декораторах операций пути*](32-dependencies-in-path-operation-decorators.md), никакое значение не будет передано в *функцию операции пути*.

В итоге пути элементов теперь такие:

* `/items/`
* `/items/{item_id}`

...как мы и хотели.

* Они будут помечены списком тегов с одной строкой `"items"`.
    * Эти «теги» особенно полезны для систем автоматической интерактивной документации (на основе OpenAPI).
* Все они будут включать предопределённые `responses`.
* Перед всеми этими *операциями пути* будет вычисляться/выполняться список `dependencies`.
    * Если вы также объявите зависимости в конкретной *операции пути*, **они тоже будут выполнены**.
    * Сначала выполняются зависимости роутера, затем [`dependencies` в декораторе](32-dependencies-in-path-operation-decorators.md), а затем обычные зависимости-параметры.
    * Можно также добавить [зависимости `Security` со `scopes`](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/).

> **Совет**
>
> `dependencies` в `APIRouter` можно использовать, например, чтобы требовать аутентификацию для целой группы *операций пути*. Даже если зависимости не добавлены в каждую из них по отдельности.

> **Совет**
>
> Параметры `prefix`, `tags`, `responses` и `dependencies` — это (как и во многих других случаях) просто возможность **FastAPI**, помогающая избежать дублирования кода.

### Импортируйте зависимости

Этот код находится в модуле `app.routers.items`, в файле `app/routers/items.py`.

А нам нужно получить функцию-зависимость из модуля `app.dependencies`, файла `app/dependencies.py`.

Поэтому для зависимостей используем относительный импорт с `..`:

```python title="app/routers/items.py"
from ..dependencies import get_token_header
```

#### Как работают относительные импорты

> **Совет**
>
> Если вы прекрасно знаете, как работают импорты, переходите к следующему разделу.

Одна точка `.`, как здесь:

```Python
from .dependencies import get_token_header
```

означает:

* Начиная с того же пакета, в котором находится этот модуль (файл `app/routers/items.py`), — директории `app/routers/`...
* найти модуль `dependencies` (воображаемый файл `app/routers/dependencies.py`)...
* и импортировать из него функцию `get_token_header`.

Но такого файла не существует — наши зависимости находятся в файле `app/dependencies.py`.

Вспомните, как выглядит структура нашего приложения/файлов:

<img src="https://fastapi.tiangolo.com/img/tutorial/bigger-applications/package.drawio.svg">

---

Две точки `..`, как здесь:

```Python
from ..dependencies import get_token_header
```

означают:

* Начиная с того же пакета, в котором находится этот модуль (файл `app/routers/items.py`), — директории `app/routers/`...
* перейти в родительский пакет (директорию `app/`)...
* и там найти модуль `dependencies` (файл `app/dependencies.py`)...
* и импортировать из него функцию `get_token_header`.

Это работает правильно! 🎉

---

Точно так же, если бы мы использовали три точки `...`, как здесь:

```Python
from ...dependencies import get_token_header
```

это означало бы:

* Начиная с того же пакета, в котором находится этот модуль (файл `app/routers/items.py`), — директории `app/routers/`...
* перейти в родительский пакет (директорию `app/`)...
* затем перейти в родительский пакет этого пакета (родительского пакета нет, `app` — верхний уровень 😱)...
* и там найти модуль `dependencies` (файл `app/dependencies.py`)...
* и импортировать из него функцию `get_token_header`.

Это указывало бы на какой-то пакет выше `app/` со своим файлом `__init__.py` и т. д. Но такого у нас нет. Поэтому в нашем примере это вызвало бы ошибку. 🚨

Но теперь вы знаете, как это работает, и можете использовать относительные импорты в своих приложениях, какими бы сложными они ни были. 🤓

### Добавьте собственные `tags`, `responses` и `dependencies`

Мы не добавляем префикс `/items` и `tags=["items"]` в каждую *операцию пути*, потому что добавили их в `APIRouter`.

Но всё равно можно добавить _ещё_ `tags`, которые будут применяться к конкретной *операции пути*, а также дополнительные `responses`, специфичные для этой *операции пути*:

```python title="app/routers/items.py"
@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(item_id: str):
    ...
```

> **Совет**
>
> У этой последней операции пути будет комбинация тегов: `["items", "custom"]`.
>
> И в документации у неё будут оба ответа: один для `404` и один для `403`.

## Основной `FastAPI`

Теперь посмотрим на модуль `app/main.py`.

Здесь импортируется и используется класс `FastAPI`.

Это будет главный файл приложения, который связывает всё воедино.

А поскольку большая часть логики теперь будет находиться в собственных отдельных модулях, главный файл будет довольно простым.

### Импортируйте `FastAPI`

Импортируйте и создайте класс `FastAPI` как обычно.

Можно даже объявить [глобальные зависимости](33-global-dependencies.md), которые будут объединяться с зависимостями каждого `APIRouter`:

```python title="app/main.py"
from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

app = FastAPI(dependencies=[Depends(get_query_token)])


app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
```

### Импортируйте `APIRouter`

Теперь импортируем другие подмодули, в которых есть `APIRouter`:

```python title="app/main.py"
from .internal import admin
from .routers import items, users
```

Поскольку файлы `app/routers/users.py` и `app/routers/items.py` — подмодули, входящие в один и тот же пакет Python `app`, для их импорта можно использовать одну точку `.` («относительный импорт»).

### Как работает импорт

Фрагмент:

```Python
from .routers import items, users
```

означает:

* Начиная с того же пакета, в котором находится этот модуль (файл `app/main.py`), — директории `app/`...
* найти подпакет `routers` (директорию `app/routers/`)...
* и импортировать из него подмодули `items` (файл `app/routers/items.py`) и `users` (файл `app/routers/users.py`)...

В модуле `items` будет переменная `router` (`items.router`). Это тот же самый объект, который мы создали в файле `app/routers/items.py`, — объект `APIRouter`.

Затем делаем то же самое для модуля `users`.

Их можно было бы также импортировать так:

```Python
from app.routers import items, users
```

> **Примечание**
>
> Первый вариант — «относительный импорт»:
>
> ```Python
> from .routers import items, users
> ```
>
> Второй вариант — «абсолютный импорт»:
>
> ```Python
> from app.routers import items, users
> ```
>
> Чтобы узнать больше о пакетах и модулях Python, прочитайте [официальную документацию Python о модулях](https://docs.python.org/3/tutorial/modules.html).

### Избегайте конфликтов имён

Мы импортируем подмодуль `items` напрямую, а не только его переменную `router`.

Это потому, что в подмодуле `users` тоже есть переменная с именем `router`.

Если бы мы импортировали их одну за другой, вот так:

```Python
from .routers.items import router
from .routers.users import router
```

`router` из `users` перезаписал бы `router` из `items`, и мы не смогли бы использовать их одновременно.

Поэтому, чтобы использовать оба в одном файле, мы импортируем подмодули напрямую:

```python title="app/main.py"
from .routers import items, users
```

### Подключите `APIRouter` для `users` и `items`

Теперь подключим `router` из подмодулей `users` и `items`:

```python title="app/main.py"
app.include_router(users.router)
app.include_router(items.router)
```

> **Примечание**
>
> `users.router` содержит `APIRouter` из файла `app/routers/users.py`.
>
> А `items.router` содержит `APIRouter` из файла `app/routers/items.py`.

С помощью `app.include_router()` можно добавить каждый `APIRouter` в основное приложение `FastAPI`.

Это включит все маршруты этого роутера в приложение.

> **Примечание | Технические подробности**
>
> FastAPI сохраняет исходный `APIRouter` и его `APIRoute` активными, когда роутер подключается к основному приложению.
>
> Это означает, что пользовательские подклассы `APIRouter` и `APIRoute` продолжают участвовать в работе и после подключения роутера.

> **Совет**
>
> О производительности при подключении роутеров беспокоиться не нужно.
>
> Это спроектировано так, чтобы быть лёгким и не добавлять накладных расходов к каждому запросу.
>
> Так что на производительность это не повлияет. ⚡

### Подключение `APIRouter` с собственными `prefix`, `tags`, `responses` и `dependencies`

Теперь представим, что ваша организация дала вам файл `app/internal/admin.py`.

Он содержит `APIRouter` с несколькими административными *операциями пути*, которые организация использует в нескольких проектах.

В этом примере он будет совсем простым. Но допустим, что поскольку он общий для других проектов организации, мы не можем изменять его и добавлять `prefix`, `dependencies`, `tags` и т. д. непосредственно в `APIRouter`:

```python title="app/internal/admin.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def update_admin():
    return {"message": "Admin getting schwifty"}
```

Но мы всё равно хотим задать собственный `prefix` при подключении `APIRouter`, чтобы все его *операции пути* начинались с `/admin`, хотим защитить его `dependencies`, которые уже есть в этом проекте, и хотим добавить `tags` и `responses`.

Всё это можно объявить, не изменяя исходный `APIRouter`, — передав эти параметры в `app.include_router()`:

```python title="app/main.py"
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)
```

Так исходный `APIRouter` останется неизменным, и тот же файл `app/internal/admin.py` можно по-прежнему использовать в других проектах организации.

В результате в нашем приложении у каждой *операции пути* из модуля `admin` будут:

* Префикс `/admin`.
* Тег `admin`.
* Зависимость `get_token_header`.
* Ответ `418`. 🍵

Но это повлияет только на этот `APIRouter` в нашем приложении, а не на любой другой код, который его использует.

Так что, например, другие проекты могут использовать тот же `APIRouter` с другим методом аутентификации.

### Подключите *операцию пути*

*Операции пути* можно также добавлять непосредственно в приложение `FastAPI`.

Здесь мы делаем это... просто чтобы показать, что так можно 🤷:

```python title="app/main.py"
@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
```

и это будет правильно работать вместе со всеми остальными *операциями пути*, добавленными через `app.include_router()`.

> **Примечание | Очень технические подробности**
>
> **Примечание**: это очень техническая деталь, которую, скорее всего, можно **просто пропустить**.
>
> ---
>
> `APIRouter` не «монтируются», они не изолированы от остального приложения.
>
> Это потому, что мы хотим включать их *операции пути* в схему OpenAPI и пользовательские интерфейсы.
>
> FastAPI сохраняет исходные роутеры и операции пути активными и объединяет префиксы роутеров, зависимости, теги, ответы и другие метаданные при обработке запросов и генерации OpenAPI.

## Настройте `entrypoint` в `pyproject.toml`

Поскольку объект `app` FastAPI находится в `app/main.py`, `entrypoint` в файле `pyproject.toml` можно настроить так:

```toml
[tool.fastapi]
entrypoint = "app.main:app"
```

что эквивалентно импорту вида:

```python
from app.main import app
```

Так команда `fastapi` будет знать, где найти приложение.

> **Примечание**
>
> Можно также передать путь команде, например:
>
> ```console
> $ uv run fastapi dev app/main.py
> ```
>
> Но тогда придётся не забывать передавать правильный путь при каждом вызове команды `fastapi`.
>
> Кроме того, другие инструменты могут не найти приложение, например [расширение для VS Code](https://fastapi.tiangolo.com/editor-support/) или [FastAPI Cloud](https://fastapicloud.com), поэтому рекомендуется использовать `entrypoint` в `pyproject.toml`.

## Посмотрите автоматическую документацию API

Теперь запустите приложение:

```console
$ uv run fastapi dev

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

И откройте документацию по адресу [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Вы увидите автоматическую документацию API, включающую пути из всех подмодулей, с правильными путями (и префиксами) и правильными тегами:

<img src="https://fastapi.tiangolo.com/img/tutorial/bigger-applications/image01.png">

## Подключение одного роутера несколько раз с разными `prefix`

Можно также использовать `.include_router()` несколько раз с *одним и тем же* роутером, используя разные префиксы.

Это может пригодиться, например, чтобы предоставить один и тот же API под разными префиксами, например `/api/v1` и `/api/latest`.

Это продвинутое использование, которое вам, скорее всего, не понадобится, но оно есть на случай, если понадобится.

## Подключение `APIRouter` в другой

Так же как `APIRouter` можно подключить к приложению `FastAPI`, `APIRouter` можно подключить к другому `APIRouter` с помощью:

```Python
router.include_router(other_router)
```

Это можно сделать до или после подключения `router` к приложению `FastAPI`. FastAPI всё равно включит *операции пути* из `other_router` в маршрутизацию и OpenAPI.

То же касается *операций пути*, добавленных в роутеры позже. Они тоже будут видны через более раннее подключение.

> **Внимание | Технические подробности**
>
> Избегайте прямого изменения `router.routes` после подключения роутера. FastAPI считает подключение роутера «живым», поэтому исходный роутер и его маршруты остаются частью маршрутизации и генерации OpenAPI.
>
> Для добавления маршрутов и роутеров используйте документированные API, такие как декораторы операций пути и `.include_router()`.
>
> Рассматривайте `router.routes` как низкоуровневое дерево маршрутов, которое может содержать определения маршрутов и подключённые роутеры, и не полагайтесь на него как на плоский список итоговых операций пути.
