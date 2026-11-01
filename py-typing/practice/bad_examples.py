"""Намеренные ошибки для анализа. Проверять отдельно: python -m mypy bad_examples.py.

Функции здесь не вызываются: файл нужен для диагностики, а не запуска приложения.
Не добавляйте type: ignore — исправьте несоответствия в учебной копии.
"""

from collections.abc import AsyncGenerator

from typed_examples import Address, apply_to_values, find_name, greet, squares, stream_labels


def bad_calls() -> None:
    count: int = "three"  # assignment: строка вместо int.
    greet(123)  # arg-type: ожидается str.
    values: list[int] = [1, "two"]  # list-item: неверный элемент.
    name = find_name({}, 1)
    print(name.upper())  # union-attr: None не имеет upper.
    address: Address = ("localhost", "8000")  # assignment: порт должен быть int.
    print(count, values, address)


def wrong_return() -> int:
    return "not an integer"  # return-value.


def increment(value: int) -> int:
    return value + 1


def bad_callback_and_generators() -> None:
    apply_to_values([1, 2], increment)  # arg-type: callback возвращает int вместо str.
    generated: list[int] = squares(3)  # assignment: генератор не список.
    async_values: AsyncGenerator[int, None] = stream_labels(3)  # assignment: выдаются str.
    print(generated, async_values)


def unsafe_collection_assignment() -> None:
    names: list[str] = ["Anna"]
    objects: list[object] = names  # assignment: изменяемый list инвариантен.
    objects.append(42)


def wrong_generator_annotation() -> int:  # misc: аннотация должна допускать генератор.
    yield 1
