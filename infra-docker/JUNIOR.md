# Docker — Junior

## Image, container, registry

**Image** — шаблон файловой системы и конфигурации запуска. **Container** — экземпляр image со своим процессом и изменяемым слоем. **Registry** — хранилище образов, откуда их скачивают и куда публикуют.

Linux-контейнеры разделяют ядро хоста, а не запускают отдельное гостевое ядро как обычная VM. На Windows/macOS для Linux-контейнеров обычно используется VM. Контейнер помогает воспроизводимо доставлять user-space окружение, но не гарантирует идентичное ядро/архитектуру и абсолютную изоляцию.

Контейнер живёт, пока работает его главный процесс. Image не меняется от работы экземпляра; изменения writable layer принадлежат контейнеру и удаляются при его удалении.

## Базовые команды

```bash
docker pull python:3.11-slim
docker run --rm python:3.11-slim python --version
docker ps
docker ps -a
docker stop <container>
docker rm <stopped-container>
```

Run создаёт новый контейнер; start запускает существующий. --rm удаляет контейнер после завершения. Ps показывает работающие, ps -a — также остановленные. Stop просит завершиться и по истечении ожидания может принудительно остановить; rm удаляет объект контейнера, не исходный image.

## Dockerfile

| Инструкция | Назначение |
|---|---|
| FROM | Базовый образ |
| WORKDIR | Рабочий каталог |
| COPY | Файлы из build context |
| RUN | Команда **во время сборки** |
| CMD | Команда/аргументы по умолчанию **при запуске** |
| ENTRYPOINT | Основной executable; CMD может задавать ему аргументы |
| USER | Пользователь процесса |
| EXPOSE | Описание порта, не публикация на хост |

Пример учебного сервера статических файлов. Рядом создай index.html с текстом `Hello`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN mkdir public
COPY index.html public/index.html
USER 10001:10001
EXPOSE 8000
ENTRYPOINT ["python", "-m", "http.server"]
CMD ["8000", "--bind", "0.0.0.0", "--directory", "public"]
```

Exec-форма с массивом избегает лишней shell. При ENTRYPOINT аргументы после имени image заменяют CMD и передаются основному executable. Содержимое build context задаёт каталог в конце docker build; `.dockerignore` исключает ненужное, в том числе .git, окружения и секреты. Сервер выше учебный, не production-сервер.

## Сборка, запуск, публикация

Из каталога Dockerfile и index.html:

```bash
docker build -t junior-web:local .
docker run -d --name junior-web -p 127.0.0.1:8000:8000 junior-web:local
docker ps
docker stop junior-web
docker rm junior-web
```

Во время работы открой `http://127.0.0.1:8000`. `-p` публикует порт хоста → порт контейнера; одного EXPOSE недостаточно. Сервер внутри слушает 0.0.0.0, а публикация ограничена loopback хоста.

Для публикации в **свой** registry с правами доступа заменяют placeholders:

```bash
docker tag junior-web:local <registry>/<namespace>/junior-web:1.0
docker login <registry>
docker push <registry>/<namespace>/junior-web:1.0
```

Tag — изменяемое имя версии, а не неизменяемое содержимое. Build собирает локально, tag добавляет имя, push отправляет образ в registry. Не копируй секреты в образ.

**Самопроверка:** чем image отличается от container? Когда выполняется RUN, а когда CMD? Как ENTRYPOINT связан с CMD? Почему EXPOSE не сделал сервис доступным с хоста?
