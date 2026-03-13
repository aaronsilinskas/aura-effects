# AGENTS

## Primary Goals

1. Keep animation runtime smooth and deterministic on constrained hardware.
2. Minimize memory allocation and garbage collection pressure in hot paths.
3. Preserve readability while prioritizing low-overhead execution patterns.

## Embedded Runtime Constraints

- CPU and RAM are limited; avoid per-frame allocations in update/value loops.
- Garbage collection pauses can cause visible animation stutter.
- Some CPython features/libraries may be unavailable or slower on CircuitPython.
- Floating point math can be expensive; avoid unnecessary repeated computation.
- Avoid for comprehensions, use simple for loops at all times.

## Performance Rules (Hot Paths)

Hot paths include:

- `Effect.update(...)`
- `Effect.value(...)`
- step `update` / per-position sampling logic

Guidelines:

- Do not allocate lists/dicts/closures/objects inside per-frame or per-pixel loops unless unavoidable.
- Reuse state objects via `EffectState.get_data(..., factory)` for one-time initialization.
- Prefer in-place mutation of state over creating replacement objects.
- Avoid exceptions for control flow.
- Keep branch-heavy logic minimal in pixel loops.
- Prefer simple data structures and explicit loops over abstraction-heavy code in hot paths.

## Docstring Preferences

- Open class docstrings with what the class is for and why it matters to the user, not an internal description of its mechanics.
- Follow with technical contracts (update model, sampling model, state ownership, etc.) using concise bullet lists under named sections.
- Method docstrings should be one line when the signature already conveys the what; expand only to describe non-obvious ordering, return semantics, or side effects.
- Use `double backticks` for all symbol references. Avoid bare words like `True`, `None`, or field names.
- Avoid restating what the code plainly does. Prefer describing intent, constraints, and caller responsibilities.
- Do not add docstrings to `__init__` when the class docstring already covers construction parameters.

## CircuitPython Compatibility

- Keep typing imports guarded where needed (`try/except ImportError`) if required by environment.
- Minimize and isolate CircuitPython dependencies so MicroPython and other environments can be used.
- Keep file/module count reasonable; startup/import cost matters on-device.
