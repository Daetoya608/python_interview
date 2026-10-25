# OAuth2 с паролем (и хешированием), Bearer с JWT-токенами

> Перевод страницы [OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Теперь, когда у нас есть весь поток безопасности, сделаем приложение по-настоящему безопасным, используя токены <abbr title="JSON Web Tokens">JWT</abbr> и безопасное хеширование паролей.

Этот код действительно можно использовать в своём приложении, хранить хеши паролей в базе данных и т. д.

Начнём с того места, где остановились в предыдущей главе, и будем его дополнять.

## О JWT

JWT означает «JSON Web Tokens».

Это стандарт кодирования JSON-объекта в длинную плотную строку без пробелов. Выглядит это так:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Он не зашифрован, поэтому любой может восстановить информацию из его содержимого.

Но он подписан. Поэтому, получив выданный вами токен, вы можете проверить, что выдали его именно вы.

Так можно создать токен со сроком действия, скажем, 1 неделя. А когда пользователь вернётся на следующий день с этим токеном, вы будете знать, что он всё ещё вошёл в вашу систему.

Через неделю срок действия токена истечёт, пользователь не будет авторизован и должен будет снова войти, чтобы получить новый токен. А если пользователь (или третья сторона) попытается изменить токен, чтобы поменять срок действия, вы сможете это обнаружить, потому что подписи не совпадут.

Если хотите поиграть с JWT-токенами и посмотреть, как они работают, загляните на [https://jwt.io](https://jwt.io/).

## Установите `PyJWT`

Чтобы генерировать и проверять JWT-токены в Python, нужно установить `PyJWT`.

Добавьте `pyjwt` в проект:

```console
$ uv add pyjwt

---> 100%
```

> **Примечание**
>
> Если вы планируете использовать алгоритмы цифровой подписи вроде RSA или ECDSA, нужно установить зависимость с криптографической библиотекой `pyjwt[crypto]`.
>
> Подробнее об этом можно прочитать в [документации по установке PyJWT](https://pyjwt.readthedocs.io/en/latest/installation.html).

## Хеширование паролей

«Хеширование» означает преобразование некоторого содержимого (в данном случае пароля) в последовательность байт (просто строку), которая выглядит как абракадабра.

Каждый раз, когда вы передаёте в точности то же содержимое (в точности тот же пароль), вы получаете в точности ту же абракадабру.

Но из абракадабры нельзя получить обратно пароль.

### Зачем хешировать пароли

Если вашу базу данных украдут, у вора не будет паролей ваших пользователей в открытом виде — только хеши.

Значит, вор не сможет попробовать использовать этот пароль в другой системе (поскольку многие пользователи используют один и тот же пароль везде, это было бы опасно).

## Установите `pwdlib`

pwdlib — отличный пакет Python для работы с хешами паролей.

Он поддерживает множество безопасных алгоритмов хеширования и утилиты для работы с ними.

Рекомендуемый алгоритм — «Argon2».

Добавьте `pwdlib` с Argon2 в проект:

```console
$ uv add "pwdlib[argon2]"

---> 100%
```

> **Совет**
>
> С помощью `pwdlib` можно даже настроить чтение паролей, созданных **Django**, плагином безопасности **Flask** или многими другими.
>
> Так можно, например, использовать одни и те же данные из базы данных приложения Django в приложении FastAPI. Или постепенно мигрировать приложение Django, используя ту же базу данных.
>
> И ваши пользователи смогут входить одновременно как из приложения Django, так и из приложения **FastAPI**.

## Хеширование и проверка паролей

Импортируйте нужные инструменты из `pwdlib`.

Создайте экземпляр PasswordHash с рекомендуемыми настройками — он будет использоваться для хеширования и проверки паролей.

> **Совет**
>
> pwdlib также поддерживает алгоритм хеширования bcrypt, но не включает устаревшие алгоритмы — для работы с устаревшими хешами рекомендуется использовать библиотеку passlib.
>
> Например, с её помощью можно читать и проверять пароли, сгенерированные другой системой (вроде Django), но хешировать новые пароли другим алгоритмом, например Argon2 или Bcrypt.
>
> И при этом быть совместимым со всеми ними одновременно.

Создайте вспомогательную функцию для хеширования пароля, пришедшего от пользователя.

И ещё одну — для проверки, соответствует ли полученный пароль сохранённому хешу.

И ещё одну — для аутентификации и возврата пользователя.

Вот полный код этой главы:

```python title="security/tutorial004_an_py310.py"
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

# чтобы получить такую строку, выполните:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
```

Когда `authenticate_user` вызывается с именем пользователя, которого нет в базе данных, мы всё равно выполняем `verify_password` с фиктивным хешем.

Это гарантирует, что эндпоинт отвечает примерно за одно и то же время независимо от того, существует ли имя пользователя, и предотвращает **атаки по времени** (timing attacks), с помощью которых можно было бы перебрать существующие имена пользователей.

> **Примечание**
>
> Если посмотреть на новую (фиктивную) базу данных `fake_users_db`, видно, как теперь выглядит хешированный пароль: `"$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc"`.

## Работа с JWT-токенами

Импортируйте установленные модули.

Создайте случайный секретный ключ, который будет использоваться для подписи JWT-токенов.

Чтобы сгенерировать безопасный случайный секретный ключ, используйте команду:

```console
$ openssl rand -hex 32

09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

И скопируйте вывод в переменную `SECRET_KEY` (не используйте ключ из примера).

Создайте переменную `ALGORITHM` с алгоритмом подписи JWT-токена и задайте ей значение `"HS256"`.

Создайте переменную для срока действия токена.

Определите модель Pydantic, которая будет использоваться в эндпоинте токена для ответа.

Создайте вспомогательную функцию для генерации нового токена доступа.

```python title="security/tutorial004_an_py310.py"
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ...

class Token(BaseModel):
    access_token: str
    token_type: str

# ...

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

## Обновите зависимости

Обновите `get_current_user`, чтобы она получала тот же токен, что и раньше, но на этот раз — JWT-токен.

Декодируйте полученный токен, проверьте его и верните текущего пользователя.

Если токен невалиден, сразу верните HTTP-ошибку.

```python title="security/tutorial004_an_py310.py"
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
```

## Обновите *операцию пути* `/token`

Создайте `timedelta` со сроком действия токена.

Создайте настоящий JWT-токен доступа и верните его.

```python title="security/tutorial004_an_py310.py"
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
```

### Технические подробности о «субъекте» JWT `sub`

Спецификация JWT говорит, что есть ключ `sub` с субъектом (subject) токена.

Использовать его не обязательно, но именно туда следует поместить идентификатор пользователя, поэтому мы используем его здесь.

JWT можно использовать и для других целей, помимо идентификации пользователя и разрешения ему выполнять операции непосредственно в вашем API.

Например, можно идентифицировать «автомобиль» или «пост в блоге».

Затем можно добавить разрешения для этой сущности, например «водить» (для автомобиля) или «редактировать» (для блога).

А затем выдать этот JWT-токен пользователю (или боту), и он сможет выполнять эти действия (водить автомобиль или редактировать пост в блоге), даже не имея учётной записи, — просто с JWT-токеном, который ваш API сгенерировал для этого.

Используя эти идеи, JWT можно применять для гораздо более сложных сценариев.

В таких случаях у нескольких сущностей может быть одинаковый ID, скажем `foo` (пользователь `foo`, автомобиль `foo` и пост в блоге `foo`).

Поэтому, чтобы избежать коллизий ID, при создании JWT-токена для пользователя можно добавить к значению ключа `sub` префикс, например `username:`. Тогда в этом примере значение `sub` могло бы быть: `username:johndoe`.

Важно помнить, что ключ `sub` должен содержать уникальный идентификатор в пределах всего приложения, и это должна быть строка.

## Проверьте

Запустите сервер и откройте документацию: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Вы увидите такой интерфейс:

<img src="https://fastapi.tiangolo.com/img/tutorial/security/image07.png">

Авторизуйте приложение так же, как раньше.

С учётными данными:

Имя пользователя: `johndoe`
Пароль: `secret`

> **Совет**
>
> Обратите внимание, что нигде в коде нет пароля «`secret`» в открытом виде — есть только хешированная версия.

<img src="https://fastapi.tiangolo.com/img/tutorial/security/image08.png">

Вызовите эндпоинт `/users/me/`, и вы получите ответ:

```JSON
{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "full_name": "John Doe",
  "disabled": false
}
```

<img src="https://fastapi.tiangolo.com/img/tutorial/security/image09.png">

Если открыть инструменты разработчика, можно увидеть, что отправляемые данные включают только токен; пароль отправляется только в первом запросе — для аутентификации пользователя и получения токена доступа, — но не после этого:

<img src="https://fastapi.tiangolo.com/img/tutorial/security/image10.png">

> **Примечание**
>
> Обратите внимание на заголовок `Authorization` со значением, начинающимся с `Bearer `.

## Продвинутое использование со `scopes`

В OAuth2 есть понятие «областей доступа» (scopes).

С их помощью можно добавить в JWT-токен определённый набор разрешений.

Затем этот токен можно выдать пользователю напрямую или третьей стороне, чтобы они взаимодействовали с вашим API с определённым набором ограничений.

Как их использовать и как они интегрированы в **FastAPI**, вы узнаете позже в **Продвинутом руководстве пользователя**.

## Итоги

С тем, что вы уже видели, можно настроить безопасное приложение **FastAPI** с использованием стандартов вроде OAuth2 и JWT.

Почти в любом фреймворке работа с безопасностью довольно быстро становится сложной темой.

Многим пакетам, которые сильно её упрощают, приходится идти на множество компромиссов с моделью данных, базой данных и доступными возможностями. А некоторые пакеты, которые упрощают всё слишком сильно, на самом деле имеют внутри уязвимости.

---

**FastAPI** не идёт ни на какие компромиссы ни с базой данных, ни с моделью данных, ни с инструментами.

Он даёт вам полную гибкость в выборе того, что лучше всего подходит вашему проекту.

И можно напрямую использовать многие хорошо поддерживаемые и широко используемые пакеты вроде `pwdlib` и `PyJWT`, потому что **FastAPI** не требует никаких сложных механизмов для интеграции внешних пакетов.

Но он даёт вам инструменты, чтобы максимально упростить процесс без ущерба для гибкости, надёжности или безопасности.

И можно относительно просто использовать и реализовывать безопасные стандартные протоколы, такие как OAuth2.

В **Продвинутом руководстве пользователя** можно узнать больше о том, как использовать «области доступа» (scopes) OAuth2 для более детальной системы разрешений по тем же стандартам. OAuth2 со scopes — механизм, который используют многие крупные провайдеры аутентификации, такие как Facebook, Google, GitHub, Microsoft, X (Twitter) и т. д., чтобы авторизовать сторонние приложения для взаимодействия с их API от имени их пользователей.
