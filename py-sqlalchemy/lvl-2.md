# SQLAlchemy — уровень 2: связи, запросы, загрузка и Alembic

Продолжение `lvl-1.md`. Код ориентирован на SQLAlchemy **2.0**; требуемый `Session.query()` разобран наряду с `select()`. Схема и запускаемые примеры находятся в `practice/`.

## 1. Учебная схема и ограничения

В `practice/models.py` определены:

```text
User 1 ─── N Task
User 1 ─── 0..1 Profile
Task N ─── M Tag  (через task_tag)
```

Далее фрагменты запросов выполняются в открытой `session`; классы и импорты можно получить так:

```python
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload
from models import Base, Profile, Tag, Task, User, make_engine
```

`ForeignKey` задаёт ссылочную целостность в **БД**, а `relationship()` — объектный доступ в **ORM**. Одно не заменяет другое. В SQLite примеры включают `PRAGMA foreign_keys=ON` для каждого соединения через обработчик connect.

## 2. One-to-Many и Many-to-One

Внешний ключ находится на стороне «много»: несколько Task могут иметь один user_id. У User — коллекция tasks, у Task — скаляр user.

Основные строки из моделей:

```python
# В User:
tasks: Mapped[list["Task"]] = relationship(
    back_populates="user", cascade="all, delete-orphan"
)

# В Task:
user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
user: Mapped["User"] = relationship(back_populates="tasks")
```

Здесь Mapped, mapped_column, relationship и ForeignKey импортируются в models.py. Фрагмент показывает части двух разных классов, а не самостоятельный модуль.

`back_populates` связывает обе стороны: присваивание task.user отражается на user.tasks и наоборот. При flush ORM определяет порядок INSERT и записывает внешний ключ; ID не обязательно известен в момент создания объектов.

```python
with Session(engine) as session, session.begin():
    user = User(name="Anna", email="anna@example.test", age=24)
    user.tasks.append(Task(title="Learn joins"))
    session.add(user)
```

`cascade="all, delete-orphan"` подходит для принадлежащих пользователю задач: удаление пользователя через ORM удалит его задачи, а удаление задачи из родительской коллекции приведёт к удалению «осиротевшей» строки при flush. Это выбор модели владения, а не настройка для любой связи.

ORM cascade и `ON DELETE CASCADE` — разные механизмы. Первый выполняет ORM unit of work, второй — сама БД. Их согласуют, при необходимости используя passive_deletes. Bulk DELETE по условию не воспроизводит обход всех объектных ORM-каскадов.

## 3. One-to-One

В User используется скалярный `profile: Mapped[Profile | None]`, а не список. В Profile — user_id с `unique=True`, NOT NULL и ForeignKey.

- Скалярная аннотация задаёт ожидание ORM: один объект вместо коллекции. В нетипизированном стиле можно использовать `uselist=False`.
- **UNIQUE на profiles.user_id** обеспечивает ограничение в БД: два профиля одного пользователя не сохранятся даже при конкурентных запросах.
- Одна только relationship/uselist=False уникальность в таблице не создаёт.
- Это связь «ноль или один профиль у пользователя»: обязательное наличие профиля для каждого User такой схемой не гарантируется.

```python
user.profile = Profile(bio="Python developer")
```

При замене профиля учитывайте UNIQUE и порядок операций: простая подстановка нового объекта может потребовать явного удаления/flush старого. Ограничение БД остаётся источником истины.

## 4. Many-to-Many

Связь Task ↔ Tag хранится в отдельной таблице:

```python
task_tag = Table(
    "task_tag",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
```

Составной первичный ключ запрещает повтор одной пары task_id/tag_id. В обоих классах используется `relationship(secondary=task_tag, back_populates=...)`.

```python
task.tags.append(tag)   # Добавит связь в task_tag при flush.
task.tags.remove(tag)   # Удалит связь, но сам общий Tag останется.
```

