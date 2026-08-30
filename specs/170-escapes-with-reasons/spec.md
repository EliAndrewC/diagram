# Feature 170 - Escapes Carry a Reason, and a Finished Run Is Not "Waiting"

**Status**: specified 2026-08-30. [`request.md`](request.md) is the authority.

## The feature, in one sentence

A guard's escape may never be silent: it records, and it refuses unless the session says WHY - and a
background run that has finished can no longer be reported as still running.

## Why this exists (the GM's words)

*"I don't see why we should ever Permit escapes without recording ... should we just always record
that they happened and force the Claude Code session, which is performing the workaround to specify
why they are doing it? Otherwise, we have no way to audit later when this workaround was taken and
whether the stated reasons were valid use cases."* And: *"In general, I do want our rules to be
enforced rather than unenforced."*

They are right, and the record backs it. Feature 162 retired a refusal because it could show that
refusal was escaped in 62% of its firings - a decision only possible because ONE guard recorded
escapes. Feature 169 made every command escape record. This feature closes the rest: the reason, which
no guard requires today, and the last branch that permits without recording.

The second half comes from a defect another session reported about itself, which the GM asked to have
captured rather than lost: it *"reported the gate as 'waiting' when it had actually failed four hours
earlier because I never saw the notification"*.

## What was measured before specifying

| finding | measured how | result |
|---|---|---|
| no guard requires a reason | read the escape branch of all six command guards | every one accepts a BARE token; all six document "with a reason" in prose only |
| one branch still permits without recording | used `GUARD_EDIT_OK` through `make-only` and read the log | no entry (feature 169 R13, deferred with a sketch) |
| the mirror `cd` half of the reported defect | drove `main-tree-hooks.sh` with the shape that actually occurred | **NOT prevented** - see FR-005. Feature 169's guard needs the `cd` and the write in ONE command; the real incident is a `cd` in one call and the write in the NEXT |
| does a bare `cd` leak across calls in this harness? | `cd /diagram` in one call, `pwd` in the next | **YES** for a path inside the project (`pwd` returned `/diagram`); a path outside it (`/tmp`) is reset with a notice. So the 2026-08-17 trap is live, and path-dependent |
| the missed-notification half | searched the guard tree for anything that notices a finished run | nothing does - `agent-stall-hooks.sh` watches AGENTS, not background commands |

## Scope, stated exactly

**IN**: the reason requirement, universal escape recording, and the finished-run report. **OUT**:
changing what any guard refuses in the first place; the 2026-08-17 read-only `cd` rule (a separate
question the GM has been asked); anything about the review cap.

## Requirements

### FR-001 - an escape without a REASON is refused

Every escape token must be followed by a reason: `TOKEN: <why>` or `TOKEN="<why>"`, with at least 15
characters of it. A bare token is refused, and the refusal shows the compliant form using the token
the session actually reached for.

**This is a refusal and not a rewrite, deliberately.** The ladder in `CLAUDE.md` says a guard that can
produce the compliant command should produce it - and here it cannot, because the missing thing is the
session's REASON, which no tool can supply. That is the same ground on which nine of the Makefile's
ten refusals stand.

**Why 15 characters.** Long enough to exclude `GATE_OK: ok`, short enough that a real reason is never
inconvenienced. The project's existing precedent is the map waiver, which demands 60+ characters; a
command comment is a smaller thing than a map waiver, so this floor is lower. It is a floor on EFFORT,
not a judgment of quality - no tool can grade a reason, and the audit the GM described is a person
reading them.

### FR-002 - every escape records, with its reason as the detail

No branch that permits an escape may be silent. This closes feature 169's R13: `_hookmatch.py`'s
`classify()` returns plain `ok` for a `GUARD_EDIT_OK` command - the same value it returns for a
command that matched nothing - so `make-only-hooks.sh` cannot tell the two apart and records neither.
It returns a distinct verdict for the escape, and the guard records and permits.

The recorded detail is the REASON, not merely the command, because the audit the GM described -
*"whether the stated reasons were valid use cases"* - is reading the reasons.

### FR-003 - the content, environment and make-variable escapes too

The census feature 169 derived has four kinds beyond the command escapes, and none may be exempt from
the reason requirement:

