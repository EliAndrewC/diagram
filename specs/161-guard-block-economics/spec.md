# Feature Specification: What a Guard Block Costs, and What It Saves

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=161-guard-block-economics`)

**Created**: 2026-08-30

**Status**: Draft - awaiting `spec-fidelity`

**Input**: [`request.md`](request.md), verbatim and unedited. That file is the authority for this
specification.

## The feature, in one sentence

Two guards the GM keeps seeing fire are re-tuned against what they have actually cost and saved,
measured from this project's own transcripts and run log: the expensive-measurement budget drops so
the SECOND run in a streak is blocked instead of the third, and the reminder it carries is moved to
the FIRST successful run where it costs no round trip; the `make quick` + `make done` rejection is
replaced by tooling that combines the two instead of bouncing the command back; every stale duration
those messages quote is replaced by one derived from the recorded run log; and from now on every
guard firing and every escape is recorded, so the next "should we tune this guard?" is answered from
a total rather than an impression.

## Why this exists (the GM's words - `request.md` is the authority)

- *"Given how expensive that is, should we make it so we start blocking at 2 in a row instead of 3 in
  a row?"*
- *"should the output of the FIRST successful expensive measurement emit a reminder about this so
  that you don't need to wait until the first failure to get this reminder message ... That might
  inform future sessions before they see the failure."*
- *"So does mean our tooling should detect when both are being run and then combine them into `make
  done` automatically instead of rejecting?"*
- *"Also I think those numbers for `make quick` are wrong and outdated, though the attempt to get a
  savings is still worthwhile."*
- *"We could also have `make quick` save off its results so that if it succeeds and then `make done`
  runs immediately after it then `make done` just skips the quick tests instead of having to bounce
  this back, since bouncing back a command forces another pass through the LLM engine, which also
  takes time."*
- *"And possibly add some other automated checks as well?"*

The last sentence of the request states the cost model the whole feature is judged against: **a
bounced-back command forces another pass through the LLM engine**. A block is not free. It is worth
paying only when the run it prevents costs more than the round trip it spends, and this project's own
transcript profile says model turn latency is 78% of wall time.

## What was measured before anything was specified

Constitution XII and the GM's own rule (*"a rate that will not move is a measurement request, not a
discovered law"*): every number below is measured, and the method is in
[`research.md`](research.md). Nothing here is an estimate.

| measurement | value | source |
|---|---|---|
| `make done` (green), median of the last 25 recorded runs | **137 s** | `dev/run-log/` |
| `make done` (green), median 2026-08-29 | **111 s** | `dev/run-log/` |
| `make done` (green), median 2026-08-27 | 35 s | `dev/run-log/` |
| scope state while the guard message says "with scope locked" | **unlocked since 2026-08-27** | `dev/switches.json` |
| `make quick`, warm (testmon, nothing changed) | **4.1 s** | measured in this clone |
| `make quick`, cold (no testmon database) | **25.3 s** | measured in this clone |
| `make lint` + `make format` + `make typecheck` | **1.8 s total** (1.0 + 0.1 + 0.65) | measured in this clone |
| quick+done blocks in this project's transcripts | **37** | transcript replay |
| of those, escaped with `GATE_OK` in the very next call | **23 (62%)** | transcript replay |
| of those, the session ran a make target instead | 5 | transcript replay |
| expensive-measurement blocks in the transcripts | 9 | transcript replay |
| of those, escaped or re-run in the very next call | **5 (4 `MEASURE_OK`, 1 plain)** | transcript replay |
| expensive measurements blocked, simulated at budget 2 / 1 | 30 / **56** | transcript replay |

Three of the GM's premises are confirmed by this and one is corrected:

1. **The numbers in the `gate-hooks.sh` message are wrong**, as the GM suspected, and wrong twice
   over: the scope has been UNLOCKED since 2026-08-27, so "~70 s with scope locked" describes a
   configuration nobody has been in for three days, and the gate it describes now costs 111-137 s.
2. **The saving is real but small**: the work a chained `make quick && make done` actually
   duplicates is one warm `quick` (4.1 s) plus the three static phases (1.8 s), not "~30 s of the
   same tests". The 25.3 s figure is a COLD quick (a fresh clone, no testmon database).
3. **The block costs more than it saves**: 23 of 37 firings were escaped in the very next call, so
   the guard spent a round trip and prevented nothing 62% of the time. This is the failure mode the
   project's own doctrine names: *"a guard that fires on correct work teaches a session to bypass
   every guard"*.
4. **Corrected**: the expensive-measurement guard is NOT firing a lot in absolute terms - **9**
   firings across the whole recorded history. What the GM has been seeing is mostly the quick+done
   guard (**37**) and, above both, `batching-hooks.sh` (**119**). Only the two the GM named are in
   scope here. Every count in this paragraph, and every row in the table above whose source is the
   transcript replay, is `measure/replay.py`'s and may be no other figure (the other rows carry
   their own sources - the run log, `dev/switches.json`, or a timing taken in this clone): the first draft of this paragraph carried three ad-hoc
   numbers from an exploratory pass (8, 38, 146) while the table beside it carried the replay's, and
   `spec-fidelity` had to find it twice - a stale number nobody noticed, inside the spec whose
   subject is stale numbers nobody noticed.

## Scope, stated exactly

**IN scope**: `scripts/measure-hooks.sh`, `scripts/gate-hooks.sh`, their companion test scripts, the
`quick` and `done` targets of `.claude/skills/diagram/Makefile`, a new shared guard-firing log with a
census that `make audit` prints, and the stale durations quoted in any guard message.

**OUT of scope**: what `make done` itself runs - which phases exist, the ORDER they run in, its
scope rules, its coverage floors; `batching-hooks.sh`, `pair-hooks.sh` and the other ten guards,
which gain nothing here, not even the firing log; the diagram engine; anything about maps.

## Requirements

### FR-001 - the budget drops by one

`scripts/measure-hooks.sh` blocks the SECOND expensive measurement in a streak rather than the third
(`BUDGET` 2 -> 1). Everything else about the state machine is unchanged: an engine edit, a `git
commit` or `MEASURE_OK` still resets it, a test edit still does not, and the block still clears the
counter so it can never deadlock.

The block message no longer says "the third".

**What this costs, recorded rather than hidden** (the project's rule for accepting a limitation): the
transcript replay says this roughly doubles the firings, 30 -> 56 over the recorded history, and
5 of the 9 real firings so far ended with the measurement running anyway. The GM asked for the
tighter budget knowing the shape of the trade; FR-002 is what makes it pay, by teaching before the
block rather than at it. `BUDGET` remains a one-line environment override
(`MEASURE_BUDGET`) so the setting can be moved again from evidence rather than by editing logic.

### FR-002 - the reminder arrives on the FIRST run, not the first failure

When an expensive measurement (`make test-full`, `make done FULL=1`) completes as the FIRST in a
streak, the session is told - in the output it is already reading, spending NO extra round trip -
what the guard would otherwise tell it later: measure once at the end of a batch, use the cheap loop
(`make quick`, `make test-file`, `make cov-file`) between edits, and what the next run will cost.

The reminder must reach the model, not only the human transcript. It is emitted once per streak (the
first run), never on every run - a reminder that repeats is a reminder that is skimmed.

### FR-003 - `quick` and `done` in one command are COMBINED, not rejected

Whenever ONE command invokes both targets - as one make call or as two chained calls - the tooling
combines them instead of bouncing the command back. Both of these run the gate exactly once, with no
`quick` test run and no refusal:

- `make quick done` (one invocation, both goals)
- `make quick && make done` (two invocations in one command) - the shape in the message the GM
  quoted, and the shape behind every one of the 37 recorded firings

The session is told in one line what was combined, so its next turn reads the output it actually
got. The `gate-hooks.sh` block for "quick and done in ONE command" is RETIRED together with the
companion test vectors that assert it fires; the `-k`-subset block in the same file is a different
rule and is untouched.

**This is possible without a refusal, and it was proved before it was specified**: a `PreToolUse`
hook in the installed harness may return a REWRITTEN command (`updatedInput`) and may speak to the
model on an allowed call (`additionalContext`), both at exit 0 and both costing no round trip. The
verification is in `plan.md`. Every guard in this repository is built out of exit code 2, which is
the only mechanism that costs the round trip the GM is objecting to.

**The one thing the rewrite may never do is guess.** Where the command does not match a shape the
rewrite can rebuild exactly - a pipe, a redirect, a subshell wrapping the pair, a `make quick`
carrying arguments (`ALL=1`, `FILE=`) whose meaning the rewrite would have to interpret - the
command is allowed THROUGH UNCHANGED and unblocked. The cost of that fallback is one warm `quick`
(4.1 s); the cost of a wrong rewrite is a session's command, which is why the fallback is never a
refusal.

### FR-004 - what `make quick` can hand to `make done`, measured

The GM's proposal - have `quick` save its results so a following `done` skips them - is answered with
the measurement rather than with an opinion, and the answer differs by which part of `quick` is meant:

- **The test run cannot be transferred, and honoring the proposal literally would strip a gate
  property the GM did not ask to weaken**: `done`'s test phase runs the WHOLE tests tree UNDER
  COVERAGE, while `quick` runs a testmon-selected subset with `--no-cov`. Deselecting from `done` the
  tests `quick` already ran would remove their coverage with them - the effect this Makefile already
  records from a measurement ("a deselected test takes its coverage with it", a module at 100%
  dropping to 52% on unchanged code) - and would make `uncovered-in-diff.py` and the three floors
  report holes that are not there. The alternative that WOULD make the proposal work literally -
  having `quick` produce coverage data of its own so its subset genuinely transfers - is priced in
  `research.md` R4 and rejected on its own numbers, not by assertion.
- **The static phases can be transferred and are worth 1.8 s**: `lint`, `format` and `typecheck`
  cost 1.0 + 0.1 + 0.65 s.

**Therefore no cross-process stamp is built - and that decline stands only because FR-003 covers
BOTH invocation shapes.** With the chained form combined, no duplicated `lint`/`format`/`typecheck`
run remains for a stamp to skip: the session never spends them twice, which is a better outcome than
spending them and then skipping them. Were FR-003 to cover only the single-invocation form, this
requirement would have to specify the stamp instead, because it would then be the only mechanism
delivering any part of *"the attempt to get a savings is still worthwhile"*. That conditional is the
requirement, not a note on it.

The declined stamp, its measured value (1.8 s of a 137 s gate, 1.3%) and the reason it is not free
(a second content key that would have to cover `tests/` and every configuration file the three
phases read, whose failure mode is a silently skipped gate phase) are recorded in `research.md` R4
under the project's rule for documenting an accepted limitation and the alternatives declined.

### FR-005 - no guard message states a hardcoded duration

Every duration a guard message quotes is DERIVED at firing time from `dev/run-log/` - the median of
the recent recorded runs of that target - and says so, or it is not stated at all. Where the log has
no entries, the message omits the number rather than inventing one.

This is the general fix for the specific defect the GM caught: a number written into a message in
August is wrong in September, and nothing tells anybody. Any remaining hardcoded duration in a guard
message or in a Makefile prompt is corrected in the same pass.

### FR-006 - a guard firing is recorded, for the two guards this feature touches

Every block, rewrite, reminder and escape (`GATE_OK`, `MEASURE_OK`) issued by **`measure-hooks.sh`
and `gate-hooks.sh` - and no other guard** - appends one file to a firing log: one file per entry,
never an appended shared file, for the same reason `dev/run-log/` is a directory (concurrent clones
conflict on every shared append).

`make audit` gains a census over that log: firings, escapes, and the escape rate per guard. The
question the GM had to open this session with - *"I notice I've been seeing a lot of this ... over
time"* - is then a query, not an archaeology run over 715 MB of transcripts, and the next tuning of
either guard starts from a total.

The log format and the census are designed so that adding a third guard later is one line in that
guard, but **the other ten guards are not touched by this feature**. `research.md` R6 records what
the transcript replay found about them - `batching-hooks.sh` fired 119 times, more than every other
guard combined - and that is put to the GM as its own question rather than folded in here.

## Success Criteria

- **SC-001**: a session that runs `make test-full` twice in a streak is blocked on the second, and
  the block message does not say "third".
- **SC-002**: the first successful expensive measurement of a streak carries the batching reminder,
  and the second identical run does not repeat it.
- **SC-003**: `make quick done` runs the gate exactly once and no `quick` test run, and is not
  blocked by any hook.
- **SC-004**: `make quick && make done` runs the gate exactly once and no `quick` test run, and is
  not blocked by any hook - the same standard as SC-003.
- **SC-005**: no guard message in `scripts/` contains a hardcoded second-count that describes a make
  target; a proving test fails if one is reintroduced.
- **SC-006**: after a block and after an escape, `dev/guard-log/` has one more entry, and `make
  audit` counts it.
- **SC-007**: every companion test (`scripts/test-measure-hooks.sh`, `scripts/test-gate-hooks.sh`)
  is green, and each retired assertion is removed rather than left passing vacuously.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| block the second expensive measurement, not the third | GM ruling, taken with the measured cost stated | FR-001, `research.md` R1 |
| teach on the first run, block later | measured (a reminder costs 0 round trips; a block costs 1) | FR-002, `research.md` R2 |
| retire the quick+done block rather than tighten it | measured (23 of 37 firings escaped in the next call) | FR-003, `research.md` R3 |
| no cross-process stamp for the static phases | declined alternative, priced at 1.8 s | FR-004, `research.md` R4 |
| durations derived from the run log | measured (the quoted numbers were 2-4x wrong and described a scope nobody was in) | FR-005, `research.md` R5 |
| one file per guard firing, never a shared append | reuses the recorded reason `dev/run-log/` is a directory | FR-006 |
| the firing log covers two guards, not twelve | `spec-fidelity` round 1: ten more guards and ten more companion tests is a separate question for the GM | FR-006, `research.md` R6 |
| having `quick` emit coverage so its subset transfers | declined alternative, priced | `research.md` R4 |

## Review history

- **Round 1** (`spec-fidelity`, 2026-08-30): CHANGES REQUIRED, 3 items. FR-003 combined only the
  single-invocation form while merely un-blocking the chained one - the shape in the message the GM
  quoted and behind all 37 recorded firings; FR-004 rested its decline on FR-003 covering a case
  FR-003 did not cover, and R4 left the one alternative that would make the GM's literal proposal
  work unpriced; FR-006 reached across all twelve guards under an invitation that named two. All
  three applied.
- **Round 2** (`spec-fidelity`, 2026-08-30): CHANGES REQUIRED, 2 items. FR-007 (reordering `make
  done`'s phases so lint runs before the reference roll) was UNREQUESTED - the request never
  mentions phase order, and FR-003 delivers the round-trip saving without it; it is removed and put
  to the GM as `research.md` R7, its own question. And the "premises" paragraph still carried the
  ad-hoc counts (38 / 8 / 146) while the table beside it carried the replay's (37 / 9 / 119) - a
  stale number nobody noticed, inside the spec whose subject is stale numbers nobody noticed. The
  first was applied; the second was patched by a script whose anchor did not match and which did not
  assert that it had, so the paragraph was unchanged while this history claimed otherwise.
- **Round 3** (`spec-fidelity`, 2026-08-30): CHANGES REQUIRED, 1 item - the round-2 count fix had not
  actually landed. Applied, this time with the edit asserting its own anchor. The reviewer recorded
  that the round limit is reached and that the escalation is **procedural rather than substantive**:
  *"Round 3 closed the substantive finding ... what remains is a single paragraph that was agreed to
  and then not edited ... a one-paragraph correction with no design content and no ambiguity about
  what it should say."* Put to the GM in the session's report; the correction and a confirming read
  were not held for it, because holding a mechanical fix would have delivered nothing while they
  were away.
- **Round 4** (confirming read only, 2026-08-30): both round-3 items CONFIRMED - the counts agree
  across the paragraph, the table, `research.md` and the Decisions table, and the Review history is
  an accurate record of what was and was not applied. One new overclaim introduced by the round-3
  edit was caught and fixed: the sentence had claimed replay provenance for the whole table when
  seven of its thirteen rows come from the run log, `dev/switches.json` or a timing in this clone -
  a wrong provenance claim in the paragraph about wrong numbers.
