# Feature 241 - no conflict markers

**Status**: DRAFT - `spec-fidelity` not yet run.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - the two incidents measured, why the state-based rule is the
wrong one, and what the backstop is for.
**Predecessors**: 164 (the REWRITE / TEACH / REFUSE ladder - what stays a refusal is what only the session
can supply), 212 (the second pass over every refusal branch, and the Makefile recipe-comment guard whose
detector is shared with a gate-phase backstop - the shape this one follows), 169 (an escape is an
invocation, not a mention), 168 (every acting branch records, per RULE), 236 (the house-style delta scan,
for why a backstop is a gate PHASE and not a pytest test).

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
  line, then a later line that is EXACTLY `=======`, then a later `>>>>>>>` line - the open and close
  markers at the start of their line, the middle one the whole of its own, because `======= foo` at column
  zero is a heading rule in someone's Markdown and not something git writes. Any one of them alone is not a
  conflict: `=======` is an ordinary underline in this project's own Markdown, and a
  session writing about merges types the others.
- **FR-002 GIT says what the command would stage; the guard does not re-implement pathspecs.** For an
  `add`, the file list comes from `git add --dry-run --ignore-missing` run with the command's own
  arguments, so `-A`, `.`, `-u`, a directory, a glob and a pathspec magic string are all answered by the
  tool that defines them; `git commit -a` asks the same of the tracked changed files and a bare
  `git commit` reads the index. The tree and the arguments are taken from the command AS WRITTEN - its
  `cd`s, its `-C`, and its `VAR=` assignments expanded - because the recorded incident was
  `CL=<clone>; git -C $CL add -A`, which a guard reading only the shell's own directory cannot see. A path
  that is not a file, is outside the repository, or cannot be read as text is skipped rather than guessed
  at.
- **FR-003 The refusal names the files and the next action.** Every offending path, and the instruction:
  resolve them, then stage. It does NOT offer to stage the rest - which file is resolved is the session's
  knowledge, not the guard's (feature 212's line: what stays a refusal is what only the session can
  supply).
- **FR-004 Prose is not a conflict - decided by COLUMN 0, and a document that must SHOW a conflict says
  so.** A marker inside a backtick span, or indented the way prose shows an example, starts no line with
  the triple and is not a conflict. **A fence is NOT an exemption**: git writes its markers at column 0
  wherever the conflict falls, including inside a fenced block in a Markdown file, and 7 of the 23 files
  of the second incident were Markdown or HTML - an exemption for fenced text would have passed them. A
  file that must carry a real triple at column 0 - a fixture, a document explaining a conflict - declares
  `CONFLICT_MARKERS_OK: <reason>` in its first 40 lines, the same file-level shape `FILE_SIZE_OK` takes,
  and `make audit` lists every file taking it. **A MENTION of that marker is not a declaration**: it must
  stand at the start of its line (modulo indentation and comment punctuation) and state a real reason, not
  a `<reason>` placeholder - the detector's own docstring describes the marker, and under the first rule
  that exempted the detector from its own backstop (R4).
- **FR-005 The escape says why.** `CONFLICT_MARKERS_OK="<reason>"`, matched as an INVOCATION through
  `_hookmatch.py escape` so a grep or a commit message quoting it does not escape anything (feature 169),
  refused without a reason of two words and eight characters (feature 170), and recorded through
  `_guardlog.sh` like every other branch, with its own rule slug (feature 168).
- **FR-006 The backstop runs at the gate AND at the push.** One scan of every TRACKED file for a triple,
  failing and naming them, wired into the skill Makefile's `static` phase and into `sync-with-main.sh` at
  push time - the same two places as `check-file-scale.py` and `spec-lint.py`, and for the same reason
  those are in both: a landing that carries a marker is usually a MERGE, whose delta can touch no engine
  Python at all and so runs no gate on the way to main. A guard can be escaped and a marker can arrive
  from outside this session; the backstop is what makes the property true of the repository rather than of
  one tool call. Its own suite proves it fires.
- **FR-007 The guard ships with its companion.** `scripts/test-conflict-marker-hooks.sh`, run by
  `make hooks-test` like every other guard's companion (constitution XVIII), proving: it fires on a staged marker; it
  stays QUIET on the `add -A` that ends a resolved merge; it stays quiet on a file that merely discusses
  markers; it fires on a triple inside a FENCE and is quiet once that file declares the marker; the
  escape works, is recorded, and is refused when bare; and a mention of the token is not an escape. It
  also drives the recorded incident's own command shape, `CL=<clone>; git -C $CL add -A`, which the first
  implementation of this guard let through.
