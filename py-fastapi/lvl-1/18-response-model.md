# Модель ответа — тип возвращаемого значения

> Перевод страницы [Response Model - Return Type](https://fastapi.tiangolo.com/tutorial/response-model/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Тип, используемый для ответа, можно объявить, аннотировав **тип возвращаемого значения** *функции операции пути*.

**Аннотации типов** используются так же, как для входных данных в **параметрах** функции: можно использовать модели Pydantic, списки, словари, скалярные значения вроде целых чисел, булевых значений и т. д.

```python title="response_model/tutorial001_01_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@app.post("/items/")
async def create_item(item: Item) -> Item:
    return item


@app.get("/items/")
async def read_items() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]
```

FastAPI использует этот тип возвращаемого значения, чтобы:

* **Валидировать** возвращаемые данные.
    * Если данные невалидны (например, не хватает поля), это значит, что сломан код *вашего* приложения — он возвращает не то, что должен, — и вместо некорректных данных будет возвращена ошибка сервера. Так вы и ваши клиенты можете быть уверены, что получите ожидаемые данные и в ожидаемой форме.
* Добавить **JSON Schema** для ответа в *операцию пути* OpenAPI.
    * Её будет использовать **автоматическая документация**.
    * Её также будут использовать инструменты автоматической генерации клиентского кода.
* **Сериализовать** возвращаемые данные в JSON с помощью Pydantic, который написан на **Rust**, так что это будет **гораздо быстрее**.

Но самое главное:

* Он **ограничит и отфильтрует** выходные данные до того, что определено в типе возвращаемого значения.
    * Это особенно важно для **безопасности**, подробнее об этом ниже.

## Параметр `response_model`

Бывают случаи, когда нужно или хочется вернуть данные, которые не в точности соответствуют объявленному типу.

Например, вы можете захотеть **вернуть словарь** или объект базы данных, но **объявить его как модель Pydantic**. Тогда модель Pydantic выполнит всю документацию данных, валидацию и т. д. для возвращённого объекта (например, словаря или объекта базы данных).

Если бы вы добавили аннотацию типа возвращаемого значения, инструменты и редакторы выдали бы (справедливую) ошибку о том, что функция возвращает тип (например, dict), отличный от объявленного (например, модели Pydantic).

В таких случаях вместо типа возвращаемого значения можно использовать параметр `response_model` *декоратора операции пути*.

Параметр `response_model` можно использовать в любой *операции пути*:

* `@app.get()`
* `@app.post()`
* `@app.put()`
* `@app.delete()`
* и т. д.

```python title="response_model/tutorial001_py310.py"
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Any:
    return item


@app.get("/items/", response_model=list[Item])
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]
```

> **Примечание**
>
> Обратите внимание, что `response_model` — это параметр метода «декоратора» (`get`, `post` и т. д.), а не вашей *функции операции пути*, как все параметры и тело.

`response_model` принимает тот же тип, который вы объявили бы для поля модели Pydantic, так что это может быть модель Pydantic, а может быть, например, `list` моделей Pydantic, вроде `List[Item]`.

FastAPI использует этот `response_model` для всей документации данных, валидации и т. д., а также для **преобразования и фильтрации выходных данных** в соответствии с объявленным типом.

> **Совет**
>
> Если в редакторе, mypy и т. п. включены строгие проверки типов, можно объявить тип возвращаемого значения функции как `Any`.
>
> Так вы сообщаете редактору, что намеренно возвращаете что угодно. Но FastAPI всё равно выполнит документацию данных, валидацию, фильтрацию и т. д. с помощью `response_model`.

### Приоритет `response_model`

Если объявить и тип возвращаемого значения, и `response_model`, приоритет будет у `response_model`, и FastAPI будет использовать именно его.

Так можно добавлять в функции правильные аннотации типов, даже если вы возвращаете тип, отличный от модели ответа, — для редактора и инструментов вроде mypy. И при этом FastAPI будет выполнять валидацию данных, документацию и т. д. с помощью `response_model`.

Можно также использовать `response_model=None`, чтобы отключить создание модели ответа для этой *операции пути*. Это может понадобиться, если вы добавляете аннотации типов для вещей, которые не являются допустимыми полями Pydantic; пример вы увидите в одном из разделов ниже.

## Возврат тех же входных данных

Здесь мы объявляем модель `UserIn`, которая будет содержать пароль в открытом виде:

```python title="response_model/tutorial002_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


# Не делайте так в продакшене!
@app.post("/user/")
async def create_user(user: UserIn) -> UserIn:
    return user
```

> **Примечание**
>
> Чтобы использовать `EmailStr`, сначала установите [`email-validator`](https://github.com/JoshData/python-email-validator).
>
> Добавьте его в проект:
>
> ```console
> $ uv add email-validator
> ```
>
> или так:
>
> ```console
> $ uv add "pydantic[email]"
> ```

И мы используем эту модель, чтобы объявить входные данные, и ту же модель — чтобы объявить выходные.

Теперь, когда браузер создаёт пользователя с паролем, API вернёт тот же пароль в ответе.

В данном случае это может быть не проблемой, потому что пароль отправляет тот же самый пользователь.

Но если использовать ту же модель для другой *операции пути*, мы можем начать отправлять пароли наших пользователей каждому клиенту.

> **Опасность**
>
> Никогда не храните пароль пользователя в открытом виде и не отправляйте его в ответе таким образом, если только вы не знаете всех подводных камней и не понимаете, что делаете.

## Добавьте выходную модель

Вместо этого можно создать входную модель с паролем в открытом виде и выходную модель без него:

```python title="response_model/tutorial003_py310.py"
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user
```

Здесь, хотя наша *функция операции пути* возвращает того же входного пользователя, который содержит пароль...

...мы объявили `response_model` как нашу модель `UserOut`, которая пароль не включает.

Поэтому **FastAPI** позаботится о том, чтобы отфильтровать все данные, не объявленные в выходной модели (с помощью Pydantic).

### `response_model` или тип возвращаемого значения

В этом случае, поскольку модели разные, если бы мы аннотировали тип возвращаемого значения функции как `UserOut`, редактор и инструменты пожаловались бы, что мы возвращаем недопустимый тип, ведь это разные классы.

Поэтому в этом примере его приходится объявлять в параметре `response_model`.

...но читайте дальше, чтобы узнать, как это обойти.

## Тип возвращаемого значения и фильтрация данных

Продолжим предыдущий пример. Мы хотели **аннотировать функцию одним типом**, но при этом иметь возможность возвращать из неё что-то, что на самом деле содержит **больше данных**.

Мы хотим, чтобы FastAPI продолжал **фильтровать** данные с помощью модели ответа. Чтобы, даже если функция возвращает больше данных, ответ содержал только поля, объявленные в модели ответа.

В предыдущем примере, поскольку классы были разными, нам пришлось использовать параметр `response_model`. Но это также означает, что мы не получаем поддержку редактора и инструментов, проверяющих тип возвращаемого значения функции.

Однако в большинстве случаев, когда нужно сделать нечто подобное, мы хотим, чтобы модель просто **отфильтровала/убрала** часть данных, как в этом примере.

И в таких случаях можно использовать классы и наследование, чтобы воспользоваться **аннотациями типов** функции, получить лучшую поддержку редактора и инструментов и при этом сохранить **фильтрацию данных** FastAPI.

```python title="response_model/tutorial003_01_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str


@app.post("/user/")
async def create_user(user: UserIn) -> BaseUser:
    return user
```

Так мы получаем поддержку инструментов — редакторов и mypy, — поскольку этот код корректен с точки зрения типов, и при этом получаем фильтрацию данных от FastAPI.

Как это работает? Давайте разберёмся. 🤓

### Аннотации типов и инструменты

Сначала посмотрим, как это видят редакторы, mypy и другие инструменты.

У `BaseUser` есть базовые поля. Затем `UserIn` наследуется от `BaseUser` и добавляет поле `password`, так что он включает все поля обеих моделей.

Мы аннотируем тип возвращаемого значения функции как `BaseUser`, но на самом деле возвращаем экземпляр `UserIn`.

Редактор, mypy и другие инструменты не будут на это жаловаться, потому что с точки зрения типизации `UserIn` — подкласс `BaseUser`, а значит, это *допустимый* тип там, где ожидается что угодно, являющееся `BaseUser`.

### Фильтрация данных в FastAPI

А FastAPI увидит тип возвращаемого значения и убедится, что возвращаемое содержит **только** поля, объявленные в этом типе.

Внутри FastAPI делает с Pydantic несколько вещей, чтобы те же правила наследования классов не применялись при фильтрации возвращаемых данных, иначе вы могли бы в итоге вернуть гораздо больше данных, чем ожидали.

Так вы получаете лучшее из обоих миров: аннотации типов с **поддержкой инструментов** и **фильтрацию данных**.

## Посмотрите в документации

В автоматической документации видно, что у входной и у выходной модели есть свои собственные JSON Schema:

<img src="https://fastapi.tiangolo.com/img/tutorial/response-model/image01.png">

И обе модели будут использованы в интерактивной документации API:

<img src="https://fastapi.tiangolo.com/img/tutorial/response-model/image02.png">

## Другие аннотации типа возвращаемого значения

Бывают случаи, когда вы возвращаете что-то, что не является допустимым полем Pydantic, и аннотируете это в функции только ради поддержки инструментов (редактора, mypy и т. д.).

### Прямой возврат Response

Самый распространённый случай — [прямой возврат Response, как описано позже в продвинутой документации](https://fastapi.tiangolo.com/advanced/response-directly/).

```python title="response_model/tutorial003_02_py310.py"
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, RedirectResponse

app = FastAPI()


@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})
```

Этот простой случай FastAPI обрабатывает автоматически, потому что аннотация типа возвращаемого значения — класс `Response` (или его подкласс).

И инструменты тоже будут довольны, потому что и `RedirectResponse`, и `JSONResponse` — подклассы `Response`, так что аннотация типа корректна.

### Аннотирование подклассом Response

В аннотации типа можно также использовать подкласс `Response`:

```python title="response_model/tutorial003_03_py310.py"
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/teleport")
async def get_teleport() -> RedirectResponse:
    return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

Это тоже сработает, потому что `RedirectResponse` — подкласс `Response`, и FastAPI автоматически обработает этот простой случай.

### Недопустимые аннотации типа возвращаемого значения

Но если вы возвращаете какой-то другой произвольный объект, который не является допустимым типом Pydantic (например, объект базы данных), и аннотируете функцию так, FastAPI попытается создать модель ответа Pydantic из этой аннотации типа и потерпит неудачу.

То же самое произойдёт, если у вас что-то вроде <dfn title='Объединение (union) нескольких типов означает «любой из этих типов».'>объединения</dfn> разных типов, где один или несколько из них не являются допустимыми типами Pydantic; например, это не сработает 💥:

```python title="response_model/tutorial003_04_py310.py"
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}
```

...это не работает, потому что аннотация типа не является типом Pydantic и не является просто классом `Response` или его подклассом — это объединение (любой из двух) `Response` и `dict`.

### Отключение модели ответа

Продолжая пример выше: возможно, вам не нужна стандартная валидация данных, документация, фильтрация и т. д., которые выполняет FastAPI.

Но при этом вы хотите сохранить аннотацию типа возвращаемого значения в функции, чтобы получать поддержку инструментов вроде редакторов и проверщиков типов (например, mypy).

В этом случае генерацию модели ответа можно отключить, задав `response_model=None`:

```python title="response_model/tutorial003_05_py310.py"
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/portal", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}
```

Так FastAPI пропустит генерацию модели ответа, и у вас могут быть любые нужные аннотации типа возвращаемого значения без влияния на приложение FastAPI. 🤓

## Параметры кодирования модели ответа

У модели ответа могут быть значения по умолчанию, например:

```python title="response_model/tutorial004_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]
```

* `description: Union[str, None] = None` (или `str | None = None` в Python 3.10) имеет значение по умолчанию `None`.
* `tax: float = 10.5` имеет значение по умолчанию `10.5`.
* `tags: List[str] = []` имеет значение по умолчанию — пустой список: `[]`.

но вы можете захотеть не включать их в результат, если они на самом деле не были сохранены.

Например, если у вас в NoSQL-базе данных модели со множеством необязательных атрибутов, но вы не хотите отправлять очень длинные JSON-ответы, полные значений по умолчанию.

### Используйте параметр `response_model_exclude_unset`

Можно задать параметр *декоратора операции пути* `response_model_exclude_unset=True` (как в примере выше),

и тогда значения по умолчанию не будут включены в ответ — только реально заданные значения.

Поэтому, если отправить запрос к этой *операции пути* для элемента с ID `foo`, ответ (без значений по умолчанию) будет таким:

```JSON
{
    "name": "Foo",
    "price": 50.2
}
```

> **Примечание**
>
> Можно также использовать:
>
> * `response_model_exclude_defaults=True`
> * `response_model_exclude_none=True`
>
> как описано в [документации Pydantic](https://pydantic.dev/docs/validation/latest/concepts/serialization/#excluding-and-including-fields-based-on-their-value) для `exclude_defaults` и `exclude_none`.

#### Данные со значениями для полей со значениями по умолчанию

Но если в ваших данных есть значения для полей модели со значениями по умолчанию, как у элемента с ID `bar`:

```Python
{
    "name": "Bar",
    "description": "The bartenders",
    "price": 62,
    "tax": 20.2
}
```

они будут включены в ответ.

#### Данные с теми же значениями, что и по умолчанию

Если в данных те же значения, что и значения по умолчанию, как у элемента с ID `baz`:

```Python
{
    "name": "Baz",
    "description": None,
    "price": 50.2,
    "tax": 10.5,
    "tags": []
}
```

FastAPI достаточно умён (на самом деле достаточно умён Pydantic), чтобы понять, что хотя `description`, `tax` и `tags` имеют те же значения, что и по умолчанию, они были заданы явно (а не взяты из значений по умолчанию).

Поэтому они будут включены в JSON-ответ.

> **Совет**
>
> Обратите внимание, что значения по умолчанию могут быть любыми, не только `None`.
>
> Это может быть список (`[]`), `float` со значением `10.5` и т. д.

### `response_model_include` и `response_model_exclude`

Можно также использовать параметры *декоратора операции пути* `response_model_include` и `response_model_exclude`.

Они принимают `set` из `str` с именами атрибутов, которые нужно включить (опустив остальные) или исключить (включив остальные).

Это можно использовать как быстрый способ, если у вас только одна модель Pydantic и нужно убрать часть данных из вывода.

> **Совет**
>
> Но всё же рекомендуется использовать идеи выше — несколько классов, — а не эти параметры.
>
> Дело в том, что JSON Schema, генерируемая в OpenAPI вашего приложения (и в документации), всё равно будет схемой полной модели, даже если вы используете `response_model_include` или `response_model_exclude`, чтобы опустить некоторые атрибуты.
>
> Это относится и к `response_model_by_alias`, который работает аналогично.

```python title="response_model/tutorial005_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}


@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]
```

> **Совет**
>
> Синтаксис `{"name", "description"}` создаёт `set` с этими двумя значениями.
>
> Это эквивалентно `set(["name", "description"])`.

#### Использование `list` вместо `set`

Если вы забудете использовать `set` и вместо него используете `list` или `tuple`, FastAPI всё равно преобразует его в `set`, и всё будет работать правильно:

```python title="response_model/tutorial006_py310.py"
@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include=["name", "description"],
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude=["tax"])
async def read_item_public_data(item_id: str):
    return items[item_id]
```

## Итоги

Используйте параметр `response_model` *декоратора операции пути*, чтобы определять модели ответа и особенно чтобы гарантировать, что приватные данные будут отфильтрованы.

Используйте `response_model_exclude_unset`, чтобы возвращать только явно заданные значения.
