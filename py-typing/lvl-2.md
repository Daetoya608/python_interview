# Типизация Python — уровень 2

Коллекции, Union, Callable, TypeAlias, Generator и AsyncGenerator. Основной код совместим с Python **3.11+**. Новое объявление `type` для Python 3.12+ показано отдельно.

## 1. Параметризованные коллекции

Параметры типа уточняют содержимое контейнера, а не создают новый экземпляр коллекции.

```python
names: list[str] = ["Anna", "Boris"]
ages: dict[str, int] = {"Anna": 24}
unique_ids: set[int] = {1, 2, 3}
fixed: tuple[str, int] = ("localhost", 8000)
numbers: tuple[int, ...] = (1, 2, 3, 4)
scores: dict[str, list[int]] = {"Anna": [4, 5]}
```

| Аннотация | Контракт |
|---|---|
| `list[str]` | Изменяемый список строк |
| `dict[str, int]` | Строковые ключи и целочисленные значения |
| `set[int]` | Множество целых чисел |
| `tuple[str, int]` | Ровно два элемента, тип зависит от позиции |
| `tuple[int, ...]` | Произвольное число элементов типа int, включая ноль |
| `list[int | str]` | Один список может содержать и int, и str |
| `list[int] | list[str]` | Либо целочисленный список, либо строковый |

`tuple[int]` — одноэлементный кортеж, не любой кортеж целых чисел. Коллекция может быть пустой, если контракт отдельно этого не запрещает; list[int] не означает «есть хотя бы один элемент».

Старые написания из typing: List[str], Dict[str, int], Tuple[str, int], Set[int]. С Python 3.9 обычно используют соответствующие встроенные типы. Изменять старый код только ради регистра букв необязательно, но в одном модуле полезен единый стиль.

## 2. Конкретная коллекция или интерфейс

Если функции достаточно перебора, не обязательно требовать именно list. Для интерфейсов в современном коде подходят типы из collections.abc:

```python
from collections.abc import Iterable, Mapping, Sequence

def total(values: Iterable[int]) -> int:
    return sum(values)

def first(values: Sequence[str]) -> str:
    if not values:
        raise ValueError("empty sequence")
    return values[0]

def find_name(users: Mapping[int, str], user_id: int) -> str | None:
    return users.get(user_id)
```

- Iterable даёт возможность пройти по значениям; не обещает индексирование или повторяемый обход. Источником может быть генератор.
- Sequence описывает последовательность с длиной и доступом по индексу.
- Mapping описывает чтение по ключам; не требует методов изменения словаря.
- Если функция действительно изменяет список через append, ей нужен соответствующий изменяемый контракт, например list[T], а не просто Iterable[T].

Read-only интерфейс **не замораживает** объект во время выполнения: переданный список может изменяться через другую ссылку.

### Почему list[str] не является list[object]

```python
names: list[str] = ["Anna"]
# objects: list[object] = names  # Ошибка анализатора.
```

Если бы такое присваивание было разрешено, через objects можно было бы добавить int и нарушить контракт names. Поэтому list инвариантен по типу элемента. Для функции, которая только читает элементы, часто достаточно Sequence[object] или Iterable[object]: такой контракт безопаснее расширяет допустимый вход.

