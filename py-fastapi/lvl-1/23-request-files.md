# Файлы в запросе

> Перевод страницы [Request Files](https://fastapi.tiangolo.com/tutorial/request-files/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

С помощью `File` можно определить файлы, которые будет загружать клиент.

> **Примечание**
>
> Чтобы получать загруженные файлы, сначала установите [`python-multipart`](https://github.com/Kludex/python-multipart).
>
> Добавьте его в проект:
>
> ```console
> $ uv add python-multipart
> ```
>
> Это нужно потому, что загружаемые файлы отправляются как «данные формы».

## Импортируйте `File`

Импортируйте `File` и `UploadFile` из `fastapi`:

```python title="request_files/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
```

## Определите параметры `File`

Создавайте параметры-файлы так же, как для `Body` или `Form`:

```python title="request_files/tutorial001_an_py310.py"
@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}
```

> **Примечание**
>
> `File` — класс, который напрямую наследуется от `Form`.
>
> Но помните, что когда вы импортируете `Query`, `Path`, `File` и другие из `fastapi`, на самом деле это функции, возвращающие специальные классы.

> **Совет**
>
> Чтобы объявить тела-файлы, нужно использовать `File`, иначе параметры будут интерпретированы как параметры запроса или параметры тела (JSON).

Файлы будут загружены как «данные формы».

Если объявить тип параметра *функции операции пути* как `bytes`, **FastAPI** прочитает файл за вас, и вы получите содержимое в виде `bytes`.

Учтите, что это означает, что всё содержимое будет храниться в памяти. Для небольших файлов это работает хорошо.

Но есть несколько случаев, когда выгоднее использовать `UploadFile`.

## Параметры-файлы с `UploadFile`

Определите параметр-файл с типом `UploadFile`:

```python title="request_files/tutorial001_an_py310.py"
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
```

У `UploadFile` есть несколько преимуществ перед `bytes`:

* Не нужно использовать `File()` в значении по умолчанию параметра.
* Используется «spooled»-файл (буферизованный):
    * Файл хранится в памяти до определённого максимального размера, а после превышения лимита сохраняется на диск.
* Это значит, что он хорошо работает с большими файлами — изображениями, видео, большими бинарными файлами и т. д., — не расходуя всю память.
* Можно получить метаданные загруженного файла.
* У него есть [файлоподобный](https://docs.python.org/3/glossary.html#term-file-like-object) `async`-интерфейс.
* Он предоставляет настоящий объект Python [`SpooledTemporaryFile`](https://docs.python.org/3/library/tempfile.html#tempfile.SpooledTemporaryFile), который можно передавать напрямую в другие библиотеки, ожидающие файлоподобный объект.

### `UploadFile`

У `UploadFile` есть следующие атрибуты:

* `filename`: `str` с исходным именем загруженного файла (например, `myimage.jpg`).
* `content_type`: `str` с типом содержимого (MIME-тип / тип медиа) (например, `image/jpeg`).
* `file`: [`SpooledTemporaryFile`](https://docs.python.org/3/library/tempfile.html#tempfile.SpooledTemporaryFile) ([файлоподобный](https://docs.python.org/3/glossary.html#term-file-like-object) объект). Это настоящий файловый объект Python, который можно передавать напрямую в другие функции или библиотеки, ожидающие «файлоподобный» объект.

У `UploadFile` есть следующие `async`-методы. Все они «под капотом» вызывают соответствующие методы файла (используя внутренний `SpooledTemporaryFile`).

* `write(data)`: записывает `data` (`str` или `bytes`) в файл.
* `read(size)`: читает `size` (`int`) байт/символов из файла.
* `seek(offset)`: переходит к позиции `offset` (`int`) в байтах в файле.
    * Например, `await myfile.seek(0)` перейдёт в начало файла.
    * Это особенно полезно, если вы один раз выполнили `await myfile.read()`, а затем нужно прочитать содержимое ещё раз.
* `close()`: закрывает файл.

Поскольку все эти методы — `async`-методы, их нужно «ожидать» (await).

Например, внутри `async` *функции операции пути* содержимое можно получить так:

```Python
contents = await myfile.read()
```

Если вы находитесь внутри обычной `def` *функции операции пути*, можно обратиться к `UploadFile.file` напрямую, например:

```Python
contents = myfile.file.read()
```

> **Примечание | Технические подробности `async`**
>
> Когда вы используете `async`-методы, **FastAPI** запускает методы файла в пуле потоков и ожидает их.

> **Примечание | Технические подробности Starlette**
>
> `UploadFile` из **FastAPI** напрямую наследуется от `UploadFile` из **Starlette**, но добавляет некоторые необходимые части, чтобы сделать его совместимым с **Pydantic** и другими частями FastAPI.

## Что такое «данные формы»

HTML-формы (`<form></form>`) обычно отправляют данные на сервер в «особой» кодировке, отличной от JSON.

**FastAPI** позаботится о том, чтобы прочитать эти данные из правильного места, а не из JSON.

> **Примечание | Технические подробности**
>
> Данные форм, не содержащие файлов, обычно кодируются с «типом медиа» `application/x-www-form-urlencoded`.
>
> Но если форма содержит файлы, она кодируется как `multipart/form-data`. Если вы используете `File`, **FastAPI** будет знать, что файлы нужно брать из правильной части тела.
>
> Если хотите узнать больше об этих кодировках и полях форм, загляните в [веб-документацию <abbr title="Mozilla Developer Network">MDN</abbr> по `POST`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST).

> **Внимание**
>
> В *операции пути* можно объявить несколько параметров `File` и `Form`, но нельзя одновременно объявить поля `Body`, которые вы ожидаете получить как JSON, поскольку тело запроса будет закодировано как `multipart/form-data`, а не `application/json`.
>
> Это не ограничение **FastAPI**, а часть протокола HTTP.

## Необязательная загрузка файла

Файл можно сделать необязательным, используя стандартные аннотации типов и задав значение по умолчанию `None`:

```python title="request_files/tutorial001_02_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes | None, File()] = None):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}
```

## `UploadFile` с дополнительными метаданными

`File()` можно использовать и вместе с `UploadFile`, например чтобы задать дополнительные метаданные:

```python title="request_files/tutorial001_03_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File(description="A file read as bytes")]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(
    file: Annotated[UploadFile, File(description="A file read as UploadFile")],
):
    return {"filename": file.filename}
```

## Загрузка нескольких файлов

Можно загружать несколько файлов одновременно.

Они будут связаны с одним и тем же «полем формы», отправленным в виде «данных формы».

Для этого объявите список `bytes` или `UploadFile`:

```python title="request_files/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.post("/files/")
async def create_files(files: Annotated[list[bytes], File()]):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
```

Как и объявлено, вы получите `list` из `bytes` или `UploadFile`.

> **Примечание | Технические подробности**
>
> Можно также использовать `from starlette.responses import HTMLResponse`.
>
> **FastAPI** предоставляет тот же `starlette.responses` в виде `fastapi.responses` просто для удобства разработчика. Но большинство доступных ответов берутся напрямую из Starlette.

### Загрузка нескольких файлов с дополнительными метаданными

И так же, как раньше, можно использовать `File()`, чтобы задать дополнительные параметры, даже для `UploadFile`:

```python title="request_files/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.post("/files/")
async def create_files(
    files: Annotated[list[bytes], File(description="Multiple files as bytes")],
):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
```

## Итоги

Используйте `File`, `bytes` и `UploadFile`, чтобы объявлять файлы, загружаемые в запросе и отправляемые как данные формы.
