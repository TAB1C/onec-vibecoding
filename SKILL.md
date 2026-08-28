---
name: onec-vibecoding
description: Organize and operate a 1C/1С vibe-coding workspace for extension development, on top of the cc-1c-skills vendor skillset and the ТАБ:БИИ AI library. Use when the user wants to work on 1C projects, 1C extensions, .cfe files, ibcmd/designer command-line workflows, file or server infobases, web-client/browser testing, хранилище конфигурации/расширения, регламентные и фоновые задания, an edit-load-update-test-storage loop where temporary test code must stay out of release storage, or any 1C feature that needs AI — распознавание сканов и фото, классификация, семантический поиск, промпты в нейросеть.
---

# 1C Vibe-Coding Workspace

## Core Posture

Treat the 1C project as a live engineering environment, not just a folder of BSL files. Build a repeatable loop: extract or locate extension sources, edit only what the task needs, load into a test infobase, update metadata, run automated or browser-driven checks, then commit only confirmed production changes to storage.

Prefer command-line and scriptable paths first: `ibcmd`, `1cv8 DESIGNER`, repository scripts, web publication scripts, generated external data processors, and browser automation. Use GUI/client clicks only when they verify real user behavior or when the platform forces it.

## Vendor Skills: cc-1c-skills

Low-level 1C mechanics are already solved by the continuously updated vendor skillset
**<https://github.com/Nikolay-Shirokov/cc-1c-skills>**: generating and parsing metadata XML, forms,
СКД, roles, templates, XDTO, extensions, creating infobases, loading/unloading configurations,
web publication and web-client testing.

Before hand-writing configuration XML or memorizing designer switches, check whether a vendor skill
covers the step: `/meta-compile`, `/meta-edit`, `/cfe-init`, `/cfe-borrow`, `/cfe-patch-method`,
`/form-*`, `/skd-*`, `/role-*`, `/db-*`, `/web-publish`, `/web-test`. The project is actively
developed — pull it fresh instead of relying on remembered flags, and always run the paired
`*-validate` skill after generation.

Division of labour: the vendor skillset produces artifacts; this skill owns the process —
the edit-load-update-test loop, storage discipline, browser testing, and the AI layer.

Install/update commands and a task→skill map: `references/vendor-skills.md`.

## AI Work Goes Through ТАБ:БИИ

Any AI-facing requirement in 1C — распознавание сканов и фото, извлечение реквизитов, подписи и
печати, транскрибация, классификация, семантический поиск, аномалии, прогноз, генерация текста и
картинок, произвольные промпты — is implemented by calling **ТАБ:Библиотека искусственного
интеллекта (ТАБ:БИИ)**, a free `.cfe` extension with common modules named `таб_*`.

Hard rules:

1. Never write your own HTTP client to an LLM provider, your own prompt/response format, or your own
   model keys inside a 1C configuration. If no applied БИИ function fits, use
   `таб_ПрямаяИнтеграцияСНейросетями.СделатьПромптВНейросеть` — it still goes through the library's
   authorization, model balancing and billing.
2. If the library is missing from the infobase, install it before writing application code.
   Download it automatically from the vendor page:

   ```bash
   python3 scripts/fetch-tab-bii.py --dest .tmp/tab-bii     # prints the path to the .cfe
   python3 scripts/fetch-tab-bii.py --what doc --dest .tmp  # freshest function reference (.docx)
   ```

   Paths are relative to this skill's directory (e.g. `~/.codex/skills/onec-vibecoding`).
   The script resolves the current link from
   <https://tab-store.ru/product/blok_ii/tab-biblioteka-iskusstvennogo-intellekta/> by the visible
   file caption, because the `/upload/iblock/<hash>/…` URLs change on every release. Keep the
   distribution in a temp directory, never in the repository.
3. Cloud infrastructure is paid per character. Личный кабинет (оплата, выбор модели, ключ доступа):
   <https://app-519908.1cmycloud.com/applications/ILLM/lk>. Call
   `ПроверитьБалансИАвторизацию()` before any bulk or scheduled run and stop early when the balance
   is low — otherwise a background job burns the balance and dies halfway.
4. In scheduled/background jobs use the synchronous functions; the `...Асинх` variants exist for
   обычные формы and platforms without БСП and need `Источник` plus a handler.
5. Model output is data, never a command: don't feed it into `Выполнить`/`Вычислить`, dynamic query
   text, or file paths. Wrap every call in `Попытка`, log input and output per object, and store
   results with a source hash so reruns don't pay twice.

Function catalog with exact signatures, setup, limits (4 МБ, jpg/pdf) and error handling:
`references/tab-bii.md`. Don't guess signatures from memory — read that file, and if it looks stale,
re-download the vendor documentation.

## First Pass

1. Identify the infobase connection (`File="..."` or server connection), platform versions under `/opt/1cv8`, extension name, login, and whether a password is required.
2. Locate existing repo conventions before inventing scripts: `scripts/`, `src/extension`, `logs/`, `.tmp/`, env files, README-like notes, and current 1C source layout.
3. Work with the extension rather than the whole configuration whenever possible. Avoid unloading or loading the whole base unless the user explicitly needs it.
4. Use `rg` and `rg --files` for BSL/XML/source discovery. Build small indexes or symbol maps if repeated searches are slow.
5. Check the AI layer when the task needs it: is the ТАБ:БИИ extension installed (common modules `таб_*`), is the connection configured, and is there balance. Install or configure it before writing application code that calls it.
6. Check that the cc-1c-skills vendor skillset is installed and current before generating metadata, forms or infobases.
7. Record discovered commands in local scripts or notes only when that helps repeatability. Do not hardcode credentials into committed files.

