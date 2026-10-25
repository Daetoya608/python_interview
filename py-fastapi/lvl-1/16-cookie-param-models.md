# Модели параметров cookie

> Перевод страницы [Cookie Parameter Models](https://fastapi.tiangolo.com/tutorial/cookie-param-models/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Если у вас есть группа связанных **cookie**, для их объявления можно создать **модель Pydantic**. 🍪

Это позволит **переиспользовать модель** во **многих местах**, а также объявить валидации и метаданные сразу для всех параметров. 😎

> **Примечание**
>
> Это поддерживается начиная с версии FastAPI `0.115.0`. 🤓

> **Совет**
>
> Этот же приём применим к `Query`, `Cookie` и `Header`. 😎

## Cookie с моделью Pydantic

Объявите нужные параметры **cookie** в **модели Pydantic**, а затем объявите параметр как `Cookie`:

```python title="cookie_param_models/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import Cookie, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Cookies(BaseModel):
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies
```

**FastAPI** **извлечёт** данные для **каждого поля** из **cookie**, полученных в запросе, и передаст вам определённую вами модель Pydantic.

## Посмотрите документацию

Объявленные cookie можно увидеть в интерфейсе документации по адресу `/docs`:

<img src="https://fastapi.tiangolo.com/img/tutorial/cookie-param-models/image01.png">

> **Примечание**
>
> Учтите, что поскольку **браузеры обрабатывают cookie** особым образом и «за кулисами», они **не** дают **JavaScript** легко с ними работать.
>
> Если открыть **интерфейс документации API** по адресу `/docs`, вы увидите **документацию** cookie для ваших *операций пути*.
>
> Но даже если **заполнить данные** и нажать «Execute», cookie не будут отправлены, потому что интерфейс документации работает на **JavaScript**, и вы увидите сообщение об **ошибке**, как будто ничего не ввели.

## Запрет лишних cookie

В некоторых особых случаях (вероятно, не очень частых) может понадобиться **ограничить** набор cookie, которые вы готовы принимать.

Теперь ваш API может сам управлять своим <dfn title="Это шутка, на всякий случай. К согласию на cookie это не имеет никакого отношения, но забавно, что теперь даже API может отвергнуть бедные cookie. Возьмите печеньку. 🍪">согласием на cookie</dfn>. 🤪🍪

Можно использовать конфигурацию модели Pydantic, чтобы запретить (`forbid`) любые лишние (`extra`) поля:

```python title="cookie_param_models/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import Cookie, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Cookies(BaseModel):
    model_config = {"extra": "forbid"}

    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies
```

Если клиент попытается отправить **лишние cookie**, он получит ответ с **ошибкой**.

Бедные баннеры cookie со всеми их стараниями получить ваше согласие — только чтобы <dfn title="Это ещё одна шутка. Не обращайте на меня внимания. Выпейте кофе к своей печеньке. ☕">API его отверг</dfn>. 🍪

Например, если клиент попытается отправить cookie `santa_tracker` со значением `good-list-please`, он получит ответ с **ошибкой**, сообщающий, что <dfn title="Санта не одобряет отсутствие печенья. 🎅 Ладно, больше никаких шуток про cookie.">cookie `santa_tracker` не разрешена</dfn>:

```json
{
    "detail": [
        {
            "type": "extra_forbidden",
            "loc": ["cookie", "santa_tracker"],
            "msg": "Extra inputs are not permitted",
            "input": "good-list-please",
        }
    ]
}
```

## Комбинирование моделей параметров

Можно комбинировать несколько моделей параметров cookie с отдельными параметрами cookie и зависимостями. Каждая модель извлекается и валидируется независимо, как описано для [моделей параметров запроса](08-query-param-models.md).

Конфигурация `extra` каждой модели применяется ко всем параметрам cookie, включая объявленные в других моделях или зависимостях. При `extra="forbid"` любая cookie вне этой модели отклоняется. При `extra="allow"` такие cookie попадают в модель как дополнительные (extras).

## Необязательные модели параметров cookie

Объявите модель параметров cookie с `| None` и значением по умолчанию `None`, чтобы сделать всю группу необязательной.

```python title="cookie_param_models/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import Cookie, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Preferences(BaseModel):
    theme: str
    locale: str


@app.get("/items/")
async def read_items(preferences: Annotated[Preferences | None, Cookie()] = None):
    return preferences
```

Если не передан ни `theme`, ни `locale`, `preferences` будет `None`. Если передан хотя бы один из них, FastAPI валидирует модель и требует оба поля.

Те же правила для значений по умолчанию, лишних полей и OpenAPI действуют, что и для [необязательных моделей параметров запроса](08-query-param-models.md).

## Итоги

В **FastAPI** можно использовать **модели Pydantic** для объявления <dfn title="Возьмите последнюю печеньку на дорожку. 🍪">**cookie**</dfn>. 😎
