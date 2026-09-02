# Feature 174 - One Hundred Percent, Enforced

**Status**: 2026-09-02, after TEN `spec-fidelity` rounds - every item applied, each round in the
Review history below. 1-4 found real drafting faults; 5 escalated the pragma to the GM under the
five-round cap and they ruled; 6 caught an arithmetic error; 7 found the ratchets still live, which
six rounds of reading the prose had missed; 8-10 are ONE failure in three files - an item closed in
the spec while a sentence asserting the old state stood in `SKILL.md`, `CLAUDE.md` and the plan
template. Round 10's own suggestion for ending that class mechanically is recorded at the foot of
the Review history.
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
| **dead code**, coverage pass | **0 left found** | ~91 statements deleted (8 functions + 3 constants + `pt_to_rect`) |
| **dead code**, pragma pass (FR-009) | **13 sites** | found only AFTER the GM's ruling sent the pragmas to be measured - so "0 left found" was true of what the coverage pass could see and was disproved by this feature's own later work. 40 engine lines |

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

**The 100% floor is enforced on a plain `make done`** (mechanically `coverage report --fail-under=100` in the skill Makefile - NOT a `fail_under` in `[tool.coverage.report]`, which `pytest-cov` would read and fire on every partial run; see SC5). Round 2 caught the first rewrite naming
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
| `GATE_STAMP_OK` | the push's documented escape (`sync-with-main.sh:244-252`) - when set, `gate-stamp.py --check` does not run AT ALL, so a push can land with no green gate | KEPT - it is feature 170's audited escape, needs a written reason, and is logged; it is not coverage-specific (it covers the guard-script gate too), and the GM did not ask to gut it. **This is the one part of the GM's sentence the feature does not deliver, and it is RAISED WITH THEM once the implementation works** (Principle XVI: carry on, then raise it), rather than claimed as met in the success criteria |
| `REF_OK` | the reference-scope bypass | stated and left as it is; it does not reach the coverage phase |
| `[tool.coverage.run] source` | 19 engine files / **1,843 statements** (`tools/` audits and drivers, `pipeline/gencache.py`) WERE outside the measured set, so they carried no coverage obligation and a new `tools/` module carried none the day it landed | **CLOSED by FR-010.** Round 8 found this row missing; it was first written STATED AND LEFT, reasoning that the GM had asked for the ratchets to go and not for the surface to widen. They then asked for exactly that widening (2026-09-02) and it was done - `source = ["l7r"]`, all 19 measured and tested |
| the `--omit` list + the 94% `SETTLEMENT_COV_FLOOR` | four trees (13,357 statements) sat outside the 100% report under a 94% ratchet, so a merge could land with settlement/ ~620 statements down | **CLOSED by FR-006** - both retired in this feature once their own condition was met. Round 7 found this row missing and two success criteria claiming it already closed; it was the GM's FIRST sentence and the largest hole of the five |
| a delta with no engine Python | tests, the Makefile, `scripts/` and docs take the DIRECT route, which runs no gate at all | STATED AND LEFT, like `REF_OK`. It is the GM's own ruling (feature 132 FR-024/FR-025: a tests-only change owes no build and no local gate) and this request does not reopen it. The exposure is bounded: the next engine change anybody makes meets the floor, red |


### FR-003b - two claims the second draft made about these targets were FALSE

Recorded because they were the argument FR-003 rested on, and both were checked and are wrong:

- *"`make test-full` is not refused under a scope lock"* - **false.** `Makefile:1022` gives it
  `$(SWEEP_OK)`, and the comment above it says so: *"test-full rolls every pool map, so the scope
  lock refuses it before `test` starts"*.
- *"`make done FULL=1` has never been green in 5 recorded runs"* - **misattributed.** Four of the
  five rows read `failed: test-full`; the never-green record belongs to `test-full` at least as much.

What IS true and worth the GM's attention: `done FULL=1` prompts and cancels by default and writes a
`dev/bypass-log/` entry, where `test-full` does neither.

### FR-010 - THE MEASURED SURFACE IS THE WHOLE ENGINE, AND IT IS DERIVED

