# SQLAlchemy — Junior

Примеры — SQLAlchemy 2.x, Python 3.11+. ORM связывает Python-классы с таблицами, строит SQL и отслеживает изменения объектов. Она не заменяет знание JOIN, ограничений и транзакций БД.

## Engine, Connection, Session

| Объект | Роль |
|---|---|
| Engine | Диалект/драйвер и пул соединений; обычно переиспользуется для конфигурации БД |
| Connection | Низкоуровневый объект работы с SQL и транзакцией через соединение |
| Session | ORM-объекты, identity map, накопление изменений и управление транзакциями; использует соединения Engine по необходимости |
| Base.metadata | Описание таблиц моделей, не сами данные |

Session не равна одному вечному соединению и не является глобальным кэшем результатов запросов.

## Модель и CRUD

```python
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))

engine = create_engine("sqlite+pysqlite:///:memory:")
Base.metadata.create_all(engine)

with Session(engine) as session, session.begin():
    user = User(name="Anna")
    session.add(user)
    session.flush()
    user_id = user.id

with Session(engine) as session, session.begin():
    user = session.get(User, user_id)
    assert user is not None
    user.name = "Anna Updated"

with Session(engine) as session:
    users = session.scalars(select(User).where(User.name == "Anna Updated")).all()
    assert len(users) == 1

with Session(engine) as session, session.begin():
    user = session.get(User, user_id)
    assert user is not None
    session.delete(user)

engine.dispose()
```

`mapped_column` — типизированное объявление колонки; встречается также Column. Mapped[str] обычно означает NOT NULL, Mapped[str | None] — nullable. `create_all` создаёт отсутствующие таблицы, но не обновляет существующую схему под изменённую модель.

## Flush, commit, rollback

- **add:** зарегистрировать новый объект для сохранения; INSERT ещё может не выполняться.
- **flush:** отправить накопленные изменения SQL в текущую транзакцию, часто получить ID. Это ещё не фиксация.
- **commit:** выполнить flush и зафиксировать транзакцию.
- **rollback:** откатить транзакцию; после ошибки flush требуется для повторного использования Session.
- **close:** освободить ресурсы/отсоединить объекты; не commit.

`with Session(...)` закрывает сессию. `with session.begin()` фиксирует при успехе и откатывает при исключении. Autoflush может отправить изменения перед ORM-запросом; commit делает flush даже при отключённом autoflush.

## Identity map и состояния объектов

В одной Session одна строка с данным ORM-ключом обычно представлена одним экземпляром. Повторный get того же PK может вернуть его без нового SELECT. Это не кэш всех произвольных запросов и не обещание постоянной свежести данных.

| Состояние | Смысл |
|---|---|
| Transient | Создан Python-объект, ещё не добавлен в Session |
| Pending | Добавлен, но ещё не вставлен flush-ем |
| Persistent | Связан с Session и строкой БД |
| Deleted | Удаление отправлено flush-ем, транзакция ещё не завершена |
| Detached | Имеет идентичность, но больше не связан с Session |

Сам вызов delete ещё не означает завершённое состояние deleted; SQL выполняется при flush. После commit удалённый объект становится detached. **Expired** — состояние атрибутов: их данные требуют перечитывания; по умолчанию commit делает объекты expired. После закрытия Session догрузить незагруженные/expired-данные через detached-объект нельзя.

## Безопасное время жизни

Одна Session — на единицу работы/запрос, не общая для конкурентных потоков. Создавать Session из общей фабрики можно, совместно использовать одну — нельзя. Не делать commit в каждой внутренней функции, если вся операция должна быть атомарной. `del user` не удаляет строку БД.

**Самопроверка:** чем Engine отличается от Session/Connection? Почему flush не commit? Зачем rollback после ошибки? Что такое pending/detached? Почему Session не глобальный кэш?
