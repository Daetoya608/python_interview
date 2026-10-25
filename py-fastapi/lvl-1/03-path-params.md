# Параметры пути

> Перевод страницы [Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

«Параметры» или «переменные» пути можно объявлять тем же синтаксисом, что используется в форматных строках Python:

```python title="path_params/tutorial001_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}
```

Значение параметра пути `item_id` будет передано в вашу функцию как аргумент `item_id`.

Поэтому, если запустить этот пример и перейти на [http://127.0.0.1:8000/items/foo](http://127.0.0.1:8000/items/foo), вы увидите ответ:

```JSON
{"item_id":"foo"}
```

## Параметры пути с типами

Тип параметра пути можно объявить в функции с помощью стандартных аннотаций типов Python:

```python title="path_params/tutorial002_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

В этом случае `item_id` объявлен как `int`.

> **Совет**
>
> Благодаря этому редактор будет помогать вам внутри функции: проверять ошибки, дополнять код и т. д.

## <dfn title="также известно как: сериализация, парсинг, маршалинг">Преобразование</dfn> данных

Если запустить этот пример и открыть в браузере [http://127.0.0.1:8000/items/3](http://127.0.0.1:8000/items/3), вы увидите ответ:

```JSON
{"item_id":3}
```

> **Совет**
>
> Обратите внимание: значение, которое функция получила (и вернула), — это `3`, Python-тип `int`, а не строка `"3"`.
>
> Так что с таким объявлением типа **FastAPI** автоматически выполняет <dfn title="преобразование строки, пришедшей в HTTP-запросе, в данные Python">«парсинг»</dfn> запроса.

## Валидация данных

Но если перейти в браузере на [http://127.0.0.1:8000/items/foo](http://127.0.0.1:8000/items/foo), вы увидите аккуратную HTTP-ошибку:

```JSON
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": [
        "path",
        "item_id"
      ],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "foo"
    }
  ]
}
```

потому что параметр пути `item_id` имел значение `"foo"`, а это не `int`.

Такая же ошибка появилась бы, если бы вы передали `float` вместо `int`, например: [http://127.0.0.1:8000/items/4.2](http://127.0.0.1:8000/items/4.2)

> **Совет**
>
> Итак, с тем же объявлением типа Python **FastAPI** выполняет валидацию данных.
>
> Обратите внимание, что ошибка также чётко указывает, в каком именно месте валидация не прошла.
>
> Это невероятно полезно при разработке и отладке кода, который взаимодействует с вашим API.

## Документация

А если открыть в браузере [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), вы увидите автоматическую интерактивную документацию API вроде такой:

<img src="https://fastapi.tiangolo.com/img/tutorial/path-params/image01.png">

> **Совет**
>
> Опять же, просто благодаря тому же объявлению типа Python **FastAPI** даёт вам автоматическую интерактивную документацию (со встроенным Swagger UI).
>
> Обратите внимание, что параметр пути объявлен как целое число.

## Преимущества стандартов, альтернативная документация

А поскольку сгенерированная схема соответствует стандарту [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md), существует множество совместимых инструментов.

Поэтому сам **FastAPI** предоставляет альтернативную документацию API (на основе ReDoc), доступную по адресу [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc):

<img src="https://fastapi.tiangolo.com/img/tutorial/path-params/image02.png">

Точно так же существует множество совместимых инструментов, в том числе инструменты генерации кода для многих языков.

## Pydantic

Вся валидация данных выполняется «под капотом» библиотекой [Pydantic](https://pydantic.dev/docs/), так что вы получаете все её преимущества. И вы знаете, что находитесь в надёжных руках.

Те же объявления типов можно использовать с `str`, `float`, `bool` и многими другими сложными типами данных.

Некоторые из них рассматриваются в следующих главах учебника.

## Порядок имеет значение

При создании *операций пути* бывают ситуации, когда у вас есть фиксированный путь.

Например, `/users/me` — допустим, для получения данных о текущем пользователе.

И при этом у вас может быть путь `/users/{user_id}` для получения данных о конкретном пользователе по его ID.

Поскольку *операции пути* проверяются по порядку, нужно убедиться, что путь `/users/me` объявлен раньше, чем `/users/{user_id}`:

```python title="path_params/tutorial003_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
```

Иначе путь `/users/{user_id}` совпадал бы и с `/users/me`, «думая», что получает параметр `user_id` со значением `"me"`.

Аналогично, нельзя переопределить операцию пути:

```python title="path_params/tutorial003b_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]