**GM 2026-09-02, ruling on FR-003a's `[tool.coverage.run] source` row**: *"a new tool absolutely
should silently owe one hundred percent coverage the day it lands. Going forward, we want one
hundred percent code coverage, period. That was not previously the case. We now want that to be the
case always. For tools, for our settlement generation, for the automated checks on our hand drawn
diagrams, for everything."* And, on the nineteen modules the old roster excluded: *"I agree that
none of that is abandoned code. Therefore, it should all have tests, and we should require one
hundred percent code coverage for it."*

**What the roster had been hiding**: 19 engine files, **1,843 statements**, carrying no coverage
obligation at all - `tools/` audits and drivers plus `pipeline/gencache.py`. Two of them
(`dwellings.py`, `l7r/diagram/__init__.py`) were not tools at all; they fell out because the roster
listed SUBPACKAGES and nothing covered top-level modules. Nobody had decided they were exempt.

**Nothing was deleted.** The audit put to the GM found every one of the seventeen real tools wired to
a make target with a stated reason, and two of them - `pipeline/gencache.py` and `pipeline/regen.py`,
263 and 56 statements - are load-bearing infrastructure that runs on every map build and was merely
filed under "tools". The GM agreed and ruled that all of it gets tests.

| | |
|---|---|
| `[tool.coverage.run] source` | a hand-maintained roster -> **`["l7r"]`**. Derived, so a new file under `l7r/` owes coverage the day it lands and nobody has to remember |
| measured statements | 20,682 -> **22,520**, measured on the tree. An earlier draft said 22,525, which is 20,682 + 1,843 - a sum of two separately-dated measurements, exactly what D4 forbids. Round 9 caught it |
| modules brought from unmeasured to 100% | **19** (five were already there once measured; fourteen needed tests) |
| docstrings claiming *"not under the 100% rule"* | 3, all removed |

**One stated exclusion, and it is not "cannot happen"**: `gencache`'s `sys.monitoring` callback RUNS
and is asserted (a test proves six engine functions come back from a real roll), but coverage cannot
SEE it - a monitoring callback's body is invisible to coverage while coverage is itself installed,
because the two use the same machinery. Measured 2026-09-02: the callback recorded 6 functions while
coverage reported only its `def` line. That is unreachable by the MEASUREMENT, the same class as the
AWS transport, and it is stated at the point of change with the measurement rather than left silent.

### FR-009 - the PRAGMA is named, counted, and left to the GM

Round 5's finding, and the one thing in five rounds that this session should not decide for itself.

`# pragma: no cover` is the third exclusion mechanism in this spec's own vocabulary (D10 names it
beside `PARKED` and the `--omit` list), and it is the one D10 calls fatal in the GM's terms: *a
pragma moves the number without moving the coverage, which is the one outcome that would make the
floor a lie*. FR-003a enumerates ROUTES TO MAIN; FR-006 dissolves the two RATCHETS. Neither reaches
the pragma, and the spec's silence read as coverage.

**Measured in this clone at HEAD, and verified by the session rather than taken from the review:**

**AS MEASURED BEFORE THE RULING WAS CARRIED OUT** (the after-figures are two paragraphs down).
SITES are the wrong unit and were the first number taken - one pragma can hide a line or a whole
function - so the LINES are measured too, with coverage's own file reporter under this project's
`pyproject.toml` excludes:

| | count |
|---|---|
| `pragma: no cover` COMMENT LINES under `l7r/` | **130** (131 grep hits less one prose mention in `tools/hamlet_floor.py`, which names the token in a docstring and is not a pragma) |
| **excluded LINES, engine-wide** | **469**, against 22,470 measured statements |
| **excluded LINES inside the hard-floor tree** | **281**, against 9,118 measured statements - **3.08% of that tree's code is not measured at all** |
| largest single files | `ci/dispatch.py` 70, `hamletgen/homesteads/wells.py` 23, `hamletgen/sink.py` 15, `tools/cache_audit.py` 10, `pipeline/gencache.py` 10 |
| added or removed by the coverage pass | **net zero** - one `+` and one `-`, the same line moving with a lifted function |

So "100.00% of 20,646" is 100% of what coverage MEASURES, and 469 lines are outside that. The
feature's own claim is exact and its scope is narrower than the bare percentage sounds; both are
stated here so the GM reads the same number the gate does.

