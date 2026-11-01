# Тестирование Python — уровень 2

Fixtures, mocking, исключения, параметризация, пирамида тестирования и async-тесты. Примеры опираются на `practice/study_app`; полный набор запускается из `practice` через `python -m pytest`.

## 1. Уровни тестирования и пирамида

| Уровень | Граница проверки | Плюсы | Ограничения |
|---|---|---|---|
| Unit | Небольшая единица поведения, контролируемые зависимости | Быстрые, хорошо локализуют ошибку | Не проверяют реальную совместимость компонентов |
| Integration | Несколько компонентов или реальная граница: драйвер, БД, HTTP-приложение | Находят ошибки соединения, конфигурации и контрактов | Дороже подготовка; сложнее диагностика |
| End-to-End | Полный пользовательский путь через развёрнутую систему и необходимые зависимости | Проверяют, что части действительно работают вместе | Медленнее, дороже и чаще нестабильны |

Пирамида предлагает много быстрых узких тестов, меньше интеграционных и небольшой набор сквозных критичных сценариев. Фиксированного обязательного процента нет: баланс зависит от архитектуры и рисков. Одна ошибка не должна без необходимости дублироваться во всех уровнях.

Инструмент не определяет уровень: pytest запускает и unit, и интеграционные тесты. E2E необязательно требует браузера — пользовательский сценарий может проходить через публичный HTTP API. Подход описан в [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html).

В практике:

- `test_calculator.py`, `test_pricing.py`, `test_async.py` — unit-проверки.
- `test_storage.py` — интеграция с настоящим SQLite-файлом во временном каталоге.
- `test_api.py` — интеграция маршрутизации, валидации и логики ASGI-приложения внутри процесса. Не проверяет реальный сервер, сетевой тракт или развёртывание.

Для настоящего E2E того же сервиса отдельно проверили бы запрос к запущенному окружению через его внешний адрес. SQLite-тест не доказывает совместимость SQL и транзакций с PostgreSQL: нужную СУБД проверяют отдельно на соответствующей границе.

## 2. Fixtures: подготовка и очистка

Fixture задаёт воспроизводимое начальное состояние и при необходимости освобождает ресурсы. Pytest передаёт её результат в тест по имени аргумента. Fixture может зависеть от другой fixture.

Из `tests/conftest.py`:

```python
import pytest
from study_app.storage import Notes

@pytest.fixture
def notes(tmp_path):
    storage = Notes(tmp_path / "notes.db")
    try:
        yield storage
    finally:
        storage.close()
```

```python
def test_add_and_read_note(notes):
    note_id = notes.add("Learn fixtures")
    assert notes.get(note_id) == "Learn fixtures"
```

Код до yield создаёт ресурс, после yield — освобождает. Очистка должна работать и при падении теста. Если подготовка упала до yield, обычный код после него может не выполниться: не оставляйте ранее созданные ресурсы без try/finally или своевременно зарегистрированного finalizer.

Общие fixtures кладут в conftest.py соответствующего каталога. Они доступны тестам в нём и ниже; не становятся автоматически доступными соседним каталогам. Импортировать conftest вручную не нужно.

### Scope и изоляция

| Scope | Время жизни |
|---|---|
| `function` | Отдельная fixture на каждый тест; default |
| `class` | Для тестов класса |
| `module` | Для модуля тестов |
| `package` | Для пакета |
| `session` | На запуск pytest |

Повторное обращение к одной fixture в одном тесте обычно использует тот же результат. Более широкий scope ускоряет дорогую подготовку, но может разделить изменяемое состояние между тестами.

Fixture широкого scope не может зависеть от более узкого: session-fixture не может напрямую использовать function-fixture tmp_path. Для общих временных каталогов есть tmp_path_factory; при этом изоляцию данных нужно продумать отдельно.

Порядок подготовки определяется зависимостями, scope и autouse, а не расположением функций в файле или порядком аргументов. `autouse=True` запускает fixture без явного запроса в её области видимости; используйте экономно, чтобы зависимости тестов оставались понятны.

Полезные встроенные fixtures:

- `tmp_path` — отдельный временный pathlib.Path для теста.
- `monkeypatch` — временная замена атрибутов, переменных окружения и другого состояния с автоматическим восстановлением.
- `capsys` — перехват stdout/stderr; `caplog` — записей logging.

Подробности: [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html).

## 3. Подготовка в unittest

