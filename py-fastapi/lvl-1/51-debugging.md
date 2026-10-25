# Отладка

> Перевод страницы [Debugging](https://fastapi.tiangolo.com/tutorial/debugging/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

К приложению можно подключить отладчик редактора, например Visual Studio Code или PyCharm.

## Вызовите `uvicorn`

В приложении FastAPI импортируйте и запустите `uvicorn` напрямую:

```python title="debugging/tutorial001_py310.py"
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    a = "a"
    b = "b" + a
    return {"hello world": b}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Про `__name__ == "__main__"`

Основное назначение `__name__ == "__main__"` — иметь код, который выполняется, когда файл запускают так:

```console
$ uv run python myapp.py
```

но не выполняется, когда его импортирует другой файл, например:

```Python
from myapp import app
```

#### Подробнее

Допустим, файл называется `myapp.py`.

Если запустить его так:

```console
$ uv run python myapp.py
```

то внутренняя переменная `__name__` в вашем файле, автоматически создаваемая Python, будет иметь значение — строку `"__main__"`.

Поэтому фрагмент:

```Python
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

выполнится.

---

Этого не произойдёт, если импортировать этот модуль (файл).

Так что, если у вас есть другой файл `importer.py` с:

```Python
from myapp import app

# Ещё какой-то код
```

то в этом случае автоматически созданная переменная `__name__` внутри `myapp.py` не будет иметь значение `"__main__"`.

Поэтому строка:

```Python
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

не будет выполнена.

> **Примечание**
>
> Подробнее см. в [официальной документации Python](https://docs.python.org/3/library/__main__.html).

## Запуск кода с отладчиком

Поскольку сервер Uvicorn запускается прямо из вашего кода, программу Python (ваше приложение FastAPI) можно вызывать прямо из отладчика.

---

Например, в Visual Studio Code можно:

* Перейти на панель «Debug» (Отладка).
* Выбрать «Add configuration...» (Добавить конфигурацию...).
* Выбрать «Python».
* Запустить отладчик с вариантом «`Python: Current File (Integrated Terminal)`».

Тогда запустится сервер с вашим кодом **FastAPI**, он будет останавливаться на точках останова и т. д.

Вот как это может выглядеть:

<img src="https://fastapi.tiangolo.com/img/tutorial/debugging/image01.png">

---

Если вы используете PyCharm, можно:

* Открыть меню «Run» (Запуск).
* Выбрать пункт «Debug...» (Отладка...).
* Появится контекстное меню.
* Выбрать файл для отладки (в данном случае `main.py`).

Тогда запустится сервер с вашим кодом **FastAPI**, он будет останавливаться на точках останова и т. д.

Вот как это может выглядеть:

<img src="https://fastapi.tiangolo.com/img/tutorial/debugging/image02.png">
