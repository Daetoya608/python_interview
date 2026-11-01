# SQLAlchemy — уровень 1: ORM, подключение, модели и CRUD

Учебный материал под требования аттестации. Основной синтаксис — **SQLAlchemy 2.0**; примеры `Column` и старого API показаны отдельно. Это изложение по теме, а не дословный перевод документации.

## 1. Что такое ORM

**ORM — Object Relational Mapper** — связывает объекты языка с реляционными таблицами: класс описывает таблицу, его атрибуты — колонки, экземпляр обычно представляет строку. ORM строит SQL, преобразует результаты в объекты и отслеживает изменения для записи.

Пример: Python-объект `User(name="Anna", ...)` становится строкой в `users`; результат SELECT можно получить как User и изменить через присваивание атрибута.

ORM сокращает повторяющийся код и помогает работать со связями, но не отменяет SQL, ограничения БД, транзакции и индексы. Неэффективный ORM-запрос может оставаться неэффективным SQL-запросом.

В SQLAlchemy есть два связанных слоя:

- **Core**: Engine, Connection, Table и SQL-выражения. Позволяет работать без ORM-классов.
- **ORM**: маппинг классов, Session, связи и управление состоянием объектов. Использует Core.

Основа примеров — [официальный ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html).

## 2. Как запустить практику

Из корня этого репозитория в PowerShell:

```powershell
cd py-sqlalchemy/practice
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe demo.py
```

В Unix/macOS команды создания и запуска окружения: `python3 -m venv .venv`, затем `.venv/bin/python ...`.

`demo.py` выполняет CRUD, связи, запросы, варианты загрузки и rollback на отдельной SQLite **в памяти**. Каждый запуск начинает с новой БД. `models.py` содержит общую схему; импорт моделей сам по себе не создаёт таблицы. API и миграции разобраны в `lvl-2.md`. Зависимости зафиксированы диапазонами совместимости, а не полным lock-файлом.

## 3. Подключение: Engine, драйвер и URL

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite+pysqlite:///study.db", echo=True)
```

Engine хранит настройки диалекта и драйвера и управляет пулом соединений. Создание Engine обычно ещё не открывает соединение: оно получается при первой операции с БД. Engine обычно создают один раз на конфигурацию БД в процессе, Session — на отдельную единицу работы.

| URL | Значение |
|---|---|
| `sqlite+pysqlite:///study.db` | Файл SQLite относительно текущего каталога |
| `sqlite+pysqlite:///:memory:` | SQLite в памяти; база связана с соединением |
| `postgresql+psycopg://user:password@host:5432/dbname` | PostgreSQL через установленный драйвер psycopg |

Диалект адаптирует SQL под СУБД; драйвер выполняет обмен с ней. SQLite-драйвер поставляется с обычным Python. PostgreSQL-драйвер устанавливают отдельно. `echo=True` выводит SQL для обучения; значения параметров могут попасть в лог.

`engine.connect()` даёт Core Connection. В ORM прикладные операции обычно выполняют через Session, которая получает соединение из Engine. Session и соединение — не одно и то же.

## 4. Base, таблицы и колонки

Минимальная самостоятельная модель:

```python
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    age: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
```

- `Base` — базовый класс декларативного маппинга. `Base.metadata` содержит описание связанных таблиц.
- `__tablename__` — реальное имя таблицы.
- `Mapped[T]` — аннотация ORM-атрибута; `mapped_column(...)` задаёт колонку и её параметры.
- `primary_key=True` — первичный ключ. ORM использует его для идентификации строки.
- `unique=True` — уникальность, проверяемая БД. Предварительный SELECT не заменяет это ограничение.
- `nullable=False` запрещает SQL NULL. В типизированном маппинге `Mapped[str]` обычно выводит NOT NULL, `Mapped[str | None]` — nullable, если не задано явное переопределение.
- `index=True` создаёт индекс при создании схемы; индекс ускоряет подходящие запросы, но имеет стоимость записи и хранения.
- `default=True` — значение, которое SQLAlchemy подставляет при INSERT при отсутствии значения. Оно не обязательно уже доступно сразу после Python-конструктора. `server_default` — default на стороне БД, применимый и к INSERT из других клиентов.

| Тип | Пример назначения |
|---|---|
| `Integer` | Целые числа |
| `String(n)` / `Text` | Строки ограниченной / произвольной длины |
| `Boolean` | Логический признак |
| `Date`, `DateTime` | Дата и дата со временем |
| `Numeric(precision, scale)` | Точные десятичные значения, например суммы |
| `Float` | Приближённые вещественные значения |
| `ForeignKey("users.id")` | Ограничение ссылки на другую таблицу |

Типы и ограничения зависят от диалекта. Например, SQLite не обеспечивает ограничение длины просто из-за `String(80)`; для входных данных нужна валидация, а для строгой схемы — подходящие ограничения БД.

### Тот же принцип через Column

