# Модели параметров заголовков

> Перевод страницы [Header Parameter Models](https://fastapi.tiangolo.com/tutorial/header-param-models/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Если у вас есть группа связанных **параметров заголовков**, для их объявления можно создать **модель Pydantic**.

Это позволит **переиспользовать модель** во **многих местах**, а также объявить валидации и метаданные сразу для всех параметров. 😎

> **Примечание**
>
> Это поддерживается начиная с версии FastAPI `0.115.0`. 🤓

## Параметры заголовков с моделью Pydantic

Объявите нужные **параметры заголовков** в **модели Pydantic**, а затем объявите параметр как `Header`:

```python title="header_param_models/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@app.get("/items/")
async def read_items(headers: Annotated[CommonHeaders, Header()]):
    return headers
```

**FastAPI** **извлечёт** данные для **каждого поля** из **заголовков** запроса и передаст вам определённую вами модель Pydantic.

## Посмотрите документацию

Обязательные заголовки можно увидеть в интерфейсе документации по адресу `/docs`:

<img src="https://fastapi.tiangolo.com/img/tutorial/header-param-models/image01.png">

## Запрет лишних заголовков

В некоторых особых случаях (вероятно, не очень частых) может понадобиться **ограничить** набор заголовков, которые вы готовы принимать.

Можно использовать конфигурацию модели Pydantic, чтобы запретить (`forbid`) любые лишние (`extra`) поля:

```python title="header_param_models/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


class CommonHeaders(BaseModel):
    model_config = {"extra": "forbid"}

    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@app.get("/items/")
async def read_items(headers: Annotated[CommonHeaders, Header()]):
    return headers
```

Если клиент попытается отправить **лишние заголовки**, он получит ответ с **ошибкой**.

Например, если клиент попытается отправить заголовок `tool` со значением `plumbus`, он получит ответ с **ошибкой**, сообщающий, что параметр заголовка `tool` не разрешён:

```json
{
    "detail": [
        {
            "type": "extra_forbidden",
            "loc": ["header", "tool"],
            "msg": "Extra inputs are not permitted",
            "input": "plumbus",
        }
    ]
}
```

## Отключение преобразования подчёркиваний

Так же как и в обычных параметрах заголовков, символы подчёркивания в именах параметров **автоматически преобразуются в дефисы**.

Например, если в коде есть параметр заголовка `save_data`, ожидаемым HTTP-заголовком будет `save-data`, и в документации он будет показан именно так.

Если по какой-то причине нужно отключить это автоматическое преобразование, это можно сделать и для моделей Pydantic с параметрами заголовков.

```python title="header_param_models/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@app.get("/items/")
async def read_items(
    headers: Annotated[CommonHeaders, Header(convert_underscores=False)],
):
    return headers
```

> **Внимание**
>
> Прежде чем задавать `convert_underscores` равным `False`, помните, что некоторые HTTP-прокси и серверы запрещают использовать заголовки с подчёркиваниями.

## Комбинирование моделей параметров

Можно комбинировать несколько моделей параметров заголовков с отдельными параметрами заголовков и зависимостями. Каждая модель извлекается и валидируется независимо, как описано для [моделей параметров запроса](08-query-param-models.md).

Конфигурация `extra` каждой модели применяется ко всем параметрам заголовков, включая объявленные в других моделях или зависимостях. При `extra="forbid"` любой заголовок вне этой модели отклоняется. При `extra="allow"` такие заголовки попадают в модель как дополнительные (extras).

Каждая модель использует собственную настройку `Header(convert_underscores=...)` — и при чтении запроса, и при генерации OpenAPI. Явно заданные псевдонимы полей остаются буквальными именами заголовков.

## Необязательные модели параметров заголовков

Объявите модель параметров заголовков с `| None` и значением по умолчанию `None`, чтобы сделать всю группу необязательной.

```python title="header_param_models/tutorial004_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


class ClientHeaders(BaseModel):
    x_client_name: str
    x_client_version: str


@app.get("/items/")
async def read_items(client: Annotated[ClientHeaders | None, Header()] = None):
    return client
```

Если не передан ни `x-client-name`, ни `x-client-version`, `client` будет `None`. Если передан хотя бы один из них, FastAPI валидирует модель и требует оба поля.

Те же правила для значений по умолчанию, лишних полей и OpenAPI действуют, что и для [необязательных моделей параметров запроса](08-query-param-models.md).

Заголовки вроде `Host` тоже подчиняются конфигурации `extra` модели. При `extra="allow"` они делают модель «присутствующей», даже если ни одно из объявленных полей не передано.

## Итоги

В **FastAPI** можно использовать **модели Pydantic** для объявления **заголовков**. 😎
