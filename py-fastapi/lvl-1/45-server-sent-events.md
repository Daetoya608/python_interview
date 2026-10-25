# Server-Sent Events (SSE)

> Перевод страницы [Server-Sent Events (SSE)](https://fastapi.tiangolo.com/tutorial/server-sent-events/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Передавать данные клиенту потоком можно с помощью **Server-Sent Events** (SSE, события, отправляемые сервером).

Это похоже на [потоковую передачу JSON Lines](44-stream-json-lines.md), но использует формат `text/event-stream`, который браузеры поддерживают нативно через [`EventSource` API](https://developer.mozilla.org/ru/docs/Web/API/EventSource).

> **Примечание**
>
> Добавлено в FastAPI 0.135.0.

## Что такое Server-Sent Events

SSE — это стандарт потоковой передачи данных от сервера клиенту по HTTP.

Каждое событие — небольшой текстовый блок с «полями» вроде `data`, `event`, `id` и `retry`, разделённый пустыми строками.

Выглядит это так:

```
data: {"name": "Portal Gun", "price": 999.99}

data: {"name": "Plumbus", "price": 32.99}

```

SSE обычно используют для потоковой передачи ответов ИИ-чатов, живых уведомлений, логов и мониторинга, а также других случаев, когда сервер отправляет клиенту обновления.

> **Совет**
>
> Если нужно передавать потоком бинарные данные, например видео или аудио, загляните в продвинутое руководство: [Потоковая передача данных](https://fastapi.tiangolo.com/advanced/stream-data/).

## Потоковая передача SSE в FastAPI

Чтобы передавать SSE потоком в FastAPI, используйте `yield` в *функции операции пути* и задайте `response_class=EventSourceResponse`.

Импортируйте `EventSourceResponse` из `fastapi.sse`:

```python title="server_sent_events/tutorial001_py310.py"
from collections.abc import AsyncIterable, Iterable

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None


items = [
    Item(name="Plumbus", description="A multi-purpose household device."),
    Item(name="Portal Gun", description="A portal opening device."),
    Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
]


@app.get("/items/stream", response_class=EventSourceResponse)
async def sse_items() -> AsyncIterable[Item]:
    for item in items:
        yield item
```

Каждый выданный через `yield` элемент кодируется в JSON и отправляется в поле `data:` SSE-события.

Если объявить тип возвращаемого значения как `AsyncIterable[Item]`, FastAPI будет использовать его, чтобы **валидировать**, **документировать** и **сериализовать** данные с помощью Pydantic.

> **Совет**
>
> Поскольку Pydantic будет сериализовать данные на стороне **Rust**, **производительность** будет гораздо выше, чем без объявления типа возвращаемого значения.

### Не-async *функции операций пути*

Можно также использовать обычные функции `def` (без `async`) и точно так же применять `yield`.

FastAPI позаботится о том, чтобы они выполнялись правильно и не блокировали цикл событий.

Поскольку в этом случае функция не асинхронная, правильным типом возвращаемого значения будет `Iterable[Item]`:

```python title="server_sent_events/tutorial001_py310.py"
@app.get("/items/stream-no-async", response_class=EventSourceResponse)
def sse_items_no_async() -> Iterable[Item]:
    for item in items:
        yield item
```

### Без типа возвращаемого значения

Тип возвращаемого значения можно и не указывать. FastAPI использует [`jsonable_encoder`](27-encoder.md), чтобы преобразовать данные и отправить их.

```python title="server_sent_events/tutorial001_py310.py"
@app.get("/items/stream-no-annotation", response_class=EventSourceResponse)
async def sse_items_no_annotation():
    for item in items:
        yield item
```

## `ServerSentEvent`

Если нужно задать поля SSE, такие как `event`, `id`, `retry` или `comment`, можно выдавать (`yield`) объекты `ServerSentEvent` вместо обычных данных.

Импортируйте `ServerSentEvent` из `fastapi.sse`:

```python title="server_sent_events/tutorial002_py310.py"
from collections.abc import AsyncIterable

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


items = [
    Item(name="Plumbus", price=32.99),
    Item(name="Portal Gun", price=999.99),
    Item(name="Meeseeks Box", price=49.99),
]


@app.get("/items/stream", response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(comment="stream of item updates")
    for i, item in enumerate(items):
        yield ServerSentEvent(data=item, event="item_update", id=str(i + 1), retry=5000)
```

Поле `data` всегда кодируется в JSON. Можно передать любое значение, которое можно сериализовать в JSON, включая модели Pydantic.

## Сырые данные

Если нужно отправить данные **без** кодирования в JSON, используйте `raw_data` вместо `data`.

Это полезно для отправки заранее отформатированного текста, строк логов или специальных <dfn title="Значение, используемое для обозначения особого условия или состояния">«сигнальных»</dfn> значений вроде `[DONE]`.

```python title="server_sent_events/tutorial003_py310.py"
from collections.abc import AsyncIterable

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent

app = FastAPI()


@app.get("/logs/stream", response_class=EventSourceResponse)
async def stream_logs() -> AsyncIterable[ServerSentEvent]:
    logs = [
        "2025-01-01 INFO  Application started",
        "2025-01-01 DEBUG Connected to database",
        "2025-01-01 WARN  High memory usage detected",
    ]
    for log_line in logs:
        yield ServerSentEvent(raw_data=log_line)
```

> **Примечание**
>
> `data` и `raw_data` взаимоисключающие. В каждом `ServerSentEvent` можно задать только одно из них.

## Возобновление с помощью `Last-Event-ID`

Когда браузер переподключается после обрыва соединения, он отправляет последний полученный `id` в заголовке `Last-Event-ID`.

Его можно прочитать как параметр заголовка и использовать, чтобы продолжить поток с того места, где остановился клиент:

```python title="server_sent_events/tutorial004_py310.py"
from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import FastAPI, Header
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


items = [
    Item(name="Plumbus", price=32.99),
    Item(name="Portal Gun", price=999.99),
    Item(name="Meeseeks Box", price=49.99),
]


@app.get("/items/stream", response_class=EventSourceResponse)
async def stream_items(
    last_event_id: Annotated[int | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    start = last_event_id + 1 if last_event_id is not None else 0
    for i, item in enumerate(items):
        if i < start:
            continue
        yield ServerSentEvent(data=item, id=str(i))
```

## SSE с POST

SSE работает с **любым HTTP-методом**, а не только с `GET`.

Это полезно для протоколов вроде [MCP](https://modelcontextprotocol.io), которые передают SSE поверх `POST`:

```python title="server_sent_events/tutorial005_py310.py"
from collections.abc import AsyncIterable

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()


class Prompt(BaseModel):
    text: str


@app.post("/chat/stream", response_class=EventSourceResponse)
async def stream_chat(prompt: Prompt) -> AsyncIterable[ServerSentEvent]:
    words = prompt.text.split()
    for word in words:
        yield ServerSentEvent(data=word, event="token")
    yield ServerSentEvent(raw_data="[DONE]", event="done")
```

## Технические подробности

FastAPI «из коробки» реализует некоторые лучшие практики SSE.

* Отправляет **комментарий `ping` для поддержания соединения** (keep alive) каждые 15 секунд, если не было сообщений, чтобы некоторые прокси не закрывали соединение, как рекомендует [спецификация HTML: Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html#authoring-notes).
* Устанавливает заголовок `Cache-Control: no-cache`, чтобы **предотвратить кэширование** потока.
* Устанавливает специальный заголовок `X-Accel-Buffering: no`, чтобы **предотвратить буферизацию** в некоторых прокси, например Nginx.

Ничего для этого делать не нужно — всё работает «из коробки». 🤓