Если у связи нужны собственные поля, например assigned_at или role, таблицу связи обычно маппят отдельным классом — **association object**. Не включайте двусторонний delete cascade между общими сущностями без понимания последствий: можно удалить намного больше графа, чем планировалось.

Основа этих трёх разделов: [Basic Relationship Patterns](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html).

## 5. Фильтрация, сортировка, пагинация

```python
statement = (
    select(User)
    .where(User.age >= 18, User.active.is_(True))
    .where(or_(User.name == "Anna", User.name == "Boris"))
    .order_by(User.age.desc(), User.id.asc())
    .offset(0)
    .limit(20)
)
users = session.scalars(statement).all()
```

- Несколько выражений в where объединяются через AND.
- OR задают `or_(...)`; для составных SQL-выражений не используют Python `and`/`or`. При `&`/`|` выражения заключают в скобки из-за приоритетов Python.
- NULL: `User.some_field.is_(None)` / `.is_not(None)`. Колонки some_field в учебной схеме нет — это общий шаблон.
- Принадлежность: `User.id.in_([1, 2, 3])`; строки: `User.name.like("Ann%")`.
- `filter_by(name="Anna")` — короткое равенство по именам полей; where/filter удобнее для сложных условий и нескольких таблиц.
- Для стабильных страниц нужен определённый order_by, желательно с уникальным дополнительным ключом. Offset на больших выборках может быть дорогим.
- Фильтруйте в БД, а не через list comprehension после загрузки всех строк.

## 6. Результаты select

| Вызов | Результат |
|---|---|
| `session.execute(select(User))` | Result со строками Row, содержащими User |
| `session.scalars(select(User))` | ScalarResult из самих User |
| `session.execute(select(User.name, User.age)).all()` | Список строк с несколькими значениями |
| `session.get(User, pk)` | User или None; учитывает identity map |
| `session.scalars(stmt).one()` | Ровно один результат; иначе исключение |
| `session.scalars(stmt).one_or_none()` | Ноль или один; при нескольких — исключение |
| `session.execute(stmt).scalar_one()` | Ровно одна строка, первое значение |

`session.scalar(stmt)` возвращает первое значение первой строки или None и не проверяет уникальность. Для намерения «ровно один» используйте соответствующий one-метод.

`Result.first()` и `ScalarResult.first()` **не добавляют SQL LIMIT**. Если нужна одна строка на стороне БД, добавьте `.limit(1)` к select. Это отличается от старого `Query.first()`.

При выборе `select(User.name, User.age)` вызов scalars оставит только первую колонку, то есть имена. Не потеряйте остальные данные случайно.

## 7. JOIN, LEFT JOIN и подзапросы

```python
# По паре значений на каждую соответствующую строку Task.
rows = session.execute(
    select(User.name, Task.title)
    .join(User.tasks)
    .where(Task.completed.is_(False))
    .order_by(User.id, Task.id)
).all()
```

`join(User.tasks)` использует описание связи. Другой вариант — явный ON: `.join(Task, Task.user_id == User.id)`. При неоднозначных путях условие нужно указывать явно.

INNER JOIN оставляет только совпавшие строки. LEFT OUTER JOIN — `.outerjoin(User.tasks)` — сохраняет и пользователей без задач. Условие на правую таблицу в WHERE может исключить строки с NULL и фактически убрать эффект LEFT JOIN; фильтр иногда нужно помещать в ON.

Соединение User с несколькими Task размножает строки пользователя. Для уникального набора ORM-объектов можно использовать `.unique()` результата; когда сама цель — проверить наличие задач, удобнее EXISTS:

```python
users = session.scalars(
    select(User).where(User.tasks.any(Task.completed.is_(False)))
).all()
```

Подзапрос с агрегатом:

```python
counts = (
    select(Task.user_id, func.count(Task.id).label("n"))
    .group_by(Task.user_id)
    .subquery()
)
users = session.scalars(
    select(User)
    .join(counts, User.id == counts.c.user_id)
    .where(counts.c.n >= 2)
).all()
```

