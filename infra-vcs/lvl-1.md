# Git — уровень 1

## Модель данных и области работы

Git — распределённая система контроля версий: локальный репозиторий содержит историю, с которой можно работать без сервера. GitHub/GitLab — сервисы размещения репозиториев и совместной работы.

- **Working tree** — файлы, которые редактируете.
- **Index / staging area** — снимок изменений, подготовленный для следующего коммита.
- **Repository (`.git`)** — объекты, коммиты, ссылки, настройки.
- **Commit** — снимок отслеживаемого дерева + родители + автор/коммитер + сообщение. Ветка — перемещаемая ссылка на коммит; `HEAD` обычно указывает на текущую ветку.
- **Remote** — именованный адрес другого репозитория. `origin/main` — локальная remote-tracking ссылка, обновляемая при fetch; это не постоянно синхронный вид сервера.

## Повседневный цикл

```bash
git clone <url>
git status
git switch -c feature/order-validation
# изменить файлы
git diff
git add path/to/file.py
git diff --cached
git commit -m "fix: reject empty orders"
git fetch origin
git merge origin/main
git push -u origin feature/order-validation
```

`add` сохраняет в index текущее содержимое: последующие правки нужно добавить снова. `commit` локален; `push` передаёт объекты и предлагает обновить ссылки remote. `fetch` получает объекты/remote-tracking ссылки, не сливая их в текущую ветку. `merge` объединяет истории: fast-forward, если возможно, иначе merge commit. `pull` = fetch + интеграция согласно параметрам/настройкам (`--rebase`, `--no-rebase`, `--ff-only`). Не считайте pull синонимом fetch.

```bash
git branch                 # локальные ветки
git branch -a              # также remote-tracking
git switch main            # переключить существующую
git branch -m new-name      # переименовать текущую
git branch -d old-name      # удалить локальную, с проверкой слитости
git push origin --delete old-name   # удалить ветку на сервере
git stash push -u -m "unfinished validation"
git stash list
git stash apply            # применить, сохранить запись
git stash pop              # применить и удалить при успехе
```

`stash` по умолчанию сохраняет изменения tracked-файлов; `-u` добавляет untracked, `-a` — также ignored. Это временное локальное хранилище, не резервная копия.

## Настройки и игнорирование

`.gitignore` исключает подходящие **неотслеживаемые** файлы из обычного добавления: `.venv/`, `__pycache__/`, `.env`. Уже tracked-файл не перестанет отслеживаться. `git rm --cached file` удаляет его из index, сохраняя рабочую копию; сначала проверьте, что изменение нужно команде. Секрет в истории одним ignore не удалить.

```bash
git config --local user.name "Your Name"
git config --local user.email "you@example.test"
git config --show-origin --list
```

Локальная конфигурация — `.git/config`, пользовательская обычно `~/.gitconfig`; есть также системная и настройки командной строки. `--local` относится к одному репозиторию, `--global` — к пользователю.

## История, review и конфликты

```bash
git log --oneline --graph --decorate --all
git show <commit>
git log -- path/to/file.py
git blame path/to/file.py
```

PR/MR — предложение объединить ветку на платформе с review и CI; это не отдельный объект Git. Перед merge проверяют небольшой понятный diff, тесты, обратную совместимость и замечания ревьюеров.

Конфликт означает, что Git не может автоматически объединить изменения. `git status` показывает файлы. Разберите блоки `<<<<<<<`, `=======`, `>>>>>>>`, запишите нужный итог, проверьте его и выполните `git add`. Для merge завершите `git commit`, для rebase — `git rebase --continue`; отмена — `git merge --abort` или `git rebase --abort`. Выбор «всегда наша версия» может молча потерять чужие изменения.

Пример рабочего процесса: короткая feature-ветка → PR → review/CI → merge → удаление ветки. **Фактический процесс вашей команды по файлам этого репозитория не установлен.** К аттестации выясните: куда ветвиться, кто одобряет PR, способ merge, правила релизов/hotfix и обязательные проверки.

Практика: `python infra-vcs/practice/demo.py` создаёт временный репозиторий, воспроизводит конфликт, разрешает его и делает revert. Рабочий репозиторий пользователя не изменяется.

Требования: [issue #9](https://github.com/Daetoya608/python_interview/issues/9). Справочник: [Git](https://git-scm.com/docs/git).