@app.get("/users")
async def read_users2():
    return ["Bean", "Elfo"]
```

Всегда будет использоваться первая, поскольку путь совпадает с ней раньше.

## Предопределённые значения

Если у вас есть *операция пути*, которая принимает *параметр пути*, и вы хотите, чтобы допустимые значения этого *параметра пути* были заранее определены, можно использовать стандартный для Python <abbr title="Перечисление">`Enum`</abbr>.

### Создайте класс `Enum`

Импортируйте `Enum` и создайте подкласс, который наследуется от `str` и от `Enum`.

Благодаря наследованию от `str` документация API сможет узнать, что значения должны быть типа `string`, и правильно их отобразит.

Затем создайте атрибуты класса с фиксированными значениями — это и будут допустимые значения:

```python title="path_params/tutorial005_py310.py"
from enum import Enum

from fastapi import FastAPI


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}
```

> **Совет**
>
> Если вам интересно: «AlexNet», «ResNet» и «LeNet» — это просто названия <dfn title="Технически — архитектур моделей глубокого обучения">моделей</dfn> машинного обучения.

### Объявите *параметр пути*

Затем создайте *параметр пути* с аннотацией типа, используя созданный класс перечисления (`ModelName`):

```python title="path_params/tutorial005_py310.py"
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    ...
```

### Посмотрите документацию

Поскольку допустимые значения *параметра пути* определены заранее, интерактивная документация может их красиво показать:

<img src="https://fastapi.tiangolo.com/img/tutorial/path-params/image03.png">

### Работа с *перечислениями* Python

Значением *параметра пути* будет *член перечисления*.

#### Сравнение *членов перечисления*

Его можно сравнивать с *членом перечисления* в созданном вами enum `ModelName`:

```python title="path_params/tutorial005_py310.py"
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
```

#### Получение *значения перечисления*

Само значение (в данном случае `str`) можно получить через `model_name.value` или, в общем случае, `your_enum_member.value`:

```python title="path_params/tutorial005_py310.py"
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
```

> **Совет**
>
> К значению `"lenet"` можно также обратиться через `ModelName.lenet.value`.

#### Возврат *членов перечисления*

Из *операции пути* можно возвращать *члены enum*, даже вложенные в тело JSON (например, в `dict`).

Перед отправкой клиенту они будут преобразованы в соответствующие значения (в данном случае строки):

```python title="path_params/tutorial005_py310.py"
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}
```

Клиент получит JSON-ответ вроде:

```JSON
{
  "model_name": "alexnet",
  "message": "Deep Learning FTW!"
}
```

## Параметры пути, содержащие пути

Допустим, у вас есть *операция пути* с путём `/files/{file_path}`.

Но нужно, чтобы сам `file_path` содержал *путь*, например `home/johndoe/myfile.txt`.

Тогда URL для этого файла был бы примерно таким: `/files/home/johndoe/myfile.txt`.

### Поддержка в OpenAPI

OpenAPI не поддерживает способа объявить *параметр пути*, содержащий внутри *путь*, поскольку это может привести к сценариям, которые сложно тестировать и описывать.

Тем не менее в **FastAPI** это всё же можно сделать с помощью одного из внутренних инструментов Starlette.

И документация по-прежнему будет работать, хотя и не будет указывать, что параметр должен содержать путь.

### Конвертер пути

Используя опцию, взятую прямо из Starlette, можно объявить *параметр пути*, содержащий *путь*, с помощью такого URL:

```
/files/{file_path:path}
```

Здесь имя параметра — `file_path`, а последняя часть, `:path`, говорит, что параметр должен соответствовать любому *пути*.

Так что можно использовать его так:

```python title="path_params/tutorial004_py310.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
```

> **Совет**
>
> Может понадобиться, чтобы параметр содержал `/home/johndoe/myfile.txt` с ведущим слешем (`/`).
>
> В этом случае URL будет таким: `/files//home/johndoe/myfile.txt`, с двойным слешем (`//`) между `files` и `home`.

## Итоги

С **FastAPI**, используя короткие, интуитивные и стандартные объявления типов Python, вы получаете:

* Поддержку редактора: проверку ошибок, автодополнение и т. д.
* «<dfn title="преобразование строки, пришедшей в HTTP-запросе, в данные Python">Парсинг</dfn>» данных
* Валидацию данных
* Аннотирование API и автоматическую документацию

И объявить всё это нужно лишь один раз.

Это, вероятно, главное видимое преимущество **FastAPI** по сравнению с альтернативными фреймворками (не считая чистой производительности).
