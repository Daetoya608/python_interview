# SQL (реляционные) базы данных

> Перевод страницы [SQL (Relational) Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

**FastAPI** не требует использовать SQL (реляционную) базу данных. Но можно использовать **любую базу данных**, какую захотите.

Здесь мы рассмотрим пример с использованием [SQLModel](https://sqlmodel.tiangolo.com/).

**SQLModel** построен поверх [SQLAlchemy](https://www.sqlalchemy.org/) и Pydantic. Его создал тот же автор, что и **FastAPI**, чтобы он идеально подходил для приложений FastAPI, которым нужны **SQL базы данных**.

> **Совет**
>
> Можно использовать любую другую библиотеку для SQL или NoSQL баз данных (в некоторых случаях их называют <abbr title="Object Relational Mapper — объектно-реляционное отображение: модное название библиотеки, где одни классы представляют SQL-таблицы, а их экземпляры — строки в этих таблицах">«ORM»</abbr>), FastAPI ничего вам не навязывает. 😎

Поскольку SQLModel основан на SQLAlchemy, можно легко использовать **любую базу данных, поддерживаемую** SQLAlchemy (а значит, и SQLModel), например:

* PostgreSQL
* MySQL
* SQLite
* Oracle
* Microsoft SQL Server и т. д.

В этом примере мы будем использовать **SQLite**, потому что она хранится в одном файле и Python имеет встроенную поддержку. Так что этот пример можно скопировать и запустить как есть.

Позже для продакшен-приложения вы, возможно, захотите использовать сервер баз данных вроде **PostgreSQL**.

> **Совет**
>
> Есть официальный генератор проектов с **FastAPI** и **PostgreSQL**, включающий фронтенд и другие инструменты: [https://github.com/fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)

Это очень простое и короткое руководство; если хотите узнать о базах данных в целом, об SQL или о более продвинутых возможностях, загляните в [документацию SQLModel](https://sqlmodel.tiangolo.com/).

## Установите `SQLModel`

Добавьте `sqlmodel` в проект:

```console
$ uv add sqlmodel
---> 100%
```

## Создайте приложение с одной моделью

Сначала создадим самую простую первую версию приложения с одной моделью **SQLModel**.

Позже мы улучшим её, повысив безопасность и универсальность с помощью **нескольких моделей** ниже. 🤓

Вот полный код первой версии:

```python title="sql_databases/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Hero]:
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.get("/heroes/{hero_id}")
def read_hero(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

Разберём его по частям.

### Создайте модели

Импортируйте `SQLModel` и создайте модель базы данных:

```python title="sql_databases/tutorial001_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str
```

Класс `Hero` очень похож на модель Pydantic (на самом деле «под капотом» он *и есть модель Pydantic*).

Есть несколько отличий:

* `table=True` сообщает SQLModel, что это *модель-таблица* (table model): она должна представлять **таблицу** в SQL базе данных, а не просто *модель данных* (как любой другой обычный класс Pydantic).

* `Field(primary_key=True)` сообщает SQLModel, что `id` — это **первичный ключ** в SQL базе данных (подробнее о первичных ключах SQL можно узнать в документации SQLModel).

    **Примечание:** мы используем `int | None` для поля первичного ключа, чтобы в коде Python можно было *создать объект без `id`* (`id=None`), предполагая, что база данных *сгенерирует его при сохранении*. SQLModel понимает, что `id` предоставит база данных, и *определяет столбец как ненулевой `INTEGER`* в схеме базы данных. Подробности — в [документации SQLModel о первичных ключах](https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#primary-key-id).

* `Field(index=True)` сообщает SQLModel, что для этого столбца нужно создать **SQL-индекс**, который ускорит поиск в базе данных при чтении данных с фильтрацией по этому столбцу.

    SQLModel будет знать, что объявленное как `str` будет SQL-столбцом типа `TEXT` (или `VARCHAR`, в зависимости от базы данных).

### Создайте движок (engine)

`engine` в SQLModel («под капотом» это на самом деле `engine` из SQLAlchemy) — это то, что **хранит подключения** к базе данных.

Для всего кода, подключающегося к одной и той же базе данных, у вас будет **один-единственный объект `engine`**.

```python title="sql_databases/tutorial001_an_py310.py"
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
```

`check_same_thread=False` позволяет FastAPI использовать одну и ту же базу данных SQLite в разных потоках. Это необходимо, поскольку **один запрос** может использовать **больше одного потока** (например, в зависимостях).

Не волнуйтесь: при той структуре кода, что мы используем, мы позже обеспечим **одну *сессию* SQLModel на запрос** — именно этого на самом деле и пытается добиться `check_same_thread`.

### Создайте таблицы

Затем добавим функцию, которая использует `SQLModel.metadata.create_all(engine)`, чтобы **создать таблицы** для всех *моделей-таблиц*.

```python title="sql_databases/tutorial001_an_py310.py"
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### Создайте зависимость сессии

**`Session`** (сессия) — это то, что хранит **объекты в памяти** и отслеживает все необходимые изменения данных, а затем **использует `engine`** для взаимодействия с базой данных.

Мы создадим **зависимость** FastAPI с `yield`, которая будет предоставлять новую `Session` для каждого запроса. Именно это гарантирует, что мы используем одну сессию на запрос. 🤓

Затем создадим `Annotated`-зависимость `SessionDep`, чтобы упростить остальной код, который будет использовать эту зависимость.

```python title="sql_databases/tutorial001_an_py310.py"
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
```

### Создайте таблицы базы данных при запуске

Таблицы базы данных мы будем создавать при запуске приложения.

```python title="sql_databases/tutorial001_an_py310.py"
app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
```

Здесь мы создаём таблицы по событию запуска приложения.

В продакшене вы, скорее всего, будете использовать скрипт миграций, который запускается перед стартом приложения. 🤓

> **Совет**
>
> В SQLModel появятся утилиты для миграций — обёртки над Alembic, но пока можно использовать [Alembic](https://alembic.sqlalchemy.org/en/latest/) напрямую.

### Создайте героя

Поскольку каждая модель SQLModel — это также модель Pydantic, её можно использовать в тех же **аннотациях типов**, что и модели Pydantic.

Например, если объявить параметр типа `Hero`, он будет прочитан из **JSON-тела**.

Точно так же его можно объявить **типом возвращаемого значения** функции, и тогда форма данных появится в интерфейсе автоматической документации API.

```python title="sql_databases/tutorial001_an_py310.py"
@app.post("/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero
```

Здесь мы используем зависимость `SessionDep` (`Session`), чтобы добавить нового `Hero` в экземпляр `Session`, зафиксировать (commit) изменения в базе данных, обновить данные в `hero`, а затем вернуть его.

### Прочитайте героев

**Читать** `Hero` из базы данных можно с помощью `select()`. Можно добавить `limit` и `offset` для постраничного вывода результатов.

```python title="sql_databases/tutorial001_an_py310.py"
@app.get("/heroes/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Hero]:
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
```

### Прочитайте одного героя

Можно **прочитать** одного `Hero`.

```python title="sql_databases/tutorial001_an_py310.py"
@app.get("/heroes/{hero_id}")
def read_hero(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero
```

### Удалите героя

Можно также **удалить** `Hero`.

```python title="sql_databases/tutorial001_an_py310.py"
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

### Запустите приложение

Запустите приложение:

```console
$ uv run fastapi dev

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Затем откройте интерфейс `/docs` — вы увидите, что **FastAPI** использует эти **модели**, чтобы **документировать** API, а также будет использовать их, чтобы **сериализовать** и **валидировать** данные.

<img src="https://fastapi.tiangolo.com/img/tutorial/sql-databases/image01.png">

## Обновите приложение, используя несколько моделей

Теперь немного **отрефакторим** это приложение, чтобы повысить **безопасность** и **универсальность**.

Если посмотреть на предыдущее приложение, в интерфейсе видно, что до сих пор оно позволяет клиенту решать, какой `id` будет у создаваемого `Hero`. 😱

Нельзя этого допускать: клиенты могут перезаписать `id`, уже назначенный в БД. Решать, какой будет `id`, должен **бэкенд** или **база данных**, **а не клиент**.

Кроме того, мы создаём для героя `secret_name`, но пока возвращаем его везде, а это не очень-то **секретно**... 😅

Исправим это, добавив несколько **дополнительных моделей**. Вот где SQLModel себя проявит. ✨

### Создайте несколько моделей

В **SQLModel** любой класс модели, у которого есть `table=True`, — это **модель-таблица**.

А любой класс модели без `table=True` — это **модель данных**; на самом деле это просто модели Pydantic (с парой небольших дополнительных возможностей). 🤓

С SQLModel можно использовать **наследование**, чтобы **не дублировать** все поля во всех случаях.

Вот полный код второй версии:

```python title="sql_databases/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str


class HeroPublic(HeroBase):
    id: int


class HeroCreate(HeroBase):
    secret_name: str


class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db


@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

#### `HeroBase` — базовый класс

Начнём с модели `HeroBase`, в которой есть все **поля, общие** для всех моделей:

* `name`
* `age`

```python title="sql_databases/tutorial002_an_py310.py"
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
```

#### `Hero` — *модель-таблица*

Затем создадим `Hero` — собственно *модель-таблицу* — с **дополнительными полями**, которых не всегда есть в других моделях:

* `id`
* `secret_name`

Поскольку `Hero` наследуется от `HeroBase`, у неё **также** есть **поля**, объявленные в `HeroBase`, поэтому все поля `Hero` таковы:

* `id`
* `name`
* `age`
* `secret_name`

```python title="sql_databases/tutorial002_an_py310.py"
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str
```

#### `HeroPublic` — публичная *модель данных*

Далее создаём модель `HeroPublic` — именно её мы будем **возвращать** клиентам API.

У неё те же поля, что и у `HeroBase`, поэтому `secret_name` в неё не войдёт.

Наконец-то личность наших героев защищена! 🥷

Она также заново объявляет `id: int`. Этим мы заключаем **контракт** с клиентами API: они всегда могут рассчитывать, что `id` будет присутствовать и будет `int` (никогда не `None`).

> **Совет**
>
> Если модель ответа гарантирует, что значение всегда доступно и всегда `int` (а не `None`), это очень полезно для клиентов API: имея такую уверенность, они могут писать гораздо более простой код.
>
> Кроме того, у **автоматически сгенерированных клиентов** будут более простые интерфейсы, так что разработчикам, взаимодействующим с вашим API, будет гораздо приятнее с ним работать. 😎

Все поля в `HeroPublic` те же, что и в `HeroBase`, а `id` объявлен как `int` (не `None`):

* `id`
* `name`
* `age`

```python title="sql_databases/tutorial002_an_py310.py"
class HeroPublic(HeroBase):
    id: int
```

#### `HeroCreate` — *модель данных* для создания героя

Теперь создадим модель `HeroCreate` — именно она будет **валидировать** данные от клиентов.

У неё те же поля, что и у `HeroBase`, а также `secret_name`.

Теперь, когда клиенты **создают нового героя**, они отправляют `secret_name`, он сохраняется в базе данных, но эти секретные имена не будут возвращаться клиентам через API.

> **Совет**
>
> Именно так следует обращаться с **паролями**: принимать их, но не возвращать через API.
>
> А также **хешировать** значения паролей перед сохранением, **никогда не храня их в открытом виде**.

Поля `HeroCreate`:

* `name`
* `age`
* `secret_name`

```python title="sql_databases/tutorial002_an_py310.py"
class HeroCreate(HeroBase):
    secret_name: str
```

#### `HeroUpdate` — *модель данных* для обновления героя

В предыдущей версии приложения у нас не было способа **обновить героя**, но теперь, с **несколькими моделями**, это можно сделать. 🎉

*Модель данных* `HeroUpdate` несколько особенная: у неё **все те же поля**, что нужны для создания нового героя, но все поля **необязательные** (у всех есть значение по умолчанию). Так при обновлении героя можно отправлять только те поля, которые нужно изменить.

Поскольку все **поля на самом деле меняются** (тип теперь включает `None`, и у них теперь значение по умолчанию `None`), их нужно **объявить заново**.

На самом деле наследоваться от `HeroBase` не обязательно, раз мы объявляем все поля заново. Я оставлю наследование просто для единообразия, но это не обязательно. Скорее дело вкуса. 🤷

Поля `HeroUpdate`:

* `name`
* `age`
* `secret_name`

```python title="sql_databases/tutorial002_an_py310.py"
class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None
```

### Создание через `HeroCreate` и возврат `HeroPublic`

Теперь, когда у нас **несколько моделей**, можно обновить части приложения, которые их используют.

В запросе мы получаем *модель данных* `HeroCreate` и из неё создаём *модель-таблицу* `Hero`.

У этой новой *модели-таблицы* `Hero` будут поля, отправленные клиентом, а также `id`, сгенерированный базой данных.

Затем мы возвращаем из функции ту же *модель-таблицу* `Hero` как есть. Но поскольку мы объявляем `response_model` с *моделью данных* `HeroPublic`, **FastAPI** будет использовать `HeroPublic` для валидации и сериализации данных.

```python title="sql_databases/tutorial002_an_py310.py"
@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

> **Совет**
>
> Теперь мы используем `response_model=HeroPublic` вместо **аннотации типа возвращаемого значения** `-> HeroPublic`, потому что возвращаемое значение на самом деле *не* `HeroPublic`.
>
> Если бы мы объявили `-> HeroPublic`, редактор и линтер пожаловались бы (вполне справедливо), что возвращается `Hero`, а не `HeroPublic`.
>
> Объявляя это в `response_model`, мы говорим **FastAPI** делать своё дело, не мешая аннотациям типов и помощи от редактора и других инструментов.

### Чтение героев с `HeroPublic`

Чтобы **читать** `Hero`, можно сделать то же, что и раньше; опять же используем `response_model=list[HeroPublic]`, чтобы данные правильно валидировались и сериализовались.

```python title="sql_databases/tutorial002_an_py310.py"
@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
```

### Чтение одного героя с `HeroPublic`

Можно **прочитать** одного героя:

```python title="sql_databases/tutorial002_an_py310.py"
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero
```

### Обновление героя с `HeroUpdate`

Можно **обновить героя**. Для этого используется HTTP-операция `PATCH`.

А в коде мы получаем `dict` со всеми данными, отправленными клиентом, — **только с данными, отправленными клиентом**, исключая значения, которые оказались бы там только потому, что они значения по умолчанию. Для этого используем `exclude_unset=True`. Это главный трюк. 🪄

Затем используем `hero_db.sqlmodel_update(hero_data)`, чтобы обновить `hero_db` данными из `hero_data`.

```python title="sql_databases/tutorial002_an_py310.py"
@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db
```

### Снова удаление героя

**Удаление** героя остаётся почти таким же.

Желание отрефакторить всё подряд здесь мы удовлетворять не будем. 😅

```python title="sql_databases/tutorial002_an_py310.py"
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

### Снова запустите приложение

Снова запустите приложение:

```console
$ uv run fastapi dev

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Если открыть интерфейс API `/docs`, вы увидите, что он обновился и больше не ожидает получать `id` от клиента при создании героя и т. д.

<img src="https://fastapi.tiangolo.com/img/tutorial/sql-databases/image02.png">

## Итоги

[**SQLModel**](https://sqlmodel.tiangolo.com/) можно использовать для взаимодействия с SQL базой данных и упрощать код с помощью *моделей данных* и *моделей-таблиц*.

Гораздо больше можно узнать в документации **SQLModel** — там есть более длинное мини-[руководство по использованию SQLModel с **FastAPI**](https://sqlmodel.tiangolo.com/tutorial/fastapi/). 🚀