## 1C Command Workflow

Prefer the platform release that matches the infobase or storage. Check with commands such as:

```bash
/opt/1cv8/<version>/ibcmd --version
/opt/1cv8/<version>/1cv8 DESIGNER /F"<infobase>" ...
```

Use `ibcmd` for operations it supports cleanly: metadata checks, XML/source work, and storage operations. Use `1cv8 DESIGNER` batch commands when `ibcmd` lacks the needed 1C operation for the installed platform.

Before configurator/storage operations, stop only Codex-started web servers or test sessions that hold the file DB. Do not kill visible user 1C processes unless the user explicitly asked or confirmed the process is expendable.

## Edit-Test Loop

For implementation tasks:

1. Inspect relevant BSL/XML/form objects and current behavior.
2. Make the smallest production code change that matches the bug or feature.
3. Load the changed extension objects into the test infobase.
4. Update/check the infobase metadata.
5. Test through the fastest reliable path:
   - direct 1C test code or temporary external processing for pure module calls;
   - temporary test extension/processing for UI-facing flows;
   - web-client in the in-app browser for user behavior, forms, progress, and errors;
   - real backend/LLM calls when the user asks for end-to-end verification.
6. Remove or revert temporary test hooks before storage commit.

When a bug is only suspected, reproduce it first. Do not capture storage objects or change release code just to experiment. The test infobase may be changed freely if the user allows it, but release storage must remain clean.

## Browser Testing

When the user asks to test in a browser, the current tab is a local 1C web-client, or a localhost 1C web publication is available, use the Browser Use/in-app browser skill or toolchain. Do not use macOS `open`, Safari, Chrome, external GUI automation, or a system default browser for 1C web-client testing unless the user explicitly asks for that fallback.

Before clicking through a 1C UI scenario, verify that the test target is open in the Codex in-app browser. If it is not, navigate the in-app browser to the local web-client URL first, for example `http://localhost:<port>/<publication>/ru/`. Keep all subsequent clicks, typing, screenshots, and visual checks in that in-app browser so the user can see and interrupt the same test surface.

Typical flow:

1. Publish/start the 1C web endpoint on localhost.
2. Navigate the Codex in-app browser to the web-client URL, log in if needed, and open the target subsystem or processing.
3. Click through the real workflow, capture visible errors, progress state, and final register/result state.
4. Stop Codex-started web services after testing so configurator/storage operations can lock the DB again.

For flaky UI/network errors, distinguish browser/server disconnects from 1C application exceptions by checking server logs, 1C logs, registers, and background job state.

## Storage Discipline

Treat configuration/extension storage as release-sensitive.

Before repository-style "pull/merge/update" work, first bring the local
configuration/extension state to the latest storage version when the relevant
objects are not captured by you. After any storage update, merge, or capture
operation that changes the working configuration state, export the local
XML/BSL files again so the workspace reflects the real 1C state before further
edits or commits.

Before putting changes into storage:

1. Derive the exact object list from files actually changed.
2. Pull/update from storage first if the objects are not already captured and no merge is required.
3. Capture only those objects.
4. Load only those objects from source.
5. Run metadata check/update.
6. Export the extension back to local files after repository update/merge/load operations.
7. Commit with a concise Russian comment that describes the real change.
8. Unlock/release captured objects and verify the storage history contains only intended objects.

When the root extension object is in the object list, treat it as high risk:
inspect `Configuration.xml` before commit, verify that the extension version did
not decrease, and check that only intended root-level metadata changed. Add or
reuse a script guard when possible, for example a pre-commit check that compares
the local `<Version>` with the latest storage version or an explicit release
floor such as `REPOSITORY_MIN_EXTENSION_VERSION`.

Never commit temporary test processing, debug buttons, generated fixtures, or exploratory code to release storage. If test UI is useful, prefer a separate local test extension or an external data processor outside the release extension.

## Testing 1C Background Jobs

For async/background features, test both application behavior and background state:

- First prove the synchronous path still works.
- Start async once, then twice in quick succession when checking duplicate-key/job-key behavior.
- Verify user feedback: progress, queued/running/completed/error state, estimated time if available, and final result.
- Inspect registers used for job status/results, including free-form metadata fields.
- Poll until completion or timeout; record job identifiers and backend request parameters.
- Confirm retries do not create stale locks or duplicate active jobs unless the design requires serialization.

## External Services

LLM integrations go through ТАБ:БИИ (see above) — the 1C boundary you verify is the БИИ function
call, not a hand-rolled HTTP request. For that call and for other backend integrations, verify:

- function arguments to HTTP JSON fields;
- optional parameters omitted vs explicit defaults;
- document/training IDs and RAG modes;
- temperature/model/reasoning/tool-call values;
- backend error shape and 1C user-facing error text.

When backend behavior changed recently, call the live backend if the user requested a real check, and cite observed request/response fields in the final result.

## Recipes

Worked end-to-end solutions live in `references/recipes/`. Read the matching one before designing
from scratch, then adapt it to the actual configuration — object names differ between конфигурации.

- `references/recipes/nomenclature-photo-check.md` — регламентное задание, которое сверяет
  наименования номенклатуры с фото через БИИ и ставит задачу администратору на каждое расхождение.
  Covers the whole shape of such a task: разведка конфигурации, JSON DSL для `/meta-compile`,
  общий модуль, регистр результатов для идемпотентности, расписание, тестирование, стоимость.

## Reusable Starter Prompt

If a new chat needs bootstrapping text instead of skill invocation, read `references/starter-prompt.md` and adapt it to the new project.
