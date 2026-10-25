# Метаданные и URL документации

> Перевод страницы [Metadata and Docs URLs](https://fastapi.tiangolo.com/tutorial/metadata/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

В приложении **FastAPI** можно настроить несколько параметров метаданных.

## Метаданные API

Можно задать следующие поля, которые используются в спецификации OpenAPI и интерфейсах автоматической документации API:

| Параметр | Тип | Описание |
|------------|------|-------------|
| `title` | `str` | Название API. |
| `summary` | `str` | Краткое описание API. <small>Доступно начиная с OpenAPI 3.1.0, FastAPI 0.99.0.</small> |
| `description` | `str` | Короткое описание API. Можно использовать Markdown. |
| `version` | `str` | Версия API. Это версия вашего собственного приложения, а не OpenAPI. Например, `2.5.0`. |
| `terms_of_service` | `str` | URL условий использования (Terms of Service) API. Если указан, это должен быть URL. |
| `contact` | `dict` | Контактная информация для публикуемого API. Может содержать несколько полей. <details><summary>Поля <code>contact</code></summary><table><thead><tr><th>Параметр</th><th>Тип</th><th>Описание</th></tr></thead><tbody><tr><td><code>name</code></td><td><code>str</code></td><td>Имя контактного лица/организации.</td></tr><tr><td><code>url</code></td><td><code>str</code></td><td>URL, указывающий на контактную информацию. ДОЛЖЕН быть в формате URL.</td></tr><tr><td><code>email</code></td><td><code>str</code></td><td>Адрес электронной почты контактного лица/организации. ДОЛЖЕН быть в формате адреса электронной почты.</td></tr></tbody></table></details> |
| `license_info` | `dict` | Информация о лицензии публикуемого API. Может содержать несколько полей. <details><summary>Поля <code>license_info</code></summary><table><thead><tr><th>Параметр</th><th>Тип</th><th>Описание</th></tr></thead><tbody><tr><td><code>name</code></td><td><code>str</code></td><td><strong>ОБЯЗАТЕЛЬНО</strong> (если задан <code>license_info</code>). Название лицензии, используемой для API.</td></tr><tr><td><code>identifier</code></td><td><code>str</code></td><td>Выражение лицензии <a href="https://spdx.org/licenses/">SPDX</a> для API. Поле <code>identifier</code> взаимоисключающее с полем <code>url</code>. <small>Доступно начиная с OpenAPI 3.1.0, FastAPI 0.99.0.</small></td></tr><tr><td><code>url</code></td><td><code>str</code></td><td>URL лицензии, используемой для API. ДОЛЖЕН быть в формате URL.</td></tr></tbody></table></details> |

Задать их можно так:

```python title="metadata/tutorial001_py310.py"
from fastapi import FastAPI

description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title="ChimichangApp",
    description=description,
    summary="Deadpool's favorite app. Nuff said.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


@app.get("/items/")
async def read_items():
    return [{"name": "Katana"}]
```

> **Совет**
>
> В поле `description` можно писать на Markdown, и это будет отображено в выводе.

С такой конфигурацией автоматическая документация API будет выглядеть так:

<img src="https://fastapi.tiangolo.com/img/tutorial/metadata/image01.png">

## Идентификатор лицензии

Начиная с OpenAPI 3.1.0 и FastAPI 0.99.0, в `license_info` можно также указать `identifier` вместо `url`.

Например:

```python title="metadata/tutorial001_1_py310.py"
    license_info={
        "name": "Apache 2.0",
        "identifier": "Apache-2.0",
    },
```

## Метаданные тегов

С помощью параметра `openapi_tags` можно также добавить дополнительные метаданные для разных тегов, которыми группируются операции пути.

Он принимает список, содержащий по одному словарю на каждый тег.

Каждый словарь может содержать:

* `name` (**обязательно**): `str` с тем же именем тега, которое вы используете в параметре `tags` в *операциях пути* и `APIRouter`.
* `description`: `str` с коротким описанием тега. Может содержать Markdown и будет показан в интерфейсе документации.
* `externalDocs`: `dict`, описывающий внешнюю документацию, с полями:
    * `description`: `str` с коротким описанием внешней документации.
    * `url` (**обязательно**): `str` с URL внешней документации.

### Создайте метаданные тегов

Попробуем это на примере с тегами для `users` и `items`.

Создайте метаданные для тегов и передайте их в параметр `openapi_tags`:

```python title="metadata/tutorial004_py310.py"
from fastapi import FastAPI

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app = FastAPI(openapi_tags=tags_metadata)


@app.get("/users/", tags=["users"])
async def get_users():
    return [{"name": "Harry"}, {"name": "Ron"}]


@app.get("/items/", tags=["items"])
async def get_items():
    return [{"name": "wand"}, {"name": "flying broom"}]
```

Обратите внимание, что внутри описаний можно использовать Markdown, например «login» будет показан жирным (**login**), а «fancy» — курсивом (_fancy_).

> **Совет**
>
> Добавлять метаданные для всех используемых тегов не обязательно.

### Используйте теги

Используйте параметр `tags` в *операциях пути* (и `APIRouter`), чтобы отнести их к разным тегам — как `tags=["users"]` и `tags=["items"]` в примере выше.

> **Примечание**
>
> Подробнее о тегах читайте в разделе [Настройка операции пути](26-path-operation-configuration.md).

### Посмотрите документацию

Теперь, если открыть документацию, в ней будут показаны все дополнительные метаданные:

<img src="https://fastapi.tiangolo.com/img/tutorial/metadata/image02.png">

### Порядок тегов

Порядок словарей с метаданными тегов также определяет порядок, в котором они показываются в интерфейсе документации.

Например, хотя по алфавиту `users` шёл бы после `items`, он показывается перед ним, потому что мы добавили его метаданные первым словарём в списке.

## URL OpenAPI

По умолчанию схема OpenAPI отдаётся по адресу `/openapi.json`.

Но это можно настроить с помощью параметра `openapi_url`.

Например, чтобы она отдавалась по адресу `/api/v1/openapi.json`:

```python title="metadata/tutorial002_py310.py"
from fastapi import FastAPI

app = FastAPI(openapi_url="/api/v1/openapi.json")


@app.get("/items/")
async def read_items():
    return [{"name": "Foo"}]
```

Если нужно полностью отключить схему OpenAPI, можно задать `openapi_url=None` — это также отключит интерфейсы документации, которые её используют.

## URL документации

Можно настроить два встроенных интерфейса документации:

* **Swagger UI**: доступен по адресу `/docs`.
    * Его URL можно задать параметром `docs_url`.
    * Его можно отключить, задав `docs_url=None`.
* **ReDoc**: доступен по адресу `/redoc`.
    * Его URL можно задать параметром `redoc_url`.
    * Его можно отключить, задав `redoc_url=None`.

Например, чтобы Swagger UI был доступен по адресу `/documentation`, а ReDoc был отключён:

```python title="metadata/tutorial003_py310.py"
from fastapi import FastAPI

app = FastAPI(docs_url="/documentation", redoc_url=None)


@app.get("/items/")
async def read_items():
    return [{"name": "Foo"}]
```
