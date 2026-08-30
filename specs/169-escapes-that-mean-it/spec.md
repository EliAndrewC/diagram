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
quietly scaling down work that was asked for. **FR-006** is the sensitive one - it stands next to a
hook the GM priced and DECLINED on 2026-08-17 - and the honest account of how it relates to that
decline is in FR-006 itself, including the part the GM has not yet been told.

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
| the unguarded write in main (FR-006) | the two incidents of 2026-08-30, each a bare `cd` into the mirror root followed by an edit and a commit | neither commit was seen by `webapp/mainguard.py`, the Makefile's `guard` or `settlement._assert_not_main_tree` - all three are in-process or `make`-time and none sees a `git commit` |

## Scope, stated exactly

**IN**: the five findings, and nothing else. **OUT**: the gate's rising median (the GM handed it to a
different session on 2026-08-30 and that has not changed); any further guard the audit did not find;
any change to what a guard REFUSES, except where a requirement below says so explicitly.

## Requirements

### FR-001 - an escape token is an INVOCATION, not a mention

A guard treats its escape token as used only when the session actually put it in the command as an
escape - not when the command greps for it, quotes it in a commit message, or carries it inside a
heredoc that is editing a document about guards. All ELEVEN tokens are covered - the ten that exist plus `MAIN_TREE_OK`, which FR-006 creates:
`GATE_OK`, `MEASURE_OK`, `POLL_OK`, `DISCARD_OK`, `NO_BRANCH_OK`, `PAIR_OK`, `REVIEW_GATE_OK`,
`SOURCE_EDIT_OK`, `GUARD_EDIT_OK`, `HOST_GIT_OK`, `MAIN_TREE_OK`.

**`HOST_GIT_OK` was missed by this spec's own first two drafts** and found by the round-2 review,
which noticed that its own audit command would have disarmed the guard it was auditing.
`repo-safety-hooks.sh` matches it against the RAW command while the sanitized copy it built fourteen
lines earlier - heredocs and quoted strings blanked, for exactly this reason - sat unused. It guards
git writes against `/host-l7r-repo`, the GM's own repository, and it is the one escape in the file
that stands beside two rules that deliberately have none. The GM's request says *"every guard's
escape token"*, so an exclusion here would be theirs to approve, not this feature's.

**`pair-hooks.sh`'s AGENT-PROMPT branch is deliberately OUT**, and this is the one place the rule
does not reach. `PAIR_OK` on a Bash command routes through the matcher like the rest; the same token
in a subagent's dispatch PROMPT does not, because a prompt is prose with no command grammar - there
is no "invocation position" in a sentence, and the matcher blanks quoted regions, which prose carries
for ordinary reasons. Converting it would trade a known false-permit for an unknown false-refusal on
the guard that decides whether a settlement review is owed. The exclusion is stated at the point of
change as well as here.

**A feature whose whole purpose is that an escape means a session escaped must not ship an escape
exempt from its own rule.** `MAIN_TREE_OK` is matched as an invocation through `_hookmatch.py` like
the other nine, and records like the other nine (feature 168: every acting branch records, with a
rule slug).

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

**THIS IS A NEW GUARD, AND IT DOES NOT MEET THE REOPENING CONDITION `CLAUDE.md` STATES.** The first
draft of this spec claimed it did, and so did the summary the GM approved - that claim was wrong, and
the correction is owed to them (see below).

