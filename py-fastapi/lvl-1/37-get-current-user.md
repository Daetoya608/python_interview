# Получение текущего пользователя

> Перевод страницы [Get Current User](https://fastapi.tiangolo.com/tutorial/security/get-current-user/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

В предыдущей главе система безопасности (основанная на системе внедрения зависимостей) передавала *функции операции пути* `token` в виде `str`:

```python title="security/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
```

Но это пока не очень полезно.

Давайте сделаем так, чтобы она давала нам текущего пользователя.

## Создайте модель пользователя

Сначала создадим модель пользователя Pydantic.

Так же как мы используем Pydantic для объявления тел запросов, его можно использовать где угодно:

```python title="security/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
```

## Создайте зависимость `get_current_user`

Создадим зависимость `get_current_user`.

Помните, что у зависимостей могут быть подзависимости?

У `get_current_user` будет зависимость от того же `oauth2_scheme`, который мы создали раньше.

Так же как раньше мы делали напрямую в *операции пути*, наша новая зависимость `get_current_user` будет получать `token` в виде `str` от подзависимости `oauth2_scheme`:

```python title="security/tutorial002_an_py310.py"
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user
```

## Получите пользователя

`get_current_user` будет использовать созданную нами (фиктивную) вспомогательную функцию, которая принимает токен в виде `str` и возвращает нашу модель Pydantic `User`:

```python title="security/tutorial002_an_py310.py"
def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )
```

## Внедрите текущего пользователя

Теперь в *операции пути* можно использовать тот же `Depends` с нашей `get_current_user`:

```python title="security/tutorial002_an_py310.py"
@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
```

Обратите внимание, что мы объявляем тип `current_user` как модель Pydantic `User`.

Это поможет нам внутри функции со всем автодополнением и проверками типов.

> **Совет**
>
> Вы, возможно, помните, что тела запросов тоже объявляются с помощью моделей Pydantic.
>
> Здесь **FastAPI** не запутается, потому что вы используете `Depends`.

> **Совет**
>
> То, как устроена эта система зависимостей, позволяет иметь разные зависимости (разные «dependable»), которые все возвращают модель `User`.
>
> Мы не ограничены только одной зависимостью, которая может возвращать такой тип данных.

## Другие модели

Теперь текущего пользователя можно получать прямо в *функциях операций пути*, а механизмы безопасности обрабатывать на уровне **внедрения зависимостей** с помощью `Depends`.

И для требований безопасности можно использовать любую модель или данные (в данном случае — модель Pydantic `User`).

Но вы не ограничены какой-то конкретной моделью данных, классом или типом.

Хотите, чтобы в модели были `id` и `email`, а `username` не было? Пожалуйста. Можно использовать те же инструменты.

Хотите просто `str`? Или просто `dict`? Или напрямую экземпляр класса модели базы данных? Всё работает одинаково.

На самом деле в ваше приложение входят не пользователи, а роботы, боты или другие системы, у которых есть только токен доступа? Опять же, всё работает так же.

Просто используйте любую модель, любой класс, любую базу данных, которые нужны вашему приложению. **FastAPI** поддержит вас системой внедрения зависимостей.

## Размер кода

Этот пример может показаться многословным. Помните, что мы смешиваем безопасность, модели данных, вспомогательные функции и *операции пути* в одном файле.

Но вот ключевой момент.

Код безопасности и внедрения зависимостей пишется один раз.

И его можно сделать сколь угодно сложным. И всё равно он будет написан лишь один раз, в одном месте. Со всей гибкостью.

При этом у вас могут быть тысячи эндпоинтов (*операций пути*), использующих одну и ту же систему безопасности.

И все они (или любая их часть) могут воспользоваться переиспользованием этих зависимостей или любых других, которые вы создадите.

И все эти тысячи *операций пути* могут занимать всего 3 строки:

```python title="security/tutorial002_an_py310.py"
@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
```

## Итоги

Теперь текущего пользователя можно получать прямо в *функции операции пути*.

Мы уже на полпути.

Осталось только добавить *операцию пути*, через которую пользователь/клиент будет действительно отправлять `username` и `password`.

Это следующий шаг.
