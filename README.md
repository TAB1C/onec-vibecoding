# onec-vibecoding

Codex skill for organizing a 1C vibe-coding workspace: extension-first development, `ibcmd`/Designer command-line loops, browser testing, and careful release storage discipline.

## Install

Clone the skill into Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/TAB1C/onec-vibecoding.git ~/.codex/skills/onec-vibecoding
```

Open a new Codex chat and invoke it:

```text
Use $onec-vibecoding for this 1C task.
```

In Russian:

```text
Используй $onec-vibecoding для этой задачи 1С.
```

## Update

```bash
git -C ~/.codex/skills/onec-vibecoding pull
```

## What It Covers

- Work with a 1C extension instead of the whole configuration when possible.
- Prefer `ibcmd`, batch `1cv8 DESIGNER`, and existing repository scripts.
- Load changes into a test infobase, update metadata, and verify behavior.
- Test user flows in the 1C web client through the in-app browser.
- Reproduce suspected bugs before changing release code.
- Commit only real production objects to configuration or extension storage.
- Keep temporary test processing, debug hooks, and fixtures out of release storage.