What `CLAUDE.md` actually says, and why the difference matters. The 2026-08-17 rule exists for a
failure that is not this one: *"actually WRITING in main is already caught three ways
(`webapp/mainguard.py`, the Makefile's `guard`, `settlement._assert_not_main_tree`). This rule
prevents the quieter failure those guards cannot see - a read-only diagnostic that confidently
reports the wrong tree, which is worse than an error because it looks like an answer."* Its reopening
condition - *"a mechanism that would catch a single-`cd` command whose section header names the other
tree"* - names that read-only case. **FR-006 explicitly excludes read-only `cd`**, and it could not
read a section header in any event, since a header lives in the model's prose and never reaches the
command payload. So the shape to beat is still unbeaten, and **the 2026-08-17 rule remains
deliberately unenforced after this feature ships.**

What FR-006 is, stated truthfully: a NEW guard against an unguarded WRITE or COMMIT in the mirror
root. That gap is real and measured - the two incidents of 2026-08-30 were each a `cd /diagram`
followed by an edit and a commit, and NONE of the three guards named above sees a git commit, which
is exactly why both happened. It is also neither of the two candidates declined in 2026-08-17:
candidate (a) demanded `git -C` on every git call (no rule here demands that), and candidate (b)
fired when one command named both a non-clone path and `.clones/` (FR-006 needs no second path). It
therefore does not contradict that decline; it sits beside it, guarding something else.

**The GM is owed this correction, and the close-out report must carry it.** Their approval of finding
5 was given against a request summary that asserted this shape *"is the condition CLAUDE.md set for
reopening it"*. That was false. `request.md` is the GM-facing verbatim record and is not edited, so
the correction is delivered in the report that closes this feature, in terms plain enough for the GM
to withdraw item 5 if the true basis does not persuade them.

**What it does NOT do**: it does not fire on a read-only `cd /diagram`, on `git -C /diagram <read>`,
or on any command naming a clone. The declined candidate (a) is not revived - no rule here demands
`git -C` on anything.

## Success Criteria

- **SC-001**: for each of the eleven tokens (`HOST_GIT_OK` and `MAIN_TREE_OK` included; `pair`'s agent-prompt branch excluded, per FR-001), a command that MENTIONS it (a grep, a quoted commit message, a heredoc body) produces no `escaped` entry and no state change; a command that USES it as an escape still escapes exactly as before.
- **SC-002**: a mention of `MEASURE_OK` or `GATE_OK` leaves the guard's state file untouched, proved by driving the guard to the edge of its threshold, sending a mention, and observing that the next expensive command is still refused.
- **SC-003**: running every guard suite leaves the live census with zero new entries, and a test fails if a recording guard's suite stops isolating the log.
- **SC-004**: every `guard_log` call in every guard passes a rule slug, proved by a DERIVED check over the guard tree rather than a hand-written list.
- **SC-005**: with a stray commit in the mirror, `sync-in` reports it, names the commit, and does not claim the clone was synced; with a clean mirror it behaves exactly as it does today.
- **SC-006**: a command that `cd`s into the mirror root and then writes or commits is refused and names the `git -C` rule; a read-only `cd` there, a `git -C` read, and any command naming a clone are untouched. Both real incidents of 2026-08-30 are fixture cases.
- **SC-007**: the close-out report to the GM states plainly that FR-006's original warrant was wrong - that this guard does NOT meet `CLAUDE.md`'s reopening condition and the 2026-08-17 rule stays unenforced - so they can withdraw item 5 if the true basis does not persuade them. It is the one requirement here that a test cannot tick.
- **SC-008**: `make hooks-test` and `make done` are green, and no guard refuses, permits or corrects anything it did not before except where a requirement above says so.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| all five findings are in scope | the GM's reply answers the whole message; narrowing would be a session scaling down asked-for work | Why this exists |
| the escape stays checked FIRST; only the MATCH changes | a guard that cannot be repaired through its own channel is a worse defect | FR-001 |
| the reminder's 56/day volume is reported, not changed | it is free, and the fix is a decision for the GM with the census in hand | FR-004 |
| `sync-in` reports, never repairs | the mirror's working tree may be the only copy, and whose it is cannot be known from outside | FR-005 |
| the mirror-`cd` hook is a NEW guard, not a reopening | it does NOT meet `CLAUDE.md`'s stated reopening condition, which names the read-only mislabeled-tree diagnostic this hook excludes; the 2026-08-17 rule stays unenforced, and the GM is told so at close-out because their approval rested on the opposite claim | FR-006 |
| the gate's rising median stays out | handed to a different session by the GM | Scope |

## Review history

Constitution XVI: this spec is reviewed against [`request.md`](request.md) by an independent
`spec-fidelity` subagent before implementation.
