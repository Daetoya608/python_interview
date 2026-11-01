# Docker — уровень 2

## Диагностика и запуск

```bash
docker logs --tail 100 -f study-counter
docker exec -it study-counter sh
docker inspect study-counter
docker stats study-counter
docker run -d --name study-counter \
  -p 127.0.0.1:8000:8000 --memory 128m --cpus 0.5 \
  --mount source=study-counter-data,target=/data study-counter:local
```

Переносы `\` выше — синтаксис POSIX shell; в PowerShell используйте одну строку. `logs` читает stdout/stderr согласно logging driver; файлы внутри контейнера не появляются в нём автоматически. `exec` запускает дополнительный процесс в работающем контейнере; `sh` должен существовать в образе.

`-p HOST_IP:HOST_PORT:CONTAINER_PORT` публикует порт. Без явного IP публикация обычно доступна на всех интерфейсах хоста. Приложение внутри контейнера должно слушать `0.0.0.0`, а не только свой loopback. `--memory` задаёт лимит памяти, `--cpus` — квоту CPU, не выделенный процессор. При превышении памяти возможен OOM kill; отдельно учитывайте swap и возможности хоста.

## Где сохраняются данные

| Хранилище | Свойства |
|---|---|
| Writable layer | Принадлежит контейнеру; удаление контейнера удаляет эти данные |
| Named volume | Управляется Docker, живёт независимо от конкретного контейнера; удобен для данных |
| Bind mount | Конкретный путь хоста; удобен для разработки, зависит от структуры/прав хоста |
| tmpfs | Временные данные в памяти на поддерживаемых платформах |

Mount скрывает содержимое образа под целевым путём; у нового пустого volume есть отдельное поведение первоначального копирования данных. Volume — не backup: ошибочное удаление/изменение данных приложением сохраняется. Bind mount по умолчанию допускает запись на хост; при необходимости используйте read-only.

## Слои и сборка

Образ состоит из переиспользуемых read-only слоёв и метаданных; контейнер получает верхний writable layer. Copy-on-write позволяет разделять неизменяемые данные. `RUN`/`COPY` могут создавать файловые изменения, а `ENV`/`CMD` преимущественно меняют конфигурацию — правило «любая строка всегда создаёт новый слой файлов» неточно.

Кэш зависит от инструкции, входов и предыдущих шагов. Сначала копируют файл зависимостей и устанавливают их, затем часто меняющийся код. Изменение раннего шага может инвалидировать последующие. Multi-stage build оставляет компиляторы/сборочные инструменты в builder-стадии, копируя в финальную только нужный результат.

Удаление секрета следующей инструкцией не удаляет его из старого слоя. Для build credentials используют BuildKit secret mounts, а для runtime — механизм секретов среды исполнения. Маленький образ ускоряет передачу и сокращает состав зависимостей; отсутствие root снижает часть рисков, но не создаёт абсолютную изоляцию.

## Контейнер против VM

VM включает гостевое ядро и ОС поверх гипервизора: изоляция сильнее и можно запускать другое ядро, но больше накладных расходов. Контейнер обычно легче и быстрее стартует, разделяя ядро; компрометация ядра затрагивает границу изоляции. VM и контейнеры часто используют вместе. Контейнеризация не заменяет ограничения прав, обновления и сетевые политики.

## Compose: несколько настроек в одном файле

[practice/compose.yml](practice/compose.yml) описывает сборку, порт, named volume и лимиты учебного счётчика. Из корня репозитория:

```bash
docker compose -f infra-docker/practice/compose.yml up --build -d
docker compose -f infra-docker/practice/compose.yml ps
docker compose -f infra-docker/practice/compose.yml logs -f
docker compose -f infra-docker/practice/compose.yml exec counter sh
docker compose -f infra-docker/practice/compose.yml down
```

Откройте `http://127.0.0.1:8000/`: GET показывает значение. Увеличьте его командой `curl -X POST http://127.0.0.1:8000/` (в Windows используйте `curl.exe`, чтобы не вызвать PowerShell alias). POST сохраняет число в `/data/count.txt`. После `down` и повторного `up` значение сохранится в volume. `down -v` удаляет volumes проекта и данные — для этой проверки не нужен. Compose DNS позволяет сервисам обращаться друг к другу по имени сервиса; `localhost` внутри контейнера означает этот контейнер. `depends_on` без healthcheck-условия не гарантирует готовность зависимости принимать запросы.

Пример — учебный HTTP-сервер стандартной библиотеки, не production-сервер. Docker Engine здесь недоступен: сборка образа и запуск Compose требуют отдельной проверки на машине с Docker. Логику хранения счётчика можно проверить локально: `python -m unittest discover -s infra-docker/practice -p "test_*.py" -v`.

Требования: [issue #11](https://github.com/Daetoya608/python_interview/issues/11). Справка: [run](https://docs.docker.com/reference/cli/docker/container/run/), [storage](https://docs.docker.com/engine/storage/), [Compose services](https://docs.docker.com/reference/compose-file/services/), [build cache](https://docs.docker.com/build/cache/).
