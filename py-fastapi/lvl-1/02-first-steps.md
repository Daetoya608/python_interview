# Первые шаги

> Перевод страницы [First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Простейший файл FastAPI может выглядеть так:

```python title="first_steps/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Скопируйте это в файл `main.py`.

> **Совет**
>
> У FastAPI есть [официальное расширение для VS Code](https://marketplace.visualstudio.com/items?itemName=FastAPILabs.fastapi-vscode) (и Cursor) с множеством возможностей: обозреватель операций пути, поиск операций пути, навигация CodeLens в тестах (переход к определению из тестов), а также развёртывание в FastAPI Cloud и просмотр логов — всё прямо из редактора.

Запустите сервер с автоперезагрузкой:

```console
$ uv run fastapi dev

   FastAPI   Starting development server 🚀

             Searching for package file structure from directories
             with __init__.py files
             Importing from /home/user/code/awesomeapp

    module   🐍 main.py

      code   Importing the FastAPI app object from the module with
             the following code:

             from main import app

       app   Using import string: main:app

    server   Server started at http://127.0.0.1:8000
    server   Documentation at http://127.0.0.1:8000/docs

       tip   Running in development mode, for production use:
             fastapi run

             Logs:

      INFO   Will watch for changes in these directories:
             ['/home/user/code/awesomeapp']
      INFO   Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C
             to quit)
      INFO   Started reloader process [383138] using WatchFiles
      INFO   Started server process [383153]
      INFO   Waiting for application startup.
      INFO   Application startup complete.
