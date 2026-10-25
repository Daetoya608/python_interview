# Формы и файлы в запросе

> Перевод страницы [Request Forms and Files](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

С помощью `File` и `Form` можно одновременно определять файлы и поля формы.

> **Примечание**
>
> Чтобы получать загруженные файлы и/или данные форм, сначала установите [`python-multipart`](https://github.com/Kludex/python-multipart).
>
> Добавьте его в проект:
>
> ```console
> $ uv add python-multipart
> ```

## Импортируйте `File` и `Form`

```python title="request_forms_and_files/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI()


@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
```

## Определите параметры `File` и `Form`

Создавайте параметры файлов и формы так же, как для `Body` или `Query` (см. пример выше).

Файлы и поля формы будут загружены как данные формы, и вы получите и файлы, и поля формы.

Одни файлы можно объявить как `bytes`, а другие — как `UploadFile`.

> **Внимание**
>
> В *операции пути* можно объявить несколько параметров `File` и `Form`, но нельзя одновременно объявить поля `Body`, которые вы ожидаете получить как JSON, поскольку тело запроса будет закодировано как `multipart/form-data`, а не `application/json`.
>
> Это не ограничение **FastAPI**, а часть протокола HTTP.

## Итоги

Используйте `File` и `Form` вместе, когда нужно получать данные и файлы в одном запросе.