`subquery()` превращает SELECT в источник строк для другого SELECT; `.c` открывает его колонки. Это **не subqueryload**, который управляет загрузкой relationship.

## 8. Агрегации

```python
rows = session.execute(
    select(User.id, User.name, func.count(Task.id).label("task_count"))
    .outerjoin(User.tasks)
    .group_by(User.id, User.name)
    .having(func.count(Task.id) >= 0)
    .order_by(func.count(Task.id).desc(), User.id)
).all()
```

Для пользователя без задач count(Task.id) даст 0. `count(*)` в таком LEFT JOIN посчитал бы и строку пользователя с NULL справа. В примере having >= 0 сохраняет всех; замените на >= 2 для пользователей с двумя и более задачами.

`WHERE` отбирает строки до группировки, `HAVING` — группы после неё. Другие агрегаты: `func.sum`, `avg`, `min`, `max`. Все выбранные неагрегированные колонки группируют явно, чтобы запрос не зависел от послаблений конкретной СУБД.

Материал запросов: [ORM SELECT](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html).

## 9. Требуемый Query: как читать старый код

В SQLAlchemy 2.x `Session.query()` доступен, но относится к **legacy API**. Для нового кода документация использует select + Session.execute/scalars. Требование «использует query» не означает, что Query удалён или обязателен во всех новых проектах.

```python
rows = (
    session.query(User.name, func.count(Task.id).label("task_count"))
    .outerjoin(User.tasks)
    .filter(User.age >= 18)
    .group_by(User.id, User.name)
    .having(func.count(Task.id) >= 1)
    .order_by(User.name.asc())
    .all()
)
```

| Legacy | Стиль 2.0 |
|---|---|
| `session.query(User).filter(...).all()` | `session.scalars(select(User).where(...)).all()` |
| `query.filter_by(name="Anna")` | `select(User).filter_by(name="Anna")` |
| `query.join(User.tasks)` | `select(User).join(User.tasks)` |
| `query.first()` | `session.scalars(select(User).limit(1)).first()` |
| `query.get(pk)` | `session.get(User, pk)` |

Обычный SELECT по классу ещё не исполняется, пока его не передали Session. Аналогично Query строится цепочкой методов и выполняется при all/first/итерации и других терминальных действиях.

`Query.count()` считает SQL-строки своего запроса; число ORM-объектов после дедупликации при JOIN может отличаться. Для заданного смысла подсчёта лучше явно выразить count, при необходимости distinct.

Справочник: [Legacy Query API](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html).

## 10. Lazy, eager, selectin, joined и subquery

**Lazy** — отложенная загрузка при обращении к связи. **Eager** — предварительная загрузка вместе с обработкой основной выборки. **Subquery loading — один из способов eager**, а не отдельная противоположная категория.

| Стратегия | Как получает связанные данные | Практический смысл |
|---|---|---|
| `lazy="select"` | Обычно SELECT при первом доступе к незагруженной связи | Удобно для редких обращений; риск N+1 |
| `selectinload()` | Дополнительные SELECT с `WHERE ... IN (...)` по ключам | Частый выбор для коллекций; возможна разбивка на пачки |
| `joinedload()` | JOIN в запросе загрузки | Удобно для скалярных связей; коллекции размножают строки |
| `subqueryload()` | Дополнительный SELECT с подзапросом исходной выборки | Более сложный SQL; обычно selectin проще, но бывают ограничения диалекта |
| `raiseload()` | Ошибка вместо незапланированной lazy-загрузки | Помогает обнаружить скрытые запросы в прикладном чтении |

**N+1:** один SELECT пользователей и затем до N дополнительных SELECT их задач в цикле. Уже загруженные связи и identity map могут сократить реальные обращения, поэтому число не всегда буквально N+1.

