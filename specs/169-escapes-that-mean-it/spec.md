# Feature 169 - Escapes That Mean It

**Status**: specified 2026-08-30. The GM's request is [`request.md`](request.md) and it is the
authority; where this document and that one differ, that one is right.

## The feature, in one sentence

Make a guard's escape mean that a session escaped - not that a command mentioned a token - and fix
the four other tooling defects the same audit turned up.

## Why this exists (the GM's words)

The GM asked what other tooling improvements this session had become aware of, naming hooks and *"our
makefile and its logic about what to run and in what order"*. Five were found and verified by driving
the real guards; the GM answered *"Yes please make these fixes as their own feature, test them out,
and then close out the feature and push back to main when you're done."*

**All five are in scope.** The session had recommended three and offered the other two for a separate
decision; the GM's reply answers the message as a whole, and narrowing it here would be a session
quietly scaling down work that was asked for. FR-005 in particular is a hook the GM priced and
DECLINED on 2026-08-17, so it is built only in the exact shape `CLAUDE.md` names as the condition for
reopening - see that requirement for the wording.

## What was measured before specifying

Every finding below was produced by driving the real hook with a real payload, not by reading code.

| finding | how it was measured | result |
|---|---|---|
| escape tokens match mentions | `grep -rn MEASURE_OK scripts/` through `measure-hooks.sh` | one `escaped` entry logged; exit 0 |
| the same, four more guards | a `grep` payload through `gate`, `no-poll`, `discard`, `no-branch` | 1 entry each |
| the state reset | `measure-hooks.sh:100` `: > "$STATE"`; `gate-hooks.sh:69` `rm -f "$STATE"` | both on the escape branch |
| the live census is polluted | 24 of 113 entries name `specs/900-x` / `specs/901-new` | `test-review-gate.sh` has no `GUARD_LOG_DIR` |
| the missing slug | `make audit` prints `guard-file rules={'reminded': 56}` | `guard-file-hooks.sh:62` passes no 4th field |
| `sync-in`'s false success | observed twice on 2026-08-30 with a stray commit in the mirror | printed `clone synced with GitHub main`, changed nothing |

## Scope, stated exactly

**IN**: the five findings, and nothing else. **OUT**: the gate's rising median (the GM handed it to a
different session on 2026-08-30 and that has not changed); any further guard the audit did not find;
any change to what a guard REFUSES, except where a requirement below says so explicitly.

## Requirements

### FR-001 - an escape token is an INVOCATION, not a mention

A guard treats its escape token as used only when the session actually put it in the command as an
escape - not when the command greps for it, quotes it in a commit message, or carries it inside a
heredoc that is editing a document about guards. All nine tokens are covered: `GATE_OK`,
`MEASURE_OK`, `POLL_OK`, `DISCARD_OK`, `NO_BRANCH_OK`, `PAIR_OK`, `REVIEW_GATE_OK`, `SOURCE_EDIT_OK`,
`GUARD_EDIT_OK`.

**The escape is still checked FIRST.** `CLAUDE.md`'s rule - *"check the ESCAPE FIRST or the guard
cannot be repaired through the channel it guards"* - is not weakened here: what changes is how the
token is MATCHED, not when. A guard that cannot be repaired through its own channel is a worse defect
than the one being fixed.

**The matcher is the one that already exists.** `scripts/_hookmatch.py` strips heredoc bodies and
quoted regions for exactly this reason, and every blocking decision in the repository already routes
through it. The escape branches are the last substring tests left.

### FR-002 - a mention must not disarm a guard

`measure-hooks.sh` clears its repeat-measurement state on the escape branch, and `gate-hooks.sh`
removes its state file. Under FR-001's matching those fire only on a real escape, which is the
correct behavior and is preserved. What must not survive is the measured case: a command that only
mentions the token silently resetting the counter that decides whether the NEXT expensive measurement
is refused.

This is the half that makes FR-001 a correctness fix rather than a reporting one.

### FR-003 - no suite writes fixture firings into the live census

`scripts/test-review-gate.sh` isolates `GUARD_LOG_DIR` for the whole file, as the other ten suites do
since features 162/164/168. The census is the input to every future tuning decision, and 24 of its
113 entries are currently fixtures from this one suite.

**And the rule is enforced rather than remembered**: a test asserts that every `test-*.sh` whose
guard records also isolates the log. Feature 168 added the isolation to nine suites by hand and
missed this one, because `review-gate.sh` is not a `*-hooks.sh` file - a hand-list again.

### FR-004 - every recording branch names its rule, and the test covers every guard

`guard-file-hooks.sh`'s `reminded` branch passes no rule slug, so the census cannot tell its three
branches apart. It gets one. The static test in `tests/tooling/test_guard_firing_log.py` that was
supposed to catch this checked a hand-written `multi` set which omitted `guard-file`, `discard`,
`no-branch`, `source-block`, `batching`, `readme`, `house-style` and `agent-stall`; it is DERIVED
instead - every guard with more than one `guard_log` call must give every call a slug.