So under FR-003 exactly as written, a session that cannot cover a line may write `# pragma: no cover`
on it and the gate goes green. That IS a mechanism by which `make done` completes below a true 100%.

**RULED BY THE GM, 2026-08-31**: *"If there is `# pragma: no cover` code that cannot happen then we
should delete all of those cases, because dead code is bad, and it's better to remove it from the
codebase."* Carried out. The method is the part worth keeping: classifying by what each pragma's
comment CLAIMS is not evidence, because a comment is an assertion written once and never re-checked.
So all 130 were STRIPPED and the whole corpus run against this feature's own new floor, which then
NAMED every line nothing executes.

**Counted in coverage's own unit, EXCLUDED LINES, because pragma comment lines and excluded lines are
not the same thing and an earlier draft of this paragraph mixed them** (round 6 caught it: a
"78 stale / 53 unreached" pair matched comment lines to statements through a +/-2 line window and did
not reconcile with the tree - one pragma on a `class` or a block hides many lines, and the well
ring-probe rescue alone is 27 comment lines):

| | |
|---|---|
| excluded lines before | **469** |
| ...still uncovered when ALL exclusions were stripped | **113** |
| **so exclusions that were hiding lines the corpus ALREADY runs** | **356** - stale, protecting nothing |
| dead sites found in the 113 and DELETED | **13** (40 engine lines) |
| pragma comment lines | **130 -> 76** |
| excluded lines after | **469 -> 385**; inside the floored tree 281 of 9,118 (3.08%) -> 216 of 9,168 filesystem-tree lines (2.36%) |

Reading the comments alone would have deleted live code and kept dead code. Of what the measurement
showed genuinely unreached: **13 were dead and are deleted**; the rest are error handling or
structural terminals whose removal converts a graceful skip into a crash or returns `None` where the
signature promises a value, and live rescues and external systems whose comments say *"no cohort map
currently"* - today's seeds miss them, which is not the same as cannot happen. Each survivor now
carries why it stays. Full working in [`pragma-census.md`](pragma-census.md).

**Two things are NOT claimed settled, and both are the GM's.** (1) Whether the 24 error-handling
guards are meant too, which trades a silent skip for a crash on malformed input. (2) **The restored
exclusions are block-scoped and therefore over-broad**: 385 lines are excluded where only ~73 are
genuinely unreached (113 measured BEFORE the 40 deleted engine lines went - round 7 caught the two eras
being mixed), because a pragma on a rescue routine or a transport class covers the executed
lines inside it as well. That was true before this feature and is still true; narrowing them is
available work, and it is named here rather than left for a future reader to rediscover.

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

### FR-004a - DUPLICATION BETWEEN THE TWO SUITES IS THE DESIGN, not waste (GM 2026-08-31)

The GM's ruling, when told that some residual coverage comes from gate tests whose lines are reached
only because a set of seeds happens to hit them:

> if it only happens to be the case that code is exercised because we have selected a set of random
> seeds, which happens to cover everything, then that probably is fine for the full tests, but I do
> not think it would be a problem to write a more targeted version of such a test for our make done
> tests. because at that point, the make done tests are doing the straightforward branch coverage
> thing while our full tests are doing the more traditional end to end testing thing. So if that
> would require "duplication" to reach one hundred percent code coverage, then I think that is okay.

**So the two suites have different jobs and may cover the same line for different reasons:**

| suite | job | what a line being covered there means |
|---|---|---|
| the gate (`make done`) | **branch coverage** | someone wrote a test that names this branch and asserts what it does |
| FULL | **end-to-end** | a real map exercised it, which is the stronger evidence that it WORKS |

A line reached only by a lucky seed is covered in the second sense and not the first, and this
feature closes it in the first sense - with a targeted unit test - rather than counting the seed.
That is why the count can go DOWN as tests are added: a branch can be "covered" today and still owe
a test that says what it is for.

**Where a case is borderline, the GM offers guidance rather than the session guessing** (their own
offer). The borderline shape is a line whose only honest test IS the whole map - and the answer so
far, on every case met, has been that a targeted test exists.

### FR-005 - the answer to the GM's cheap-tests question, recorded as a decision

