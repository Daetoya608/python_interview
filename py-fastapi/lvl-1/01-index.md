# Учебник — Руководство пользователя

> Перевод страницы [Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/) документации FastAPI.
> Оригинал: © Sebastián Ramírez, лицензия MIT.

Этот учебник шаг за шагом показывает, как использовать **FastAPI** и большинство его возможностей.

Каждый раздел постепенно опирается на предыдущие, но учебник разбит на отдельные темы, так что вы можете сразу перейти к нужной, чтобы решить конкретную задачу своего API.

Он также задуман как справочник на будущее: вы сможете вернуться и найти именно то, что вам нужно.

## Запуск кода

Все блоки кода можно скопировать и использовать как есть (на самом деле это протестированные файлы Python).

Чтобы запустить любой из примеров, скопируйте код в файл `main.py` и запустите `fastapi dev` через `uv run`:

```console
$ uv run fastapi dev

   FastAPI   Starting development server 🚀

             Searching for package file structure from directories
             with __init__.py files
             Importing from /home/user/code/awesomeapp

    module   🐍 main.py

      code   Importing the FastAPI app object from the module with
             the following code:

             from main import app

       app   Using import string: main:app

    server   Server started at http://127.0.0.1:8000
    server   Documentation at http://127.0.0.1:8000/docs

       tip   Running in development mode, for production use:
             fastapi run

             Logs:

      INFO   Will watch for changes in these directories:
             ['/home/user/code/awesomeapp']
      INFO   Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C
             to quit)
      INFO   Started reloader process [383138] using WatchFiles
      INFO   Started server process [383153]
      INFO   Waiting for application startup.
      INFO   Application startup complete.
```

**НАСТОЯТЕЛЬНО рекомендуется** самостоятельно писать или копировать код, изменять его и запускать локально.

Именно работа с кодом в редакторе по-настоящему показывает преимущества FastAPI: вы видите, как мало кода нужно писать, видите все проверки типов, автодополнение и т. д.

---

## Установка FastAPI

Первый шаг — настроить проект и добавить в него FastAPI.

Установите [`uv`](https://docs.astral.sh/uv/getting-started/installation/), затем создайте проект и добавьте FastAPI:

```console
$ uv init awesome-project --bare
$ cd awesome-project
$ uv add "fastapi[standard]"

---> 100%
```

`uv add` создаёт виртуальное окружение проекта в `.venv`, добавляет FastAPI в `pyproject.toml` и создаёт `uv.lock`, чтобы позже можно было установить те же самые версии пакетов.

<details>
<summary>Что делают эти команды</summary>

* `uv init`: создать новый проект Python.
* `awesome-project`: создать проект в новой директории с этим именем.
* `--bare`: создать только минимальный файл `pyproject.toml`, без генерации примеров `main.py`, `README.md` и других файлов. Файлы приложения вы создадите сами на следующих шагах этого учебника.

Затем `cd awesome-project` переходит в директорию нового проекта, прежде чем добавлять FastAPI.

`uv` использует совместимую версию Python, уже установленную в вашей системе, или при необходимости скачает её.

Когда вы запускаете `uv add`, он подбирает совместимые версии FastAPI и всех пакетов, от которых зависит FastAPI. Точные версии записываются в `uv.lock`, что позволяет позже установить те же версии пакетов на другом компьютере или при развёртывании приложения.

Создание или обновление этого файла называется [**фиксацией (locking)** зависимостей проекта](https://docs.astral.sh/uv/concepts/projects/sync/). `uv` делает это автоматически при добавлении пакета.

</details>

<details>
<summary>Варианты установки FastAPI</summary>

При установке через `uv add "fastapi[standard]"` вместе с FastAPI ставятся стандартные необязательные зависимости, в том числе `fastapi-cloud-cli`, который позволяет развёртывать приложение в [FastAPI Cloud](https://fastapicloud.com).

Если эти необязательные зависимости вам не нужны, можно установить просто `uv add fastapi`.

Если вы хотите установить стандартные зависимости, но без `fastapi-cloud-cli`, используйте `uv add "fastapi[standard-no-fastapi-cloud-cli]"`.

</details>

<details>
<summary>Использование <code>pip</code> вместо uv</summary>

Если вы предпочитаете управлять виртуальным окружением и пакетами вручную, создайте и активируйте виртуальное окружение, а затем установите FastAPI командой `pip install "fastapi[standard]"`.

Подробные шаги описаны в [руководстве по виртуальным окружениям](https://tiangolo.com/guides/virtual-environments/).

</details>

## Навыки для ИИ-агентов

FastAPI включает официальный навык (skill) для ИИ-агентов, пишущих код. Он поставляется вместе с пакетом, поэтому его рекомендации всегда соответствуют версии FastAPI, установленной в вашем проекте, и обновляются вместе с FastAPI.

После установки FastAPI в проект навык можно установить с помощью [Library Skills](https://library-skills.io):

```bash
uvx library-skills
```

> **Примечание**
>
> `uvx` — это псевдоним для `uv tool run`. Он запускает Library Skills во временном изолированном окружении, при этом Library Skills сканирует пакеты, установленные в вашем проекте.

Навык совместим с Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, Pi, OpenCode и большинством других агентов для написания кода. Для Claude Code, когда спросят, куда установить навык, выберите `.claude/skills`.

## Продвинутое руководство пользователя

Есть также **Продвинутое руководство пользователя** (Advanced User Guide), которое можно прочитать позже, после этого **Учебника — Руководства пользователя**.

**Продвинутое руководство** опирается на это, использует те же концепции и учит некоторым дополнительным возможностям.

Но сначала стоит прочитать **Учебник — Руководство пользователя** (то, что вы читаете сейчас).

Он построен так, чтобы вы могли создать полноценное приложение, используя только **Учебник — Руководство пользователя**, а затем расширять его разными способами в зависимости от своих потребностей, пользуясь дополнительными идеями из **Продвинутого руководства**.
