# Docker — уровень 1

## Контейнер и образ

Контейнер — изолированный процесс или группа процессов с ограниченным представлением файловой системы, сети и других ресурсов. Linux containers используют ядро хоста: namespaces дают изоляцию, cgroups — учёт и ограничения ресурсов. На Windows/macOS Linux-контейнеры обычно работают через Linux VM Docker Desktop.

**Image** — шаблон файловой системы и настроек запуска. **Container** — экземпляр image со своим writable layer и состоянием процесса. **Registry** — хранилище образов. Образ помогает воспроизводимо доставлять приложение с его user-space зависимостями; не гарантирует одинаковое ядро/архитектуру CPU или безопасность любого кода.

```bash
docker pull python:3.11-slim
docker images
docker run --rm python:3.11-slim python --version
docker ps                 # работающие
docker ps -a              # также остановленные
docker stop <container>
docker rm <stopped-container>
```

`run` создаёт новый контейнер; `start` запускает уже созданный. `--rm` удаляет контейнер после завершения. Контейнер живёт, пока работает главный процесс: запуск сервиса в background без foreground-процесса обычно завершит контейнер.

## Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
USER 10001:10001
EXPOSE 8000
CMD ["python", "app.py"]
```

- `FROM` — базовый образ; `WORKDIR` — рабочий каталог следующих инструкций/процесса.
- `COPY` — файлы из build context. `.dockerignore` исключает ненужное из контекста.
- `RUN` выполняется при **сборке**, например установка зависимостей.
- `ENV` задаёт переменные среды, `ARG` — параметры сборки; оба не подходят для хранения секретов.
- `CMD` — команда/аргументы запуска по умолчанию; аргументы `docker run image ...` заменяют CMD.
- `ENTRYPOINT` задаёт основной executable; CMD может дать ему аргументы. Exec form (`["python", ...]`) избегает лишней shell и помогает доставке сигналов.
- `USER` выбирает пользователя процесса. `EXPOSE` описывает порт, но не публикует его на хост.

Показанный фрагмент объясняет синтаксис; полный пример с подготовкой пользователя/каталога данных находится в [practice/Dockerfile](practice/Dockerfile).

```bash
docker build -t study-counter:local infra-docker/practice
docker run --rm -p 127.0.0.1:8000:8000 study-counter:local
docker tag study-counter:local <registry>/<namespace>/study-counter:1.0
docker login <registry>
docker push <registry>/<namespace>/study-counter:1.0
```

Последние команды — шаблон публикации в **свой** registry при наличии прав, а не обязательная часть локальной практики. Tag — изменяемое имя; digest идентифицирует конкретное содержимое образа. Для воспроизводимого релиза фиксируют проверенные версии/digests и контролируют обновления.

Требования: [issue #11](https://github.com/Daetoya608/python_interview/issues/11). Детали: [контейнеры](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/), [Dockerfile](https://docs.docker.com/reference/dockerfile/), [CLI](https://docs.docker.com/reference/cli/docker/).
