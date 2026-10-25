# Обработка ошибок

> Перевод страницы [Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Существует множество ситуаций, когда нужно сообщить об ошибке клиенту, использующему ваш API.

Этим клиентом может быть браузер с фронтендом, чужой код, IoT-устройство и т. д.

Может понадобиться сообщить клиенту, что:

* У клиента недостаточно прав для этой операции.
* У клиента нет доступа к этому ресурсу.
* Элемент, к которому клиент пытался обратиться, не существует.
* и т. д.

В таких случаях обычно возвращается **HTTP-код статуса** в диапазоне **400** (от 400 до 499).

Это похоже на HTTP-коды статуса 200 (от 200 до 299). Коды «200» означают, что запрос в каком-то смысле был «успешным».

Коды статуса в диапазоне 400 означают, что ошибка произошла на стороне клиента.

Помните все эти ошибки (и шутки) **«404 Not Found»**?

## Используйте `HTTPException`

Чтобы вернуть клиенту HTTP-ответ с ошибкой, используется `HTTPException`.

### Импортируйте `HTTPException`

```python title="handling_errors/tutorial001_py310.py"
from fastapi import FastAPI, HTTPException

app = FastAPI()

items = {"foo": "The Foo Wrestlers"}


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}
```

### Возбудите `HTTPException` в своём коде

`HTTPException` — это обычное исключение Python с дополнительными данными, относящимися к API.

Поскольку это исключение Python, его не возвращают (`return`), а возбуждают (`raise`).

Это также значит, что если вы находитесь внутри вспомогательной функции, которую вызываете из *функции операции пути*, и возбуждаете `HTTPException` внутри этой вспомогательной функции, то остальной код *функции операции пути* не выполнится — запрос будет сразу завершён, и клиенту будет отправлена HTTP-ошибка из `HTTPException`.

Преимущество возбуждения исключения перед возвратом значения станет более очевидным в разделе о зависимостях и безопасности.

В этом примере, когда клиент запрашивает элемент по несуществующему ID, мы возбуждаем исключение с кодом статуса `404`:

```python title="handling_errors/tutorial001_py310.py"
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
```

### Итоговый ответ

Если клиент запросит `http://example.com/items/foo` (`item_id` равен `"foo"`), он получит HTTP-код статуса 200 и JSON-ответ:

```JSON
{
  "item": "The Foo Wrestlers"
}
```

Но если клиент запросит `http://example.com/items/bar` (несуществующий `item_id` `"bar"`), он получит HTTP-код статуса 404 (ошибка «не найдено») и JSON-ответ:

```JSON
{
  "detail": "Item not found"
}
```

> **Совет**
>
> При возбуждении `HTTPException` в параметре `detail` можно передать любое значение, которое можно преобразовать в JSON, а не только `str`.
>
> Можно передать `dict`, `list` и т. д.
>
> **FastAPI** обработает их автоматически и преобразует в JSON.

## Добавление собственных заголовков

Бывают ситуации, когда полезно добавить к HTTP-ошибке собственные заголовки. Например, для некоторых видов безопасности.

Скорее всего, вам не придётся использовать это напрямую в своём коде.

Но если это понадобится для продвинутого сценария, собственные заголовки можно добавить так:

```python title="handling_errors/tutorial002_py310.py"
from fastapi import FastAPI, HTTPException

app = FastAPI()

items = {"foo": "The Foo Wrestlers"}


@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}
```

## Установка собственных обработчиков исключений

Собственные обработчики исключений можно добавлять с помощью [тех же утилит для исключений из Starlette](https://starlette.dev/exceptions/).

Допустим, у вас есть собственное исключение `UnicornException`, которое вы (или используемая вами библиотека) можете возбудить (`raise`).

И вы хотите обрабатывать это исключение глобально с помощью FastAPI.

Можно добавить собственный обработчик исключений с помощью `@app.exception_handler()`:

```python title="handling_errors/tutorial003_py310.py"
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


app = FastAPI()


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}
```

Здесь, если запросить `/unicorns/yolo`, *операция пути* возбудит (`raise`) `UnicornException`.

Но оно будет обработано `unicorn_exception_handler`.

Так что вы получите аккуратную ошибку с HTTP-кодом статуса `418` и JSON-содержимым:

```JSON
{"message": "Oops! yolo did something. There goes a rainbow..."}
```

> **Примечание | Технические подробности**
>
> Можно также использовать `from starlette.requests import Request` и `from starlette.responses import JSONResponse`.
>
> **FastAPI** предоставляет тот же `starlette.responses` в виде `fastapi.responses` просто для удобства разработчика. Но большинство доступных ответов берутся напрямую из Starlette. То же самое с `Request`.

## Переопределение стандартных обработчиков исключений

У **FastAPI** есть несколько стандартных обработчиков исключений.

Эти обработчики отвечают за возврат стандартных JSON-ответов, когда вы возбуждаете (`raise`) `HTTPException` и когда в запросе невалидные данные.

Эти обработчики исключений можно переопределить своими.

### Переопределение исключений валидации запроса

Когда запрос содержит невалидные данные, **FastAPI** внутри возбуждает `RequestValidationError`.

И для него также есть стандартный обработчик исключений.

Чтобы переопределить его, импортируйте `RequestValidationError` и используйте его в `@app.exception_handler(RequestValidationError)`, чтобы задекорировать обработчик исключения.

Обработчик исключения получит `Request` и само исключение.

```python title="handling_errors/tutorial004_py310.py"
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}
```

Теперь, если перейти на `/items/foo`, вместо стандартной JSON-ошибки:

```JSON
{
    "detail": [
        {
            "loc": [
                "path",
                "item_id"
            ],
            "msg": "value is not a valid integer",
            "type": "type_error.integer"
        }
    ]
}
```

вы получите текстовую версию:

```
Validation errors:
Field: ('path', 'item_id'), Error: Input should be a valid integer, unable to parse string as an integer
```

### Переопределение обработчика ошибок `HTTPException`

Точно так же можно переопределить обработчик `HTTPException`.

Например, вы можете захотеть возвращать для этих ошибок ответ обычным текстом вместо JSON — см. обработчик `http_exception_handler` в примере выше:

```python title="handling_errors/tutorial004_py310.py"
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
```

> **Примечание | Технические подробности**
>
> Можно также использовать `from starlette.responses import PlainTextResponse`.
>
> **FastAPI** предоставляет тот же `starlette.responses` в виде `fastapi.responses` просто для удобства разработчика. Но большинство доступных ответов берутся напрямую из Starlette.

> **Внимание**
>
> Учтите, что `RequestValidationError` содержит информацию об имени файла и строке, где произошла ошибка валидации, чтобы при желании можно было показать её в логах вместе с нужными сведениями.
>
> Но это означает, что если просто преобразовать его в строку и вернуть эту информацию напрямую, можно раскрыть немного информации о своей системе; поэтому здесь код извлекает и показывает каждую ошибку по отдельности.

### Использование тела из `RequestValidationError`

`RequestValidationError` содержит полученное тело (`body`) с невалидными данными.

Его можно использовать во время разработки приложения, чтобы логировать тело и отлаживать его, возвращать пользователю и т. д.

```python title="handling_errors/tutorial005_py310.py"
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


class Item(BaseModel):
    title: str
    size: int


@app.post("/items/")
async def create_item(item: Item):
    return item
```

Теперь попробуйте отправить невалидный элемент, например:

```JSON
{
  "title": "towel",
  "size": "XL"
}
```

Вы получите ответ, сообщающий, что данные невалидны, и содержащий полученное тело:

```JSON
{
  "detail": [
    {
      "loc": [
        "body",
        "size"
      ],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ],
  "body": {
    "title": "towel",
    "size": "XL"
  }
}
```

#### `HTTPException` из FastAPI и `HTTPException` из Starlette

У **FastAPI** есть собственный `HTTPException`.

И класс ошибки `HTTPException` из **FastAPI** наследуется от класса ошибки `HTTPException` из Starlette.

Единственное различие в том, что `HTTPException` из **FastAPI** принимает в поле `detail` любые данные, которые можно преобразовать в JSON, а `HTTPException` из Starlette — только строки.

Так что в своём коде можно, как обычно, продолжать возбуждать `HTTPException` из **FastAPI**.

Но при регистрации обработчика исключений его следует регистрировать для `HTTPException` из Starlette.

Так, если какая-либо часть внутреннего кода Starlette, расширение или плагин Starlette возбудит `HTTPException` из Starlette, ваш обработчик сможет его перехватить и обработать.

В этом примере, чтобы оба `HTTPException` можно было использовать в одном коде, исключение Starlette переименовано в `StarletteHTTPException`:

```Python
from starlette.exceptions import HTTPException as StarletteHTTPException
```

### Переиспользование обработчиков исключений **FastAPI**

Если вы хотите использовать исключение вместе с теми же стандартными обработчиками исключений из **FastAPI**, можно импортировать и переиспользовать стандартные обработчики из `fastapi.exception_handlers`:

```python title="handling_errors/tutorial006_py310.py"
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"OMG! An HTTP error!: {repr(exc)}")
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}
```

В этом примере вы просто печатаете ошибку с очень выразительным сообщением, но идея понятна: можно использовать исключение, а затем просто переиспользовать стандартные обработчики исключений.
