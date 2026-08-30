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
4. **Corrected**: the expensive-measurement guard is NOT firing a lot in absolute terms - 8 firings
   against 161 expensive invocations. What the GM has been seeing is mostly the quick+done guard (38)
   and, above both, `batching-hooks.sh` (146). Only the two the GM named are in scope here.

## Scope, stated exactly

**IN scope**: `scripts/measure-hooks.sh`, `scripts/gate-hooks.sh`, their companion test scripts, the
`quick` and `done` targets of `.claude/skills/diagram/Makefile`, a new shared guard-firing log with a
census that `make audit` prints, and the stale durations quoted in any guard message.

**OUT of scope**: what `make done` itself runs (its phases, its scope rules, its coverage floors);
`batching-hooks.sh`, `pair-hooks.sh` and the other nine guards, except that they gain the shared
firing log; the diagram engine; anything about maps.

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

The tooling detects that both were asked for and does the right thing instead of bouncing the
command back:

- `make quick done` (one invocation, both targets) runs `done` only. `quick` prints one line saying
  it was skipped because `done` supersedes it, and exits 0.
- The `gate-hooks.sh` block for "quick and done in ONE command" is RETIRED, together with the
  companion test vectors that assert it fires. The `-k`-subset block, which is a different rule in
  the same file, stays exactly as it is.

After this change, a chained `make quick && make done` costs one warm `quick` (4.1 s) more than
`make done` alone, against the 20-60 s round trip a rejection spends. The rejection was the more
expensive half.

### FR-004 - what `make quick` can hand to `make done`, measured

The GM's proposal - have `quick` save its results so a following `done` skips them - is answered with
the measurement rather than with an opinion, and the answer differs by which part of `quick` is meant:

- **The test run cannot be reused, and the spec records why**: `done`'s test phase runs the WHOLE
  tests tree UNDER COVERAGE, while `quick` runs a testmon-selected subset with `--no-cov`.
  Deselecting from `done` the tests `quick` already ran would remove their coverage with them, which
  is precisely the effect this Makefile already documents ("a deselected test takes its coverage with
  it"), and would make `uncovered-in-diff.py` and the three floors report holes that are not there.
- **The static phases can be reused, and are worth 1.8 s**: `lint`, `format` and `typecheck` cost
  1.0 + 0.1 + 0.65 s.

Therefore: FR-003 removes the duplication for the single-command form entirely (there is no `quick`
run left to reuse), and NO cross-process stamp is built for the 1.8 s of static phases. That
declined alternative, its measured value and the reason (a content key that does not exactly cover
`tests/` would skip a lint that should have run, weakening a gate phase to save 1.8 s of a 137 s
gate) are recorded in `research.md` under the project's rule for documenting a declined option.

### FR-005 - no guard message states a hardcoded duration

Every duration a guard message quotes is DERIVED at firing time from `dev/run-log/` - the median of
the recent recorded runs of that target - and says so, or it is not stated at all. Where the log has
no entries, the message omits the number rather than inventing one.

This is the general fix for the specific defect the GM caught: a number written into a message in
August is wrong in September, and nothing tells anybody. Any remaining hardcoded duration in a guard
message or in a Makefile prompt is corrected in the same pass.

### FR-006 - a guard firing is recorded

Every block a guard issues, and every escape a session takes (`GATE_OK`, `MEASURE_OK`, `PAIR_OK`,
`REF_OK`, `DISCARD_OK`, `NO_BRANCH_OK`, `POLL_OK`), appends one file to `dev/guard-log/` - one file
per firing, never an appended shared file, for the same reason `dev/run-log/` is a directory:
concurrent clones conflict on every shared append.

`make audit` gains a per-guard census: firings, escapes, and the escape rate. The question the GM had
to ask this session - "I keep seeing this one, is it worth what it costs?" - is then a query, not an
archaeology run over 715 MB of transcripts.

This is the "other automated checks" the GM invited, and it is deliberately the LEAST intrusive
thing on that list: it changes no guard's behavior, only what is known about it.

## Success Criteria

- **SC-001**: a session that runs `make test-full` twice in a streak is blocked on the second, and
  the block message does not say "third".
- **SC-002**: the first successful expensive measurement of a streak carries the batching reminder,
  and the second identical run does not repeat it.
- **SC-003**: `make quick done` runs the gate exactly once and no `quick` test run, and is not
  blocked by any hook.
- **SC-004**: `make quick && make done` is not blocked by any hook.
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