- **content markers** (`SOURCE_EDIT_OK`, `GUARD_EDIT_OK` in edit text): the marker is followed by its
  reason in the text, under the same floor.
- **environment escapes** (`REVIEW_GATE_OK`, `GATE_STAMP_OK`): the variable's VALUE is the reason and
  must meet the floor; an empty or trivial value is refused.
- **the make override** (`REF_OK`): its companion `REF_WHY` already carries the reason, so it is
  brought under the same floor rather than left as the one exception.

### FR-004 - a finished background run cannot be reported as running

When a run the session started has FINISHED and its result has not been surfaced, the session is told
at two points: at the next prompt (one line, as `idle-tests` already does with its verdict) and at
turn end, where a Stop hook says so rather than letting the turn close on a claim that the run is
still going.

**The defect, in the reporting session's own words**: *"I reported the gate as 'waiting' when it had
actually failed four hours earlier because I never saw the notification."* Nothing notices this today:
`agent-stall-hooks.sh` watches subagent transcripts, not background commands, and a completion
notification that is missed is simply gone.

**It reports; it does not block the work.** The message names the run, its exit status and how long
ago it finished. Once acknowledged, it is not reported again.

### FR-005 - the mirror guard must see the session's CWD, not only the command

`main-tree-hooks.sh` (feature 169) refuses a `cd` into the mirror root followed by a write IN THE SAME
COMMAND. That is not the shape the reported incident took, and the session that reported it said so
plainly: *"I let a bare `cd /diagram` leak into the next command"*. Measured here: a bare `cd` into a
path INSIDE the project persists into the following Bash call (`pwd` returned `/diagram`), while a
path outside it is reset with a notice - so the leak is real and path-dependent, and a guard reading
only the command text cannot see it. Driven with the real shape - a commit issued while the cwd is
already the mirror, no `cd` in the command - the guard returns 0.

So the guard reads the session's working directory, which the hook payload already carries (
`clone-sync-hooks.sh` reads the same `cwd` field). When the session's cwd is main's tree and not a
clone under it, a command that writes or commits is refused exactly as if the `cd` were in the command
- and a command that merely ENTERS the mirror gets a free warning saying the cwd is now main's tree,
because at that moment nothing has gone wrong yet and the session is one command away from it.

**This is the correction to a claim this session made to the GM**, who asked directly whether the new
tooling would have prevented the reported error. The honest answer is that it prevents the
single-command shape and not the one that actually happened; FR-005 is what makes the answer yes.

## Success Criteria

- **SC-001**: for every escape token, a bare use is refused with a message showing the compliant form; a use with a reason of 15+ characters is permitted exactly as before.
- **SC-002**: every permitted escape produces a firing-log entry whose detail is the reason - proved by driving each guard, not by reading the source.
- **SC-003**: `make audit` can answer "every escape taken, with its stated reason" from the log alone.
- **SC-004**: a finished, unsurfaced background run is reported at the next prompt and at turn end, with its exit status and age; an acknowledged one is not reported again.
- **SC-005**: no guard refuses anything it did not refuse before, except a bare escape token.
- **SC-006**: a write issued while the session's cwd is main's tree - with no `cd` in the command - is refused; the same write from a clone, and a READ from main's tree, are untouched. Both shapes of the reported incident are fixture cases.
- **SC-007**: `make hooks-test` and `make done` green.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| a bare escape token is REFUSED, not rewritten | the missing thing is the session's reason, which no tool can supply | FR-001 |
| 15 characters | a floor on effort, not a judgment; the map waiver's 60 is the precedent, and a command comment is a smaller thing | FR-001 |
| the recorded detail is the REASON | the GM's audit is reading the reasons, not the commands | FR-002 |
| the finished-run check REPORTS rather than blocks | the failure was a session not KNOWING; blocking a turn would punish the wrong thing | FR-004 |
| the mirror guard reads the session's CWD | the 2026-08-17 leak is real and MEASURED in this harness; a guard reading only the command text cannot see the shape that actually happened | FR-005 |

## Review history

Constitution XVI: reviewed against [`request.md`](request.md) by an independent `spec-fidelity`
subagent before implementation, up to five rounds (raised from three by the GM on 2026-08-30).
