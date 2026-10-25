# Параметры заголовков

> Перевод страницы [Header Parameters](https://fastapi.tiangolo.com/tutorial/header-params/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Параметры заголовков можно определять так же, как параметры `Query`, `Path` и `Cookie`.

## Импортируйте `Header`

Сначала импортируйте `Header`:

```python title="header_params/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Header

app = FastAPI()


@app.get("/items/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}
```

## Объявите параметры `Header`

Затем объявите параметры заголовков, используя ту же структуру, что и для `Path`, `Query` и `Cookie`.

Можно задать значение по умолчанию, а также все дополнительные параметры валидации или аннотаций:

```python title="header_params/tutorial001_an_py310.py"
@app.get("/items/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}
```

> **Примечание | Технические подробности**
>
> `Header` — «родственный» класс для `Path`, `Query` и `Cookie`. Он тоже наследуется от того же общего класса `Param`.
>
> Но помните, что когда вы импортируете `Query`, `Path`, `Header` и другие из `fastapi`, на самом деле это функции, возвращающие специальные классы.

> **Примечание**
>
> Чтобы объявить заголовки, нужно использовать `Header`, иначе параметры будут интерпретированы как параметры запроса.

## Автоматическое преобразование

У `Header` есть немного дополнительной функциональности по сравнению с `Path`, `Query` и `Cookie`.

Большинство стандартных заголовков разделены символом «дефис», также известным как «минус» (`-`).

Но переменная вроде `user-agent` в Python недопустима.

Поэтому по умолчанию `Header` преобразует символы подчёркивания (`_`) в именах параметров в дефисы (`-`), чтобы извлекать и документировать заголовки.

Кроме того, HTTP-заголовки нечувствительны к регистру, поэтому их можно объявлять в стандартном стиле Python (также известном как «snake_case»).

Так что можно использовать `user_agent`, как обычно в коде на Python, и не нужно писать первые буквы заглавными, как `User_Agent` или что-то подобное.

Если по какой-то причине нужно отключить автоматическое преобразование подчёркиваний в дефисы, задайте параметр `convert_underscores` у `Header` равным `False`:

```python title="header_params/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Header

app = FastAPI()


@app.get("/items/")
async def read_items(
    strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    return {"strange_header": strange_header}
```

> **Внимание**
>
> Прежде чем задавать `convert_underscores` равным `False`, помните, что некоторые HTTP-прокси и серверы запрещают использовать заголовки с подчёркиваниями.

## Повторяющиеся заголовки

Можно получать повторяющиеся заголовки, то есть один и тот же заголовок с несколькими значениями.

Такие случаи можно описать, используя список в объявлении типа.

Все значения повторяющегося заголовка вы получите в виде `list` Python.

Например, чтобы объявить заголовок `X-Token`, который может встречаться несколько раз, можно написать:

```python title="header_params/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import FastAPI, Header

app = FastAPI()


@app.get("/items/")
async def read_items(x_token: Annotated[list[str] | None, Header()] = None):
    return {"X-Token values": x_token}
```

Если обратиться к этой *операции пути*, отправив два HTTP-заголовка:

```
X-Token: foo
X-Token: bar
```

ответ будет таким:

```JSON
{
    "X-Token values": [
        "bar",
        "foo"
    ]
}
```

## Итоги

Объявляйте заголовки с помощью `Header`, используя тот же общий шаблон, что и для `Query`, `Path` и `Cookie`.

И не беспокойтесь о подчёркиваниях в именах переменных — **FastAPI** позаботится об их преобразовании.
