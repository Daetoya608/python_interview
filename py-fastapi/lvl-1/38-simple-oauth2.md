# Простой OAuth2 с паролем и Bearer

> Перевод страницы [Simple OAuth2 with Password and Bearer](https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Теперь продолжим с того места, где остановились в предыдущей главе, и добавим недостающие части, чтобы получить полный поток безопасности.

## Получите `username` и `password`

Чтобы получить `username` и `password`, воспользуемся утилитами безопасности **FastAPI**.

OAuth2 требует, чтобы при использовании «password flow» (который мы используем) клиент/пользователь отправлял поля `username` и `password` как данные формы.

И спецификация говорит, что поля должны называться именно так. Так что `user-name` или `email` не подойдут.

Но не волнуйтесь: во фронтенде вы можете показывать их конечным пользователям как угодно.

А модели базы данных могут использовать любые другие имена.

Но для *операции пути* входа в систему нужно использовать эти имена, чтобы соответствовать спецификации (и иметь возможность, например, пользоваться встроенной системой документации API).

Спецификация также указывает, что `username` и `password` должны отправляться как данные формы (то есть никакого JSON).

### `scope`

Спецификация также говорит, что клиент может отправить ещё одно поле формы — «`scope`».

Поле формы называется `scope` (в единственном числе), но на самом деле это длинная строка с «областями доступа» (scopes), разделёнными пробелами.

Каждая «область доступа» — это просто строка (без пробелов).

Обычно они используются для объявления конкретных разрешений безопасности, например:

* `users:read` или `users:write` — распространённые примеры.
* `instagram_basic` используется Facebook / Instagram.
* `https://www.googleapis.com/auth/drive` используется Google.

> **Примечание**
>
> В OAuth2 «scope» — это просто строка, объявляющая требуемое конкретное разрешение.
>
> Неважно, содержит ли она другие символы вроде `:` или является URL.
>
> Эти детали зависят от реализации.
>
> Для OAuth2 это просто строки.

## Код для получения `username` и `password`

Теперь воспользуемся утилитами, которые предоставляет **FastAPI**.

### `OAuth2PasswordRequestForm`

Сначала импортируйте `OAuth2PasswordRequestForm` и используйте его как зависимость с `Depends` в *операции пути* для `/token`. Вот полный код этой главы:

```python title="security/tutorial003_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # Это вообще не обеспечивает никакой безопасности
    # Смотрите следующую версию
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
```

`OAuth2PasswordRequestForm` — это зависимость-класс, которая объявляет тело формы с:

* `username`.
* `password`.
* Необязательным полем `scope` — большой строкой, составленной из строк, разделённых пробелами.
* Необязательным `grant_type`.

> **Совет**
>
> Спецификация OAuth2 на самом деле *требует* поле `grant_type` с фиксированным значением `password`, но `OAuth2PasswordRequestForm` этого не проверяет.
>
> Если нужно это проверять, используйте `OAuth2PasswordRequestFormStrict` вместо `OAuth2PasswordRequestForm`.

* Необязательным `client_id` (в нашем примере он не нужен).
* Необязательным `client_secret` (в нашем примере он не нужен).

> **Примечание**
>
> `OAuth2PasswordRequestForm` — не специальный для **FastAPI** класс, в отличие от `OAuth2PasswordBearer`.
>
> `OAuth2PasswordBearer` сообщает **FastAPI**, что это схема безопасности. Поэтому она соответствующим образом добавляется в OpenAPI.
>
> А `OAuth2PasswordRequestForm` — просто зависимость-класс, которую вы могли бы написать сами, или же можно было объявить параметры `Form` напрямую.
>
> Но поскольку это распространённый сценарий, **FastAPI** предоставляет его напрямую, просто для удобства.

### Используйте данные формы

> **Совет**
>
> У экземпляра зависимости-класса `OAuth2PasswordRequestForm` не будет атрибута `scope` с длинной строкой, разделённой пробелами; вместо этого у него будет атрибут `scopes` с настоящим списком строк — по одной на каждую переданную область доступа.
>
> В этом примере мы не используем `scopes`, но эта функциональность есть, если понадобится.

Теперь получите данные пользователя из (фиктивной) базы данных, используя `username` из поля формы.

Если такого пользователя нет, возвращаем ошибку «Incorrect username or password» (неверное имя пользователя или пароль).

Для ошибки используем исключение `HTTPException`:

```python title="security/tutorial003_an_py310.py"
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
```

### Проверьте пароль

На этом этапе у нас есть данные пользователя из базы данных, но пароль мы ещё не проверили.

Сначала поместим эти данные в модель Pydantic `UserInDB`.

Никогда не следует хранить пароли в открытом виде, поэтому мы будем использовать (фиктивную) систему хеширования паролей.

Если пароли не совпадают, возвращаем ту же ошибку.

#### Хеширование паролей

«Хеширование» означает преобразование некоторого содержимого (в данном случае пароля) в последовательность байт (просто строку), которая выглядит как абракадабра.

Каждый раз, когда вы передаёте в точности то же содержимое (в точности тот же пароль), вы получаете в точности ту же абракадабру.

Но из абракадабры нельзя получить обратно пароль.

##### Зачем хешировать пароли

Если вашу базу данных украдут, у вора не будет паролей ваших пользователей в открытом виде — только хеши.

Значит, вор не сможет попробовать использовать те же пароли в другой системе (поскольку многие пользователи используют один и тот же пароль везде, это было бы опасно).

```python title="security/tutorial003_an_py310.py"
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
```

#### Про `**user_dict`

`UserInDB(**user_dict)` означает:

*Передать ключи и значения `user_dict` напрямую как именованные аргументы, что эквивалентно:*

```Python
UserInDB(
    username=user_dict["username"],
    email=user_dict["email"],
    full_name=user_dict["full_name"],
    disabled=user_dict["disabled"],
    hashed_password=user_dict["hashed_password"],
)
```

> **Примечание**
>
> Более полное объяснение `**user_dict` смотрите в [документации по **дополнительным моделям**](19-extra-models.md).

## Верните токен

Ответ эндпоинта `token` должен быть JSON-объектом.

В нём должен быть `token_type`. В нашем случае, поскольку мы используем токены «Bearer», тип токена должен быть «`bearer`».

И в нём должен быть `access_token` — строка с нашим токеном доступа.

В этом простом примере мы поступим совершенно небезопасно и вернём в качестве токена тот же `username`.

> **Совет**
>
> В следующей главе вы увидите по-настоящему безопасную реализацию — с хешированием паролей и токенами <abbr title="JSON Web Tokens">JWT</abbr>.
>
> Но пока сосредоточимся на нужных нам конкретных деталях.

```python title="security/tutorial003_an_py310.py"
    return {"access_token": user.username, "token_type": "bearer"}
```

> **Совет**
>
> Согласно спецификации, нужно возвращать JSON с `access_token` и `token_type`, как в этом примере.
>
> Это нужно сделать самостоятельно в своём коде и убедиться, что используются именно эти ключи JSON.
>
> Это почти единственное, что нужно не забыть сделать правильно самостоятельно, чтобы соответствовать спецификациям.
>
> Всё остальное **FastAPI** делает за вас.

## Обновите зависимости

Теперь обновим наши зависимости.

Мы хотим получать `current_user` *только* если этот пользователь активен.

Поэтому создаём дополнительную зависимость `get_current_active_user`, которая, в свою очередь, использует `get_current_user` как зависимость.

Обе эти зависимости просто вернут HTTP-ошибку, если пользователь не существует или неактивен.

Так что в нашем эндпоинте мы получим пользователя, только если он существует, был правильно аутентифицирован и активен:

```python title="security/tutorial003_an_py310.py"
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ...


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
```

> **Примечание**
>
> Дополнительный заголовок `WWW-Authenticate` со значением `Bearer`, который мы здесь возвращаем, тоже часть спецификации.
>
> Любой HTTP-код статуса (ошибки) 401 «UNAUTHORIZED» должен также возвращать заголовок `WWW-Authenticate`.
>
> В случае bearer-токенов (наш случай) значение этого заголовка должно быть `Bearer`.
>
> На самом деле этот дополнительный заголовок можно не передавать, и всё равно будет работать.
>
> Но он указан здесь для соответствия спецификациям.
>
> Кроме того, могут существовать инструменты, которые ожидают и используют его (сейчас или в будущем), и это может быть полезно вам или вашим пользователям — сейчас или в будущем.
>
> В этом и польза стандартов...

## Посмотрите в действии

Откройте интерактивную документацию: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Аутентифицируйтесь

Нажмите кнопку «Authorize».

Используйте учётные данные:

Пользователь: `johndoe`

Пароль: `secret`

<img src="https://fastapi.tiangolo.com/img/tutorial/security/image04.png">

После аутентификации в системе вы увидите следующее:

<img src="https://fastapi.tiangolo.com/img/tutorial/security/image05.png">

### Получите данные своего пользователя

Теперь используйте операцию `GET` с путём `/users/me`.

Вы получите данные своего пользователя, например:

```JSON
{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "full_name": "John Doe",
  "disabled": false,
  "hashed_password": "fakehashedsecret"
}
```

<img src="https://fastapi.tiangolo.com/img/tutorial/security/image06.png">

Если нажать на значок замка и выйти из системы, а затем снова попробовать ту же операцию, вы получите HTTP-ошибку 401:

```JSON
{
  "detail": "Not authenticated"
}
```

### Неактивный пользователь

Теперь попробуйте с неактивным пользователем, аутентифицируйтесь с:

Пользователь: `alice`

Пароль: `secret2`

И попробуйте использовать операцию `GET` с путём `/users/me`.

Вы получите ошибку «Inactive user» (неактивный пользователь):

```JSON
{
  "detail": "Inactive user"
}
```

## Итоги

Теперь у вас есть инструменты, чтобы реализовать полноценную систему безопасности для своего API на основе `username` и `password`.

С помощью этих инструментов систему безопасности можно сделать совместимой с любой базой данных и любой моделью пользователя или данных.

Единственная недостающая деталь — на самом деле она пока не «безопасна».

В следующей главе вы увидите, как использовать безопасную библиотеку хеширования паролей и токены <abbr title="JSON Web Tokens">JWT</abbr>.
