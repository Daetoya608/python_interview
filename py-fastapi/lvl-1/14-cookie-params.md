# Параметры cookie

> Перевод страницы [Cookie Parameters](https://fastapi.tiangolo.com/tutorial/cookie-params/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Параметры cookie можно определять так же, как параметры `Query` и `Path`.

## Импортируйте `Cookie`

Сначала импортируйте `Cookie`:

```python title="cookie_params/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import Cookie, FastAPI

app = FastAPI()


@app.get("/items/")
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    return {"ads_id": ads_id}
```

## Объявите параметры `Cookie`

Затем объявите параметры cookie, используя ту же структуру, что и для `Path` и `Query`.

Можно задать значение по умолчанию, а также все дополнительные параметры валидации или аннотаций:

```python title="cookie_params/tutorial001_an_py310.py"
@app.get("/items/")
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    return {"ads_id": ads_id}
```

> **Примечание | Технические подробности**
>
> `Cookie` — «родственный» класс для `Path` и `Query`. Он тоже наследуется от того же общего класса `Param`.
>
> Но помните, что когда вы импортируете `Query`, `Path`, `Cookie` и другие из `fastapi`, на самом деле это функции, возвращающие специальные классы.

> **Примечание**
>
> Чтобы объявить cookie, нужно использовать `Cookie`, иначе параметры будут интерпретированы как параметры запроса.

> **Примечание**
>
> Учтите, что поскольку **браузеры обрабатывают cookie** особым образом и «за кулисами», они **не** дают **JavaScript** легко с ними работать.
>
> Если открыть **интерфейс документации API** по адресу `/docs`, вы увидите **документацию** cookie для ваших *операций пути*.
>
> Но даже если **заполнить данные** и нажать «Execute», cookie не будут отправлены, потому что интерфейс документации работает на **JavaScript**, и вы увидите сообщение об **ошибке**, как будто ничего не ввели.

## Итоги

Объявляйте cookie с помощью `Cookie`, используя тот же общий шаблон, что и для `Query` и `Path`.