Альтернативный самостоятельный фрагмент для понимания существующего кода. Не добавляйте его в `models.py` рядом с уже объявленным User.

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
```

`Column` остаётся допустимым способом объявления колонок; `mapped_column` удобно сочетать с аннотациями Mapped. Это не две разные ORM.

## 5. Создание схемы

```python
Base.metadata.create_all(engine)
```

Здесь Base и engine уже определены. create_all создаёт отсутствующие таблицы из metadata и подходит для учебной БД. Он **не обновляет произвольно существующие таблицы** под изменения Python-модели. Для последовательного изменения схемы применяют Alembic.

Модуль с моделями должен быть импортирован до обращения к metadata, иначе соответствующих таблиц в ней ещё не будет.

## 6. Session и транзакция

Session — рабочая область ORM. Она связывает загруженные объекты с БД, хранит identity map, отслеживает изменения и отправляет их при flush. Транзакция обеспечивает согласованное применение группы SQL-операций.

| Метод | Что делает |
|---|---|
| `add()` / `add_all()` | Регистрирует новые объекты для сохранения |
| `flush()` | Отправляет накопленные INSERT/UPDATE/DELETE внутри текущей транзакции |
| `commit()` | Делает flush и фиксирует транзакцию |
| `rollback()` | Откатывает текущую транзакцию и приводит Session в состояние для дальнейшей работы |
| `refresh(obj)` | Перечитывает данные объекта из БД |
| `close()` | Освобождает ресурсы Session; не фиксирует незавершённые изменения |
| `get(Model, pk)` | Получает объект по первичному ключу или None |

**Flush не равен commit.** После flush INSERT уже выполнен и сгенерированный ID обычно известен, но изменения ещё можно откатить. Commit завершает транзакцию.

По умолчанию autoflush может отправить изменения перед ORM-запросом или загрузкой связи. Поэтому ошибка ограничения иногда возникает на SELECT: перед ним Session попыталась записать накопленные изменения. Отключение autoflush не отменяет flush при commit.

`with Session(engine) as session:` закрывает сессию, но **не делает автоматический commit**. Для транзакции можно добавить `with session.begin():`: при успехе commit, при исключении rollback. Session обычно начинает транзакцию автоматически при первой операции — autobegin.

Подробности: [Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html).

## 7. CRUD: создать, прочитать, изменить, удалить

Далее используются engine с созданной схемой и User из `practice/models.py`. Блоки выполняются последовательно; `user_id` сохраняется после создания.

### Create

```python
from sqlalchemy.orm import Session

with Session(engine) as session, session.begin():
    user = User(name="Anna", email="anna@example.test", age=24)
    session.add(user)
    session.flush()
    user_id = user.id
```

После выхода из begin транзакция зафиксирована. Сам `User(...)` ещё не вставляет строку; add регистрирует объект, flush отправляет SQL.

### Read

```python
from sqlalchemy import select

with Session(engine) as session:
    user = session.get(User, user_id)
    adults = session.scalars(
        select(User).where(User.age >= 18).order_by(User.id)
    ).all()
    names = [item.name for item in adults]
```

`select(User)` создаёт описание запроса. `session.scalars(...)` выполняет его и извлекает значения первой выбранной колонки — здесь ORM-объекты User. `all()` потребляет результат в список.

### Update

```python
with Session(engine) as session, session.begin():
    user = session.get(User, user_id)
    if user is None:
        raise LookupError("User not found")
    user.name = "Anna Updated"
```

Session отслеживает изменение загруженного объекта и выполняет UPDATE при flush/commit. Повторно add для такого объекта не нужен.

### Delete

```python
with Session(engine) as session, session.begin():
    user = session.get(User, user_id)
    if user is not None:
        session.delete(user)
```

`del user` удалил бы только Python-имя. Для удаления строки нужны session.delete и фиксация транзакции.

## 8. Ошибки и безопасное управление Session

```python
from sqlalchemy.exc import IntegrityError

with Session(engine) as session:
    session.add(User(name="One", email="same@example.test", age=20))
    session.add(User(name="Two", email="same@example.test", age=21))
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        # Теперь эту Session можно использовать снова.
```

При неудачном flush БД может уже откатить транзакцию, но для повторного использования той же Session всё равно нужен `rollback()`. Альтернатива — закрыть и выбросить эту Session. Нельзя просто поймать ошибку и продолжить запросы в её неактивном состоянии.

Стабильные правила:

- Одна Session на единицу работы/запрос; не одна глобальная Session на приложение.
- Не использовать одну Session одновременно в нескольких потоках; AsyncSession — одновременно в нескольких asyncio-задачах.
- Engine и фабрику sessionmaker переиспользуют; Session создают отдельно.
- Для нескольких связанных изменений выбирают одну транзакцию, а не commit в каждой вспомогательной функции.
- Данные пользователя передают SQL-выражениям как значения параметров: `User.name == value`. Не собирают SQL через f-string с пользовательским вводом.

Фабрика сессий:

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)
with SessionLocal.begin() as session:
    session.add(User(name="Boris", email="boris@example.test", age=30))
```

`SessionLocal.begin()` создаёт Session, управляет транзакцией и закрывает Session при выходе.

## 9. Identity map и состояния объектов

Для одной пары «модель + первичный ключ» Session поддерживает один объект в своей identity map. Повторный get может вернуть тот же Python-экземпляр без SELECT, если состояние уже доступно. Это **не кэш результатов любых запросов**.

Состояния: transient — новый объект вне Session; pending — добавлен, ожидает INSERT; persistent — связан с Session и сохранён/загружен; deleted — удалён при flush в текущей транзакции; detached — больше не связан с Session.

После commit атрибуты по умолчанию становятся expired: следующий доступ может перечитать данные. После close объект detached; уже загруженные и неистёкшие значения могут быть доступны, но отложенная загрузка без Session — нет. Для ответа API данные читают/преобразуют до завершения нужного времени жизни Session.

## 10. Самопроверка уровня 1

1. Что ORM делает вместо вас, а что всё равно требует знания SQL?
2. Чем Engine отличается от Session и соединения?
3. Почему Base.metadata знает о таблицах только после импорта моделей?
4. Что произойдёт после add, flush, commit и rollback?
5. Почему SELECT может неожиданно вызвать ошибку UNIQUE?
6. Почему del user не удаляет строку?
7. Чем create_all отличается от миграции?

Практический критерий: самостоятельно создать модель, подключить SQLite, выполнить четыре CRUD-операции и показать, что после нарушения UNIQUE можно откатить транзакцию и продолжить работу.