```python
# Сначала пользователи, затем коллекции задач отдельной выборкой/пачками.
users = session.scalars(
    select(User).options(selectinload(User.tasks))
).all()

# Для joined eager loading коллекции нужен явный unique().
users = session.scalars(
    select(User).options(joinedload(User.tasks))
).unique().all()

users = session.scalars(
    select(User).options(subqueryload(User.tasks)).order_by(User.id).limit(20)
).all()
```

При subqueryload с limit/offset нужен стабильный порядок, включающий уникальный ключ, чтобы повтор исходной выборки выбрал тех же родителей.

`.join(User.tasks)` меняет SQL-выборку для фильтрации/соединения, но **сам по себе не означает заполнение user.tasks**. `joinedload` задаёт загрузку связи. Когда нужно использовать свой JOIN именно для заполнения связи, существует contains_eager.

При сравнении стратегий используйте свежую Session: загруженная раньше коллекция способна скрыть эффект новой настройки. Смотрите SQL через echo=True или счётчик запросов. Детали: [Relationship Loading Techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html).

## 11. Транзакции и устойчивость

Для одной бизнес-операции выбирайте внешнюю границу транзакции:

```python
with Session(engine) as session:
    with session.begin():
        user = User(name="Anna", email="anna@example.test", age=24)
        session.add(user)
        session.flush()
        session.add(Task(title="First task", user_id=user.id))
```

Обе записи фиксируются вместе. Исключение внутри begin приводит к rollback. Ранние commit в вызываемых функциях разрушили бы эту атомарность.

Не вызывайте `with session.begin()` после произвольного чтения в той же Session, не учитывая autobegin: транзакция уже может быть открыта. Разместите begin снаружи всей операции или явно управляйте существующей транзакцией.

После ошибки flush при ручном управлении вызывайте rollback; не продолжайте работу с неактивной Session. Не передавайте одну Session в конкурентный gather. Для синхронного SQLAlchemy в FastAPI используются def-маршруты; синхронный драйвер внутри async def блокировал бы цикл событий.

## 12. Alembic: версии схемы

Alembic хранит последовательность изменений БД в Python-файлах миграций. `upgrade()` применяет изменение, `downgrade()` описывает обратное. Файл версии содержит revision и down_revision; таблица `alembic_version` в БД отслеживает применённую ревизию, но не хранит копию всей схемы.

`create_all()` создаёт отсутствующие таблицы. Alembic позволяет контролируемо изменить уже существующую схему: добавить колонку, индекс, ограничение, преобразовать данные.

### Рабочий сценарий на учебной схеме

Выполняйте из каталога `practice` с установленными зависимостями. Ниже `python` — Python его виртуального окружения; в PowerShell без активации используйте `.\.venv\Scripts\python.exe`.

1. Создайте окружение миграций:

```console
python -m alembic init migrations
```

2. В созданном `alembic.ini` задайте **отдельную учебную БД**:

```ini
sqlalchemy.url = sqlite:///migration_study.db
```

3. В `migrations/env.py` замените `target_metadata = None`:

```python
from models import Base

target_metadata = Base.metadata
```

Все модели в примере находятся в models.py, поэтому импорт Base регистрирует их все. В проекте с несколькими модулями нужно импортировать и их. Модуль models не должен при импорте выполнять create_all: иначе базовая autogenerate-миграция увидит уже созданные таблицы.

4. Сгенерируйте, **просмотрите** и примените начальную версию:

```console
python -m alembic revision --autogenerate -m "create study tables"
python -m alembic upgrade head
python -m alembic current
```

5. Для практики добавьте в класс User поле `nickname: Mapped[str | None] = mapped_column(String(80))`, затем:

```console
python -m alembic revision --autogenerate -m "add user nickname"
python -m alembic upgrade head
python -m alembic history
python -m alembic downgrade -1
python -m alembic upgrade head
python -m alembic check
```

До downgrade/повторного upgrade проверьте содержимое сгенерированного файла. Откат удаления колонки может потерять её данные; проверку отката выполняют на учебной копии.