Это пример различия между «str подходит вместо object» и «любой контейнер str подходит вместо изменяемого контейнера object». Основа параметризации — [спецификация generics](https://typing.python.org/en/latest/spec/generics.html); теория совместимости — [PEP 483](https://peps.python.org/pep-0483/).

## 3. Union и сужение типов

`int | str` означает одно значение, которое может быть int или str. Старое написание — `Union[int, str]`. `Optional[T]` — частный случай `T | None`.

```python
def normalize_id(value: int | str) -> str:
    if isinstance(value, int):
        return str(value)
    return value.strip()
```

В первой ветке доступно целое число, после неё — строка. Без сужения типизатор разрешает только операции, допустимые для всех ещё возможных вариантов.

Union не преобразует строку в число и не сохраняет автоматически связь между типами разных переменных. Например, `def transform(x: int | str) -> int | str` не обещает анализатору «для int результат всегда int». Для зависимых сигнатур позже изучают overload или параметризацию, если это нужно контракту.

Не используйте Any вместо перечисления реально допустимых альтернатив. Сужение через isinstance и проверки None сохраняет проверку операций. [Сужение типов mypy](https://mypy.readthedocs.io/en/stable/type_narrowing.html).

## 4. Callable: функция как аргумент

```python
from collections.abc import Callable, Iterable

def apply_to_values(
    values: Iterable[int],
    transform: Callable[[int], str],
) -> list[str]:
    return [transform(value) for value in values]

def label(value: int) -> str:
    return f"item-{value}"

result = apply_to_values([1, 2], label)
```

`Callable[[int], str]` — вызываемый объект, который допускает передаваемый int-аргумент и возвращает str. Это может быть обычная функция, lambda, совместимый bound method или объект с подходящим __call__.

- `Callable[[], int]` — вызов без аргументов, результат int.
- `Callable[[str, int], bool]` — два позиционных аргумента и результат bool.
- `Callable[..., str]` — результат str без точного описания параметров. Такая запись ослабляет проверку вызова, а не гарантирует, что реальная функция примет любые аргументы.

В функцию передают callback `label`, а не результат `label(1)`. Если callback вместо str возвращает int, контракт нарушен, даже если сам код построения списка может выполниться.

Функция callback должна принимать все аргументы, которые вызывающий код вправе ей передать. Простая форма Callable не описывает все варианты keyword-only и имён параметров; для более сложного API применяют callback Protocol, а для сохранения сигнатур декораторов — ParamSpec. Для данных требований достаточно базовой формы. [Спецификация Callable](https://typing.python.org/en/latest/spec/callables.html).

## 5. TypeAlias: имя сложного типа

Для Python 3.10–3.11:

```python
from typing import TypeAlias

Address: TypeAlias = tuple[str, int]
Scores: TypeAlias = dict[str, list[int]]

def format_address(address: Address) -> str:
    host, port = address
    return f"{host}:{port}"
```

Псевдоним упрощает чтение и позволяет повторять один контракт. Для анализатора Address и tuple[str, int] эквивалентны: alias **не создаёт отдельный номинальный тип**, не проверяет значения и не является моделью с полями.

`Address: TypeAlias = ...` объявляет псевдоним. `address: Address = ("localhost", 8000)` аннотирует обычную переменную. Имена типов обычно пишут с заглавной буквы.

Альтернатива с Python 3.12:

```python
type Address = tuple[str, int]
type Scores = dict[str, list[int]]
```

Этот блок **не запускается на Python 3.11**: новый синтаксис не добавляется через from __future__ import annotations. TypeAlias остаётся полезен для совместимости; новые type-псевдонимы имеют собственное runtime-представление, поэтому равнозначность для анализатора не означает одинаковое поведение всех операций над ними во время выполнения.

Если задача — различать UserId и OrderId статически, простые псевдонимы int не обеспечат этого. Для такого контракта рассматривают NewType или классы, а не ожидают различения от TypeAlias. [Спецификация псевдонимов](https://typing.python.org/en/latest/spec/aliases.html).

## 6. Generator: три параметра типа

Наличие yield делает обычную def-функцию генераторной: при вызове получается генератор, а не непосредственно выдаваемый элемент.

```python
from collections.abc import Generator

def squares(limit: int) -> Generator[int, None, None]:
    for number in range(limit):
        yield number * number
```

Сигнатура: **Generator[YieldType, SendType, ReturnType]**.

| Параметр | Значение |
|---|---|
| YieldType | Что получает потребитель от yield / next |
| SendType | Что потребитель передаёт внутрь через send |
| ReturnType | Итоговый результат return после завершения генератора |

В squares выдаются int, содержательного send и итогового результата нет. Это не `-> int` и не `-> list[int]`: `list(squares(3))` отдельно материализует все элементы в список.

### Генератор с итоговым return

```python
def numbers_with_total(limit: int) -> Generator[int, None, int]:
    total = 0
    for number in range(limit):
        total += number
        yield number
    return total
```

Для limit=3 потребитель получит 0, 1, 2, а при завершении итог 3 попадёт в StopIteration.value. Обычный for не отдаёт этот итог как очередной элемент. Получить его можно при ручном обходе с перехватом StopIteration или через yield from внутри другого генератора.

### Генератор с send

```python
def accumulator() -> Generator[int, int, None]:
    total = 0
    while True:
        increment = yield total
        total += increment

running = accumulator()
try:
    print(next(running))   # 0: запуск до первого yield.
    print(running.send(5)) # 5: отправка int и получение следующего int.
    print(running.send(2)) # 7.
finally:
    running.close()
```

В выражении `increment = yield total` total — выходящее значение, increment — входящее. Это разные направления. Новый генератор сначала запускают через next; нельзя отправить ему значение, отличное от None, до первой остановки yield.

Если интерфейсу потребителя не нужны send и итоговый return, можно указать `Iterator[int]` или `Iterable[int]`. Iterator предоставляет next и сам является iterable; Iterable обещает возможность получить итератор. Выбирают контракт, который действительно нужен вызывающему коду.

В примерах явно указаны все три параметра для Python 3.11. В новых версиях Python 3.13+ у SendType/ReturnType появились defaults None; сокращения из новой документации нельзя автоматически переносить на старый runtime. [Генераторы и корутины в typing](https://docs.python.org/3/library/typing.html#annotating-generators-and-coroutines).

## 7. AsyncGenerator: два параметра типа

```python
import asyncio
from collections.abc import AsyncGenerator

async def stream_numbers(limit: int) -> AsyncGenerator[int, None]:
    for number in range(limit):
        await asyncio.sleep(0)
        yield number

async def consume() -> list[int]:
    return [number async for number in stream_numbers(3)]
```

Сигнатура: **AsyncGenerator[YieldType, SendType]**.

- YieldType — элемент, получаемый через async for / await anext(...).
- SendType — значение, отправляемое через await generator.asend(value).
- Третьего ReturnType **нет**: в async-генераторе нельзя использовать return со значением. Для завершения допустим пустой return.

AsyncGenerator тоже не является готовым списком. Его перебирают через async for; сам объект async-генератора не ожидают как `await stream_numbers(3)`. При досрочном прекращении работы с ресурсным генератором обеспечивают закрытие через aclose или подходящий контекстный менеджер.

Если достаточно последовательного чтения, аннотация может быть `AsyncIterator[int]` или `AsyncIterable[int]`. У них нет обещания полного интерфейса asend/aclose генератора. В Python 3.11 для AsyncGenerator указывают оба параметра; default для SendType появился с 3.13.

## 8. Корутина и async-генератор — разные объекты

```python
async def fetch_label(value: int) -> str:
    await asyncio.sleep(0)
    return f"item-{value}"
```

У обычной async def без yield результат `-> str` означает значение **после await**. При непосредственном вызове fetch_label(1) создаётся объект корутины. Не нужно аннотировать такую функцию `-> Coroutine[..., str]`, если она в своём теле возвращает обычную строку: это обещало бы ещё один объект корутины после await.

Callback для асинхронного результата:

```python
from collections.abc import Awaitable, Callable

async def use_loader(
    value: int,
    loader: Callable[[int], Awaitable[str]],
) -> str:
    return await loader(value)
```

Здесь loader — функция, чей вызов возвращает awaitable; await этого объекта даёт str. В practice/demo.py такой зависимостью служит fetch_label.

| Объявление | Что делает вызов | Как получить данные |
|---|---|---|
| `def f() -> int` | Выполняет функцию и возвращает int | `f()` |
| `def f() -> Generator[int, None, None]` с yield | Создаёт генератор | for / next |
| `async def f() -> int` без yield | Создаёт корутину | `await f()` |
| `async def f() -> AsyncGenerator[int, None]` с yield | Создаёт async-генератор | async for / await anext |

## 9. Где заканчивается польза аннотаций

- `list[int]` не проверяет элементы во время обычного append без отдельного валидатора.
- `isinstance(value, list[int])` не является runtime-проверкой такого контракта: параметризованный generic нельзя использовать так. Проверяют list и при необходимости его элементы явно.
- Alias не превращает JSON-словарь в валидированную модель и не создаёт новые гарантии формата данных.
- `cast(T, value)` сообщает анализатору предположение, но не проверяет и не преобразует объект.
- Any ослабляет проверку; object требует сужения до специфических операций.
- Из корректной сигнатуры не следует правильность вычисления, освобождение ресурсов или отсутствие гонок.

Для диагностики mypy поддерживает reveal_type. В Python 3.11+ его можно импортировать из typing; реальный вызов также печатает runtime-тип, но для обычной проверки программы отладочные вызовы не нужны. Не подавляйте ошибки cast/ignore без основания.

## 10. Проверка практики

```console
python -m mypy
python demo.py
python -m mypy bad_examples.py
```

Первые две команды должны успешно завершиться. Третья должна обнаружить намеренные ошибки. В typed_examples.py есть базовые функции, коллекции, два alias, callback, оба направления обмена генератора и async-примеры. Demo показывает реальные результаты без сети.

Упражнения:

1. Изменить тип элемента коллекции и увидеть ошибку list-item.
2. Убрать проверку None из display_name и увидеть union-attr.
3. Передать callback с неправильным результатом в apply_to_values.
4. Исправить Address с портом-строкой, не заменяя аннотацию на Any.
5. Объяснить, почему squares нельзя присвоить list[int] без материализации.
6. Изменить тип yield и аннотацию генератора так, чтобы они снова совпали.
7. Сравнить вызов fetch_label и stream_labels и способы их потребления.

## 11. Самопроверка уровня 2

1. Чем tuple[int, str] отличается от tuple[int, ...]?
2. Чем list[int | str] отличается от list[int] | list[str]?
3. Почему функция может принимать Iterable, а возвращать конкретный list?
4. Что означает Callable[[int], str] и почему передают функцию без вызова?
5. Создаёт ли TypeAlias новый различимый тип?
6. Какие параметры есть у Generator и в каком направлении движутся значения?
7. Куда попадает return обычного генератора и почему его не видно в for?
8. Почему AsyncGenerator не имеет третьего параметра типа?
9. Чем тип результата async def отличается от типа объекта её вызова?
