# Подготовка к аттестации: issues №5–14

Все десять тем из [списка issues](https://github.com/Daetoya608/python_interview/issues) от №5 до последнего на момент подготовки (№14). В каждой папке есть **один краткий `КОНСПЕКТ.md` по всей теме**, а `lvl-N.md` раскрывают требования соответствующего уровня с примерами и вопросами для самопроверки. Обязательные и желательные пункты включены; у №5–7 есть третий уровень. Исходные материалы других тем сохранены.

Приоритеты всех 21 тем и маршрут на три дня: [порядок подготовки](ПОРЯДОК-ПОДГОТОВКИ.md).

## Навигатор

| Issue | Тема и краткое повторение | Разбор по уровням |
|---|---|---|
| [5](https://github.com/Daetoya608/python_interview/issues/5) | [Индексы](db-indices/КОНСПЕКТ.md) | [1](db-indices/lvl-1.md), [2](db-indices/lvl-2.md), [3](db-indices/lvl-3.md) |
| [6](https://github.com/Daetoya608/python_interview/issues/6) | [Транзакции](db-transactions/КОНСПЕКТ.md) | [1](db-transactions/lvl-1.md), [2](db-transactions/lvl-2.md), [3](db-transactions/lvl-3.md) |
| [7](https://github.com/Daetoya608/python_interview/issues/7) | [Проектирование БД](db-design/КОНСПЕКТ.md) | [1](db-design/lvl-1.md), [2](db-design/lvl-2.md), [3](db-design/lvl-3.md) |
| [8](https://github.com/Daetoya608/python_interview/issues/8) | [Брокеры сообщений](message-brokers-basics/КОНСПЕКТ.md) | [1](message-brokers-basics/lvl-1.md) |
| [9](https://github.com/Daetoya608/python_interview/issues/9) | [Git](infra-vcs/КОНСПЕКТ.md) | [1](infra-vcs/lvl-1.md), [2](infra-vcs/lvl-2.md) |
| [10](https://github.com/Daetoya608/python_interview/issues/10) | [CI/CD](infra-ci-cd/КОНСПЕКТ.md) | [1](infra-ci-cd/lvl-1.md), [2](infra-ci-cd/lvl-2.md) |
| [11](https://github.com/Daetoya608/python_interview/issues/11) | [Docker](infra-docker/КОНСПЕКТ.md) | [1](infra-docker/lvl-1.md), [2](infra-docker/lvl-2.md) |
| [12](https://github.com/Daetoya608/python_interview/issues/12) | [Принципы проектирования](design-principles/КОНСПЕКТ.md) | [1](design-principles/lvl-1.md), [2](design-principles/lvl-2.md) |
| [13](https://github.com/Daetoya608/python_interview/issues/13) | [Архитектура систем](architecture-basics/КОНСПЕКТ.md) | [1](architecture-basics/lvl-1.md), [2](architecture-basics/lvl-2.md) |
| [14](https://github.com/Daetoya608/python_interview/issues/14) | [Веб-протоколы](web-protocols/КОНСПЕКТ.md) | [1](web-protocols/lvl-1.md), [2](web-protocols/lvl-2.md) |

## Как повторять

Сначала прочитайте конспект темы и попробуйте объяснить каждый пункт без подсказки. Непонятные места разберите в соответствующем уровне, затем запустите пример и ответьте на вопросы своими словами. Перед аттестацией возвращайтесь к конспектам, а не к длинному списку внешних материалов. Ссылки в конце уровней нужны для проверки деталей, не обязательны для первого прохода.

Для БД примеры возможностей PostgreSQL явно отделены от автономной SQLite-практики. Особенности движка/версии важны: нельзя проверкой SQLite подтвердить PostgreSQL Serializable, CREATE INDEX CONCURRENTLY или prepared transactions.

## Практика из корня репозитория

Python 3.11+, стандартная библиотека; Git нужен только Git-примеру:

```bash
python db-indices/practice/demo.py
python db-transactions/practice/demo.py
python db-design/practice/demo.py
python message-brokers-basics/practice/demo.py
python infra-vcs/practice/demo.py
python -m unittest discover -s infra-ci-cd/practice -p "test_*.py" -v
python -m unittest discover -s infra-docker/practice -p "test_*.py" -v
python design-principles/practice/demo.py
python web-protocols/practice/demo.py
```

Git-пример создаёт и удаляет собственный временный репозиторий. БД-примеры работают в памяти. Примеры брокера и HTTP — модели механики внутри процесса, не реальные сетевые сервисы с устойчивым хранением. У архитектуры вместо искусственного приложения — разобранный кейс выбора решения.

Для Docker дополнительно нужны Docker Engine и Compose: инструкции в [уровне 2](infra-docker/lvl-2.md). Учебный [workflow CI](infra-ci-cd/practice/workflow.yml) хранится вне `.github/workflows` и не активирует Actions.

## Что проверено и что требует своей среды

- Семь Python-демонстраций и три unit-теста проходят локально; SQL-схема SQLite выполняется и отклоняет нарушения ограничений.
- Локальные Markdown-ссылки проверены. Python-примеры проверены на синтаксис.
- Docker build/Compose и PostgreSQL-специфичные команды не выполнялись: соответствующие серверы/инструменты здесь отсутствуют. Workflow не запускался на GitHub Actions.
- Реальный Git flow и pipeline вашей команды не определяются этими учебными файлами: их нужно сверить с рабочим проектом.

Материалы добавлены локально. Issues описывают требования; их состояние и содержимое на GitHub не изменялись.
