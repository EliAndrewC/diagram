# Feature 241 - no conflict markers

**Status**: DRAFT - `spec-fidelity` not yet run.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - the two incidents measured, why the state-based rule is the
wrong one, and what the backstop is for.
**Predecessors**: 212 (a guard does the right thing where it can, and refuses where only the session has
what is missing), 169 (an escape is an invocation, not a mention), 168 (every acting branch records, per
RULE), 164 (teach before blocking where the lesson can arrive earlier), 236 (the recipe-comment guard and
its gate-phase backstop, the shape this follows).

## Summary

Twice in one day a conflicted merge was committed with its markers still in it: once one file, caught by
accident when `make notes-census` could not parse it, and once **23 files**, caught by the gate's lint
phase after the commit (research R1). Both times the command was `git add -A`, and both times the harm was
not the staging - it was the COMMIT, because the history here is never rewritten, so the merge had to be
redone from the merge base.

The guard is on CONTENT, not on merge state. A `git add` or `git commit` that would stage a file holding a
conflict triple is refused, naming the files. That is silent on the correct `add -A` at the end of a
resolved merge - the thing a state-based rule would refuse - and it catches a marker that arrived by any
route, which a state-based rule would not (R2, R3).

## Functional requirements

- **FR-001 The refusal is on the triple.** A file counts as carrying a conflict when it holds a `<<<<<<<`
  line, a later `=======` line and a later `>>>>>>>` line, each at the start of a line. Any one of them
  alone is not a conflict: `=======` is an ordinary underline in this project's own Markdown, and a
  session writing about merges types the others.
- **FR-002 It reads only what the command would stage.** `git add <paths>` is judged on those paths;
  `git add -A` / `git add .` / `git commit -a` on the working tree's changed files; `git commit` with no
  `-a` on what is already staged. A path that is not a file, is outside the repository, or cannot be read
  as text is skipped rather than guessed at.
- **FR-003 The refusal names the files and the next action.** Every offending path, and the instruction:
  resolve them, then stage. It does NOT offer to stage the rest - which file is resolved is the session's
  knowledge, not the guard's (feature 212's line: what stays a refusal is what only the session can
  supply).
- **FR-004 Prose is not a conflict.** A marker inside a fenced code block, an indented block, or a
  backtick span is text ABOUT a marker. This feature's own spec and research carry them, as does the
  guard's suite, and the guard must stay quiet on all of it.
- **FR-005 The escape says why.** `CONFLICT_MARKERS_OK="<reason>"`, matched as an INVOCATION through
  `_hookmatch.py escape` so a grep or a commit message quoting it does not escape anything (feature 169),
  refused without a reason of two words and eight characters (feature 170), and recorded through
  `_guardlog.sh` like every other branch, with its own rule slug (feature 168).
- **FR-006 A gate phase is the backstop.** One phase scans every TRACKED file for a triple and fails,
  naming them. A guard can be escaped and a marker can arrive from outside this session; the backstop is
  what makes the property true of the repository rather than of one tool call. Its own suite proves it
  fires.
- **FR-007 The guard ships with its companion.** `scripts/test-conflict-marker-hooks.sh`, run by
  `make hooks-test` like the other twelve (constitution XVIII), proving: it fires on a staged marker; it
  stays QUIET on the `add -A` that ends a resolved merge; it stays quiet on a file that merely discusses
  markers; the escape works, is recorded, and is refused when bare; and a mention of the token is not an
  escape.
- **FR-008 The doctrine is written where the others are.** A row in `CLAUDE.md`'s enforcement table, with
  both incidents and the reason the rule is on content rather than on merge state - so the next session
  reads why this is not "never use `add -A`".

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003) Incident 2 replayed: a tree with 23 marker-carrying files staged by
  `git add -A` is refused, and the refusal names them.
- **SC-002** (FR-001, FR-004) The correct end of a merge is NOT refused: every file resolved, `git add -A`
  passes; and a file containing `=======` as a Markdown underline, or a fenced block showing a conflict,
  passes.
- **SC-003** (FR-005) A bare `CONFLICT_MARKERS_OK` is refused; one with a reason permits and is recorded
  with its rule; `grep CONFLICT_MARKERS_OK` escapes nothing.
- **SC-004** (FR-006) The gate phase fails on a tracked file carrying a triple and names it, and passes on
  the clean tree.
- **SC-005** (FR-007, FR-008, spec-wide) `make hooks-test` green with the new suite among them,
  `make done` green, and the table row present.

## Decisions Recorded

- **D1 - content, not merge state** (R2). The state rule would refuse the correct `add -A` that ends every
  resolved merge, and would miss a marker that arrived any other way. Recorded because the state rule is
  the obvious one and the next reader will wonder why it was not taken.
- **D2 - the triple, not any single marker.** `=======` alone is a Markdown underline and appears in this
  repository's own docs; `<<<<<<<` alone appears in prose about merges. Only the three in order are
  unambiguous.
- **D3 - it refuses rather than fixing.** Feature 212's ladder asks whether the guard can supply the
  compliant command. It cannot: the compliant command stages the files that are RESOLVED, and which those
  are is the session's knowledge. This is the same class as `make-only`'s `guard-write` and
  `guard-file`'s no-marker refusal, the two largest refusal families that stayed refusals.
- **D4 - the backstop is a gate phase, not a pytest test** (the shape feature 236 used for the house-style
  delta scan): a scan whose own code never changes would sit unexecuted under testmon through exactly the
  edits it exists to catch.
