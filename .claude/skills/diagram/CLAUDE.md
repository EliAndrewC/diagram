# /diagram skill - the index

This directory is the `/diagram` skill: building plans (Mode A) and settlement maps (Mode B). What you read
next depends on what you are doing:

| you are | read |
|---|---|
| drawing or invoking a map | [`SKILL.md`](SKILL.md) |
| changing the engine, a pool generator or a test | [`l7r/diagram/CLAUDE.md`](l7r/diagram/CLAUDE.md) - the dev loop; it auto-loads when you read a file under `l7r/diagram/`, `pool/` or `tests/` |
| writing or checking the research record | [`research/CLAUDE.md`](research/CLAUDE.md) - it auto-loads under `research/` |

**Why this file is short** (feature 250, GM 2026-09-26): everything here auto-loads into every session that
reads ANY file below it, the research record included. The dev loop lived here and cost a research session
about 7,500 tokens on every turn; it now loads only where it applies.

The skill's Python is under `l7r/diagram/` and is run as modules from this directory
(`python3 -m l7r.diagram.pipeline.regen ...`); `pool/` holds the shipped maps; `Makefile` and
`pyproject.toml` stay here. Everything runs through `make` (the root CLAUDE.md, "Verification and iteration").
