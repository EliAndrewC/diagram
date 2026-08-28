# Implementation Plan: Rust-based type checker experiment (feature 142)

**Branch**: none - `SPECIFY_FEATURE=142-rust-type-checker` | **Date**: 2026-08-28 | **Spec**: [spec.md](spec.md)

## Summary

The experiment is done ([research.md](research.md)): both Rust checkers run the whole engine cold
in ~0.5 s with nothing resident, against mypy's 12.7 s cold / 0.13 s warm daemon at 400-600 MB
per clone. **pyrefly** is the pick - it natively enforces "an unannotated function is an error",
ty has no such rule. So the contingent half of the spec proceeds: pyrefly replaces mypy in the
quick target and the gate as a one-shot process, its configuration lands in `pyproject.toml` beside
`[tool.mypy]`, the 24 residual diagnostics are resolved (2-3 real tightenings, ~16 suppressions of
one documented pyrefly limitation, 6 defensive initializations), the dmypy DAEMON machinery is
removed, mypy stays installed, and `report.md` puts the pick, the numbers, and the two reserved
questions (mypy in the lockfiles; the constitution's `mypy --strict` wording) to the GM. Nothing
pushes until they accept.

## Technical Context

**Language/Version**: Python 3.14.4; pyrefly 1.2.0 (Rust binary wheel, no Python deps)
**Primary Dependencies**: pyrefly added to `requirements-dev.in` and re-locked with pip-compile; mypy stays pinned
**Testing**: pytest via the quick target and the gate; `scripts/test-*.sh` via `make hooks-test`
**Target Platform**: this container and the CodeBuild image (`Dockerfile.ci` installs both lockfiles)
**Project Type**: tooling change under the diagram skill - NO generator change
**Performance Goals**: per-quick type check ~0.6 s one-shot; 0 resident processes
**Constraints**: the engine file set is unchanged; no map is regenerated; the residual-diagnostic fixes ARE engine edits, so the route is GATED and the gate must be green
**Single-artifact target**: N/A - no generator change; the "artifact" is the quick target's type phase
**Every step is two steps**: N/A - no map is rolled

## Performance bookends

N/A - the generator is untouched; the diagnostic fixes are `bool(...)` wraps, `None`
initializations and comments. `make perf-review` at push time will confirm no change.

## Constitution Check

- I, II: N/A - no UI in this repository.
- III, IV, VII, VIII, IX: N/A - no pool content, no SOURCE blocks, no in-world text.
- V: PASS - no task touches a SOURCE block.
- VI: PASS - every task names its verification (the quick target while iterating, the gate once, `make hooks-test` after the guard removal; a planted-error test). Review subagents: none owed (no map).
- X: **DEFERRED-BY-DESIGN, flagged to the GM** - Principle X names `mypy --strict`. This feature runs pyrefly with the mypy-equivalent rules instead and leaves mypy installed; the constitution's wording is the GM's to amend (FR-007b) and the report puts the change to them. Until they rule, `python3 -m mypy` still passes on the tree (it is not removed), so the letter of X is not broken.
- XII: N/A - nothing asserted about the world; Decisions Recorded omitted per the spec.
- XIII: PASS - baseline is a green gate on unmodified code (the sync-in tip); every failure after the switch is diagnosed.
- XIV: PASS - the residual diagnostics that are real (`castle_civic.py:266`, the two `bool()` returns) are fixed in this work.
- XV, XVI: PASS - spec reviewed FAITHFUL on round 2; no exception carved.

## Project Structure

```
specs/142-rust-type-checker/{gm-request.md, spec.md, research.md, plan.md, tasks.md, report.md}
.claude/skills/diagram/pyproject.toml            [tool.pyrefly] beside [tool.mypy]
.claude/skills/diagram/Makefile                  MYPY -> TYPECHECK (pyrefly check); DMYPY_SWEEP gone
.claude/skills/diagram/requirements-dev.{in,txt} + pyrefly
.claude/skills/diagram/tests/test_typecheck.py   the one planted-error test (tooling)
scripts/dmypy-hooks.sh, scripts/test-dmypy-hooks.sh   removed
.claude/settings.json                            SessionEnd dmypy entry removed
CLAUDE.md, docs/, dev/                           the daemon row and notes retired; the switch recorded
```

## Phase 0 - research: DONE (research.md R1-R6)

## Phase 1 - design

- **Configuration**: `[tool.pyrefly]` with `project-includes` = the mypy `files` list (one list,
  copied verbatim; a test asserts the two lists are equal while both exist), `search-path = ["."]`
  (the `mypy_path` equivalent), `python-version = "3.14"`, `replace-imports-with-any = ["boto3.*",
  "botocore.*"]` (the override's equivalent), and `[tool.pyrefly.errors]` enabling
  `unannotated-parameter`, `unannotated-return`, `unannotated-attribute`,
  `implicit-any-type-argument`, `no-any-return-implicit`, `unused-ignore`.
- **Makefile**: `TYPECHECK = pyrefly check` replaces `MYPY` at both call sites; no CodeBuild branch
  needed (the one-shot form is the only form); `DMYPY_SWEEP` and its comment block go; the
  header comment's mypy ratchet note updated.
- **Suppressions**: `# pyrefly: ignore[rule]  # <reason>` at each `.get(k, Any-default)` site, the
  reason pointing at research R5.
- **The test**: `tests/test_typecheck.py` (marker `tooling`) writes a fixture file with a wrong
  argument type into a temp package, runs `pyrefly check` on it through the same config, asserts
  non-zero exit; and asserts `project-includes == [tool.mypy].files`.
- **Guard removal**: `dmypy-hooks.sh`, its test, the `SessionEnd` entry, the `CLAUDE.md` table row
  and the two dev notes; `make hooks-test` proves the suite is green without it.

## Complexity Tracking

None.
