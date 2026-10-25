# Тестирование

> Перевод страницы [Testing](https://fastapi.tiangolo.com/tutorial/testing/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Благодаря [Starlette](https://starlette.dev/testclient/) тестировать приложения **FastAPI** легко и приятно.

Тестирование основано на [HTTPX](https://www.python-httpx.org), который, в свою очередь, спроектирован по образцу Requests, так что всё очень знакомо и интуитивно.

С его помощью можно напрямую использовать [pytest](https://docs.pytest.org/) с **FastAPI**.

## Использование `TestClient`

> **Примечание**
>
> Чтобы использовать `TestClient`, сначала установите [`httpx`](https://www.python-httpx.org).
>
> Добавьте его в проект:
>
> ```console
> $ uv add httpx
> ```

Импортируйте `TestClient`.

Создайте `TestClient`, передав ему своё приложение **FastAPI**.

Создайте функции, имена которых начинаются с `test_` (это стандартное соглашение `pytest`).

Используйте объект `TestClient` так же, как вы используете `httpx`.

Пишите простые инструкции `assert` со стандартными выражениями Python, которые нужно проверить (опять же, стандартный `pytest`).

```python title="app_testing/tutorial001_py310.py"
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
```

> **Совет**
>
> Обратите внимание, что тестовые функции — обычные `def`, а не `async def`.
>
> И вызовы клиента — тоже обычные вызовы, без `await`.
>
> Это позволяет использовать `pytest` напрямую без сложностей.

> **Примечание | Технические подробности**
>
> Можно также использовать `from starlette.testclient import TestClient`.
>
> **FastAPI** предоставляет тот же `starlette.testclient` в виде `fastapi.testclient` просто для удобства разработчика. Но он берётся напрямую из Starlette.

> **Совет**
>
> Если в тестах нужно вызывать `async`-функции помимо отправки запросов к приложению FastAPI (например, асинхронные функции работы с базой данных), загляните в раздел [Асинхронные тесты](https://fastapi.tiangolo.com/advanced/async-tests/) продвинутого руководства.

## Разделение тестов

В реальном приложении тесты, скорее всего, будут в отдельном файле.

А приложение **FastAPI** может состоять из нескольких файлов/модулей и т. д.

### Файл приложения **FastAPI**

Допустим, у вас структура файлов, как описано в разделе [Большие приложения](43-bigger-applications.md):

```
.
├── app
│   ├── __init__.py
│   └── main.py
```

В файле `main.py` находится приложение **FastAPI**:

```python title="app_testing/app_a_py310/main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}
```

### Файл тестов

Тогда тесты можно поместить в файл `test_main.py`. Он может находиться в том же пакете Python (той же директории с файлом `__init__.py`):

```
.
├── app
│   ├── __init__.py
│   ├── main.py
│   └── test_main.py
```

Поскольку этот файл находится в том же пакете, для импорта объекта `app` из модуля `main` (`main.py`) можно использовать относительный импорт:

```python title="app_testing/app_a_py310/test_main.py"
from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
```

...а код тестов остаётся таким же, как раньше.

## Тестирование: расширенный пример

Теперь расширим этот пример и добавим подробностей, чтобы посмотреть, как тестировать разные части.

### Расширенный файл приложения **FastAPI**

Продолжим с той же структурой файлов:

```
.
├── app
│   ├── __init__.py
│   ├── main.py
│   └── test_main.py
```

Допустим, теперь в файле `main.py` с приложением **FastAPI** есть и другие **операции пути**.

Есть операция `GET`, которая может вернуть ошибку.

Есть операция `POST`, которая может вернуть несколько ошибок.

Обеим *операциям пути* нужен заголовок `X-Token`.

```python title="app_testing/app_b_an_py310/main.py"
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

fake_secret_token = "coneofsilence"

fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}

app = FastAPI()


class Item(BaseModel):
    id: str
    title: str
    description: str | None = None


@app.get("/items/{item_id}", response_model=Item)
async def read_main(item_id: str, x_token: Annotated[str, Header()]):
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@app.post("/items/")
async def create_item(item: Item, x_token: Annotated[str, Header()]) -> Item:
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item.id in fake_db:
        raise HTTPException(status_code=409, detail="Item already exists")
    fake_db[item.id] = item.model_dump()
    return item
```

### Расширенный файл тестов

Затем можно обновить `test_main.py`, добавив расширенные тесты:

```python title="app_testing/app_b_an_py310/test_main.py"
from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_read_item():
    response = client.get("/items/foo", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "foo",
        "title": "Foo",
        "description": "There goes my hero",
    }


def test_read_item_bad_token():
    response = client.get("/items/foo", headers={"X-Token": "hailhydra"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid X-Token header"}


def test_read_nonexistent_item():
    response = client.get("/items/baz", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_create_item():
    response = client.post(
        "/items/",
        headers={"X-Token": "coneofsilence"},
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "foobar",
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }


def test_create_item_bad_token():
    response = client.post(
        "/items/",
        headers={"X-Token": "hailhydra"},
        json={"id": "bazz", "title": "Bazz", "description": "Drop the bazz"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid X-Token header"}


def test_create_existing_item():
    response = client.post(
        "/items/",
        headers={"X-Token": "coneofsilence"},
        json={
            "id": "foo",
            "title": "The Foo ID Stealers",
            "description": "There goes my stealer",
        },
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Item already exists"}
```

Если вам нужно, чтобы клиент передал какую-то информацию в запросе, а вы не знаете как, можно поискать (в Google), как сделать это в `httpx` или даже в `requests`, поскольку дизайн HTTPX основан на дизайне Requests.

Затем просто сделайте то же самое в своих тестах.

Например:

* Чтобы передать параметр *пути* или *запроса*, добавьте его прямо в URL.
* Чтобы передать JSON-тело, передайте объект Python (например, `dict`) в параметр `json`.
* Если нужно отправить *данные формы* вместо JSON, используйте параметр `data`.
* Чтобы передать *заголовки*, используйте `dict` в параметре `headers`.
* Для *cookie* — `dict` в параметре `cookies`.

Подробнее о том, как передавать данные в бэкенд (с помощью `httpx` или `TestClient`), смотрите в [документации HTTPX](https://www.python-httpx.org).

> **Примечание**
>
> Обратите внимание, что `TestClient` принимает данные, которые можно преобразовать в JSON, а не модели Pydantic.
>
> Если в тесте есть модель Pydantic и нужно отправить её данные в приложение во время тестирования, можно использовать `jsonable_encoder`, описанный в разделе [JSON-совместимый кодировщик](27-encoder.md).

## Запуск

После этого нужно просто установить `pytest`.

Добавьте его в проект:

```console
$ uv add pytest

---> 100%
```

Он автоматически обнаружит файлы и тесты, выполнит их и сообщит вам результаты.

Запустите тесты командой:

```console
$ uv run pytest

================ test session starts ================
platform linux -- Python 3.6.9, pytest-5.3.5, py-1.8.1, pluggy-0.13.1
rootdir: /home/user/code/superawesome-cli/app
plugins: forked-1.1.3, xdist-1.31.0, cov-2.8.1
collected 6 items

---> 100%

test_main.py ......                            [100%]

================= 1 passed in 0.03s =================
```
