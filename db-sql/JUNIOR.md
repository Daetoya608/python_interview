# SQL — Junior

## Чтение и изменение данных

Примеры используют customers(id, name) и orders(id, customer_id, amount_cents, status). customer_id может быть NULL для гостевого заказа. Денежная сумма — целые копейки.

```sql
SELECT id, amount_cents FROM orders
WHERE status = 'paid' AND amount_cents >= 10000
ORDER BY amount_cents DESC, id
LIMIT 10;

INSERT INTO customers(id, name) VALUES (4, 'Anna');
UPDATE customers SET name = 'Anna Updated' WHERE id = 4;
DELETE FROM customers WHERE id = 4;
```

SELECT читает; INSERT добавляет; UPDATE изменяет; DELETE удаляет строки. Без WHERE UPDATE/DELETE затронет все строки. Без ORDER BY порядок результата не гарантирован. LIMIT ограничивает результат; конкретный синтаксис зависит от СУБД.

**DML** — операции над данными. SELECT иногда отдельно относят к DQL; для работы нужны все четыре команды. **DDL** меняет структуру: CREATE/ALTER/DROP. DELETE не удаляет сам объект таблицы. Пользовательские значения передают параметрами драйвера, а не склеивают с SQL-строкой.

## NULL и трёхзначная логика

NULL — неизвестное/отсутствующее значение, не ноль и не пустая строка. Сравнение `x = NULL` даёт UNKNOWN. WHERE сохраняет только TRUE, поэтому используют `IS NULL`/`IS NOT NULL`.

```sql
SELECT id FROM orders WHERE customer_id IS NULL;
SELECT COALESCE(SUM(amount_cents), 0) FROM orders WHERE status = 'paid';
```

COALESCE выбирает первое не-NULL значение. Подставлять ноль нужно только при таком бизнес-смысле.

В логике SQL: TRUE AND UNKNOWN → UNKNOWN; FALSE AND UNKNOWN → FALSE; TRUE OR UNKNOWN → TRUE; FALSE OR UNKNOWN → UNKNOWN; NOT UNKNOWN → UNKNOWN. Это объясняет неожиданные фильтры с NULL.

## Агрегаты, GROUP BY и HAVING

| Выражение | Что считает |
|---|---|
| COUNT(*) | Число строк |
| COUNT(x) | Число не-NULL значений |
| COUNT(DISTINCT x) | Число разных не-NULL значений |
| SUM / AVG / MIN / MAX | Сумму / среднее / минимум / максимум не-NULL значений |

Без GROUP BY на пустом входе COUNT даёт 0, остальные перечисленные — NULL. AVG не считает пропущенные значения нулями. MIN/MAX возвращают значение, не всю строку с ним.

```sql
SELECT customer_id, COUNT(*) AS order_count, SUM(amount_cents) AS total_cents
FROM orders
WHERE status = 'paid' AND customer_id IS NOT NULL
GROUP BY customer_id
HAVING SUM(amount_cents) >= 20000
ORDER BY total_cents DESC, customer_id;
```

WHERE отбирает строки до группировки, GROUP BY создаёт группы, HAVING отбирает группы после вычисления агрегатов. Для переносимого запроса выбранные неагрегированные колонки включают в GROUP BY.

## JOIN

| Вид | Результат |
|---|---|
| INNER | Совпавшие пары |
| LEFT | Все строки слева; при отсутствии совпадения справа — NULL |
| RIGHT | Все строки справа; при отсутствии совпадения слева — NULL |
| FULL | Совпадения и несовпавшие строки обеих сторон |
| CROSS | Все сочетания: M × N строк |

**Self-join** — таблица в двух ролях с разными alias, например сотрудник и его руководитель. Это не отдельный алгоритм соединения.

```sql
SELECT c.id, c.name, COUNT(o.id) AS paid_count
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id AND o.status = 'paid'
GROUP BY c.id, c.name;
```

Так сохраняются и клиенты без оплаченных заказов; COUNT(o.id) у них даст 0.

Типичные ошибки:

- `WHERE o.status = 'paid'` после LEFT JOIN удалит NULL-дополненные строки. Если нужно сохранить всех клиентов, отбор совпадений помещают в ON.
- COUNT(*) после LEFT JOIN посчитает строку клиента без заказа; для числа заказов нужен COUNT(o.id).
- Один родитель с несколькими детьми повторяется закономерно. Две независимые дочерние коллекции могут перемножиться и завысить SUM. Сначала агрегируют нужную сторону или проверяют наличие через EXISTS.
- SUM(DISTINCT amount_cents) не универсальное исправление: разные заказы могут иметь одну сумму.
- `NOT IN (подзапрос)` с NULL может исключить ожидаемые строки из-за UNKNOWN. Для отсутствия связанных строк часто используют NOT EXISTS:

```sql
SELECT c.id FROM customers AS c
WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id);
```

## VIEW, процедура, триггер

**VIEW** хранит именованный запрос, а не автоматически кэш результата. Позволяет переиспользовать выборку; возможность изменения данных через view зависит от СУБД/запроса.

```sql
CREATE VIEW paid_orders AS
SELECT id, customer_id, amount_cents FROM orders WHERE status = 'paid';
```

**Процедура** — сохранённая серверная операция с параметрами, вызывается явно (например CALL). **Триггер** запускается автоматически на событие, например INSERT/UPDATE/DELETE; может вести аудит или обслуживать данные. AFTER не означает «после commit»: обычная запись аудита откатится с транзакцией.

Объекты и синтаксис зависят от СУБД: SQLite, например, не имеет обычных хранимых процедур, а RIGHT/FULL JOIN поддерживает с версии 3.39.

**Самопроверка:** COUNT(*) или COUNT(column)? WHERE или HAVING? Почему LEFT JOIN потерял клиента? Откуда дубли после JOIN? Почему NOT IN с NULL опасен? Чем view отличается от процедуры и триггера?
