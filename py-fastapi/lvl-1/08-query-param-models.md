# Модели параметров запроса

> Перевод страницы [Query Parameter Models](https://fastapi.tiangolo.com/tutorial/query-param-models/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Если у вас есть группа связанных **параметров запроса**, для их объявления можно создать **модель Pydantic**.

Это позволит **переиспользовать модель** во **многих местах**, а также объявить валидации и метаданные сразу для всех параметров. 😎

> **Примечание**
>
> Это поддерживается начиная с версии FastAPI `0.115.0`. 🤓

## Параметры запроса с моделью Pydantic

Объявите нужные **параметры запроса** в **модели Pydantic**, а затем объявите параметр как `Query`:

```python title="query_param_models/tutorial001_an_py310.py"
from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query
```

**FastAPI** **извлечёт** данные для **каждого поля** из **параметров запроса** и передаст вам определённую вами модель Pydantic.

## Посмотрите документацию

Параметры запроса можно увидеть в интерфейсе документации по адресу `/docs`:

<img src="https://fastapi.tiangolo.com/img/tutorial/query-param-models/image01.png">

## Запрет лишних параметров запроса

В некоторых особых случаях (вероятно, не очень частых) может понадобиться **ограничить** набор параметров запроса, которые вы готовы принимать.

Можно использовать конфигурацию модели Pydantic, чтобы запретить (`forbid`) любые лишние (`extra`) поля:

```python title="query_param_models/tutorial002_an_py310.py"
from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query
```

Если клиент попытается отправить **лишние** данные в **параметрах запроса**, он получит ответ с **ошибкой**.

Например, если клиент попытается отправить параметр запроса `tool` со значением `plumbus`:

```http
https://example.com/items/?limit=10&tool=plumbus
```

он получит ответ с **ошибкой**, сообщающий, что параметр запроса `tool` не разрешён:

```json
{
    "detail": [
        {
            "type": "extra_forbidden",
            "loc": ["query", "tool"],
            "msg": "Extra inputs are not permitted",
            "input": "plumbus"
        }
    ]
}
```

## Комбинирование моделей параметров

Можно объявить несколько моделей параметров запроса и комбинировать их с отдельными параметрами запроса или зависимостями.

```python title="query_param_models/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


class Pagination(BaseModel):
    limit: int = Field(10, ge=1)
    offset: int = Field(0, ge=0)


class Filters(BaseModel):
    tags: list[str] = []


@app.get("/items/")
def read_items(
    pagination: Annotated[Pagination, Query()],
    filters: Annotated[Filters, Query()],
    search: str | None = None,
):
    return {"pagination": pagination, "filters": filters, "search": search}
```

Параметры запроса остаются на одном уровне.

```http
https://example.com/items/?limit=5&offset=10&tags=red&tags=blue&search=shirt
```

В строке запроса нет ключей `pagination` или `filters`. Каждая модель валидирует параметры запроса независимо, со своими значениями по умолчанию, валидаторами полей и валидаторами модели. То же самое относится к случаю, когда модели или отдельные параметры объявлены в зависимостях.

Если у моделей совпадает имя или псевдоним параметра, каждая модель валидирует этот параметр запроса независимо. Для независимых значений используйте разные имена или псевдонимы. OpenAPI перечисляет общий параметр один раз — так же, как для параметров, общих с зависимостями, — поэтому общие объявления должны описывать один и тот же тип и ограничения.

Конфигурация `extra` каждой модели применяется ко всем параметрам запроса, включая объявленные в других моделях или зависимостях. При `extra="forbid"` любой параметр вне этой модели отклоняется. При `extra="allow"` такие параметры попадают в модель как дополнительные (extras).

Это работает и для моделей `Header` и `Cookie`.

## Необязательные модели параметров запроса

Объявите модель параметров запроса с `| None` и значением по умолчанию `None`, чтобы сделать всю группу необязательной.

```python title="query_param_models/tutorial004_an_py310.py"
from datetime import date
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()


class DateRange(BaseModel):
    start: date
    end: date


@app.get("/items/")
async def read_items(
    limit: int = 10,
    date_range: Annotated[DateRange | None, Query()] = None,
):
    return {"limit": limit, "date_range": date_range}
```

Если не передан ни `start`, ни `end`, `date_range` будет `None`. Если передан хотя бы один из них, FastAPI валидирует модель и требует оба поля.

Использование `| None` без значения по умолчанию по-прежнему делает параметр обязательным.

Лишние параметры подчиняются конфигурации `extra` модели. Проигнорированные лишние параметры не делают модель «присутствующей».

OpenAPI перечисляет поля группы по отдельности и помечает их как необязательные.

Можно также объявлять необязательные [модели параметров заголовков](17-header-param-models.md) и [модели параметров cookie](16-cookie-param-models.md).

## Итоги

В **FastAPI** можно использовать **модели Pydantic** для объявления **параметров запроса**. 😎

> **Совет**
>
> Спойлер: модели Pydantic можно также использовать для объявления cookie и заголовков, но об этом вы прочитаете позже в учебнике. 🤫
