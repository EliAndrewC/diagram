# Feature Specification: The Three Rulings

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=165-three-rulings`)

**Created**: 2026-08-30

**Status**: Draft - awaiting `spec-fidelity`

**Input**: [`request.md`](request.md), verbatim and unedited. That file is the authority for this
specification, and it carries the three recommendations the ruling agrees to.

## The feature, in one sentence

Three narrow changes the GM has ruled on, each one already measured and priced in feature 164's
research and each one deliberately left undone there because it was not a session's call to make:
`discard` stops firing on a merge's own conflict-resolution verb, `no-poll` permits the one wait
shape the harness itself documents, and `review-gate` stops refusing the spec-number claim that this
repository's own protocol requires.

## Why this exists (the GM's words - `request.md` is the authority)

- *"I agree with your recommendations, so please implement them for those things."*

The three recommendations are quoted in `request.md`. Each was put to the GM rather than taken,
because each changes what a guard FORBIDS - not what it says or how it says it - and feature 164's
own standard is that a session does not retune a guard's rule on its own judgment.

## What was already measured (feature 164, not repeated here)

| ruling | the evidence | where |
|---|---|---|
| `discard` | 5 firings; 2 legitimate deliberate discards with reasons written, 2 re-issued, and **one `git checkout --ours` during an active merge** | 164 `research.md` R3, and the five firings read out for the GM |
| `no-poll` | fired twice on 2026-08-30 on a backgrounded wait that is the harness's own documented shape, and the only way to wait on a `setsid --fork` run | 164 `research.md` R5 |
| `review-gate` | cost this session the numbers 161 AND 163; the second renumber swept 67 files, 51 of them wrongly | 164 `research.md` R4 |

## Scope, stated exactly

**IN scope**: `scripts/discard-hooks.sh`, `scripts/no-poll-hooks.sh`, `scripts/review-gate.sh` and
their companion suites.

**OUT of scope**: everything else about those three guards. Each change is a NARROWING of one
specific shape; no other command that is refused today becomes permitted, and no rule loses its
escape.

## Requirements

### FR-001 - `discard` does not fire on a merge's own conflict-resolution verb

While a merge is in progress - `MERGE_HEAD` present in the git directory the command names -
`git checkout --ours <path>` and `git checkout --theirs <path>` are allowed, as are their `restore`
equivalents. Everything else is refused exactly as today: the same verbs OUTSIDE a merge, a plain
`git checkout -- <path>` on a dirty file inside one, and every shape the guard refuses now.

The reasoning, recorded at the point of change: during a merge those two flags pick a SIDE of a
conflict, which is the normal way to resolve one; the "uncommitted work" the guard protects is the
session's own edits, and a conflicted file's content is not that. The guard's escape (`DISCARD_OK`)
stays as it is for every other case.

### FR-002 - `no-poll` permits the detached-run wait, and nothing wider

A loop containing `sleep` is permitted when BOTH hold:

- the command is being run in the background (`run_in_background` true in the payload - the hook can
  see it, proved in 164), and
- the loop's condition READS A FILE, in the closed form below - the shape of a wait on a run
  detached with `setsid --fork`, and nothing else:
  - a `grep` whose match target is a PATH OPERAND (not stdin arriving through a pipe), or
  - a `test` / `[` whose operands are a path and its file-test operators (`-e`, `-f`, `-s`, `-r` and
    the like), or
  - an INPUT redirect (`<`) from a path;
  - and the condition contains NO command substitution, NO pipeline into the matcher, and NO output
    redirection. **An output redirection is not a file read**: without that clause,
    `until curl -sf https://host/x > /tmp/out; do sleep 5; done` qualifies, and appending
    `>/dev/null` to any condition at all becomes a general bypass - which is the exact risk the GM
    named when declining the wider option (`spec-fidelity` round 1 caught this in the first draft).

A foreground loop is refused exactly as today. A backgrounded loop whose condition is anything else -
a network call, a bare sleep, a process check - is refused exactly as today. The GM declined the
wider option (permit whenever backgrounded) in the same message that chose this one, on the grounds
that it could be used as a general bypass, and that reason is recorded at the point of change so the
narrowing is not later "simplified" back to the wider form.

`POLL_OK` remains the escape for every wait this does not cover.

### FR-003 - `review-gate` passes the number claim, and only the number claim

A push whose delta is EXACTLY one new `specs/NNN-slug/` directory - every path under it, no file
anywhere else, and no modification to a spec that already exists - is not refused for lacking a
FAITHFUL verdict. Any delta that also touches one other file is judged exactly as today.

This restores the numbering protocol that `CLAUDE.md` requires (*"the moment `/speckit-specify`
writes `spec.md`, commit the new `specs/NNN-slug/` in the clone and run
`scripts/sync-with-main.sh push`"*), which the review gate has been making impossible: a spec written
one minute ago cannot carry a verdict. The reviewed-before-implementation property is untouched,
because no implementation can be present in a delta that contains nothing but one new spec directory.

## Success Criteria

- **SC-001**: with a merge in progress, `git checkout --ours -- <dirty tracked file>` is allowed; without one, the same command is refused.
- **SC-002**: `git checkout -- <dirty tracked file>` is refused whether or not a merge is in progress.
- **SC-003**: a backgrounded `until grep -q X log; do sleep 5; done` is allowed; the same loop in the foreground is refused; a backgrounded `until curl ...; do sleep 5; done` is refused.
- **SC-003a**, the cases that discriminate the closed definition from a loose one: backgrounded `until curl -sf https://host/x > /tmp/out; do sleep 5; done` is REFUSED (an output redirect is not a file read); backgrounded `until ps aux | grep -q make; do sleep 5; done` is REFUSED (a process check through a pipe); backgrounded `until [ -s /tmp/gate.log ]; do sleep 5; done` is ALLOWED.
- **SC-004**: a push whose delta is one new `specs/NNN-slug/` directory passes the review gate with no verdict; the same delta plus one file elsewhere is refused; a modified EXISTING spec with no verdict is refused.
- **SC-005**: each guard's companion suite is green, every new assertion is proved to FIRE by removing the code it guards, and no suite writes fixture events into the real firing log.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| a merge's `--ours`/`--theirs` is not a discard | GM ruling on measured evidence (1 of 5 firings) | FR-001, 164 R3 |
| a backgrounded file-watching wait is permitted; a backgrounded wait on anything else is not | GM ruling; the wider option was priced and declined | FR-002, 164 R5 |
| the number claim passes the review gate | GM ruling; two numbers lost in one session | FR-003, 164 R4 |