```

В выводе есть строка примерно такого вида:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Эта строка показывает URL, по которому ваше приложение доступно на локальной машине.

### Проверьте

Откройте в браузере [http://127.0.0.1:8000](http://127.0.0.1:8000).

Вы увидите JSON-ответ:

```JSON
{"message": "Hello World"}
```

### Интерактивная документация API

Теперь перейдите на [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Вы увидите автоматическую интерактивную документацию API (её предоставляет [Swagger UI](https://github.com/swagger-api/swagger-ui)):

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)

### Альтернативная документация API

А теперь перейдите на [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

Вы увидите альтернативную автоматическую документацию (её предоставляет [ReDoc](https://github.com/Redocly/redoc)):

![ReDoc](https://fastapi.tiangolo.com/img/index/index-02-redoc-simple.png)

### OpenAPI

**FastAPI** генерирует «схему» всего вашего API по стандарту **OpenAPI**, предназначенному для описания API.

#### «Схема»

«Схема» — это определение или описание чего-либо. Не код, который это реализует, а просто абстрактное описание.

#### «Схема» API

В данном случае [OpenAPI](https://github.com/OAI/OpenAPI-Specification) — это спецификация, которая определяет, как описывать схему вашего API.

Такое описание схемы включает пути вашего API, параметры, которые они могут принимать, и т. д.

#### «Схема» данных

Термин «схема» может также обозначать форму каких-либо данных, например содержимого JSON.

В этом случае имеются в виду атрибуты JSON, их типы данных и т. д.

#### OpenAPI и JSON Schema

OpenAPI определяет схему для вашего API. И эта схема включает определения (или «схемы») данных, которые ваш API отправляет и получает, с использованием **JSON Schema** — стандарта для схем данных JSON.

#### Посмотрите `openapi.json`

Если вам интересно, как выглядит «сырая» схема OpenAPI, — FastAPI автоматически генерирует JSON (схему) с описанием всего вашего API.

Её можно посмотреть напрямую по адресу: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json).

Вы увидите JSON, который начинается примерно так:

```JSON
{
    "openapi": "3.1.0",
    "info": {
        "title": "FastAPI",
        "version": "0.1.0"
    },
    "paths": {
        "/items/": {
            "get": {
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {



...
```

#### Для чего нужен OpenAPI

Схема OpenAPI — это то, на чём работают обе встроенные системы интерактивной документации.

Существуют десятки альтернатив, и все они основаны на OpenAPI. Любую из них можно легко добавить в приложение, созданное на **FastAPI**.

Схему также можно использовать для автоматической генерации кода клиентов, которые взаимодействуют с вашим API. Например, фронтенд-, мобильных или IoT-приложений.

### Настройка `entrypoint` приложения в `pyproject.toml`

Где находится ваше приложение, можно указать в файле `pyproject.toml`, например так:

```toml
[tool.fastapi]
entrypoint = "main:app"
```

Этот `entrypoint` сообщает команде `fastapi`, что приложение нужно импортировать так:

```python
from main import app
```

Если бы ваш код был организован так:

```
.
├── backend
│   ├── main.py
│   ├── __init__.py
```

то `entrypoint` нужно было бы указать так:

```toml
[tool.fastapi]
entrypoint = "backend.main:app"
```

что эквивалентно:

```python
from backend.main import app
```

### `fastapi dev` с путём или с опцией CLI `--entrypoint`

Можно также передать команде `fastapi dev` путь к файлу, и она сама определит, какой объект приложения FastAPI использовать:

```console
$ uv run fastapi dev main.py
```

Или можно передать команде `fastapi dev` опцию `--entrypoint`:

```console
$ uv run fastapi dev --entrypoint main:app
```

Но тогда придётся не забывать передавать правильный путь/entrypoint при каждом вызове команды `fastapi`.

Кроме того, другие инструменты могут не найти приложение, например [расширение для VS Code](https://fastapi.tiangolo.com/editor-support/) или [FastAPI Cloud](https://fastapicloud.com), поэтому рекомендуется использовать `entrypoint` в `pyproject.toml`.

### Развёртывание приложения (необязательно)

При желании можно развернуть приложение FastAPI в [FastAPI Cloud](https://fastapicloud.com) одной командой. 🚀

```console
$ uv run fastapi deploy

Deploying to FastAPI Cloud...

✅ Deployment successful!

🐔 Ready the chicken! Your app is ready at https://myapp.fastapicloud.dev
```

CLI автоматически обнаружит ваше приложение FastAPI и развернёт его в облаке. Если вы не вошли в систему, откроется браузер, чтобы завершить аутентификацию.

Вот и всё! Теперь приложение доступно по этому URL. ✨

## Итоги, шаг за шагом

### Шаг 1: импортируйте `FastAPI`

```python title="first_steps/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

`FastAPI` — это класс Python, который предоставляет всю функциональность для вашего API.

> **Примечание | Технические подробности**
>
> `FastAPI` — это класс, который напрямую наследуется от `Starlette`.
>
> С `FastAPI` можно использовать и всю функциональность [Starlette](https://starlette.dev/).

### Шаг 2: создайте «экземпляр» `FastAPI`

```python title="first_steps/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Здесь переменная `app` будет «экземпляром» класса `FastAPI`.

Это будет основная точка взаимодействия при создании всего вашего API.

### Шаг 3: создайте *операцию пути*

#### Путь

«Путь» здесь — это последняя часть URL, начиная с первого `/`.

То есть в URL вида:

```
https://example.com/items/foo
```

...путь будет:

```
/items/foo
```

> **Примечание**
>
> «Путь» также часто называют «эндпоинтом» (endpoint) или «маршрутом» (route).

При создании API «путь» — основной способ разделять «зоны ответственности» и «ресурсы».

#### Операция

«Операция» здесь — это один из HTTP-«методов».

Один из:

* `POST`
* `GET`
* `PUT`
* `DELETE`

...и более экзотические:

* `OPTIONS`
* `HEAD`
* `PATCH`
* `TRACE`

В протоколе HTTP к каждому пути можно обращаться с помощью одного (или нескольких) из этих «методов».

---

При создании API обычно используют определённые HTTP-методы для выполнения определённых действий.

Как правило:

* `POST`: создать данные.
* `GET`: прочитать данные.
* `PUT`: обновить данные.
* `DELETE`: удалить данные.

Поэтому в OpenAPI каждый из HTTP-методов называется «операцией».

Мы тоже будем называть их «**операциями**».

#### Определите *декоратор операции пути*

```python title="first_steps/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

`@app.get("/")` сообщает **FastAPI**, что функция прямо под ним отвечает за обработку запросов, которые приходят:

* на путь `/`
* с помощью <dfn title="HTTP-метод GET">операции <code>get</code></dfn>

> **Примечание | О `@декораторах`**
>
> Синтаксис `@something` в Python называется «декоратором».
>
> Его ставят над функцией. Как красивую декоративную шляпу (думаю, отсюда и пошёл термин).
>
> «Декоратор» берёт функцию под ним и что-то с ней делает.
>
> В нашем случае этот декоратор сообщает **FastAPI**, что функция под ним соответствует **пути** `/` с **операцией** `get`.
>
> Это «**декоратор операции пути**».

Можно использовать и другие операции:

* `@app.post()`
* `@app.put()`
* `@app.delete()`

И более экзотические:

* `@app.options()`
* `@app.head()`
* `@app.patch()`
* `@app.trace()`

> **Совет**
>
> Вы можете использовать каждую операцию (HTTP-метод) так, как считаете нужным.
>
> **FastAPI** не навязывает им никакого конкретного смысла.
>
> Информация здесь дана как рекомендация, а не как требование.
>
> Например, при использовании GraphQL обычно все действия выполняются только через операции `POST`.

### Шаг 4: определите **функцию операции пути**

Это наша «**функция операции пути**»:

* **путь**: `/`.
* **операция**: `get`.
* **функция**: функция под «декоратором» (под `@app.get("/")`).

```python title="first_steps/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Это функция Python.

**FastAPI** будет вызывать её каждый раз, когда получит запрос на URL «`/`» с операцией `GET`.

В данном случае это `async`-функция.

---

Её можно определить и как обычную функцию вместо `async def`:

```python title="first_steps/tutorial003_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}
```

> **Примечание**
>
> Если вы не знаете, в чём разница, загляните в раздел [Async: *«Нет времени?»*](https://fastapi.tiangolo.com/async/#in-a-hurry).

### Шаг 5: верните содержимое

```python title="first_steps/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Можно вернуть `dict`, `list`, отдельные значения вроде `str`, `int` и т. д.

Можно также возвращать модели Pydantic (подробнее об этом позже).

Есть много других объектов и моделей, которые будут автоматически преобразованы в JSON (включая ORM и т. п.). Попробуйте использовать ваши любимые — весьма вероятно, что они уже поддерживаются.

### Шаг 6: разверните приложение

Разверните приложение в **[FastAPI Cloud](https://fastapicloud.com)** одной командой: `fastapi deploy`. 🎉

#### О FastAPI Cloud

**[FastAPI Cloud](https://fastapicloud.com)** создан тем же автором и командой, что и **FastAPI**.

Он упрощает процесс **создания**, **развёртывания** и **доступа** к API с минимальными усилиями.

Он переносит тот же **опыт разработчика**, что и при создании приложений на FastAPI, на их **развёртывание** в облаке. 🎉

FastAPI Cloud — основной спонсор и источник финансирования open source-проектов *FastAPI and friends*. ✨

#### Развёртывание у других облачных провайдеров

FastAPI — open source-проект, основанный на стандартах. Приложения FastAPI можно развернуть у любого облачного провайдера по вашему выбору.

Следуйте руководствам вашего облачного провайдера, чтобы развернуть у него приложения FastAPI. 🤓

## Итоги

* Импортируйте `FastAPI`.
* Создайте экземпляр `app`.
* Напишите **декоратор операции пути**, например `@app.get("/")`.
* Определите **функцию операции пути**, например `def root(): ...`.
* Запустите сервер разработки командой `fastapi dev`.
* При желании разверните приложение командой `fastapi deploy`.
