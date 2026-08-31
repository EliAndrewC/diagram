# Feature 174 - One Hundred Percent, Enforced

**Status**: Draft - rewritten 2026-08-31 against `spec-fidelity` round 1 (CHANGES REQUIRED, seven
items, all applied below) and against measurements the first draft did not have.
[`request.md`](request.md) is the authority; [`research.md`](research.md) holds every number.

## The feature, in one sentence

The coverage floor becomes a hard 100% that a merge cannot get past, on a run that deselects nothing.

## Why this exists (the GM's words)

> ...moved back up to one hundred percent with the standard `fail_under = 100` configuration option
> set so that in the future, we literally cannot complete our make done in order to merge back into
> main, and there will no longer be any mechanism by which this can be accomplished.

They exempted `make quick` themselves and gave the reason. They also asked, mid-feature, whether a
CHEAPER test set could reach 100% - answered in R5 and in FR-005 below.

## The GM's premises, measured (R1-R7)

| premise | verdict |
|---|---|
| *"make done is close to one hundred percent"* | **RIGHT.** 97.26% over the whole measured set (565 of 20,618) as this spec is written, from 96.07% at the start of the feature. The first draft answered 99.28%, which was the hamlet path alone - one of three floors - and the session corrected it to the GM unprompted |
| *"we have some ratchets somewhere that enforce less than one hundred percent"* | **RIGHT, and FR-006 names them**: `SETTLEMENT_COV_FLOOR = 94` and the `--omit='*/settlement/*,*/waterfields/*,*/interactive/*,*/overlap/*'` list |
| *"we turned this off because we were doing a large refactor"* | **PARTLY.** True of feature 166's check-battery retirement; NOT true of the 94 ratchet, whose own comment (2026-08-16) says the frozen pool maps leave the town/city/capital wings "exercised by nothing until those tiers convert" |
| *"a cheaper, less valuable test set could get there faster"* | **NO - and the lever is elsewhere.** The whole suite runs in 50 s untraced and 237 s traced: the TESTS are not the expense, the coverage TRACING is. Dropping the end-to-end sweeps would save ~6 s and lose their bug-finding (R5) |

## Scope, stated exactly

**IN**: closing every uncovered statement in the measured set; deleting what is dead rather than
covering it; naming the run that carries the floor and pricing the alternative; and turning
`fail_under = 100` on LAST. **OUT**: `make quick` (the GM exempted it); converting any settlement
tier.

## Requirements

### FR-001 - the census is the WHOLE measured set, not one floor

565 uncovered statements over 182 files, in four buckets, each with its own route:

| bucket | now | route |
|---|---|---|
| the hamlet path's remainder | **25** | 4 fallback rungs inside long drawing methods - constructed geometry or a lift |
| the existing hard floor's own misses | **33** | unit tests; `ci/`, `switches.py`, `pool_index.py`, CLI entry points |
| the four exempt trees | **~507** | mostly TOWN/CITY drawing methods, which unit-test cheaply - proven below |
| **dead code** | **0 left found** | ~91 statements deleted (8 functions + 3 constants + `pt_to_rect`) |

**The exempt trees are the cheapest work, not the hardest** - the opposite of what the first draft
assumed. Measured: `town_ways.py` 21% -> **100%** with one test file; `civic_grounds/lodging.py` 46%
-> **99%** with three tests; `shrines_wells/shrines.py` 52% -> 71%. None needed a map roll. Every
test pins a documented RULE (a flophouse derives its angle from its road, asserted by rotating the
road; a market clearing draws no building yet still reserves its court).

### FR-002 - a census is MEASURED against a pushed tree, never tallied

Kept from the first draft, and the review was right that the request does not ask for it - so it is
labeled: **this is a method requirement the session added, and the GM may strike it.** It is here
because it failed three times in one day: a peer's summary said minus six where its own rows said
minus two; this session's tally said 61 closed where the measurement said 60 (a test that passed
while covering nothing, having returned at an earlier guard); and a `make test-file` run BESIDE a
running `test-full` corrupted a measurement into reporting 44% for a tree at 95% (R6).

### FR-003 - the floor is enforced on `make done` ITSELF, because that is what the request says

> ...so that in the future, we literally cannot complete our **make done** in order to merge back
> into main, and there will no longer be any mechanism by which this can be accomplished.

