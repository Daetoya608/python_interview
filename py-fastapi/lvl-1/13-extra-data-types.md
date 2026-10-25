# Дополнительные типы данных

> Перевод страницы [Extra Data Types](https://fastapi.tiangolo.com/tutorial/extra-data-types/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

До сих пор вы использовали распространённые типы данных, такие как:

* `int`
* `float`
* `str`
* `bool`

Но можно использовать и более сложные типы данных.

И у вас по-прежнему будут все те же возможности, что вы видели до сих пор:

* Отличная поддержка редактора.
* Преобразование данных из входящих запросов.
* Преобразование данных для ответов.
* Валидация данных.
* Автоматическое аннотирование и документация.

## Другие типы данных

Вот некоторые дополнительные типы данных, которые можно использовать:

* `UUID`:
    * Стандартный «универсальный уникальный идентификатор» (Universally Unique Identifier), часто используемый как ID во многих базах данных и системах.
    * В запросах и ответах представляется как `str`.
* `datetime.datetime`:
    * `datetime.datetime` из Python.
    * В запросах и ответах представляется как `str` в формате ISO 8601, например: `2008-09-15T15:53:00+05:00`.
* `datetime.date`:
    * `datetime.date` из Python.
    * В запросах и ответах представляется как `str` в формате ISO 8601, например: `2008-09-15`.
* `datetime.time`:
    * `datetime.time` из Python.
    * В запросах и ответах представляется как `str` в формате ISO 8601, например: `14:23:55.003`.
* `datetime.timedelta`:
    * `datetime.timedelta` из Python.
    * В запросах и ответах представляется как `float` — общее число секунд.
    * Pydantic также позволяет представлять его в «кодировке разницы времени ISO 8601», [подробнее см. в документации](https://pydantic.dev/docs/validation/latest/concepts/serialization/#custom-serializers).
* `frozenset`:
    * В запросах и ответах обрабатывается так же, как `set`:
        * В запросах читается список, из него удаляются дубликаты, и он преобразуется в `set`.
        * В ответах `set` преобразуется в `list`.
        * В сгенерированной схеме будет указано, что значения `set` уникальны (с помощью `uniqueItems` из JSON Schema).
* `bytes`:
    * Стандартный `bytes` из Python.
    * В запросах и ответах обрабатывается как `str`.
    * В сгенерированной схеме будет указано, что это `str` с «форматом» `binary`.
* `Decimal`:
    * Стандартный `Decimal` из Python.
    * В запросах и ответах обрабатывается так же, как `float`.
* Все допустимые типы данных Pydantic можно посмотреть здесь: [Типы данных Pydantic](https://pydantic.dev/docs/validation/latest/concepts/types/).

## Пример

Вот пример *операции пути* с параметрами, использующими некоторые из перечисленных типов.

```python title="extra_data_types/tutorial001_an_py310.py"
from datetime import datetime, time, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Body, FastAPI

app = FastAPI()


@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }
```

Обратите внимание, что параметры внутри функции имеют свои естественные типы данных, и с ними можно, например, выполнять обычные операции над датами:

```python title="extra_data_types/tutorial001_an_py310.py"
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
```
