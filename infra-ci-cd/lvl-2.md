# CI/CD — уровень 2

## Как читать и изменять pipeline

По конфигурации найдите: trigger и фильтры веток/путей → permissions → runner → зависимости jobs → команды установки и проверки → artifacts → условия выпуска → secrets/environments → concurrency и timeout. При падении сначала определите job/step и первую значимую ошибку, затем воспроизведите ту же команду с теми же версиями локально. Не лечите провал теста `continue-on-error`.

В текущем репозитории при подготовке материалов **активный CI-конфиг не обнаружен**. Поэтому ниже учебный pipeline, а не описание реально используемой командой инфраструктуры. Для аттестации отдельно узнайте, где находится конфиг вашего проекта, что блокирует merge и как происходит deployment.

## Разобранный пример GitHub Actions

Полный файл: [practice/workflow.yml](practice/workflow.yml). Он хранится вне `.github/workflows`, поэтому не включает автоматизацию сам по себе. Чтобы применить его в отдельном учебном репозитории, сохраните как `.github/workflows/study.yml`, сохранив структуру `infra-ci-cd/practice`.

```yaml
name: study-ci
on: [push, pull_request, workflow_dispatch]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    strategy:
      matrix:
        python: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: python -m unittest discover -s infra-ci-cd/practice -p "test_*.py" -v
```

`on` задаёт события; `permissions` ограничивает встроенный токен чтением; matrix создаёт отдельную job на каждую версию Python. Checkout получает код, setup-python выбирает интерпретатор, последняя команда запускает тесты и возвращает ненулевой код при ошибке. Зависимости здесь не устанавливаются: пример использует только стандартную библиотеку. В реальном проекте добавьте установку зафиксированных зависимостей и его проверки.

Теги actions удобны для чтения; политика проекта может требовать полный проверенный commit SHA для фиксации зависимостей автоматизации. Версии runner/actions должны быть совместимы, особенно на self-hosted runners.

## Практика изменения

1. Запустите локально ту же команду из `run`.
2. Добавьте тест граничного значения; намеренно сломайте функцию и убедитесь, что команда падает; верните исправление.
3. Чтобы добавить версию Python, измените matrix. Чтобы добавить lint, заведите отдельный шаг/job с явной установкой инструмента.
4. Для integration tests добавьте тестовую БД/сервис, readiness-проверку и изолированные данные; не подключайте production БД.
5. Для build/release используйте зависимости `needs`, версионированный artifact и отдельные права. Для production задайте environment, правила допуска, проверку здоровья и предотвращение конкурирующих выкладок.

Не выдавайте секреты недоверенному коду из forks. Особенно внимательно проверяйте сочетание `pull_request_target`, прав записи и checkout кода PR: изменение trigger может менять модель доверия, а не только момент запуска. Кэш ключуют по версии среды и файлу зависимостей; cache miss должен влиять на скорость, а не корректность.

Минимальный ответ о **своём** pipeline: «запускается на …; jobs …; зависимости ставим …; merge блокируют …; artifact …; выпускаем …; при ошибке …». Заполните фактическими данными, не примером из конспекта.

Требования: [issue #10](https://github.com/Daetoya608/python_interview/issues/10). Справка: [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [checkout](https://github.com/actions/checkout), [setup-python](https://github.com/actions/setup-python).
