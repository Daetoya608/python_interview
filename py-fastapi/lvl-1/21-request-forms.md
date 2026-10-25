# Данные форм

> Перевод страницы [Form Data](https://fastapi.tiangolo.com/tutorial/request-forms/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Когда нужно получать поля формы вместо JSON, можно использовать `Form`.

> **Примечание**
>
> Чтобы использовать формы, сначала установите [`python-multipart`](https://github.com/Kludex/python-multipart).
>
> Добавьте его в проект:
>
> ```console
> $ uv add python-multipart
> ```

## Импортируйте `Form`

Импортируйте `Form` из `fastapi`:

```python title="request_forms/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Form

app = FastAPI()


@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}
```

## Определите параметры `Form`

Создавайте параметры формы так же, как для `Body` или `Query` (см. пример выше).

Например, в одном из способов использования спецификации OAuth2 (он называется «password flow») требуется отправлять `username` и `password` как поля формы.

<dfn title="спецификация">Спецификация</dfn> требует, чтобы поля назывались именно `username` и `password` и отправлялись как поля формы, а не JSON.

С `Form` можно объявлять те же настройки, что и с `Body` (а также `Query`, `Path`, `Cookie`), включая валидацию, примеры, псевдоним (например, `user-name` вместо `username`) и т. д.

> **Примечание**
>
> `Form` — класс, который напрямую наследуется от `Body`.

> **Совет**
>
> Чтобы объявить тело формы, нужно явно использовать `Form`, потому что без него параметры будут интерпретированы как параметры запроса или параметры тела (JSON).

## Булевы поля формы

При отправке HTML-форм браузеры не включают неотмеченные чекбоксы. Объявите булев параметр формы со значением по умолчанию `False`, чтобы получать `False`, когда чекбокс не отмечен:

```python title="request_forms/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Form

app = FastAPI()


@app.post("/preferences/")
async def update_preferences(subscribe: Annotated[bool, Form()] = False):
    return {"subscribe": subscribe}
```

Отмеченный чекбокс отправляет своё значение, по умолчанию `"on"`. **FastAPI** принимает `"on"` как `True`.

## О «полях формы»

HTML-формы (`<form></form>`) обычно отправляют данные на сервер в «особой» кодировке, отличной от JSON.

**FastAPI** позаботится о том, чтобы прочитать эти данные из правильного места, а не из JSON.

> **Примечание | Технические подробности**
>
> Данные форм обычно кодируются с «типом медиа» `application/x-www-form-urlencoded`.
>
> Но если форма содержит файлы, она кодируется как `multipart/form-data`. О работе с файлами вы прочитаете в следующей главе.
>
> Можно использовать `Form(media_type="multipart/form-data")`, чтобы описать multipart-форму в OpenAPI. При комбинировании параметров или моделей формы достаточно указать это на одном параметре.
>
> Если хотите узнать больше об этих кодировках и полях форм, загляните в [веб-документацию <abbr title="Mozilla Developer Network">MDN</abbr> по `POST`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST).

> **Внимание**
>
> В *операции пути* можно объявить несколько параметров `Form`, но нельзя одновременно объявить поля `Body`, которые вы ожидаете получить как JSON, поскольку тело запроса будет закодировано как `application/x-www-form-urlencoded`, а не `application/json`.
>
> Это не ограничение **FastAPI**, а часть протокола HTTP.

## Итоги

Используйте `Form`, чтобы объявлять входные параметры из данных формы.