The reminder's own volume - 56 firings in one day - is REPORTED by this feature and not otherwise
changed. It is free (`additionalContext`, no round trip), the question of whether it should be once
per file per session is a real one, and answering it is a decision for the GM with the census in
front of them rather than a change to make silently.

### FR-005 - `sync-in` says so when the mirror is not main

`scripts/sync-with-main.sh sync-in` reports the mirror's true state instead of printing
`clone synced with GitHub main` when it did nothing. When the mirror's HEAD is not on its
`origin/main` - a commit made in main's tree, the trap below - it says so, names the commit, and says
the clone was not merged and why.

`CLAUDE.md` already documents this behavior (*"A hand commit in `/diagram` stops the next sync-in
(mirror cannot fast-forward)"*), so this requirement makes the code match the documentation rather
than adding a rule. Observed failing twice on 2026-08-30.

**It reports; it does not repair.** The mirror's working tree may be the only copy of that work, and
whose work it is cannot be known from another session - the recovery belongs to the session that made
the commit, exactly as feature 168's refusal already says.

### FR-006 - a `cd` into the MIRROR ROOT that then writes is refused

A single Bash command that changes directory into the mirror root (`/diagram`, derived from git as
everything else here is - never hardcoded) and then writes, commits, or otherwise modifies state is
refused, naming the leak and the `git -C` rule. Escape: `MAIN_TREE_OK` with a reason, because reading
in main is legitimate and so, rarely, is render-sync.

**This hook was priced and DECLINED once (GM 2026-08-17), and this requirement is built only because
`CLAUDE.md` states the exact condition for reopening it**: *"Reopen only with a mechanism that would
catch a single-`cd` command whose section header names the other tree - that is the shape to beat,
and neither candidate above does."* The two candidates declined then were (a) demanding `git -C` on
every git call, which fires on nearly every correct command, and (b) firing when one command names
both a non-clone path and `.clones/`, which would have caught neither incident.

The shape specified here is narrower than both and is measured against the two real incidents of
2026-08-30, each of which was a bare `cd` into the mirror root followed by an edit and a commit in
the same or the next command. It would have caught both. It fires on almost nothing legitimate,
because a session never writes in main - that is already enforced three other ways
(`webapp/mainguard.py`, the Makefile's `guard`, `settlement._assert_not_main_tree`), none of which
sees a git commit.

**What it does NOT do**: it does not fire on a read-only `cd /diagram`, on `git -C /diagram <read>`,
or on any command naming a clone. The declined candidate (a) is not revived - no rule here demands
`git -C` on anything.

## Success Criteria

- **SC-001**: for each of the nine tokens, a command that MENTIONS it (a grep, a quoted commit message, a heredoc body) produces no `escaped` entry and no state change; a command that USES it as an escape still escapes exactly as before.
- **SC-002**: a mention of `MEASURE_OK` or `GATE_OK` leaves the guard's state file untouched, proved by driving the guard to the edge of its threshold, sending a mention, and observing that the next expensive command is still refused.
- **SC-003**: running every guard suite leaves the live census with zero new entries, and a test fails if a recording guard's suite stops isolating the log.
- **SC-004**: every `guard_log` call in every guard passes a rule slug, proved by a DERIVED check over the guard tree rather than a hand-written list.
- **SC-005**: with a stray commit in the mirror, `sync-in` reports it, names the commit, and does not claim the clone was synced; with a clean mirror it behaves exactly as it does today.
- **SC-006**: a command that `cd`s into the mirror root and then writes or commits is refused and names the `git -C` rule; a read-only `cd` there, a `git -C` read, and any command naming a clone are untouched. Both real incidents of 2026-08-30 are fixture cases.
- **SC-007**: `make hooks-test` and `make done` are green, and no guard refuses, permits or corrects anything it did not before except where a requirement above says so.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| all five findings are in scope | the GM's reply answers the whole message; narrowing would be a session scaling down asked-for work | Why this exists |
| the escape stays checked FIRST; only the MATCH changes | a guard that cannot be repaired through its own channel is a worse defect | FR-001 |
| the reminder's 56/day volume is reported, not changed | it is free, and the fix is a decision for the GM with the census in hand | FR-004 |
| `sync-in` reports, never repairs | the mirror's working tree may be the only copy, and whose it is cannot be known from outside | FR-005 |
| the mirror-`cd` hook is built in the narrowest shape only | `CLAUDE.md` names that shape as the condition for reopening a hook it declined in 2026-08-17 | FR-006 |
| the gate's rising median stays out | handed to a different session by the GM | Scope |

## Review history

Constitution XVI: this spec is reviewed against [`request.md`](request.md) by an independent
`spec-fidelity` subagent before implementation.
