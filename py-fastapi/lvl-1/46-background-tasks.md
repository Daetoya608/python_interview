# Фоновые задачи

> Перевод страницы [Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Можно определять фоновые задачи, которые будут выполняться *после* возврата ответа.

Это полезно для операций, которые должны произойти после запроса, но клиенту на самом деле не нужно ждать их завершения, прежде чем получить ответ.

Например:

* Уведомления по электронной почте, отправляемые после выполнения действия:
    * Поскольку подключение к почтовому серверу и отправка письма обычно «медленные» (несколько секунд), можно сразу вернуть ответ, а уведомление отправить в фоне.
* Обработка данных:
    * Например, допустим, вы получаете файл, который должен пройти медленную обработку; можно вернуть ответ «Accepted» (HTTP 202) и обработать файл в фоне.

## Использование `BackgroundTasks`

Сначала импортируйте `BackgroundTasks` и объявите в *функции операции пути* параметр с типом `BackgroundTasks`:

```python title="background_tasks/tutorial001_py310.py"
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
```

**FastAPI** создаст за вас объект типа `BackgroundTasks` и передаст его в этот параметр.

## Создайте функцию задачи

Создайте функцию, которая будет выполняться как фоновая задача.

Это обычная функция, которая может принимать параметры.

Это может быть функция `async def` или обычная `def` — **FastAPI** будет знать, как правильно с ней работать.

В данном случае функция задачи будет записывать в файл (имитируя отправку письма).

А поскольку операция записи не использует `async` и `await`, функцию объявляем обычным `def` — см. `write_notification` в примере выше.

## Добавьте фоновую задачу

Внутри *функции операции пути* передайте функцию задачи в объект *фоновых задач* методом `.add_task()`:

```python title="background_tasks/tutorial001_py310.py"
    background_tasks.add_task(write_notification, email, message="some notification")
```

`.add_task()` принимает в качестве аргументов:

* Функцию задачи, которую нужно выполнить в фоне (`write_notification`).
* Любую последовательность аргументов, которые нужно по порядку передать функции задачи (`email`).
* Любые именованные аргументы, которые нужно передать функции задачи (`message="some notification"`).

## Внедрение зависимостей

`BackgroundTasks` работает и с системой внедрения зависимостей: параметр типа `BackgroundTasks` можно объявлять на нескольких уровнях — в *функции операции пути*, в зависимости (dependable), в подзависимости и т. д.

**FastAPI** знает, что делать в каждом случае и как переиспользовать один и тот же объект, так что все фоновые задачи объединяются и затем выполняются в фоне:

```python title="background_tasks/tutorial002_an_py310.py"
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI

app = FastAPI()


def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)


def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(write_log, message)
    return q


@app.post("/send-notification/{email}")
async def send_notification(
    email: str, background_tasks: BackgroundTasks, q: Annotated[str, Depends(get_query)]
):
    message = f"message to {email}\n"
    background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}
```

В этом примере сообщения будут записаны в файл `log.txt` *после* отправки ответа.

Если в запросе был query-параметр, он будет записан в лог в фоновой задаче.

А затем другая фоновая задача, созданная в *функции операции пути*, запишет сообщение с использованием параметра пути `email`.

## Технические подробности

Класс `BackgroundTasks` берётся напрямую из [`starlette.background`](https://starlette.dev/background/).

Он импортируется/включается напрямую в FastAPI, чтобы его можно было импортировать из `fastapi` и случайно не импортировать альтернативный `BackgroundTask` (без `s` на конце) из `starlette.background`.

Если использовать только `BackgroundTasks` (а не `BackgroundTask`), его можно применять как параметр *функции операции пути*, а **FastAPI** сделает всё остальное за вас — так же, как при прямом использовании объекта `Request`.

В FastAPI по-прежнему можно использовать отдельный `BackgroundTask`, но тогда нужно создать объект в своём коде и вернуть `Response` из Starlette, включающий его.

Подробнее см. в [официальной документации Starlette о фоновых задачах](https://starlette.dev/background/).

## Предостережение

Если нужно выполнять тяжёлые фоновые вычисления и не обязательно, чтобы они выполнялись тем же процессом (например, не нужно разделять память, переменные и т. д.), может быть полезно использовать другие, более крупные инструменты, например [Celery](https://docs.celeryq.dev).

Обычно они требуют более сложной настройки и менеджера очередей сообщений/задач, например RabbitMQ или Redis, но позволяют выполнять фоновые задачи в нескольких процессах и, особенно, на нескольких серверах.

Но если нужен доступ к переменным и объектам того же приложения **FastAPI** или нужно выполнять небольшие фоновые задачи (например, отправлять уведомление по почте), можно просто использовать `BackgroundTasks`.

## Итоги

Импортируйте и используйте `BackgroundTasks` в параметрах *функций операций пути* и зависимостей, чтобы добавлять фоновые задачи.
