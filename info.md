# Junior — критерии по скиллам (уровень 1)

Для каждого навыка — что нужно уметь/знать на уровне 1 (junior) по матрице компетенций.

## SQL и БД

### SQL (db-sql)
- Писать SELECT, INSERT, UPDATE, DELETE; отличать DML от DDL
- Работать с NULL (трёхзначная логика, `IS NULL` / `IS NOT NULL`, COALESCE)
- Считать агрегаты: COUNT / SUM / AVG / MIN / MAX
- Использовать GROUP BY вместе с WHERE и HAVING
- Писать JOIN (INNER, LEFT, RIGHT, FULL, CROSS, self-join) и объяснять типичные ошибки: WHERE после LEFT JOIN, размножение строк, NOT IN с NULL
- Понимать базово: VIEW, процедуры, триггеры

### Транзакции (db-transactions)
- Объяснить назначение транзакции и управляющие команды: BEGIN/COMMIT/ROLLBACK, SAVEPOINT
- Знать ACID (Atomicity, Consistency, Isolation, Durability)
- Знать границы: autocommit, aborted state после ошибки, почему не держат транзакцию открытой долго

### Индексы (db-indices)
- Объяснить, зачем нужны индексы и чем обычный отличается от уникального
- Знать цену индекса: место + поддержка при записи
- Понимать, что наличие индекса не гарантирует его использование оптимизатором

### Проектирование БД (db-design)
- Описывать структуру через DDL: CREATE/ALTER/DROP/TRUNCATE
- Использовать ограничения: PRIMARY KEY, UNIQUE, NOT NULL, CHECK, FOREIGN KEY
- Понимать ссылочную целостность и правила ON DELETE: NO ACTION / CASCADE / SET NULL

## Python

### Основы Python (py-basics)
- Знать синтаксис языка: изменяемость, ссылки/копирование, коллекции, hashability
- Функции и defaults, области видимости, исключения
- Итераторы/генераторы, декораторы, контекстные менеджеры
- Основы ООП

### asyncio (py-asyncio)
- Понимать event loop, чем корутина отличается от Task
- Использовать await, create_task, gather, TaskGroup
- Знать отмену задач, timeout, почему блокирующий код останавливает event loop

### Память (py-memory)
- Знать, что такое GC и зачем он нужен
- Понимать refcounting и циклический сборщик, del/__del__
- Понимать heap/stack, __slots__ (обзорно)

### SQLAlchemy (py-sqlalchemy)
- Понимать, что делает ORM, а что требует знания SQL
- Различать Engine / Session / Connection
- Описывать Base и модели, выполнять CRUD
- Понимать flush/commit/rollback, identity map, состояния объектов
- Безопасно управлять Session: одна на единицу работы, не в нескольких потоках

### Тестирование (py-testing)
- Использовать структуру Arrange → Act → Assert
- Писать тесты на pytest и понимать unittest
- Проверять значения, запускать один тест / файл / набор
- Выбирать сценарии: успех, границы, ошибки

### Типизация (py-typing)
- Понимать разницу динамической и статической типизации
- Знать, что аннотации не дают runtime-гарантий
- Использовать Optional / `T | None`, type narrowing
- Запускать mypy и читать диагностику

### Упаковка (py-packaging)
- Понимать pyproject.toml, build backend, package/module/distribution
- Различать wheel и sdist
- Собирать и устанавливать пакет (базово)

### FastAPI
- Описывать view-функцию и указывать нужный HTTP-глагол (GET/POST/PUT/PATCH/DELETE)
- Работать с path- и query-параметрами; отличать nullable от необязательности
- Описывать и обрабатывать тело HTTP-запроса через Pydantic-модель
- Описывать HTTP-ответ: response_model, status_code, HTTPException
- Запускать локальный сервер для отладки (fastapi dev / uvicorn)

### Потоки (threading)
- Понимать, что такое потоки и многопоточность, разницу между потоками и процессами
- Создавать и запускать потоки через `threading.Thread`
- Использовать `start()`, `join()`, `is_alive()`
- Использовать `Lock` для простейшей синхронизации (гонки, `with lock:`)
- Понимать проблему GIL: почему CPU-bound на потоках не ускоряется, а I/O-bound ускоряется

### multiprocessing
- Понимать разницу между многопоточностью и многопроцессностью и роль GIL
- Создавать и запускать процессы через `multiprocessing.Process`
- Использовать `start()`, `join()`, `terminate()` (и `if __name__ == "__main__":`)
- Передавать данные между процессами через `multiprocessing.Queue`
- Понимать преимущества (параллельность, изоляция) и ограничения (накладные расходы, IPC) относительно потоков

## Инфраструктура

### Git (infra-vcs)
- Знать, что такое git; модель данных: working tree / index / commit / HEAD
- Выполнять ежедневный цикл: add, commit, push, fetch, merge, pull
- Работать с .gitignore, ветками, stash
- Разрешать конфликты, понимать PR/MR

### Docker (infra-docker)
- Понимать image / container / registry
- Выполнять базовые команды: pull, run, ps, stop, rm
- Писать Dockerfile: FROM, COPY, RUN, CMD, ENTRYPOINT, USER, EXPOSE
- Собирать: build, tag, push

### CI/CD (infra-ci-cd)
- Знать, что такое CI и CD, принципы непрерывной интеграции, тестирования и поставки
- Различать pipeline / job / step / artifact / secret
- Понимать требования к воспроизводимым и «зелёным» проверкам

## Прочее

### Веб-протоколы (web-protocols)
- Понимать структуру HTTP, статусы (2xx/3xx/4xx/5xx)
- Различать safe и идемпотентные методы
- Понимать REST / RPC / SOAP
- Желательно: OSI, SSE, WebSocket

### Принципы проектирования (design-principles)
- Понимать ООП: инкапсуляция, абстракция, наследование, полиморфизм
- Различать композицию и наследование
- Применять SOLID на примерах
- Знать KISS/DRY/YAGNI и базовые паттерны: Singleton, Proxy, Builder, Factory, Decorator

### Архитектура систем (architecture-basics)
- Понимать модель клиент-сервер, протокол и API
- Различать логические слои и отдельные процессы
- Понимать, почему сервер обязан повторно проверять вход
- Знать про идемпотентность (timeout после POST ≠ отмена)

### Брокеры сообщений (message-brokers-basics)
- Понимать producer / consumer / queue / broker
- Знать, что происходит при сбое: ack, повторная доставка
- Различать at-most-once / at-least-once
- Понимать идемпотентность обработчика, DLQ, transactional outbox (базово)
