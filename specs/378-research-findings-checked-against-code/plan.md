# Implementation Plan: a research feature ends with its findings checked against the code (feature 378)

**Spec**: `spec.md` | **Request**: `request.md`

## Summary

One small reader that composes what exists, `scripts/record/impl_check.py`, asked by `make impl-check` and by the closing
check every closing route already asks. It is backed by the template task, the guidelines and a line in each open
research-record spec. Everything is tooling: every task is `research: rendering`. One engine file changes (`l7r/diagram/tools/claims.py`,
D6), so the landing is GATED on `make done`.

## Technical Context

- **Code.** Python 3 stdlib under `scripts/record/` and `scripts/gates/`.
- **Tests.** `tests/tooling/` over a real git tree.
- **Reused, not copied.** The claims index's own reader (`scripts/record/claims.py`: `current`, `owed`, `load_index`)
  and `make speckit-todo`'s tag line.

## Performance bookends

N/A. A close reads every claim once, about 10 s (observed 2026-10-10; method: `time` on `claims.current`), and only for a
research-record feature whose commits changed a question.

## Constitution Check

- **I-V, VI, XII**: N/A.
- **X**: every branch has a test.
- **XIII**: the tooling tests are green before and after.
- **XVI**: built as written.

## Decisions

**D1 - The changed questions** are read from git: every non-merge commit whose SUBJECT line opens `Feature NNN` or
`NNN:` (git's `--grep` would match any line, so the subject is filtered here), then each commit's
paths matching a findings page, `research/questions/NNNN-<id>.html`. Before feature 329 those paths carried the old
`.claude/skills/diagram/` prefix, so that prefix is accepted. `.notes`, `.drawing` and `.originals` pages are not
findings. Measured on real features: 317 changed 0081, 315 changed 0046, 310 changed 0038.

**D2 - A claim cites a question** when one of its pointers names the question's FINDINGS page,
`research/questions/NNNN-<id>.html`. A pointer to the drawing page alone does not count: such a claim is fingerprinted on
the drawing page, so a rewritten finding never re-owes it (plan review, round 1: 31 questions are cited only through
drawing pages). **Checked** means it is not in `claims.owed()`: a changed finding re-owes every claim resting on it (feature 318),
so a finding the feature changed cannot pass on a verdict reached before it. Every reason `owed()` gives counts,
triage included (spec review round 1).

**D3 - The record** is `specs/NNN-*/implementation-check.md`, with lines `- NNNN: no code implements it - <why>; searched:
<units and grep>`. It is for a question NO code decides, and a line without its `searched:` part is missing. Merge
commits are read for no feature (`git log --no-merges`).

**D4 - The closing check** (`close_check.reasons`) appends `impl_check.missing(d, <its repository>)`. The tag test runs
first and the commit read second, so a feature that owes nothing pays no claims scan.

**D5 - The text.** The tasks template's standard task, CLAUDE.md's research section, `research/CLAUDE.md`, and a line
in each spec `make speckit-todo AFFECTS="research record"` lists open at landing (seven on 2026-10-10: 336, 337, 338, 343,
352, 368, 374).

**D6 - Claimed units outside the hamlet scope** (spec FR-009). `l7r/diagram/tools/claims.py:all_units` also yields,
through `claimed_outside`, every unit of an engine module outside the scope that carries its OWN claim, not one
inherited from a module docstring, with that module's constants for its fingerprint. `coverage` is unchanged in effect:
an out-of-scope module's unclaimed units are never yielded, so they owe nothing. Today this brings in 3 units with 4
claims (`compound.county_magistracy_program`, `compound_model.NOTICE_BOARD_MAX_FT`, `site_pages.frame`), owed their
`impl-drift` check before the push (`claims-gate.sh`). It is an engine file (`l7r/**`), so the landing is GATED on
`make done`.

## Project Structure

```text
scripts/record/impl_check.py            new
scripts/gates/close_check.py            the closing requirement
Makefile                                impl-check
.specify/templates/tasks-template.md    the standard task
CLAUDE.md, research/CLAUDE.md, specs/{336,337,338,343,352,368,374}-*/spec.md
tests/tooling/test_impl_check.py        new
```