A cheaper, less valuable test set is NOT the route to 100%, and the measurement says why: the suite
is 50 s untraced and 237 s traced. **The expense is the tracing, paid once per gate whatever runs.**
So the end-to-end sweeps stay - they cost ~6 s of the total and buy the bug-finding the GM correctly
values above coverage.

### FR-006 - what becomes of the two ratchets, stated

- **`SETTLEMENT_COV_FLOOR = 94`**: retired when `settlement/` reaches 100%, not before. Until then it
  stays and is RAISED as the number climbs (its own comment: "RAISE the floor as each tier converts;
  NEVER lower it"). **It reached 100% under this feature** - 10,342 statements, 0 missing - so the
ratchet's own condition was met and it did not merely rise, it RETIRED, together with the `--omit`
list that kept four trees out of the 100% report. A ratchet whose condition is met is not a ratchet,
it is a hole: settlement/ could have shed ~620 statements and still passed.
- **the `--omit` list** (`settlement/`, `waterfields/`, `interactive/`, `overlap/`): dissolved, one
  tree at a time, as each reaches 100%. A tree leaves the omit list the day it can.

Neither is replaced by a new exemption, and **no question remains outstanding about the two this
requirement governs** - the `--omit` list and `SETTLEMENT_COV_FLOOR`. `hill.py` is covered by tests
like any other engine module (FR-004). The sentence that used to stand here reserved the `hill.py`
question, a survival from the second draft that round 2 struck and round 4 found still standing; the
unqualified "no exemption question remains" that replaced it was round 5's finding, because the
THIRD exclusion mechanism - the pragma - is not this requirement's and is not closed (FR-009).

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

1. The measured set is the WHOLE ENGINE and reports 100% - **22,520 statements, 0 missing**,
   measured on the tree, never tallied (D4). No ratchet, no per-tree omit, no roster.
   **What it still excludes is stated, not implied**: coverage does not count a line carrying
   `# pragma: no cover`, and the engine holds **77** such comment lines excluding **398** lines. Two
   histories fold in here and BOTH ARE CLOSED, not pending: the pragma, which the GM ruled on
   (FR-009 - 13 dead sites deleted, the rest kept as error handling, each with its reason), and the
   measured SURFACE, which the GM ruled on (FR-010 - `source = ["l7r"]`, the 19 files / 1,843
   statements brought in and tested). Earlier drafts asserted each as an open residue and then, once
   the GM closed it, were not swept - round 9's finding, and the sixth time this document has closed
   an item in one section while an absolute claim stood in another.
2. A run below the floor cannot complete. Of the routes FR-003a enumerates, **two are deliberately
   left open** and neither is claimed away here: feature 170's `GATE_STAMP_OK`, which skips the
   stamp check entirely but demands a written reason and is logged where `make audit` reads it; and
   the DIRECT route for a delta with no engine Python, which is the GM's own feature-132 ruling and
   which this request does not reopen. Both are stated in FR-003a, and the first is put to the GM.
3. Every closure is a test that asserts BEHAVIOR; every exemption is a deletion or a GM ruling.
4. `make quick` is unchanged.
5. The `--omit` list and `SETTLEMENT_COV_FLOOR` are both gone - **done**: the gate's coverage phase
   is a single `--fail-under=100` over the whole MEASURED set, with no per-tree omit and no ratchet
   beside it. (`pyproject.toml` still omits tests and the map generators, which are not engine code,
   and its `source` list is no longer a boundary at all - FR-010 made it `["l7r"]`, the whole engine.)
   Round 7 caught that this, the GM's FIRST sentence, had been left undone while two criteria claimed
   it met; retiring them was the last substantive act of the feature.

## Decisions recorded

ONE table, one numbering (round 3: the spec had grown a second `Decisions Recorded` section whose
ids collided with these, so no cross-reference resolved). D1-D7 were recorded at spec time; D8-D16
by the implementation. Class is the spec-time shorthand for D1-D7 and constitution XII's
`accurate` / `deviation` / `guess` for D8-D16.

| # | decision | class | why, and what was declined |
|---|---|---|---|
| D1 | the exempt trees are cheap to cover, not hard - the first draft's exclusion is withdrawn | measured, reversed | recorded at spec time, before the implementation ran |
| D2 | the floor sits on a run that deselects nothing; `make done`'s literal cost is priced at +148 s for the GM to weigh | measured | recorded at spec time, before the implementation ran |
| D3 | no `PARKED`, no pragma, no new omit entry - and HELD: the two pragmas this feature briefly added were removed after review, by patching the branch's own discriminator instead (R8) | decided, tested | recorded at spec time, before the implementation ran |
| D4 | counts are measured against a pushed tree, never tallied (three failures in one day) | decided; FR-002 labeled as session-added | recorded at spec time, before the implementation ran |
| D5 | where a function can DECLINE as well as act, coverage usually has the acting - assert the decline beside the action | method | recorded at spec time, before the implementation ran |
| D6 | `waterfields/hill.py` (99) is pending conversion work, NOT dead - the session's contrary claim was wrong and is recorded | corrected | recorded at spec time, before the implementation ran |
| D7 | deadness is proven by the roll records and pre-deletion archaeology, never by a caller grep | method, after the D6 error | recorded at spec time, before the implementation ran |
| D8 | The floor is enforced by making `done`'s test phase `test-full` on BOTH branches, not by adding a second, cheaper floored phase | deviation | The floors live behind `COV_FLOORS=1`, which is the SAME switch that turns off `--ignore=tests/full`, the roll deselect and the tier select. A deselected test takes its coverage with it (measured 2026-08-24 and still true), so a "cheap floored phase" reports holes that are not there, on every run - the fastest way to teach a session to read a red gate as normal. Declined: a second floor at a lower number (that is a ratchet, not the 100% the GM asked for) |
| D9 | The gate's wall clock went up and that was reported, not used to decline | deviation | The GM's request names the cost implicitly - a floor over the whole tree needs the whole tree traced. `make quick` is untouched, which is where the iteration loop actually lives, and the GM exempted it themselves. If they would rather have the cheap gate, moving the floor back is a one-line change to the phase list |
| D10 | No `pragma: no cover` was added to reach 100% | accurate | A pragma moves the number without moving the coverage, which is the one outcome that would make the floor a lie. No pragma was added TO REACH A NUMBER - the coverage half of this feature is net zero on them, its one
`+` and one `-` being the same line travelling with a lifted function. **One WAS added later and is
disclosed**: FR-010's `gencache.on_start`, which runs and is asserted but is invisible to coverage
because coverage uses the same `sys.monitoring` machinery - so the engine holds 77 comment lines, not
76. Round 9 caught this row still claiming none existed while FR-010 disclosed it three sections away. The GM then ruled on the
existing ones (FR-009) and that ruling WAS carried out here: **130 comment lines -> 76**, 13 dead
sites deleted (40 engine lines), 469 -> 385 excluded lines. Two earlier drafts of this row were wrong
and each was caught by review - "the two pre-existing pragmas" (wrong by 128, round 5) and "net zero"
(true of the coverage pass, false of the feature, round 6). Where a line was genuinely unreachable it was DELETED (`pool_index.py`'s empty-rows guard, which `_sections` makes impossible), and where it was merely hard to reach the closure around it was lifted out |
| D11 | Five closures were lifted to module level rather than reached through a whole map roll | accurate | The GM's own doctrine (2026-08-28, feature 146): an inner function that is hard to test gets lifted out, its captured values become parameters, and the inner caller delegates so there is ONE body. Each of the five now takes plain tuples and lists; `_detour_links` and `_fine_lattice_links` previously needed a hamlet stranded at exactly the right distance |
| D12 | The along-sampler's exact-divisor gap is RECORDED, not corrected | deviation | Where every segment divides `_ALONG_STEP_FT` exactly, the carried remainder lands on `t == seg` and the strict `<` misses it, so such a way offers only its two ends. Correcting it moves the links that rung draws, and so the lanes of any map that reaches it. A coverage feature does not get to change map output; the behavior is pinned by a test and stated on the function, so the next reader meets a decision rather than a bug |
| D13 | `GATE_RECIPE` salts the stamp key | accurate | FR-003a. `sync-with-main.sh --check` is the whole of what the push demands, and every stamp written before this feature certifies a run that was ALLOWED to finish below the floor. Salting retires them all at once. Declined: adding the Makefile to the hashed area, which would re-key the gate on every unrelated Makefile edit |
| D14 | `GATE_STAMP_OK` is KEPT | accurate | It is feature 170's audited escape: it demands a written reason of at least two words, and it is logged where `make audit` reads it. An escape that says why is this project's own answer to a bypass; removing it is not this feature's call, and the GM did not ask for it |
| D15 | The `done` ratchet was re-pinned rather than disarmed | accurate | The GM's condition on D1 of feature 171 (2026-08-30) was to RE-PIN once real runs exist. This feature deliberately changes what `done` does, so the old baseline measures a different target. The hard ceiling (45 s) and its `hard_at_or_below` trigger (35 s) are untouched - those are the GM's own numbers and not this feature's to move |
| D16 | `tests/settlement/test_structures.py` was split when feature 173's check failed on it | accurate | The rule fired on this feature's own work, which is the rule working. One file per submodule of the subject, the mapping DERIVED from which package names each test exercises, with its own "look here when" index - the same shape `tests/hamletgen/ways/` took. Declined: `FILE_SIZE_OK`, which is for ordered data and a derived roster, and a test suite is neither |

## Review history

Constitution XVI: reviewed against [`request.md`](request.md) by an independent `spec-fidelity`
subagent.

| round | verdict | what it found |
|---|---|---|
| 1 | CHANGES REQUIRED | **Seven items, all applied in this rewrite.** The spec had been written PARTWAY THROUGH implementation - disclosed to the reviewer, who confirmed the ordering showed: its scope was drawn around the work in flight (the 89 the session was already closing), and both exclusions landed exactly on work not yet started. Also: FR-003 named no run and never priced the literal instruction; FR-004's exclusion was disproved by the feature's own commits; the R3 deselection table was stale (the scope lock has been OFF since 2026-08-27); 35 statements inside the existing hard floor were missing from the census; FR-002 was unrequested; the two ratchets the GM's first sentence names were never addressed; and the "close to 100%" answer quoted the hamlet path (99.28%) rather than the whole set (96.07%) |
| 2 | CHANGES REQUIRED | **The central one: FR-003 was a no-op.** It named `make test COV_FLOORS=1` as the run to carry the floor - which is already where all three floors live, so the requirement changed nothing about `make done`, nothing about the push, and nothing about what a merge demands. Verified: a plain `make done` runs `test` with `COV_FLOORS` empty, stamps green anyway, and `gate-stamp.py --check` is the whole of what the push demands - so the mechanism the GM's request names would have survived the feature intact. The reviewer read that as the ordering pull surviving at the one requirement carrying the request's core, and that is the right diagnosis. Also: no requirement delivered success criterion 2's "no mechanism" (now FR-003a); FR-004 replaced a wrong exclusion with a question the request already forecloses (now decided); two stated facts about `test-full` were false (now FR-003b); and `research.md` R1 and R3 were stale while the spec declared research.md held every number (R1 corrected in place; **R3 was NOT, and round 3 caught the false claim that it had been** - corrected there) |
| 3 | CHANGES REQUIRED | **Three items, all applied, and all smaller than round 2's** - which is the pattern the five-round cap exists to permit rather than cut off (CLAUDE.md, GM 2026-08-30). (a) Success criterion 2 claimed "the push cannot land without that run" while FR-003a's own table KEEPS `GATE_STAMP_OK`, which skips `gate-stamp.py --check` entirely - the criterion asserted something the spec itself contradicted one section earlier. SC2 now states the residue, and FR-003a says it is raised with the GM rather than claimed as met. (b) The round-2 row said `research.md` R1 and R3 were "corrected in place"; only R1 was, and R3 still asserted the scope lock was on when it has been OFF since 2026-08-27 - the same finding recorded as fixed and not fixed. R3 carries its own correction now, and the round-2 row says what actually happened. (c) The spec had grown TWO `Decisions Recorded` sections with colliding ids (D1, D3 and D6 each meant two different things), so no cross-reference in this feature or any later one resolved; merged into one table with one numbering. The reviewer also named a fifth route to main below the floor - a delta with no engine Python takes the DIRECT route and runs no gate - which is now a stated-and-left row in FR-003a, since it is the GM's own feature-132 ruling and this request does not reopen it |
| 4 | CHANGES REQUIRED | **Two items, both new and both smaller again.** (a) THE ROUND-3 FIX SUBSTITUTED A NEW OVERCLAIM FOR THE OLD ONE - the exact failure the reviewer was asked to watch for. SC2's rewrite said `GATE_STAMP_OK` was "the only remaining way" to land without the floored run, while the same edit had just ADDED a second open row to FR-003a: a delta with no engine Python takes the DIRECT route and runs no gate. So the criterion again asserted a completeness the spec disproved two sections above it. SC2 now names both open routes and claims neither closed. (b) FR-006 still ended "FR-004's `hill.py` question is the only one outstanding" - a survival from the second draft that round 2 struck, and one that reads as this spec holding an exemption question open against a request that permits none, directly contradicting FR-004's own title. Also applied, from the reviewer's asides: the Status line was three rounds stale, and the Review history had fragmented into three headerless tables - cosmetic, but it is the record of exactly what round 3 was about |
| 5 | CHANGES REQUIRED -> **ESCALATED** | **The cap's own procedure, working as designed.** Four items: three were factual (D10 said "the two pre-existing pragmas" when 130 stood - wrong by 128; SC1 and FR-006 overclaimed), and the fourth was substantive and NOT the session's to settle - `# pragma: no cover` was ungoverned, and it is the exclusion mechanism D10 itself calls fatal. Under CLAUDE.md's five-round cap this went to the GM rather than to a sixth round, with the count measured first so the question arrived costed. **The GM ruled** (delete what cannot happen; merge once done), and FR-009 records the ruling and its execution |
| 6 | CHANGES REQUIRED | **Post-ruling check, and it caught an arithmetic error in the session's own account** - including in what had already been reported to the GM. FR-009 claimed "78 of the 131 stale, 53 unreached, 13 deleted", which does not reconcile: 131 - 78 - 13 = 40 against a tree holding 76. The pair mixed UNITS, matching pragma comment lines to uncovered statements through a +/-2 line window the session had already watched miss cases. Every count is now in coverage's own unit and reconciles (469 excluded -> 113 still uncovered when stripped -> 356 stale; 130 -> 76 comment lines; 13 dead sites deleted). Also: four passages still asserted the PRE-ruling state and now contradicted FR-009 (SC1, D10, FR-001's census row, FR-009's own before-table, now labelled as such), and 131 was corrected to 130 - one grep hit is a prose mention in a docstring. The reviewer's asides are taken too: this Status line and these rows |

**The ordering was wrong and is recorded as such**: implementation began before the spec existed,
contrary to Principle XVI. The rewrite above is drawn from the request and the measurements rather
than from the work already done, which is why FR-004 now REVERSES the first draft's exclusion and
FR-001's census grew from 89 to 565.
| 7 | CHANGES REQUIRED | **The verdict round found the largest hole of all, and it was the GM's own first sentence.** The `--omit` list and `SETTLEMENT_COV_FLOOR = 94` were STILL LIVE in the Makefile: the 100% floor this feature put on `make done` covered 7,325 statements while 13,357 more sat under a 94% ratchet, so settlement/ could have shed ~620 statements and the gate would still have gone green. Two success criteria asserted both were gone, FR-003a's route table omitted it, and FR-006 made retirement conditional on a threshold that had ALREADY been met (settlement/ measured 10,342 statements, 0 missing). Both are now retired and the coverage phase is one `--fail-under=100` over the whole MEASURED set - 20,682 statements, 0 missing, no per-tree omit and no ratchet. (Round 8 then caught this row, SC1 and SC5 all saying "the whole engine"/"nothing omitted", which overstates: `[tool.coverage.run] source` leaves 19 engine files / 1,843 statements unmeasured by a pre-existing decision this feature did not change.) Also fixed: "~113 genuinely unreached" mixed the pre- and post-deletion eras (~73 after the 40 deleted lines), and the derived percentages did not reproduce (3.08% -> 2.36%, the raw line counts having always been exact). The lesson the ledger should keep: six rounds went into the spec's PROSE while the requirement's own subject sat unimplemented, because every round after the first graded the words rather than re-checking the Makefile |
| 8 | CHANGES REQUIRED | **The same substitution, a fifth time, and this one reached the GM's report.** Fixing round 7 replaced an ACCURATE success criterion ("The measured set reports 100%, with no ratchet and no parked lines") with a stronger false one ("the measured set is now the WHOLE engine"). Measured: `[tool.coverage.run] source` names the measured modules one by one and leaves **19 engine files / 1,843 statements** outside - `tools/` audits and drivers plus `pipeline/gencache.py` - so the engine is 22,525 statements of which 20,682 are measured. That exclusion is LARGER than the pragma one the feature escalated to the GM at round 5, on the very grounds that "the spec's silence read as coverage". SC1, SC5, the round-7 row and `SKILL.md` all corrected; FR-003a gains a seventh route, stated-and-left, since the GM asked for the ratchets to go and not for the measured surface to widen. Two count errors from the same root cause also fixed: the old floored report covered **7,325** statements, not 9,168, and the exclusions inside the measured set are **327 of 20,682 (1.58%)**, not 385 - the census had counted excluded lines across the filesystem tree, including files coverage never reports at all |
| 9 | CHANGES REQUIRED | **The same mechanical failure a sixth time, and this round names it as the drafting method rather than the sentence.** FR-010 recorded that the GM had CLOSED the measured-surface residue - and the four places round 8 had forced to STATE that residue were never swept, so the document asserted both at once and the false half sat in the success criteria. Worst of the four was **`SKILL.md`**, which is not a record but the file the next session reads before touching the config, and which still carried the sentence the GM reversed verbatim: *"`source` ... names the measured modules one by one ... so a new tool does not owe 100% the day it lands"*. Also: **the headline count was a TALLY, not a measurement** - 22,525 is 20,682 + 1,843, two separately-dated figures added together, which is exactly what this feature's own D4 forbids; the tree measures **22,520**, and the wrong number had already been reported to the GM. And D10 still said "no pragma was added" while FR-010 disclosed one three sections away (77 comment lines, not 76; 398 excluded lines, not 385). All corrected, plus the reviewer's asides: the constitution named `pytest --cov-fail-under=100` when the mechanism is `coverage report --fail-under=100` in the Makefile, and `CLAUDE.md`'s guard row met the pre-widening number first. **The lesson recorded for the ledger**: rounds 7, 8 and 9 are one failure, not three - an edit that closes an item without SWEEPING the tree for the sentences that asserted the old state |
| 10 | CHANGES REQUIRED | **The same failure again, and this round proved the session had REPORTED a fix it never made.** `git show` on the round-9 commit showed it touched `SKILL.md`, `pyproject.toml`, `spec.md` and `tasks.md` - and not `CLAUDE.md`, which the session had told the GM was corrected. The edit script had died on an assertion in an earlier block and the batch was reported applied without checking. So `CLAUDE.md` still carried **20,646 statements** (a third-era figure that appears nowhere else outside this spec) and "with no `pragma: no cover` added", which FR-010 had disclosed to be false three documents away; and it still named `pytest --cov-fail-under=100` as the mechanism, which the constitution had just been amended to deny. Two more places the sweep had never reached: **`.specify/templates/plan-template.md`**, whose Constitution Check still demanded the floor *"on pure-logic packages"* - the narrowed rule the GM globalized, in the template EVERY future plan copies, so the next feature would have been taught the exemption this one exists to remove - and the **constitution's own SYNC IMPACT REPORT**, which recorded no 2.15.0 amendment while the footer claimed the version. Plus the Status line, three rounds stale for the SECOND time. All verified individually this time, each edit asserted rather than assumed |

**ROUND 10'S OWN DIAGNOSIS, kept because it is the useful part.** Rounds 7-10 found the same
mechanical failure in four different files: an item settled in the spec while a sentence asserting
the old state stood in an operative document. The spec has been substantively right since round 7.
The reviewer's suggestion for ending the class is not editorial but MECHANICAL, and it is left here
for the GM rather than built unasked: *a gate check that the statement count quoted in `CLAUDE.md`,
`SKILL.md` and `pyproject.toml` equals the measured one* - the same shape as `make notes-census`,
which exists because a stated count and a drawn count drifted apart three times.
