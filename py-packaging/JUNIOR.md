# Упаковка Python — Junior

## Module, package, distribution

- **Module** — импортируемый модуль, часто один файл `.py`.
- **Package** — импортируемый пакет с подмодулями; в обычном варианте каталог с `__init__.py`.
- **Distribution** — устанавливаемый/распространяемый проект с метаданными и файлами. Имя для pip не обязано совпадать с именем import.

Например устанавливают distribution, а импортируют содержащийся в нём package. Сборка дистрибутива не то же самое, что создание импортируемого каталога.

## pyproject.toml и инструменты

**pyproject.toml** описывает сборочную систему, метаданные проекта и настройки инструментов. **Build backend** умеет собирать wheel/sdist (например setuptools). **Frontend** вызывает backend: `build` собирает, pip устанавливает и при необходимости организует сборку.

Минимальная структура:

```text
project/
  pyproject.toml
  src/
    junior_demo/
      __init__.py
```

Содержимое pyproject.toml:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "junior-demo-study"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
```

В `src/junior_demo/__init__.py`:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

`build-system.requires` — зависимости **сборки**; `project.dependencies` — зависимости **установленного приложения/библиотеки**. requires-python задаёт совместимость с интерпретатором. src-layout помогает не принять импорт прямо из рабочей директории за проверку корректной установки.

## Wheel и sdist

| Формат | Что означает |
|---|---|
| Wheel (.whl) | Готовый установочный дистрибутив; проект не надо заново собирать из исходников |
| Sdist (обычно .tar.gz) | Исходный дистрибутив; для установки может потребоваться сборка wheel и сборочные зависимости |

Wheel может быть чистым Python, без машинного кода. Wheels с нативными расширениями могут зависеть от ОС/архитектуры/версии Python. Sdist — подготовленный комплект исходников, а не обязательно весь Git-репозиторий.

## Собрать и установить

Из project, в отдельном виртуальном окружении:

```console
python -m pip install build
python -m build
python -m pip install dist/junior_demo_study-0.1.0-py3-none-any.whl
python -c "from junior_demo import greet; print(greet('Anna'))"
```

Для указанного чистого Python-примера dist содержит wheel и sdist; имя distribution нормализуется в имени wheel. Сборка обычно создаёт изолированное окружение и устанавливает зависимости backend. Для проверки import полезно выйти из каталога проекта, оставаясь в том же виртуальном окружении.

Базовая установка прямо из проекта: `python -m pip install .`. Для разработки: `python -m pip install -e .` — editable-установка связывает окружение с исходниками; не заменяет проверку собранного wheel. Публиковать проект для локальной сборки/установки не требуется.

**Самопроверка:** чем import-пакет отличается от distribution? Кто frontend, кто backend? Почему setuptools не обязательно runtime-зависимость? Когда для установки потребуется сборка?
