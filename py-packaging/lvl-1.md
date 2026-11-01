# Упаковка Python-проектов

> Перевод страницы [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/) из Python Packaging User Guide.
> Оригинал: © 2013–2020, PyPA и участники проекта. Руководство распространяется под [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); перевод — под той же лицензией.
> Перевод выполнен 1 ноября 2026 года. Содержание статьи, примеры и примечания сохранены; веб-навигация и оформление вкладок заменены Markdown. Текст примера лицензии MIT оставлен на английском.

Это руководство показывает, как упаковать простой Python-проект: добавить необходимые файлы, организовать структуру, собрать пакет и загрузить его в Python Package Index — PyPI.

> **Совет.** Если при выполнении команд возникнут проблемы, скопируйте команду вместе с её выводом и [создайте issue](https://github.com/pypa/packaging-problems/issues/new?template=packaging_tutorial.yml&title=Trouble+with+the+packaging+tutorial&guide=https://packaging.python.org/tutorials/packaging-projects) в репозитории [packaging-problems](https://github.com/pypa/packaging-problems). Мы постараемся помочь.

Некоторым командам требуется новая версия pip, поэтому сначала обновите его.

Unix/macOS:

```bash
python3 -m pip install --upgrade pip
```

Windows:

```powershell
py -m pip install --upgrade pip
```

## Простой проект

В руководстве используется проект `example_package_YOUR_USERNAME_HERE`. Если ваше имя пользователя — `me`, пакет будет называться `example_package_me`. Так вы получите уникальное имя, не совпадающее с именами пакетов других читателей. Прежде чем упаковывать собственный проект, рекомендуем пройти руководство на этом примере.

Создайте локально следующую структуру:

```text
packaging_tutorial/
└── src/
    └── example_package_YOUR_USERNAME_HERE/
        ├── __init__.py
        └── example.py
```

Каталог с Python-файлами должен совпадать по имени с проектом. Это упрощает настройку и делает структуру понятнее пользователям, устанавливающим пакет.

Рекомендуется создать `__init__.py`: его наличие позволяет импортировать каталог как обычный пакет, даже если файл пуст, как в этом примере. Подробнее об исключении из этого правила — в примечании в конце.

`example.py` — пример модуля, который может содержать логику пакета: функции, классы, константы и так далее. Откройте файл и добавьте:

```python
def add_one(number):
    return number + 1
```

Если вы ещё не знакомы с модулями и импортируемыми пакетами Python, ознакомьтесь с [документацией Python о модулях и пакетах](https://docs.python.org/3/tutorial/modules.html#packages).

После создания структуры выполняйте все команды этого руководства из каталога `packaging_tutorial`.

## Создание файлов пакета

Теперь добавим файлы для подготовки проекта к распространению. В результате структура будет такой:

```text
packaging_tutorial/
├── LICENSE
├── pyproject.toml
├── README.md
├── src/
│   └── example_package_YOUR_USERNAME_HERE/
│       ├── __init__.py
│       └── example.py
└── tests/
```

## Создание каталога для тестов

`tests/` предназначен для файлов тестов. Пока оставьте его пустым.

## Выбор backend сборки

Такие инструменты, как pip и build, сами не преобразуют исходный код в дистрибутив, например wheel. Эту работу выполняет **backend сборки** — build backend. Он определяет, как задаются настройки проекта, включая метаданные — например, имя и категории, показываемые на PyPI, — и входные файлы.

Возможности backend различаются: например, не все поддерживают сборку модулей расширения. Выбирайте подходящий вашим требованиям и предпочтениям.

В этом руководстве по умолчанию используется [Hatchling](https://hatch.pypa.io/), но те же шаги работают с [Setuptools](https://setuptools.pypa.io/), [Flit](https://flit.pypa.io/), [PDM](https://pdm-project.org/) и другими backend, поддерживающими таблицу `[project]` для метаданных.

> **Примечание.** Некоторые backend входят в более крупные инструменты с интерфейсом командной строки: они умеют создавать проекты, управлять версиями, собирать, загружать и устанавливать пакеты. Здесь используются отдельные инструменты, каждый для своей задачи.

Файл `pyproject.toml` сообщает **frontend сборки** — таким инструментам, как pip и build, — какой backend нужно использовать. Ниже приведены варианты для распространённых backend; дополнительные сведения смотрите в документации выбранного инструмента. Выберите один вариант.

### Hatchling

```toml
[build-system]
requires = ["hatchling >= 1.26"]
build-backend = "hatchling.build"
```

### Setuptools

```toml
[build-system]
requires = ["setuptools >= 77.0.3"]
build-backend = "setuptools.build_meta"
```

### Flit

```toml
[build-system]
requires = ["flit_core >= 3.12.0, <5"]
build-backend = "flit_core.buildapi"
```

### PDM

```toml
[build-system]
requires = ["pdm-backend >= 2.4.0"]
build-backend = "pdm.backend"
```

### uv-build

```toml
[build-system]
requires = ["uv_build >= 0.13.5, <0.14.0"]
build-backend = "uv_build"
```

`requires` — список пакетов, необходимых для сборки. Frontend должен установить их автоматически. Обычно сборка происходит в изолированном окружении, поэтому отсутствие зависимости в этом списке может привести к ошибке сборки. Список должен включать пакет самого backend, а при необходимости — и другие сборочные зависимости. Минимальные версии в приведённых примерах — версии, в которых появилась поддержка новых метаданных лицензии.

`build-backend` — имя Python-объекта, который frontend использует для выполнения сборки.

Оба значения берут из документации backend или получают от его интерфейса командной строки. Обычно изменять их самостоятельно не требуется.

Дополнительные настройки инструмента сборки размещаются в секции `tool` файла `pyproject.toml` либо в отдельном файле, который определяет инструмент. Например, Setuptools может читать настройки из `setup.py` или `setup.cfg`; указание `setuptools.build_meta` позволяет инструментам автоматически найти и использовать эти файлы.

### Настройка метаданных

Откройте `pyproject.toml` и добавьте следующее содержимое. Измените `name`, включив своё имя пользователя, чтобы не совпасть с пакетами других читателей.

```toml
[project]
name = "example_package_YOUR_USERNAME_HERE"
version = "0.0.1"
authors = [
  { name="Example Author", email="author@example.com" },
]
description = "A small example package"
readme = "README.md"
requires-python = ">=3.9"
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]
license = "MIT"
license-files = ["LICEN[CS]E*"]

[project.urls]
Homepage = "https://github.com/pypa/sampleproject"
Issues = "https://github.com/pypa/sampleproject/issues"
```

- `name` — имя дистрибутива. Оно может содержать буквы, цифры, `.`, `_` и `-` и не должно быть занято на PyPI. Для этого руководства обязательно добавьте своё имя пользователя.
- `version` — версия пакета. Некоторые backend позволяют получать её другим способом, например из файла или Git-тега.
- `authors` — сведения об авторах: имя и электронная почта каждого. В том же формате можно указать `maintainers` — сопровождающих.
- `description` — краткое описание пакета одним предложением.
- `readme` — путь к файлу с подробным описанием. Его содержимое показывается на странице пакета в PyPI. Здесь используется распространённый вариант `README.md`; существует и более сложная табличная форма, описанная в руководстве по pyproject.toml.
- `requires-python` — поддерживаемые версии Python. Установщик, например pip, может просматривать более старые версии пакета, пока не найдёт подходящую для используемой версии Python.
- `classifiers` — дополнительные метаданные для индекса и pip. В данном примере пакет предназначен для Python 3 и не зависит от ОС. Указывайте поддерживаемые версии Python и операционные системы. Полный список — на странице [классификаторов PyPI](https://pypi.org/classifiers/).
- `license` — SPDX-выражение лицензии архивов дистрибутива.
- `license-files` — список glob-шаблонов путей к файлам лицензий относительно каталога с `pyproject.toml`.
- `urls` — дополнительные ссылки на странице PyPI: исходники, документация, трекер ошибок и другие ресурсы.

Подробности об этих и других полях `[project]` приведены в [руководстве по pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/). Часто также используют `keywords` для облегчения поиска и `dependencies` для зависимостей, необходимых при установке пакета.

## Создание README.md

Откройте `README.md` и добавьте следующий текст. При желании измените его:

```markdown
# Пример пакета

Это простой пример пакета. Для оформления содержимого можно использовать
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/).
```

## Создание LICENSE

В каждый архив дистрибутива, загружаемый в Python Package Index, важно включать лицензию. Она сообщает пользователям условия использования. С выбором поможет [choosealicense.com](https://choosealicense.com/).

Выбрав лицензию, откройте `LICENSE` и добавьте её текст. Например, для MIT:

```text
Copyright (c) 2018 The Python Packaging Authority

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Большинство backend автоматически включает файлы лицензии в пакет; подробности зависят от backend. Если указать путь в `license-files` и backend поддерживает [PEP 639](https://peps.python.org/pep-0639/), файл будет включён автоматически.

## Включение других файлов

Перечисленные выше файлы автоматически попадут в исходный дистрибутив — sdist. Чтобы добавить другие файлы, обратитесь к документации backend.

## Создание архивов дистрибутива

Следующий шаг — собрать дистрибутивы: архивы, которые загружаются в Python Package Index и устанавливаются через pip.

Убедитесь, что установлена новая версия инструмента build от PyPA.

Unix/macOS:

```bash
python3 -m pip install --upgrade build
```

Windows:

```powershell
py -m pip install --upgrade build
```

> **Совет.** Если установка вызывает затруднения, обратитесь к руководству [Installing Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/).

Теперь из каталога с `pyproject.toml` выполните:

Unix/macOS:

```bash
python3 -m build
```

Windows:

```powershell
py -m build
```

Команда выведет сообщения сборки и создаст в `dist` два файла:

```text
dist/
├── example_package_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
└── example_package_YOUR_USERNAME_HERE-0.0.1.tar.gz
```

`tar.gz` — исходный дистрибутив, **source distribution**, а `.whl` — собранный дистрибутив, **built distribution**. Новые версии pip предпочитают готовые дистрибутивы, но при необходимости используют исходные.

Следует загружать исходный дистрибутив и предоставлять собранные дистрибутивы для поддерживаемых платформ. В этом примере пакет работает на любой платформе с Python, поэтому достаточно одного wheel.

## Загрузка архивов дистрибутива

Теперь можно загрузить пакет в Python Package Index.

Сначала зарегистрируйтесь в **TestPyPI** — отдельном экземпляре индекса для тестирования и экспериментов. Он подходит для учебных задач, когда не хочется загружать пакет в основной индекс. Откройте [страницу регистрации](https://test.pypi.org/account/register/) и выполните указанные действия. Перед загрузкой потребуется подтвердить электронную почту.

Подробнее — в руководстве [Using TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/).

Для безопасной загрузки нужен [API-токен](https://docs.pypi.org/api/api-tokens/). Создайте его в [настройках TestPyPI](https://test.pypi.org/manage/account/#api-tokens), выбрав Scope — Entire account. **Не закрывайте страницу, пока не скопируете и не сохраните токен: повторно увидеть его не получится.**

Для загрузки дистрибутивов используется Twine. Установите его:

Unix/macOS:

```bash
python3 -m pip install --upgrade twine
```

Windows:

```powershell
py -m pip install --upgrade twine
```

Загрузите все архивы из `dist`:

Unix/macOS:

```bash
python3 -m twine upload --repository testpypi dist/*
```

Windows:

```powershell
py -m twine upload --repository testpypi dist/*
```

Twine запросит API-токен. Введите полное значение, включая префикс `pypi-`. Ввод скрыт, поэтому вставляйте токен внимательно.

После выполнения вывод будет примерно таким:

```text
Uploading distributions to https://test.pypi.org/legacy/
Enter your API token:
Uploading example_package_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.2/8.2 kB • 00:01 • ?
Uploading example_package_YOUR_USERNAME_HERE-0.0.1.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.8/6.8 kB • 00:00 • ?
```

После загрузки пакет будет доступен в TestPyPI, например по адресу `https://test.pypi.org/project/example_package_YOUR_USERNAME_HERE`.

## Установка только что загруженного пакета

Установите пакет через pip и проверьте его работу. Создайте [виртуальное окружение](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) и установите пакет из TestPyPI.

Unix/macOS:

```bash
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-YOUR-USERNAME-HERE
```

Windows:

```powershell
py -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-YOUR-USERNAME-HERE
```

Не забудьте подставить своё имя пользователя в имя пакета.

Пример вывода pip:

```text
Collecting example-package-YOUR-USERNAME-HERE
  Downloading https://test-files.pythonhosted.org/packages/.../example_package_YOUR_USERNAME_HERE_0.0.1-py3-none-any.whl
Installing collected packages: example_package_YOUR_USERNAME_HERE
Successfully installed example_package_YOUR_USERNAME_HERE-0.0.1
```

> **Примечание.** Флаг `--index-url` выбирает TestPyPI вместо основного PyPI. Также указан `--no-deps`: набор пакетов в TestPyPI отличается, поэтому установка зависимостей может завершиться ошибкой или установить неожиданный пакет. У нашего примера зависимостей нет, но при работе с TestPyPI разумно не устанавливать их автоматически.

Чтобы проверить установку, оставаясь в виртуальном окружении, запустите Python:

Unix/macOS:

```bash
python3
```

Windows:

```powershell
py
```

Импортируйте пакет:

```pycon
>>> from example_package_YOUR_USERNAME_HERE import example
>>> example.add_one(2)
3
```

## Дальнейшие шаги

Вы упаковали и распространили Python-проект.

В этом руководстве пакет загружался в TestPyPI, который не предназначен для постоянного хранения: тестовая система периодически удаляет пакеты и учётные записи. Используйте её для проверки и экспериментов.

> **Совет.** Для проектов, публикуемых через поддерживаемую CI/CD-платформу, рекомендуется [Trusted Publishing](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) вместо хранения долгоживущего API-токена. По ссылке показана настройка с GitHub Actions.

Когда будете готовы опубликовать реальный пакет в основном PyPI, выполните похожие действия со следующими отличиями:

- Выберите запоминающееся уникальное имя. Добавлять имя пользователя необязательно, но занятое имя использовать нельзя.
- Зарегистрируйтесь на [pypi.org](https://pypi.org/). Это отдельный сервер: учётные данные TestPyPI не переносятся в основной индекс.
- Для ручной публикации выполните `twine upload dist/*` и используйте учётные данные основного PyPI. Параметр `--repository` не нужен: по умолчанию Twine загружает пакет в основной PyPI.
- Установите пакет из основного индекса: `python3 -m pip install [your-package]`, подставив его имя.

Чтобы подробнее разобраться в упаковке библиотек:

- Изучите расширенные настройки выбранного backend: [Hatchling](https://hatch.pypa.io/latest/config/metadata/), [Setuptools](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html), [Flit](https://flit.pypa.io/en/stable/pyproject_toml.html), [PDM](https://pdm-project.org/latest/reference/pep621/).
- Посмотрите [практические руководства](https://packaging.python.org/en/latest/guides/) и [обсуждения концепций](https://packaging.python.org/en/latest/discussions/).
- Рассмотрите инструменты с единым CLI для управления проектом и упаковкой: Hatch, Flit, PDM и Poetry.

## Примечание: пакеты без __init__.py

Технически Python-пакет можно создать без `__init__.py`. Такие пакеты называют [namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/). Это продвинутая тема, не рассматриваемая здесь. При знакомстве с упаковкой рекомендуется использовать обычные пакеты с `__init__.py`, пусть даже пустым.