- **FR-008 The doctrine is written where the others are.** A row in `CLAUDE.md`'s enforcement table, with
  both incidents and the reason the rule is on content rather than on merge state - so the next session
  reads why this is not "never use `add -A`".

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003) Incident 2 replayed: a tree with 23 marker-carrying files staged by
  `git add -A` is refused, and the refusal names them.
- **SC-002** (FR-001, FR-002, FR-004) The correct end of a merge is NOT refused: every file resolved,
  `git add -A` passes, and so does `git add .` in a clean subdirectory of a tree whose marker lies
  elsewhere; a file containing `=======` as a Markdown underline passes; a fenced triple is REFUSED and
  passes only once its file declares `CONFLICT_MARKERS_OK: <reason>`.
- **SC-003** (FR-005) A bare `CONFLICT_MARKERS_OK` is refused; one with a reason permits and is recorded
  with its rule; `grep CONFLICT_MARKERS_OK` escapes nothing.
- **SC-004** (FR-006) The scan fails on a tracked file carrying a triple and names it, and passes on the
  clean tree - including on THIS repository, whose spec, research and suite all discuss markers; and it
  runs at the push as well as at the gate.
- **SC-005** (FR-007, FR-008, spec-wide) `make hooks-test` green with the new suite among them,
  `make done` green, and the table row present.

## Decisions Recorded

- **D1 - content, not merge state, WHICH DEPARTS FROM WHAT THE GM APPROVED** (R2). The proposal the GM
  said yes to was the state one, in the session's own framing relayed to them: *"`add -A` is not wrong in
  general, but is never right while a merge is unresolved, and the state is exactly detectable"*. What is
  built instead refuses on CONTENT and never looks at `MERGE_HEAD`. That is a departure from an approved
  design, so it is flagged here under Principle XVI rather than quietly resolved, it was put to
  `spec-fidelity` with the GM's request verbatim, and it is raised with the GM in the same report that
  says the feature works.

  The reason for the departure: the state rule refuses the correct command. The end of every resolved
  merge is `git add -A` with `MERGE_HEAD` still present, so a state rule fires on the single most common
  correct use of the command it guards - and a guard that fires on correct work teaches a session to
  pattern-match past every guard (this repository's own stated reason for what it declines to enforce).
  The content rule is also strictly wider on the harm: it catches a marker from a `git am`, a patch
  script or a typo, which no merge-state rule sees.

- **D5 - what the content rule cannot see, priced and accepted.** A conflict that leaves NO triple -
  a binary file conflicted on both sides, or a delete/modify - is invisible to this guard, and that
  half of the state rule is genuinely lost. It was not recovered by also refusing while an unmerged
  path exists, because an unmerged path is exactly the state a correctly-resolved text file is in
  until the `add` registers it: such a rule cannot distinguish the resolved file from the unresolved
  one, which is the same defect as the state rule itself. The backstop (FR-006) is where a binary
  conflict is caught instead, and a landing is what it catches it before.
- **D2 - the triple, not any single marker.** `=======` alone is a Markdown underline and appears in this
  repository's own docs; `<<<<<<<` alone appears in prose about merges. Only the three in order are
  unambiguous.
- **D3 - it refuses rather than fixing.** Feature 164's ladder, re-judged per branch by 212, asks whether
  the guard can supply the compliant command. It cannot: the compliant command stages the files that are RESOLVED, and which those
  are is the session's knowledge. This is the same class as `make-only`'s `guard-write` (41 refusals) and
  `guard-file`'s no-marker branch (77) - the class feature 212 described as "the compliant form is an
  Edit carrying a REASON, which only the session has". It is not the largest refusal family in the
  record: `batching` is, at 629, and it stays a refusal for a different reason - no rewrite of one
  command can make a session take fewer turns.
- **D4 - the backstop is a gate phase, not a pytest test**, the shape feature 236 used for the
  house-style delta scan: a scan whose own code never changes would sit unexecuted under testmon through
  exactly the edits it exists to catch. The DETECTOR is shared between the hook and the scan rather than
  written twice, which is feature 212's arrangement for the Makefile recipe-comment hazard
  (`_hm_make.py` behind both the guard and `tests/tooling/test_makefile_recipe_comments.py`); here
  `_hm_conflict.has_conflict` is behind both the hook and `--tracked`.
