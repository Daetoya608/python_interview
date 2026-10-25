# JSON-совместимый кодировщик

> Перевод страницы [JSON Compatible Encoder](https://fastapi.tiangolo.com/tutorial/encoder/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Бывают случаи, когда нужно преобразовать тип данных (например, модель Pydantic) во что-то совместимое с JSON (например, `dict`, `list` и т. д.).

Например, если нужно сохранить его в базе данных.

Для этого **FastAPI** предоставляет функцию `jsonable_encoder()`.

## Использование `jsonable_encoder`

Представим, что у вас есть база данных `fake_db`, которая принимает только данные, совместимые с JSON.

Например, она не принимает объекты `datetime`, поскольку они несовместимы с JSON.

Значит, объект `datetime` нужно преобразовать в `str` с данными в [формате ISO](https://ru.wikipedia.org/wiki/ISO_8601).

Точно так же эта база данных не примет модель Pydantic (объект с атрибутами) — только `dict`.

Для этого можно использовать `jsonable_encoder`.

Он принимает объект, например модель Pydantic, и возвращает его JSON-совместимую версию:

```python title="encoder/tutorial001_py310.py"
from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

fake_db = {}


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


app = FastAPI()


@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
```

В этом примере он преобразует модель Pydantic в `dict`, а `datetime` — в `str`.

Результат его вызова — нечто, что можно закодировать стандартной функцией Python [`json.dumps()`](https://docs.python.org/3/library/json.html#json.dumps).

Он не возвращает большую `str` с данными в формате JSON (в виде строки). Он возвращает стандартную структуру данных Python (например, `dict`), все значения и вложенные значения которой совместимы с JSON.

> **Примечание**
>
> На самом деле `jsonable_encoder` используется самим **FastAPI** внутри для преобразования данных. Но он полезен и во многих других сценариях.
