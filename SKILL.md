---
name: onec-vibecoding
description: Organize and operate a 1C/1С vibe-coding workspace for extension development. Use when the user wants Codex to work on 1C projects, 1C extensions, .cfe files, ibcmd/designer command-line workflows, file or server infobases, web-client/browser testing, хранилище конфигурации/расширения, or an edit-load-update-test-storage loop where temporary test code must stay out of release storage.
---

# 1C Vibe-Coding Workspace

## Core Posture

Treat the 1C project as a live engineering environment, not just a folder of BSL files. Build a repeatable loop: extract or locate extension sources, edit only what the task needs, load into a test infobase, update metadata, run automated or browser-driven checks, then commit only confirmed production changes to storage.

Prefer command-line and scriptable paths first: `ibcmd`, `1cv8 DESIGNER`, repository scripts, web publication scripts, generated external data processors, and browser automation. Use GUI/client clicks only when they verify real user behavior or when the platform forces it.

## First Pass

1. Identify the infobase connection (`File="..."` or server connection), platform versions under `/opt/1cv8`, extension name, login, and whether a password is required.
2. Locate existing repo conventions before inventing scripts: `scripts/`, `src/extension`, `logs/`, `.tmp/`, env files, README-like notes, and current 1C source layout.
3. Work with the extension rather than the whole configuration whenever possible. Avoid unloading or loading the whole base unless the user explicitly needs it.
4. Use `rg` and `rg --files` for BSL/XML/source discovery. Build small indexes or symbol maps if repeated searches are slow.
5. Record discovered commands in local scripts or notes only when that helps repeatability. Do not hardcode credentials into committed files.

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

When the user asks to test in a browser or the current tab is a local 1C web-client, use the Browser Use/in-app browser skill or toolchain rather than macOS `open`.

Typical flow:

1. Publish/start the 1C web endpoint on localhost.
2. Navigate to the web-client URL, log in if needed, and open the target subsystem or processing.
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

For backend or LLM integrations, verify request mapping at the 1C boundary:

- function arguments to HTTP JSON fields;
- optional parameters omitted vs explicit defaults;
- document/training IDs and RAG modes;
- temperature/model/reasoning/tool-call values;
- backend error shape and 1C user-facing error text.

When backend behavior changed recently, call the live backend if the user requested a real check, and cite observed request/response fields in the final result.

## Reusable Starter Prompt

If a new chat needs bootstrapping text instead of skill invocation, read `references/starter-prompt.md` and adapt it to the new project.