**`fail_under = 100` is enforced on a plain `make done`.** Round 2 caught the first rewrite naming
`make test COV_FLOORS=1` instead - which changes NOTHING, because that is already where all three
floors live (`Makefile:1021-1023, 1058-1067`). Verified in the tree, a plain `make done` today:

- runs `test` with `COV_FLOORS` empty (`Makefile:111`, the phase loop `hooks-test $(if $(FULL),test-full perf-gate,test)`)
  and prints *"coverage floors: deferred to `make done FULL=1`"*;
- **stamps green anyway**, and `sync-with-main.sh:255`'s `gate-stamp.py --check` is the whole of what
  the push demands.

So a merge below 100% is available today and would have stayed available under the first rewrite.
That is the clause the GM wrote the request around, and the spec had left it standing.

**The cost is stated, not used as a reason to decline**: +148 s per gate (89 s -> 237 s, R5, with
R6's hybrid-CPU caveat). An expensive request is still the request. **If the GM would rather have
the cheap gate, the amendment is theirs to make** - the floor moves to the run the push requires and
`make done` stays at 89 s - and this requirement is written so that choice is a one-line change
rather than a redesign.

### FR-003a - the OTHER routes below the floor, named and closed

Success criterion 2 says "no mechanism", and round 2 was right that no requirement delivered it. A
route to main below the floor is closed only when each of these is closed:

| route | what it is | disposition |
|---|---|---|
| the FULL-only deferral | `COV_FLOORS` empty on a plain `make done` | closed by FR-003 |
| `already-verified` | `make done` short-circuits on a green record for the same engine content | a record taken BEFORE the floor existed must not satisfy a push after it; the verification key must move when the floor does |
| `GATE_STAMP_OK` | the push's documented escape (`sync-with-main.sh:244-252`) | KEPT - it is feature 170's audited escape, needs a written reason, and is logged. An escape that says why is the project's own answer; removing it is not this feature's call |
| `REF_OK` | the reference-scope bypass | stated and left as it is; it does not reach the coverage phase |

### FR-003b - two claims the second draft made about these targets were FALSE

Recorded because they were the argument FR-003 rested on, and both were checked and are wrong:

- *"`make test-full` is not refused under a scope lock"* - **false.** `Makefile:1022` gives it
  `$(SWEEP_OK)`, and the comment above it says so: *"test-full rolls every pool map, so the scope
  lock refuses it before `test` starts"*.
- *"`make done FULL=1` has never been green in 5 recorded runs"* - **misattributed.** Four of the
  five rows read `failed: test-full`; the never-green record belongs to `test-full` at least as much.

What IS true and worth the GM's attention: `done FULL=1` prompts and cancels by default and writes a
`dev/bypass-log/` entry, where `test-full` does neither.

### FR-004 - `waterfields/hill.py` is COVERED BY TESTS, not exempted and not asked about

The first draft excluded the town/city wings as un-producible; this feature's own commits disproved
that, and the second draft then put `hill.py` (99 statements) to the GM as a three-option question.
**Round 2 was right that this is the same mistake in a smaller box**, and the request forecloses it:
there is no carve-out in it, and the stop-and-ask calculus does not authorize the interrupt - 99
statements of unit tests are cheap to unwind, and the GM starts work and leaves.

It is also more tractable than what has already been closed: `build_terraces` and `build_ribbon` are
pure geometry builders taking plain numbers, both are already named in the public-surface census
(`tests/waterfields/test_surface.py:75-76`), and both frozen exhibit gens supply a WORKING CALL
verbatim (`tanada.gen.py:35`, `yatsuda.gen.py:38`) to copy.

**It is not dead code** - the session claimed that, was wrong (D6), and the migration plan lists both
archetypes as "NOT STARTED | engine builder exists". So it is covered like any other engine module.

### FR-005 - the answer to the GM's cheap-tests question, recorded as a decision

A cheaper, less valuable test set is NOT the route to 100%, and the measurement says why: the suite
is 50 s untraced and 237 s traced. **The expense is the tracing, paid once per gate whatever runs.**
So the end-to-end sweeps stay - they cost ~6 s of the total and buy the bug-finding the GM correctly
values above coverage.

### FR-006 - what becomes of the two ratchets, stated

- **`SETTLEMENT_COV_FLOOR = 94`**: retired when `settlement/` reaches 100%, not before. Until then it
  stays and is RAISED as the number climbs (its own comment: "RAISE the floor as each tier converts;
  NEVER lower it"). It is at 97% now, so the floor may already rise.
- **the `--omit` list** (`settlement/`, `waterfields/`, `interactive/`, `overlap/`): dissolved, one
  tree at a time, as each reaches 100%. A tree leaves the omit list the day it can.

Neither is replaced by a new exemption. FR-004's `hill.py` question is the only one outstanding.

### FR-007 - dead code is DELETED, not covered - and deadness is proven, not grepped

~91 statements went this way. The proof standard is the one the independent reviewer used, after the
session's own grep-based claim about `hill.py` proved wrong: **the roll records** (`.gencache/rolls/*/meta.json`)
say which functions actually EXECUTE, and pre-deletion archaeology (`git grep <name> <pre-166>`) says
who used to call them. A grep for callers is a negative statement about what is written; the roll
record is a positive one about what runs. **Check the frozen `.gen.py` trees explicitly** - that is
the channel that made `hill.py` live and that a live-code grep misses.

### FR-008 - the floor goes on LAST

`fail_under = 100` is set only once the measured set meets it. Setting it earlier leaves the gate
permanently red, and a red gate everyone routes around is how the ratchets arrived in the first place.

## Success criteria

1. The measured set reports 100%, with no ratchet and no parked lines.
2. A run below the floor cannot complete, and the push cannot land without that run.
3. Every closure is a test that asserts BEHAVIOR; every exemption is a deletion or a GM ruling.
4. `make quick` is unchanged.
5. The `--omit` list and `SETTLEMENT_COV_FLOOR` are both gone.

## Decisions recorded

| # | decision | class |
|---|---|---|
| D1 | the exempt trees are cheap to cover, not hard - the first draft's exclusion is withdrawn | measured, reversed |
| D2 | the floor sits on a run that deselects nothing; `make done`'s literal cost is priced at +148 s for the GM to weigh | measured |
| D3 | no `PARKED`, no pragma, no new omit entry | decided |
| D4 | counts are measured against a pushed tree, never tallied (three failures in one day) | decided; FR-002 labeled as session-added |
| D5 | where a function can DECLINE as well as act, coverage usually has the acting - assert the decline beside the action | method |
| D6 | `waterfields/hill.py` (99) is pending conversion work, NOT dead - the session's contrary claim was wrong and is recorded | corrected |
| D7 | deadness is proven by the roll records and pre-deletion archaeology, never by a caller grep | method, after the D6 error |

## Review history

Constitution XVI: reviewed against [`request.md`](request.md) by an independent `spec-fidelity`
subagent.

| round | verdict | what it found |
|---|---|---|
| 1 | CHANGES REQUIRED | **Seven items, all applied in this rewrite.** The spec had been written PARTWAY THROUGH implementation - disclosed to the reviewer, who confirmed the ordering showed: its scope was drawn around the work in flight (the 89 the session was already closing), and both exclusions landed exactly on work not yet started. Also: FR-003 named no run and never priced the literal instruction; FR-004's exclusion was disproved by the feature's own commits; the R3 deselection table was stale (the scope lock has been OFF since 2026-08-27); 35 statements inside the existing hard floor were missing from the census; FR-002 was unrequested; the two ratchets the GM's first sentence names were never addressed; and the "close to 100%" answer quoted the hamlet path (99.28%) rather than the whole set (96.07%) |

| 2 | CHANGES REQUIRED | **The central one: FR-003 was a no-op.** It named `make test COV_FLOORS=1` as the run to carry the floor - which is already where all three floors live, so the requirement changed nothing about `make done`, nothing about the push, and nothing about what a merge demands. Verified: a plain `make done` runs `test` with `COV_FLOORS` empty, stamps green anyway, and `gate-stamp.py --check` is the whole of what the push demands - so the mechanism the GM's request names would have survived the feature intact. The reviewer read that as the ordering pull surviving at the one requirement carrying the request's core, and that is the right diagnosis. Also: no requirement delivered success criterion 2's "no mechanism" (now FR-003a); FR-004 replaced a wrong exclusion with a question the request already forecloses (now decided); two stated facts about `test-full` were false (now FR-003b); and `research.md` R1 and R3 were stale while the spec declared research.md held every number (corrected in place) |

**The ordering was wrong and is recorded as such**: implementation began before the spec existed,
contrary to Principle XVI. The rewrite above is drawn from the request and the measurements rather
than from the work already done, which is why FR-004 now REVERSES the first draft's exclusion and
FR-001's census grew from 89 to 565.
