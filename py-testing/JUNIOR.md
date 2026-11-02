# Тестирование — Junior

## Что проверяет тест

Тест проверяет наблюдаемое поведение по контракту. **Arrange → Act → Assert:** подготовить данные → вызвать реальную проверяемую логику → сравнить с ожидаемым результатом. Ожидание не следует получать копированием реализации: так можно повторить её ошибку.

Нужны три вида сценариев: обычный успех, границы и некорректные входы/ошибки. Например для деления: 10/2, 0/2, отрицательные числа и деление на ноль. Тесты должны быть независимы от порядка запуска и не оставлять общее изменённое состояние.

## Pytest

Сохрани пример в `test_calculator.py`:

```python
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError("denominator must not be zero")
    return a / b

def test_divide():
    a, b = 10, 2                    # Arrange
    actual = divide(a, b)           # Act
    assert actual == 5              # Assert

def test_zero_numerator():
    assert divide(0, 2) == 0

def test_zero_denominator():
    with pytest.raises(ValueError):
        divide(1, 0)
```

В проекте функцию обычно импортируют из рабочего модуля; здесь она рядом, чтобы пример был самостоятельным. Pytest обнаруживает `test_*.py`/`*_test.py` и функции `test_*`.

```console
python -m pip install pytest
python -m pytest
python -m pytest -q
python -m pytest test_calculator.py -v
python -m pytest test_calculator.py::test_divide
```

Первый запуск pytest без пути ищет набор тестов в текущем проекте. Путь к файлу ограничивает файл, `::имя` — отдельный тест. `-v` даёт подробности, `-q` сокращает вывод.

## Проверки и unittest

| Проверяем | pytest | unittest.TestCase |
|---|---|---|
| Значение | assert actual == expected | self.assertEqual(actual, expected) |
| Истинность/ложность | assert value / assert not value | assertTrue / assertFalse |
| Именно None | assert value is None | assertIsNone |
| Float с допуском | assert value == pytest.approx(expected) | assertAlmostEqual |
| Исключение | pytest.raises(Error) | self.assertRaises(Error) |

`==` сравнивает значения, `is` — идентичность. `assert result` слабее проверки конкретного значения. Для float выбирают осмысленный допуск. В raises оставляют только ожидаемо падающую операцию, чтобы не принять постороннюю ошибку за правильный результат.

Unittest входит в стандартную библиотеку, тесты пишутся методами test_* класса TestCase:

```python
import unittest

class ArithmeticTest(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(2 + 3, 5)
```

Запуск: `python -m unittest discover -s tests -p "test_*.py" -v`, если файлы в tests. Pytest умеет запускать TestCase; unittest не запускает обычные pytest-функции.

Зелёный набор подтверждает проверенные сценарии, а не отсутствие всех ошибок. Обязательную валидацию рабочего кода не строят на assert: он может отключаться при оптимизации интерпретатора.

**Самопроверка:** где Arrange/Act/Assert? Как запустить один тест? Какие границы есть у функции? Почему проверка «результат истинный» может пропустить ошибку?
