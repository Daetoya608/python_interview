# Git — уровень 2

## Отмена и переписывание

| Команда | Что меняет | Когда применять |
|---|---|---|
| `git revert <commit>` | Создаёт новый обратный коммит | Отмена опубликованного изменения с сохранением истории; возможны конфликты |
| `git reset --soft <commit>` | Передвигает ветку, сохраняет index и working tree | Пересобрать локальные коммиты |
| `git reset --mixed <commit>` | Также сбрасывает index, оставляет working tree | Убрать коммиты/подготовку, сохранив правки |
| `git reset --hard <commit>` | Сбрасывает также tracked-содержимое working tree; мешающие untracked-файлы тоже могут пострадать | Только когда эти локальные изменения точно не нужны |
| `git restore --staged file` | Убирает изменение из index | Оставить правки в working tree |
| `git restore file` | Возвращает рабочий файл из index | Отказаться от незастейдженных правок |
| `git clean -nd` | Показывает удаляемые untracked файлы/каталоги | Обязательный предварительный просмотр |
| `git clean -fd` | Удаляет показанные untracked объекты | Очистка; `-x` дополнительно затрагивает ignored, включая окружения и секреты |

`reset` с путями сбрасывает index для путей и не передвигает ветку. `checkout` исторически совмещает переключение и восстановление: `git checkout main`, `git checkout -- file`, `git checkout <commit> -- file`. Для ясности обычно используют `switch`/`restore`. `git switch --detach <commit>` открывает detached HEAD: чтобы сохранить новые коммиты в именованной ветке, создайте её.

```bash
git commit --amend          # новый коммит вместо последнего, другой hash
git rebase -i HEAD~3        # reword / squash / fixup / перестановка
git rebase origin/main     # перенести свои коммиты поверх новой базы
git cherry-pick <commit>   # применить изменение отдельного коммита к текущей ветке
git cherry-pick --abort    # отменить незавершённый перенос
git reflog                 # локальные перемещения ссылок
```

Rebase воспроизводит коммиты, поэтому меняет идентификаторы; merge сохраняет исходную топологию. Переписывание общей ветки требует согласования команды. `--force-with-lease` проверяет ожидаемое состояние удалённой ссылки, но не разрешает организационный конфликт само по себе. Reflog может помочь найти прежний коммит; он локален, ограничен сроками хранения и не заменяет backup.

## Worktree

```bash
git worktree add ../study-hotfix -b hotfix/example main
git worktree list
# закончить работу, проверить/сохранить изменения в этой директории
git worktree remove ../study-hotfix
```

Несколько рабочих каталогов используют общую базу объектов и ссылки репозитория, но собственные HEAD/index. Удобно проверять релиз параллельно с незавершённой задачей. Одна ветка обычно не может быть одновременно checkout в двух worktree. Это не независимый clone и не sandbox для команд удаления.

## Командные процессы

| Подход | Организация | Компромисс |
|---|---|---|
| Gitflow | `main`, `develop`, feature/release/hotfix ветки | Подходит для раздельных версий и релизных циклов; больше долгоживущих веток и сложных слияний |
| GitHub flow | Короткая ветка от main, PR, проверки, merge | Прост для частых релизов; main должен оставаться пригодным к выпуску |
| Trunk-based | Очень короткие ветки или частая интеграция в trunk | Меньше расхождений; нужны быстрые тесты, feature flags и дисциплина |

Конвенция коммитов — договорённость, не правило Git. Conventional Commits: `type(scope)!: description`, например `feat(api): add pagination`; `!` или footer `BREAKING CHANGE:` обозначает несовместимость. Альтернатива — обычное повелительное сообщение с номером задачи. Главное: согласованность, отдельное логическое изменение в коммите, описание причины и отсутствие мусорных `fix2` в итоговой истории. Squash очищает историю задачи, но убирает внутренние точки развития; merge сохраняет их.

## Pre-commit hook

Файл `.githooks/pre-commit` с LF:

```sh
#!/bin/sh
git diff --cached --check
```

Подключение для текущего репозитория: `git config --local core.hooksPath .githooks`. На Unix задайте executable bit (`chmod +x .githooks/pre-commit`); в Git for Windows нужен доступный интерпретатор из shebang. Hook отклоняет whitespace-ошибки подготовленного diff. Для запуска линтера можно подключить framework `pre-commit` с согласованным конфигом и `pre-commit install`.

Hooks не устанавливаются у коллег автоматически при clone, могут обходиться `--no-verify` и не заменяют CI. Проверка рабочего дерева вместо staged-снимка может проверить другое содержимое, чем попадёт в коммит.

Самопроверка: объясните `revert` против `reset`, merge против rebase, судьбу untracked при clean, назначение worktree и способ восстановления случайно потерянной ветки через reflog.

Требования: [issue #9](https://github.com/Daetoya608/python_interview/issues/9). Детали: [reset](https://git-scm.com/docs/git-reset), [rebase](https://git-scm.com/docs/git-rebase), [worktree](https://git-scm.com/docs/git-worktree), [hooks](https://git-scm.com/docs/githooks), [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
