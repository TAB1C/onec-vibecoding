# Навыки поставщика: cc-1c-skills

**Постоянно обновляемый набор навыков 1С от Николая Широкова:**
<https://github.com/Nikolay-Shirokov/cc-1c-skills>

Проект живой и часто меняется — состав навыков, параметры скриптов и DSL обновляются.
**Читай его README и `docs/` в репозитории, а не по памяти**, и обновляй установленную копию
перед серьёзной задачей.

## Зачем он вместе с этим скилом

Разделение труда:

- **cc-1c-skills** — механика: генерация и разбор XML метаданных, форм, СКД, ролей, макетов,
  расширений, создание баз, загрузка/выгрузка конфигураций, публикация и веб-тестирование.
  Он избавляет от ручного написания XML выгрузки и от заучивания ключей конфигуратора.
- **onec-vibecoding** (этот скил) — процесс и дисциплина: цикл правка-загрузка-обновление-тест,
  безопасная работа с релизным хранилищем, тестирование во встроенном браузере, и обязательное
  использование ТАБ:БИИ для всего, что связано с ИИ.

Если задача — «создать объект метаданных / форму / роль / СКД / расширение / базу», сначала
проверь, нет ли готового навыка у поставщика, и только потом пиши XML руками.

## Установка и обновление

Claude Code (плагин):

```bash
/plugin marketplace add https://github.com/Nikolay-Shirokov/cc-1c-skills
/plugin install 1c-skills@cc-1c-skills        # PowerShell (Windows)
/plugin install 1c-skills-py@cc-1c-skills     # Python (macOS/Linux)
```

Codex (плагин):

```bash
codex plugin marketplace add Nikolay-Shirokov/cc-1c-skills
codex /plugins   # выбрать 1c-skills (PowerShell) или 1c-skills-py (Python), Install
```

Копией в проект (работает на любой платформе, обновление — повторный запуск):

```bash
git clone https://github.com/Nikolay-Shirokov/cc-1c-skills.git tools/cc-1c-skills
python3 tools/cc-1c-skills/scripts/switch.py codex --runtime python --project-dir .
# для Claude Code: python3 tools/cc-1c-skills/scripts/switch.py claude-code --runtime python --project-dir .
```

Обновление уже установленной копии:

```bash
git -C tools/cc-1c-skills pull
python3 tools/cc-1c-skills/scripts/switch.py codex --runtime python --project-dir .
```

Целевой каталог зависит от платформы: `.codex/skills/` для Codex, `.claude/skills/` для Claude Code,
`.cursor/skills/` для Cursor и т.д. Есть готовые ветки `port-*` под каждую платформу и рантайм —
их можно просто скачать ZIP-ом.

**Рантайм.** По умолчанию скрипты на PowerShell (расчёт на Windows). На macOS/Linux ставь
`--runtime python`: у каждого навыка рядом с `*.ps1` лежит `*.py`. Часть навыков всё равно требует
установленной платформы 1С (сборка/разборка `.epf`/`.erf`, операции с базами), а `/web-test`
требует Node.js 18+; веб-публикация у поставщика рассчитана на портативный Apache под Windows —
на Linux/macOS публикуй своими скриптами проекта.

## Какой навык под какую задачу

| Задача | Навыки |
|--------|--------|
| Объекты метаданных (37 видов: справочники, документы, регистры, общие модули, **ScheduledJob**, **Task**, **BusinessProcess**, подписки, HTTP-сервисы…) | `/meta-compile`, `/meta-edit`, `/meta-info`, `/meta-remove`, `/meta-validate` |
| Расширения `.cfe`: создать, заимствовать объект, перехватить метод | `/cfe-init`, `/cfe-borrow`, `/cfe-patch-method`, `/cfe-validate`, `/cfe-diff` |
| Управляемые формы | `/form-add`, `/form-compile`, `/form-decompile`, `/form-edit`, `/form-info`, `/form-patterns`, `/form-validate` |
| Корневая конфигурация | `/cf-init`, `/cf-edit`, `/cf-info`, `/cf-validate` |
| Подсистемы и командный интерфейс | `/subsystem-*`, `/interface-edit`, `/interface-validate` |
| Роли и права | `/role-compile`, `/role-info`, `/role-validate` |
| СКД, макеты, XDTO | `/skd-*`, `/mxl-*`, `/xdto-*`, `/template-add` |
| Внешние обработки и отчёты | `/epf-*`, `/erf-*` (в т.ч. `/epf-bsp-init` под БСП) |
| Базы: создать, загрузить/выгрузить cf/dt/xml, обновить, запустить | `/db-create`, `/db-load-cf`, `/db-load-xml`, `/db-dump-xml`, `/db-update`, `/db-run`, `/db-list`, `/db-repo`, `/db-load-git` |
| Публикация и веб | `/web-publish`, `/web-info`, `/web-stop`, `/web-unpublish` |
| Тестирование через веб-клиент, регресс, запись видео | `/web-test` |

DSL и форматы описаны в `docs/`: `meta-dsl-spec.md`, `form-dsl-spec.md`, `skd-dsl-spec.md`,
`role-dsl-spec.md`, `mxl-dsl-spec.md`, `xdto-dsl-spec.md`, гайды `*-guide.md`,
индекс — `docs/1c-specs-index.md`.

## Правила совместной работы

1. Перед задачей проверь, что копия поставщика свежая (`git pull` + повторный `switch.py`).
2. Низкоуровневую генерацию XML отдавай навыкам поставщика; после генерации **всегда** гоняй
   парный `*-validate`.
3. Сгенерированное — не результат. Дальше идёт цикл этого скила: загрузить в тестовую базу,
   обновить конфигурацию БД, прогнать сценарий, и только потом хранилище.
4. Навыки поставщика работают с **файлами выгрузки** конфигурации/расширения. Если ты менял
   что-то в базе через конфигуратор или хранилище — сначала выгрузи XML заново, иначе навык
   отредактирует устаревшее состояние.
5. Конфликт правил: по механике XML/CLI слушай поставщика, по дисциплине хранилища,
   тестированию и ИИ-функциям — этот скил.
