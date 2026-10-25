# Глобальные зависимости

> Перевод страницы [Global Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/global-dependencies/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Для некоторых типов приложений может понадобиться добавить зависимости ко всему приложению.

Так же как можно [добавить `dependencies` в *декораторы операций пути*](32-dependencies-in-path-operation-decorators.md), их можно добавить в приложение `FastAPI`.

В этом случае они будут применяться ко всем *операциям пути* в приложении:

```python title="dependencies/tutorial012_an_py310.py"
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])


@app.get("/items/")
async def read_items():
    return [{"item": "Portal Gun"}, {"item": "Plumbus"}]


@app.get("/users/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]
```

И все идеи из раздела о [добавлении `dependencies` в *декораторы операций пути*](32-dependencies-in-path-operation-decorators.md) по-прежнему применимы, но в данном случае — ко всем *операциям пути* в приложении.

## Зависимости для групп *операций пути*

Позже, читая о том, как структурировать большие приложения ([Большие приложения — несколько файлов](43-bigger-applications.md)), возможно, с несколькими файлами, вы узнаете, как объявить один параметр `dependencies` для группы *операций пути*.
