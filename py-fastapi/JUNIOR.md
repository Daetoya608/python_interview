# FastAPI — Junior

FastAPI — ASGI-фреймворк для HTTP API. Функция маршрута (view/path operation) обрабатывает запрос; декоратор связывает её с HTTP-методом и путём. Pydantic проверяет/преобразует входные данные, FastAPI использует модели для схемы OpenAPI и сериализации.

## Методы и параметры

| Метод | Обычное назначение |
|---|---|
| GET | Получить данные, не изменяя бизнес-состояние |
| POST | Создать ресурс или выполнить обработку |
| PUT | Создать/заменить состояние ресурса по заданному URI |
| PATCH | Применить частичное изменение |
| DELETE | Удалить ресурс/привязку |

Имя метода не реализует операции автоматически: обновление/удаление нужно написать. Пути проверяются по порядку; фиксированный `/users/me` объявляют раньше `/users/{user_id}`.

- Имя параметра есть в `/items/{item_id}` → **path**, всегда обязательный.
- Простой параметр вне пути → обычно **query** (`?q=book`).
- Pydantic BaseModel → обычно JSON **body**.

## Мини-приложение

Сохрани в `main.py`. Здесь GET показывает чтение параметров, POST — расчёт по телу, без постоянной БД.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class OrderIn(BaseModel):
    price_cents: int = Field(gt=0)
    quantity: int = Field(gt=0)
    comment: str | None = None

class TotalOut(BaseModel):
    total_cents: int

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    if item_id != 1:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, "q": q}

@app.post("/total", response_model=TotalOut, status_code=200)
def calculate_total(order: OrderIn):
    return {
        "total_cents": order.price_cents * order.quantity,
        "internal_note": "not included in response",
    }
```

`GET /items/1?q=book` передаст int item_id и строку q. `GET /items/abc` не пройдёт проверку int и по умолчанию даст **422**. JSON для POST: `{"price_cents":100,"quantity":2}`. Ответ: `{"total_cents":200}`; внутреннее поле отфильтровано моделью ответа.

## Nullable и обязательность

- `name: str` — требуется, None запрещён.
- `name: str | None` в Pydantic v2 — требуется, но None допустим.
- `name: str | None = None` — можно пропустить.

Наличие None в типе не создаёт default. У query нет встроенного JSON null: `?q=null` — строка "null", а не None. `Field(gt=0)` задаёт проверку значения; аннотации обычного Python без FastAPI/Pydantic runtime-проверок не выполняют.

## Ответ и ошибка

**response_model** проверяет возвращаемые данные, сериализует и фильтрует поля, описывает ответ в OpenAPI. Ошибка входа — обычно 422; неправильные данные ответа — ошибка приложения, обычно 500. Возврат готового Response обходит автоматическую проверку его body моделью.

**status_code** в декораторе задаёт обычный код: 200 — успех, 201 — создан ресурс, 204 — без тела. Дополнительные ошибки явно реализуют в коде. **HTTPException нужно raise, а не return**; стандартное тело содержит detail.

## Запуск и отладка

```console
python -m pip install "fastapi[standard]"
fastapi dev main.py
```

Альтернатива: `uvicorn main:app --reload`. main — модуль, app — объект приложения; --reload используется в разработке. По умолчанию сервер доступен на `http://127.0.0.1:8000`, интерактивная документация — `/docs`, схема — `/openapi.json`.

`async def` выбирают для ожидания async-библиотек. Обычные def-обработчики FastAPI запускает в пуле потоков. Синхронная функция, которую самостоятельно вызвали внутри async def, автоматически туда не переносится и может блокировать event loop.

**Самопроверка:** откуда взялся параметр — path/query/body? Чем nullable отличается от необязательности? Почему 422 не равно ошибке ответа? Как response_model убирает поле? Что означает main:app?