| Команда | Действие |
|---|---|
| `revision --autogenerate` | Сравнить текущую БД с metadata и создать кандидат миграции; БД не обновляет |
| `upgrade head` | Применить изменения до последней целевой ревизии |
| `downgrade -1` | Выполнить downgrade одной ревизии |
| `current` | Показать версию данной БД |
| `history` | Показать историю файлов миграций |
| `check` | Проверить, не предлагает ли autogenerate новые операции |

### Что обязательно проверить в миграции

- Правильная ли БД выбрана и все ли модели импортированы? Пустая metadata может породить ошибочное предложение удалить таблицы.
- Соответствуют ли операции намерению? Переименование колонки/таблицы autogenerate часто видит как удаление и добавление: это может уничтожить данные.
- Как заполнить новую NOT NULL-колонку в существующих строках? Типичный путь: временно nullable/default, заполнение данных, затем ограничение.
- Нужны ли отдельные изменения данных? Alembic не выводит бизнес-преобразование из аннотаций модели.
- Действительно ли downgrade восстанавливает прежнее состояние? Формально обратная DDL не вернёт уже удалённые данные.

Для SQLite ряд изменений структуры выполняют через пересоздание и перенос данных в **batch mode**:

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("nickname", sa.String(80), nullable=True))

def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("nickname")
```

Это пример тел функций в версии; заголовок revision/down_revision оставьте сгенерированным. Для генерации batch-операций можно добавить `render_as_batch=True` в context.configure подходящих веток env.py. Точность autogenerate ограничена; ручная проверка обязательна.

Источники: [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html), [Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html), [SQLite batch migrations](https://alembic.sqlalchemy.org/en/latest/batch.html).

## 13. Практика API на FastAPI

В `practice/api.py` реализованы:

| Метод и путь | Результат |
|---|---|
| `POST /users` | Создать пользователя; 409 при занятом email |
| `GET /users?limit=20` | Список с ограничением размера |
| `GET /users/{id}` | Пользователь с задачами, загруженными через selectinload |
| `POST /users/{id}/tasks` | Создать задачу пользователя |
| `PUT /tasks/{id}` | Заменить изменяемые поля задачи |
| `DELETE /tasks/{id}` | Удалить задачу; 204 без тела |

Запуск из practice:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

Документация API — `/docs`. Создайте пользователя, задачу, перечитайте пользователя, измените задачу и удалите её.

У примера отдельная Session через yield-зависимость на запрос; commit выполняется до успешного ответа; ошибка UNIQUE обрабатывается с rollback. Модели ответа Pydantic читают ORM-атрибуты через from_attributes. Коллекция задач загружается заранее; синхронные маршруты объявлены def.

По умолчанию API создаёт `study.db` и таблицы через create_all при запуске. Это учебный режим. Чтобы использовать миграции, уберите create_all из lifespan и направьте API в подготовленную Alembic БД через `STUDY_DATABASE_URL`. Engine/Session здесь синхронные; установка FastAPI сама не превращает их в AsyncSession.

## 14. Самопроверка уровня 2

1. Почему one-to-one требует UNIQUE, а не только uselist=False?
2. Как удалить связь many-to-many, сохранив обе сущности?
3. Чем WHERE отличается от HAVING? Почему count(Task.id) и count(*) различаются в LEFT JOIN?
4. Почему JOIN может вернуть пользователя несколько раз?
5. Чем join отличается от joinedload? Когда обязателен unique()?
6. Почему subqueryload является eager loading? Чем он отличается от subquery()?
7. Как проявляется N+1 и как проверить его по числу запросов?
8. Что гарантирует begin-блок и чего не гарантирует обычный with Session?
9. Почему autogenerate нужно проверять вручную? Что произойдёт при переименовании поля?
10. Почему create_all не заменяет версионирование схемы?

Практический критерий: построить все три связи с ограничениями БД, написать JOIN и агрегат, сравнить lazy/eager на свежих Session, выполнить upgrade/downgrade миграции и показать CRUD через API.