В TestCase используются setUp/tearDown, а для общего ресурса класса — setUpClass/tearDownClass. Общий изменяемый ресурс класса может нарушить изоляцию так же, как широкая fixture.

Пример гарантированного закрытия файла:

```python
import tempfile
import unittest

class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = tempfile.TemporaryFile(mode="w+t", encoding="utf-8")
        self.addCleanup(self.file.close)

    def test_write_and_read(self):
        self.file.write("hello")
        self.file.seek(0)
        self.assertEqual(self.file.read(), "hello")
```

Cleanup регистрируют после успешного получения ресурса: он выполнится и если последующий setUp завершится ошибкой. Pytest способен запускать TestCase, но обычные fixture-аргументы нельзя просто добавить в его тестовый метод. Также обычная pytest-параметризация не превращает методы TestCase в параметризованные тесты. Для неё выбирайте pytest-функции; для unittest доступны subTest и его hooks. [Совместимость pytest с unittest](https://docs.pytest.org/en/stable/how-to/unittest.html).

## 4. Проверка исключений

```python
import pytest
from study_app.calculator import divide

def test_zero_denominator():
    with pytest.raises(ValueError, match="denominator must not be zero"):
        divide(10, 0)
```

Если исключения нет — тест падает; если возник другой неподходящий тип — тоже. Указанный класс допускает его подклассы. `match` — регулярное выражение, не буквальное сравнение; при необходимости полного совпадения используют якоря или сравнивают str(exc.value).

Внутри raises оставляйте именно операцию, которая должна завершиться ошибкой. Иначе исключение из подготовки может ошибочно сделать тест зелёным. Проверки самого исключения размещают **после** контекстного блока: до них внутри блока выполнение уже не дойдёт.

```python
def test_exception_details():
    with pytest.raises(ValueError) as error:
        divide(10, 0)
    assert str(error.value) == "denominator must not be zero"
```

Эквивалент unittest: `with self.assertRaises(ValueError): ...` или assertRaisesRegex. Избегайте чрезмерно общего `raises(Exception)`: нужный сценарий может пройти из-за совсем другой ошибки.

Проверяйте не только факт ошибки, но и существенные последствия: например, при ошибке валидации платёж не вызван, а неудачная транзакция откатилась. [Assertions и исключения pytest](https://docs.pytest.org/en/stable/how-to/assert.html).

## 5. Параметризация

```python
import pytest
from study_app.calculator import divide

@pytest.mark.parametrize(
    "a,b,expected",
    [(10, 2, 5), (-6, 2, -3), (0, 2, 0)],
    ids=["positive", "negative", "zero-numerator"],
)
def test_divide(a, b, expected):
    assert divide(a, b) == expected
```

Это три отдельных тестовых случая с отдельными результатами. ids делают вывод понятнее. Каждая строка должна отражать осмысленный сценарий, а не случайный набор чисел.

Несколько декораторов parametrize дают декартово произведение наборов. Для дорогих вариантов ресурсов можно параметризовать fixtures через params. Indirect-параметризация передаёт параметры в подготовку fixture, а не прямо как значение аргумента теста.

Pytest не копирует автоматически изменяемые объекты из параметров: изменение переданного списка может повлиять на другой случай, если он использует тот же объект. Создавайте независимые данные или копируйте их осмысленно.

В unittest:

```python
import unittest
from study_app.calculator import divide

class TestDivision(unittest.TestCase):
    def test_cases(self):
        for a, b, expected in [(10, 2, 5), (-6, 2, -3)]:
            with self.subTest(a=a, b=b):
                self.assertEqual(divide(a, b), expected)
```

subTest показывает, какой набор не прошёл, и позволяет продолжить цикл после assertion failure. Это не полностью эквивалентные отдельные pytest-items: setUp не запускается заново для каждой итерации subTest. [Параметризация pytest](https://docs.pytest.org/en/stable/how-to/parametrize.html).

## 6. Mocking и тестовые двойники

Mocking — замена зависимости контролируемым объектом, чтобы воспроизвести нужный ответ/ошибку и проверить взаимодействие без реального вызова этой зависимости.

Практические термины:

- **Stub** возвращает подготовленные ответы.
- **Mock** записывает обращения для проверки взаимодействий.
- **Fake** реализует упрощённое рабочее поведение, например хранилище в памяти.

Один Mock из unittest.mock может использоваться в нескольких ролях. Mocking не является синонимом unit-тестирования: чистой функции моки не нужны. Подмена БД проверит реакцию на подготовленный ответ, но не совместимость SQL с настоящей БД.

В практике price_in_rubles читает курс через getenv. Тест подменяет чтение конфигурации, а не сам расчёт:

```python
from decimal import Decimal
from unittest.mock import patch
from study_app.pricing import price_in_rubles

def test_uses_configured_rate():
    with patch("study_app.pricing.getenv", autospec=True, return_value="100") as getenv:
        result = price_in_rubles(Decimal("2.5"))
    assert result == Decimal("250")
    getenv.assert_called_once_with("USD_RATE", "90")
```

### Где делать patch

Подменяют имя **там, где его ищет проверяемый код**.

Если pricing.py сделал `from os import getenv`, вызов обращается к `study_app.pricing.getenv`; патч только `os.getenv` после такого импорта не заменит уже привязанное локальное имя. Если код вызывает `os.getenv` через импортированный модуль os, место поиска другое.

`with patch(...)` восстанавливает объект после выхода, в том числе при ошибке теста. Для изменений окружения удобно `monkeypatch.setenv(...)`, которое также откатывает изменение после теста.

### Полезные возможности unittest.mock

| Средство | Для чего |
|---|---|
| `Mock(return_value=value)` | Задать результат обычного вызова |
| `MagicMock` | Мок с поддержкой многих специальных методов |
| `side_effect=SomeError(...)` | Вызвать исключение |
| `side_effect=[a, b, c]` | Последовательность результатов вызовов |
| `side_effect=function` | Вычислять результат по аргументам |
| `spec` / `spec_set` | Ограничить доступные атрибуты; spec_set также запрещает произвольное присваивание новых |
| `autospec=True` | Строить мок по интерфейсу и сигнатуре подменяемого объекта |
| `assert_called_once_with(...)` | Проверить один вызов и аргументы |
| `assert_not_called()` | Проверить отсутствие вызова |

Spec помогает ловить опечатки в API, но не доказывает, что реальный сервис принимает и возвращает нужные данные. Autospec проверяет сигнатуру, а не все семантические правила.

Проверка ошибок зависимости:

```python
def test_configuration_failure():
    with patch("study_app.pricing.getenv", side_effect=OSError("unavailable")):
        with pytest.raises(OSError, match="unavailable"):
            price_in_rubles(Decimal("1"))
```

Здесь нужны импорты pytest, patch, Decimal и price_in_rubles из примеров выше. Мокать функцию, которую и собирались проверить, и затем проверять её настроенный return_value — бесполезно: реальная логика не выполняется. Не привязывайте тесты к каждому внутреннему вызову, если это не существенная часть контракта. [unittest.mock](https://docs.python.org/3/library/unittest.mock.html).

## 7. Асинхронные тесты через pytest-asyncio

Вызов async-функции создаёт корутину. Чтобы проверить её поведение, нужно дождаться выполнения, а не сравнивать объект корутины.

```python
from decimal import Decimal
from unittest.mock import AsyncMock
import pytest
from study_app.pricing import quote

@pytest.mark.asyncio
async def test_quote():
    provider = AsyncMock(return_value=Decimal("100"))
    result = await quote(Decimal("2"), provider)
    assert result == Decimal("200")
    provider.assert_awaited_once_with("USD")
```

AsyncMock создаёт ожидаемую зависимость. Его return_value — значение, получаемое после await, обычно не готовая корутина. `assert_called...` проверяет вызов, `assert_awaited...` — факт ожидания: одно не заменяет другое.

В практике установлен pytest-asyncio и явно выбран `asyncio_mode = strict`:

- Async-тесты помечают `@pytest.mark.asyncio` или соответствующим pytestmark модуля.
- Async-fixtures объявляют через `@pytest_asyncio.fixture`.
- В auto-режиме плагин может автоматически обрабатывать async-тесты и обычные pytest.fixture; режим должен быть осознанно настроен, особенно если есть другие async-плагины.

Async-клиент, подключение или Lock могут быть привязаны к event loop. Согласуйте их время жизни и loop scope; не переиспользуйте закрытый клиент или ресурс, созданный в другом цикле. В практике fixtures и тесты имеют function scope.

Async-тесты по умолчанию выполняются последовательно. Маркер asyncio сам по себе не включает параллельный прогон всего набора. Обычный pytest без async-плагина не является достаточным способом запуска корутин. [Концепции pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html).

## 8. Асинхронные тесты через unittest

```python
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock
from study_app.pricing import quote

class TestQuote(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.provider = AsyncMock(return_value=Decimal("100"))

    async def test_quote(self):
        result = await quote(Decimal("2"), self.provider)
        self.assertEqual(result, Decimal("200"))
        self.provider.assert_awaited_once_with("USD")
```

IsolatedAsyncioTestCase запускает async-тест в изолированном цикле, поддерживает asyncSetUp/asyncTearDown и addAsyncCleanup. Не нужно добавлять pytest.mark.asyncio или вручную создавать цикл в обычном TestCase. [IsolatedAsyncioTestCase](https://docs.python.org/3.11/library/unittest.html#unittest.IsolatedAsyncioTestCase).

Правила для обоих способов:

- Внутри работающего async-теста используют await, а не asyncio.run(): второй цикл в том же потоке создавать нельзя.
- Созданные задачи ожидают; при досрочном выходе отменяют и тоже ожидают завершения.
- Не проверяют «успело выполниться за 0,01 секунды» без необходимости. Для согласования используют Event/очередь, а таймаут — как ограничитель зависания.
- Timeout и отмена — отдельные сценарии. В практике test_cancellation_reaches_provider_cleanup дожидается старта через Event, отменяет задачу и проверяет её finally.

## 9. API-тесты

Проверяют статус, тело и значимые побочные эффекты, а не только `status_code < 500`. Обычный набор: успех, ошибка валидации, отсутствующий ресурс/маршрут, ожидаемая бизнес-ошибка. Для авторизованного API дополнительно нужны проверки доступа.

В практике ASGI-приложение вызывается без реального сетевого сервера:

```python
import httpx
import pytest
import pytest_asyncio
from study_app.api import create_app

@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_divide_endpoint(client):
    response = await client.post("/divide", json={"a": 10, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 5}
```

У `ASGITransport` нет автоматического запуска startup/shutdown lifespan. В учебном приложении таких ресурсов нет. Если приложение готовит подключения в lifespan, тест должен отдельно обеспечить его выполнение. Синхронный TestClient в контекстном менеджере — другой подход, удобный для обычных def-тестов. [HTTPX ASGI transport](https://www.python-httpx.org/advanced/transports/#asgi-transport).

Тесты должны получать отдельные данные и окружение. Не направляйте интеграционный тест на рабочую БД; контролируемые fixtures и временные файлы позволяют повторять сценарии.

## 10. Маркеры, покрытие и нестабильные тесты

В `pytest.ini` практики зарегистрированы unit и integration; строгие markers помогают обнаружить опечатку вместо тихого неправильного отбора.

```console
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -k "zero"
python -m pytest --cov=study_app --cov-branch --cov-report=term-missing
```

Unittest-примеры в практике не имеют этих пользовательских маркеров и запускаются полным pytest-прогоном либо отдельной unittest-командой.

Coverage показывает исполненные строки/ветви; это не доказательство корректности. Можно выполнить все строки, но ничего полезного не проверить. Используйте отчёт для поиска пропущенных сценариев, а не как замену требованиям.

`skip` пропускает неподходящий сценарий с объяснением; `xfail` отмечает ожидаемый сбой. `xfail(strict=True)` позволит обнаружить неожиданное исправление как неуспешный прогон, чтобы убрать устаревшую отметку. Не скрывайте так неизвестные регрессии.

Flaky-тест проходит или падает без изменения проверяемого кода. Частые причины: порядок тестов, общие изменяемые fixtures, внешняя сеть, реальное время, случайность без контроля и гонки. Повторный запуск иногда помогает диагностике, но не устраняет причину. Долгий sleep обычно маскирует проблему согласования.

## 11. Что выполнить самостоятельно

1. Запустить pytest и отдельно unittest-примеры; посмотреть collect-only.
2. Добавить параметр к делению и увидеть отдельный случай в отчёте.
3. Проверить, что два теста notes не наследуют данные друг друга.
4. Подменить getenv в месте использования и проверить результат и аргументы вызова.
5. Проверить исключение провайдера, затем отсутствие его вызова при неверном вводе.
6. Запустить API-тесты успеха, 400, 422 и 404; объяснить их интеграционную границу.
7. Запустить AsyncMock-тест и IsolatedAsyncioTestCase; объяснить разницу между called и awaited.
8. Посмотреть coverage и найти сценарий, который нужен по смыслу, даже если строки уже покрыты.

Критерий уровня 2: выбирать границу теста, изолировать состояние, корректно заменять зависимости и освобождать sync/async-ресурсы, сохраняя осмысленные проверки поведения.
