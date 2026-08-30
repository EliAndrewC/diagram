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
| branches that permit without recording | used `GUARD_EDIT_OK` through `make-only` and read the log; then grepped every escape site for `guard_log` | **TWO**, not one. `make-only` (169 R13), and `GATE_STAMP_OK` at `sync-with-main.sh:231`, which prints its bypass to stderr and logs nothing - that file contains no `guard_log` call at all and never sources `_guardlog.sh`. Found by the round-1 review; I had specified only the first |
| the mirror `cd` half of the reported defect | drove `main-tree-hooks.sh` with the shape that actually occurred | **NOT prevented** - see FR-005. Feature 169's guard needs the `cd` and the write in ONE command; the real incident is a `cd` in one call and the write in the NEXT. What 169 added for that shape is after-the-fact DETECTION, not prevention: `sync-with-main.sh` dies on a mirror ahead of GitHub, and `clone-sync-hooks.sh` names the stray commit - both only once the commit exists |
| does a bare `cd` leak across calls in this harness? | `cd /diagram` in one call, `pwd` in the next | **YES** for a path inside the project (`pwd` returned `/diagram`); a path outside it (`/tmp`) is reset with a notice. So the 2026-08-17 trap is live, and path-dependent |
| the missed-notification half | searched the guard tree for anything that notices a finished run | nothing does - `agent-stall-hooks.sh` watches AGENTS, not background commands |

## Scope, stated exactly

**IN**: the reason requirement, universal escape recording, and the finished-run report. **OUT**:
changing what any guard refuses in the first place; the 2026-08-17 read-only `cd` rule (a separate
question the GM has been asked); anything about the review cap.

## Requirements

### FR-001 - an escape without a REASON is refused

Every escape token must be followed by a reason: `TOKEN: <why>` or `TOKEN="<why>"`, of **at least two
words and eight characters**. A bare token is refused, and the refusal shows the compliant form using
the token the session actually reached for.

**This is a refusal and not a rewrite, deliberately.** The ladder in `CLAUDE.md` says a guard that can
produce the compliant command should produce it - and here it cannot, because the missing thing is the
session's REASON, which no tool can supply. That is the same ground on which nine of the Makefile's
ten refusals stand.

**Why two words and eight characters, and why NOT a longer character floor.** The first draft said 15
characters and justified it by the map waiver's 60 - a mechanism this repository RETIRED
(`dev/gate.md`: *"Waivers are gone, and the doctrine they carried is not"*), so the justification cited
something that no longer exists, and nothing enforces a character floor anywhere today. The round-1
review also put the real objection: a 15-character floor REFUSES A TRUE SHORT REASON. *"CI is down"* is
ten characters and is a perfectly good reason; the GM's request licenses demanding a reason, not
refusing a short true one.

Two words and eight characters excludes exactly what it should - a bare token, `GATE_OK: ok`,
`MEASURE_OK: yes` - and admits *"CI is down"*. It is a floor on EFFORT, not on quality: no tool can
grade a reason, and the audit the GM described (*"whether the stated reasons were valid use cases"*) is
a person reading them.

### FR-002 - every escape records, with its reason as the detail

No branch that permits an escape may be silent. There are TWO such branches, and the second was found
by the round-1 review after this requirement had already been drafted around the first:

1. **`sync-with-main.sh:231`** permits a `GATE_STAMP_OK` bypass of the green-gate rule - the rule that
   nothing is pushed which a gate did not see - and prints to stderr. The file has no `guard_log` call
   anywhere and never sources `_guardlog.sh`, so this escape is invisible to `make audit`. It is also
   the most consequential of the eleven, which is what makes its silence worst.
2. **`make-only`** (feature 169 R13): `_hookmatch.py`'s
`classify()` returns plain `ok` for a `GUARD_EDIT_OK` command - the same value it returns for a
   command that matched nothing - so `make-only-hooks.sh` cannot tell the two apart and records
   neither. It returns a distinct verdict for the escape, and the guard records and permits.

The recorded detail is the REASON, not merely the command, because the audit the GM described -
*"whether the stated reasons were valid use cases"* - is reading the reasons.

### FR-003 - the content, environment and make-variable escapes too

The census feature 169 derived has four kinds beyond the command escapes. **Three of them owe a
reason**; the fourth, `not-an-escape` (`SWEEP_OK`, `REMOTE_OK`), owes nothing because those are
Makefile macros that permit nothing at all - there is no workaround to explain. The first draft of this
requirement said "four kinds" and then listed three, which is the shape this review exists to catch:

- **content markers** (`SOURCE_EDIT_OK`, `GUARD_EDIT_OK` in edit text): the marker is followed by its
  reason in the text, under the same floor.
- **environment escapes** (`REVIEW_GATE_OK`, `GATE_STAMP_OK`): the variable's VALUE is the reason and
  must meet the floor; an empty or trivial value is refused.
- **the make override** (`REF_OK`): its companion `REF_WHY` already carries the reason, so it is
  brought under the same floor rather than left as the one exception.

### FR-003b - the one branch the matcher does not reach still owes a reason

`pair-hooks.sh`'s AGENT-PROMPT branch permits a `settlement-review` dispatch on a bare `PAIR_OK` in the
prompt. Feature 169 deliberately left it out of the MATCHER (a prompt is prose with no command
grammar) and the round-3 review adjudicated that exclusion legitimate - but that was about how the
token is FOUND, and says nothing about whether a reason is owed. **A reason is owed.** The GM's rule is
*"always record that they happened and force the session ... to specify why"*, with no exception for
prose, and the GM's own documented form for this very token is `PAIR_OK="<reason>"`. So the branch
keeps its prose matching and gains the reason floor: a bare `PAIR_OK` in a dispatch prompt is refused
like any other bare token.

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
| two words and eight characters | excludes a bare token and `GATE_OK: ok` while admitting a true short reason like "CI is down"; the 15-character first draft would have refused that, and justified itself by the RETIRED map-waiver rule | FR-001 |
| the recorded detail is the REASON | the GM's audit is reading the reasons, not the commands | FR-002 |
| the finished-run check REPORTS rather than blocks | the failure was a session not KNOWING; blocking a turn would punish the wrong thing | FR-004 |
| the mirror guard reads the session's CWD | the 2026-08-17 leak is real and MEASURED in this harness; a guard reading only the command text cannot see the shape that actually happened | FR-005 |

## Review history

Constitution XVI: reviewed against [`request.md`](request.md) by an independent `spec-fidelity`
subagent before implementation, up to five rounds (raised from three by the GM on 2026-08-30).
