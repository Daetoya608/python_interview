# Проектирование БД — уровень 1

По [issue №7](https://github.com/Daetoya608/python_interview/issues/7): DDL и внешние ключи.

## DDL: описание структуры

| Команда | Назначение |
|---|---|
| CREATE TABLE/INDEX/VIEW | Создать объект |
| ALTER TABLE | Изменить структуру таблицы |
| DROP TABLE/INDEX/VIEW | Удалить объект |
| TRUNCATE TABLE | Удалить все строки, сохранив таблицу; поддержка и ограничения зависят от СУБД |

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    email VARCHAR(200) NOT NULL UNIQUE
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
);
ALTER TABLE customers ADD COLUMN name VARCHAR(80);
CREATE INDEX idx_orders_customer ON orders(customer_id);
```

DDL меняет схему; INSERT/UPDATE/DELETE меняют строки. TRUNCATE обычно относят к DDL, хотя он очищает данные: у него особые правила блокировок, FK, триггеров и сброса счётчиков. В SQLite этой команды нет. Поддержка конкретных ALTER и транзакционность DDL зависят от СУБД: миграцию нужно проверять на целевой версии. DROP удаляет объект и его данные, а не просто очищает результаты SELECT.

## Ограничения

- PRIMARY KEY — уникальный идентификатор строки без NULL; может быть составным.
- UNIQUE — уникальность набора значений; особенности NULL зависят от СУБД.
- NOT NULL — обязательное значение.
- CHECK — условие допустимости, например quantity > 0. Не всегда исключает NULL без NOT NULL.
- FOREIGN KEY — значения ссылки должны соответствовать допустимому ключу родителя; nullable FK может означать отсутствие связи.

Внешний ключ обеспечивает **ссылочную целостность**, а не автоматически ускоряет JOIN. Например, PostgreSQL не создаёт индекс на ссылающейся стороне только из-за FK. Такой индекс часто нужен отдельно для JOIN и проверки/обслуживания изменений родителя.

## Поведение при удалении

| Правило | Результат |
|---|---|
| NO ACTION / RESTRICT | Запретить удаление, нарушающее ссылку; точный момент проверки может различаться |
| CASCADE | Удалить/изменить зависимые строки согласно действию FK |
| SET NULL | Сбросить ссылку; колонка должна допускать NULL |

Не выбирайте CASCADE механически: заказ может требоваться сохранить после отключения клиента. Политика удаления следует доменной модели и требованиям хранения.

В SQLite foreign keys включают `PRAGMA foreign_keys=ON` для каждого соединения до транзакции. Возможности типов/ограничений SQLite не идентичны PostgreSQL.

Практика: `python db-design/practice/demo.py` создаёт нормализованную схему и проверяет FK, UNIQUE и составной PK.

Самопроверка: чем PK отличается от FK? Почему индекс не заменяет FK? Что произойдёт при удалении родителя? Какие ALTER поддерживает целевая СУБД?

Источник: [PostgreSQL Data Definition](https://www.postgresql.org/docs/18/ddl.html).
