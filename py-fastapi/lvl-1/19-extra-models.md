# Дополнительные модели

> Перевод страницы [Extra Models](https://fastapi.tiangolo.com/tutorial/extra-models/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Продолжая предыдущий пример: часто бывает больше одной связанной модели.

Особенно это касается моделей пользователей, потому что:

* **Входная модель** должна уметь содержать пароль.
* **Выходная модель** не должна содержать пароль.
* **Модели базы данных**, скорее всего, нужен хеш пароля.

> **Опасность**
>
> Никогда не храните пароли пользователей в открытом виде. Всегда храните «безопасный хеш», который затем можно проверить.
>
> Если вы не знаете, что такое «хеш пароля», вы узнаете это в [главах о безопасности](38-simple-oauth2.md).

## Несколько моделей

Вот общее представление о том, как могут выглядеть модели с полями паролей и где они используются:

```python title="extra_models/tutorial001_py310.py"
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


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: str | None = None


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved
```

### Про `**user_in.model_dump()`

#### `.model_dump()` в Pydantic

`user_in` — модель Pydantic класса `UserIn`.

У моделей Pydantic есть метод `.model_dump()`, который возвращает `dict` с данными модели.

Так что, если создать объект Pydantic `user_in` так:

```Python
user_in = UserIn(username="john", password="secret", email="john.doe@example.com")
```

а затем вызвать:

```Python
user_dict = user_in.model_dump()
```

в переменной `user_dict` окажется `dict` с данными (это `dict`, а не объект модели Pydantic).

А если вызвать:

```Python
print(user_dict)
```

мы получим `dict` Python с таким содержимым:

```Python
{
    "username": "john",
    "password": "secret",
    "email": "john.doe@example.com",
    "full_name": None,
}
```

#### Распаковка `dict`

Если взять `dict`, например `user_dict`, и передать его в функцию (или класс) как `**user_dict`, Python его «распакует». Он передаст ключи и значения `user_dict` напрямую как именованные аргументы.

Так что, продолжая с `user_dict` выше, запись:

```Python
UserInDB(**user_dict)
```

даст результат, эквивалентный:

```Python
UserInDB(
    username="john",
    password="secret",
    email="john.doe@example.com",
    full_name=None,
)
```

Или, точнее, с использованием `user_dict` напрямую, с любым содержимым, которое у него может быть в будущем:

```Python
UserInDB(
    username=user_dict["username"],
    password=user_dict["password"],
    email=user_dict["email"],
    full_name=user_dict["full_name"],
)
```

#### Модель Pydantic из содержимого другой модели

Поскольку в примере выше мы получили `user_dict` из `user_in.model_dump()`, этот код:

```Python
user_dict = user_in.model_dump()
UserInDB(**user_dict)
```

эквивалентен:

```Python
UserInDB(**user_in.model_dump())
```

...потому что `user_in.model_dump()` — это `dict`, и мы заставляем Python его «распаковать», передавая в `UserInDB` с префиксом `**`.

Так мы получаем модель Pydantic из данных другой модели Pydantic.

#### Распаковка `dict` и дополнительные именованные аргументы

А затем добавление дополнительного именованного аргумента `hashed_password=hashed_password`, как здесь:

```Python
UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
```

...в итоге работает так:

```Python
UserInDB(
    username=user_dict["username"],
    password=user_dict["password"],
    email=user_dict["email"],
    full_name=user_dict["full_name"],
    hashed_password=hashed_password,
)
```

> **Внимание**
>
> Вспомогательные функции `fake_password_hasher` и `fake_save_user` нужны лишь для демонстрации возможного потока данных; разумеется, никакой реальной безопасности они не обеспечивают.

## Уменьшение дублирования

Уменьшение дублирования кода — одна из ключевых идей **FastAPI**.

Дублирование кода повышает вероятность багов, проблем безопасности, рассинхронизации кода (когда вы обновили одно место, но не другие) и т. д.

А все эти модели разделяют много данных и дублируют имена и типы атрибутов.

Можно сделать лучше.

Можно объявить модель `UserBase`, которая служит основой для других наших моделей. А затем создать подклассы этой модели, наследующие её атрибуты (объявления типов, валидацию и т. д.).

Всё преобразование данных, валидация, документация и т. д. по-прежнему будут работать как обычно.

Так можно объявить только различия между моделями (с паролем в открытом виде `password`, с `hashed_password` и без пароля):

```python title="extra_models/tutorial002_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved
```

## `Union` или `anyOf`

Ответ можно объявить как `Union` двух или более типов — это означает, что ответ может быть любым из них.

В OpenAPI это будет описано через `anyOf`.

Для этого используйте стандартную подсказку типа Python [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union):

> **Примечание**
>
> При определении [`Union`](https://pydantic.dev/docs/validation/latest/concepts/unions/) сначала указывайте наиболее конкретный тип, а затем менее конкретный. В примере ниже более конкретный `PlaneItem` стоит перед `CarItem` в `Union[PlaneItem, CarItem]`.

```python title="extra_models/tutorial003_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type: str = "car"


class PlaneItem(BaseItem):
    type: str = "plane"
    size: int


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}


@app.get("/items/{item_id}", response_model=PlaneItem | CarItem)
async def read_item(item_id: str):
    return items[item_id]
```

### `Union` в Python 3.10

В этом примере мы передаём `Union[PlaneItem, CarItem]` как значение аргумента `response_model`.

Поскольку мы передаём его как **значение аргумента**, а не помещаем в **аннотацию типа**, нам приходится использовать `Union` даже в Python 3.10.

Если бы это было в аннотации типа, можно было бы использовать вертикальную черту:

```Python
some_variable: PlaneItem | CarItem
```

Но если написать это в присваивании `response_model=PlaneItem | CarItem`, мы получим ошибку, потому что Python попытается выполнить **недопустимую операцию** между `PlaneItem` и `CarItem`, а не интерпретировать это как аннотацию типа.

> *Примечание переводчика:* в актуальном коде примера используется `response_model=PlaneItem | CarItem`, и это работает с современными версиями Python и Pydantic; текст раздела в оригинале описывает более старое поведение.

## Список моделей

Точно так же можно объявлять ответы в виде списков объектов.

Для этого используйте стандартный `list` Python:

```python title="extra_models/tutorial004_py310.py"
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str


items = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]


@app.get("/items/", response_model=list[Item])
async def read_items():
    return items
```

## Ответ с произвольным `dict`

Ответ можно также объявить как обычный произвольный `dict`, указав только тип ключей и значений, без использования модели Pydantic.

Это полезно, если вы заранее не знаете допустимых имён полей/атрибутов (которые были бы нужны для модели Pydantic).

В этом случае можно использовать `dict`:

```python title="extra_models/tutorial005_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/keyword-weights/", response_model=dict[str, float])
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}
```

## Итоги

Используйте несколько моделей Pydantic и свободно наследуйте их для каждого случая.

Не обязательно иметь одну модель данных на сущность, если эта сущность может находиться в разных «состояниях». Пример — «сущность» **пользователя** с состояниями, включающими `password`, `password_hash` или отсутствие пароля.
