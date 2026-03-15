# AGENTS

Skills referenced in this file are available at https://github.com/aaronsilinskas/ai-skills and should be installed to `~/.agents/skills/`.

The `embedded-dev` skill (`~/.agents/skills/embedded-dev/`) applies to all coding work on this project.

## Embedded Runtime Constraints

General rules are in the `embedded-dev` skill (`~/.agents/skills/embedded-dev/`). Hot paths in this library are:

- `Effect.update(...)`
- `Effect.value(...)`
- step `update` / per-position sampling logic

Project-specific guidelines:

- Reuse state objects via `EffectState.get_data(..., factory)` for one-time initialization.
- Prefer in-place mutation of state over creating replacement objects.
- Keep branch-heavy logic minimal in pixel loops.
- Prefer simple data structures and explicit loops over abstraction-heavy code in hot paths.

## Docstring Preferences

Governed by the `python-docstrings` skill (`~/.agents/skills/python-docstrings/`).
