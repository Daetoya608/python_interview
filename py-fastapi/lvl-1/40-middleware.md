# Middleware

> Перевод страницы [Middleware](https://fastapi.tiangolo.com/tutorial/middleware/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

В приложения **FastAPI** можно добавлять middleware (промежуточное ПО).

«Middleware» — это функция, которая работает с каждым **запросом** до того, как его обработает какая-либо конкретная *операция пути*. А также с каждым **ответом** перед его возвратом.

* Она принимает каждый **запрос**, приходящий в приложение.
* Затем она может что-то сделать с этим **запросом** или выполнить любой нужный код.
* Затем она передаёт **запрос** на обработку остальной части приложения (какой-либо *операции пути*).
* Затем она принимает **ответ**, сгенерированный приложением (какой-либо *операцией пути*).
* Она может что-то сделать с этим **ответом** или выполнить любой нужный код.
* Затем она возвращает **ответ**.

> **Примечание | Технические подробности**
>
> Если у вас есть зависимости с `yield`, их код выхода выполнится *после* middleware.
>
> Если были фоновые задачи (о них рассказывается в разделе [Фоновые задачи](46-background-tasks.md), вы увидите его позже), они выполнятся *после* всех middleware.

## Создание middleware

Чтобы создать middleware, используйте декоратор `@app.middleware("http")` над функцией.

Функция middleware получает:

* `request` (запрос).
* Функцию `call_next`, которая принимает `request` в качестве параметра.
    * Эта функция передаст `request` соответствующей *операции пути*.
    * Затем она вернёт `response` (ответ), сгенерированный соответствующей *операцией пути*.
* Затем можно дополнительно изменить `response` перед его возвратом.

```python title="middleware/tutorial001_py310.py"
import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

> **Совет**
>
> Помните, что собственные проприетарные заголовки можно добавлять [с префиксом `X-`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers).
>
> Но если у вас есть собственные заголовки, которые должен видеть клиент в браузере, их нужно добавить в настройки CORS ([CORS (Cross-Origin Resource Sharing)](41-cors.md)) с помощью параметра `expose_headers`, описанного в [документации Starlette по CORS](https://starlette.dev/middleware/#corsmiddleware).

> **Примечание | Технические подробности**
>
> Можно также использовать `from starlette.requests import Request`.
>
> **FastAPI** предоставляет его для удобства разработчика. Но он берётся напрямую из Starlette.

### До и после `response`

Можно добавить код, который будет выполняться с `request` до того, как его получит какая-либо *операция пути*.

А также после того, как `response` сгенерирован, перед его возвратом.

Например, можно добавить собственный заголовок `X-Process-Time`, содержащий время в секундах, затраченное на обработку запроса и генерацию ответа — как в примере выше.

> **Совет**
>
> Здесь мы используем [`time.perf_counter()`](https://docs.python.org/3/library/time.html#time.perf_counter) вместо `time.time()`, потому что для таких задач он может быть точнее. 🤓

## Порядок выполнения нескольких middleware

Когда вы добавляете несколько middleware с помощью декоратора `@app.middleware()` или метода `app.add_middleware()`, каждый новый middleware оборачивает приложение, образуя стек. Последний добавленный middleware — *самый внешний*, а первый — *самый внутренний*.

На пути запроса *самый внешний* middleware выполняется первым.

На пути ответа — последним.

Например:

```Python
app.add_middleware(MiddlewareA)
app.add_middleware(MiddlewareB)
```

Это приводит к следующему порядку выполнения:

* **Запрос**: MiddlewareB → MiddlewareA → маршрут

* **Ответ**: маршрут → MiddlewareA → MiddlewareB

Такое поведение стека гарантирует, что middleware выполняются в предсказуемом и контролируемом порядке.

## Другие middleware

Позже можно подробнее прочитать о других middleware в [Продвинутом руководстве пользователя: продвинутые middleware](https://fastapi.tiangolo.com/advanced/middleware/).

В следующем разделе вы прочитаете о том, как работать с <abbr title="Cross-Origin Resource Sharing">CORS</abbr> с помощью middleware.
