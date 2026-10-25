# Модели форм

> Перевод страницы [Form Models](https://fastapi.tiangolo.com/tutorial/request-form-models/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

В FastAPI можно использовать **модели Pydantic** для объявления **полей формы**.

> **Примечание**
>
> Чтобы использовать формы, сначала установите [`python-multipart`](https://github.com/Kludex/python-multipart).
>
> Добавьте его в проект:
>
> ```console
> $ uv add python-multipart
> ```

> **Примечание**
>
> Это поддерживается начиная с версии FastAPI `0.113.0`. 🤓

## Модели Pydantic для форм

Нужно просто объявить **модель Pydantic** с полями, которые вы хотите получать как **поля формы**, а затем объявить параметр как `Form`:

```python title="request_form_models/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()


class FormData(BaseModel):
    username: str
    password: str


@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data
```

**FastAPI** **извлечёт** данные для **каждого поля** из **данных формы** в запросе и передаст вам определённую вами модель Pydantic.

Для [HTML-чекбоксов](21-request-forms.md) объявляйте булевы поля со значением по умолчанию `False`.

## Посмотрите документацию

Это можно проверить в интерфейсе документации по адресу `/docs`:

<img src="https://fastapi.tiangolo.com/img/tutorial/request-form-models/image01.png">

## Запрет лишних полей формы

В некоторых особых случаях (вероятно, не очень частых) может понадобиться **ограничить** поля формы только теми, что объявлены в модели Pydantic, и **запретить** любые **лишние** поля.

> **Примечание**
>
> Это поддерживается начиная с версии FastAPI `0.114.0`. 🤓

Можно использовать конфигурацию модели Pydantic, чтобы запретить (`forbid`) любые лишние (`extra`) поля:

```python title="request_form_models/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()


class FormData(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}


@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data
```

Если клиент попытается отправить лишние данные, он получит ответ с **ошибкой**.

Например, если клиент попытается отправить поля формы:

* `username`: `Rick`
* `password`: `Portal Gun`
* `extra`: `Mr. Poopybutthole`

он получит ответ с ошибкой, сообщающий, что поле `extra` не разрешено:

```json
{
    "detail": [
        {
            "type": "extra_forbidden",
            "loc": ["body", "extra"],
            "msg": "Extra inputs are not permitted",
            "input": "Mr. Poopybutthole"
        }
    ]
}
```

## Комбинирование моделей форм

Можно комбинировать несколько моделей форм с отдельными параметрами `Form`.

```python title="request_form_models/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()


class Profile(BaseModel):
    name: str


class Preferences(BaseModel):
    tags: list[str] = []


@app.post("/profiles/")
async def create_profile(
    profile: Annotated[Profile, Form()],
    preferences: Annotated[Preferences, Form()],
    token: Annotated[str, Form()],
):
    return {"profile": profile, "preferences": preferences, "token": token}
```

Клиент отправляет `name`, `tags` и `token` как поля формы. Каждая модель валидирует поля формы независимо.

Конфигурация `extra` каждой модели применяется ко всем полям формы, включая поля и файлы, объявленные в других параметрах или зависимостях. При `extra="forbid"` любое поле вне этой модели отклоняется. При `extra="allow"` такие поля попадают в модель как дополнительные (extras).

Если несколько объявлений используют одно и то же имя поля формы, каждое из них валидирует значение этого поля. Используйте совместимые типы и ограничения для общих полей, чтобы схема OpenAPI могла описать их согласованно.

## Необязательные модели форм

Объявите модель формы с `| None` и значением по умолчанию `None`, чтобы сделать всю группу необязательной.

```python title="request_form_models/tutorial005_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()


class Profile(BaseModel):
    name: str
    age: int


@app.post("/profiles/")
async def create_profile(
    token: Annotated[str, Form()],
    profile: Annotated[Profile | None, Form()] = None,
):
    return {"token": token, "profile": profile}
```

Если не передан ни `name`, ни `age`, `profile` будет `None`. Если передан хотя бы один из них, FastAPI валидирует модель и требует оба поля. Пустое отправленное значение тоже считается переданным полем.

Использование `| None` без значения по умолчанию по-прежнему делает параметр обязательным.

Лишние поля подчиняются конфигурации `extra` модели. Проигнорированные лишние поля не делают модель «присутствующей».

Необязательная модель, содержащая только неотмеченные чекбоксы, опускается. Чтобы передать её явно, отправьте значение, например `enabled=false`.

## Необязательные объединения моделей форм

Можно также использовать необязательное объединение моделей.

```python title="request_form_models/tutorial006_an_py310.py"
from typing import Annotated, Literal

from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()


class Person(BaseModel):
    kind: Literal["person"]
    name: str


class Company(BaseModel):
    kind: Literal["company"]
    company_name: str


@app.post("/contacts/")
async def create_contact(
    contact: Annotated[Person | Company | None, Form(discriminator="kind")] = None,
):
    return contact
```

Если поля формы не переданы, `contact` будет `None`. Отправьте `kind=person` вместе с `name` или `kind=company` вместе с `company_name`. Дискриминатор определяет, какую модель валидировать.

## Комбинирование объединений моделей форм

Объединения можно комбинировать с другими моделями форм, отдельными параметрами `Form` и параметрами `File`. Каждое объединение валидируется независимо.

```python title="request_form_models/tutorial007_an_py310.py"
from typing import Annotated, Literal

from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()


class Person(BaseModel):
    contact_type: Literal["person"]
    name: str


class Company(BaseModel):
    contact_type: Literal["company"]
    company_name: str


class Email(BaseModel):
    notification_type: Literal["email"]
    email: str


class SMS(BaseModel):
    notification_type: Literal["sms"]
    phone: str


@app.post("/contacts/")
async def create_contact(
    contact: Annotated[Person | Company, Form(discriminator="contact_type")],
    token: Annotated[str, Form()],
    notification: Annotated[
        Email | SMS | None, Form(discriminator="notification_type")
    ] = None,
):
    return {"contact": contact, "notification": notification, "token": token}
```

Отправляйте все поля в одной форме. Например: `contact_type=person`, `name=Rick`, `notification_type=email`, `email=rick@example.com` и `token=secret`.

Не передавайте поля уведомления, чтобы `notification` остался `None`.

## Модели форм и файлы

Модель формы можно также комбинировать с [параметрами-файлами](23-request-files.md).

```python title="request_form_models/tutorial004_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Form, UploadFile
from pydantic import BaseModel

app = FastAPI()


class Profile(BaseModel):
    name: str


@app.post("/profiles/")
async def create_profile(profile: Annotated[Profile, Form()], avatar: UploadFile):
    return {"profile": profile, "filename": avatar.filename}
```

Здесь клиент отправляет поле `name` и файл `avatar` в кодировке `multipart/form-data`.

## Итоги

В FastAPI можно использовать модели Pydantic для объявления полей формы. 😎
