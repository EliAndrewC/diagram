# Feature Specification: cut the cost of the test suite

**Feature**: 147-test-suite-cost
**Created**: 2026-08-29
**Status**: APPROVED. `spec-fidelity` round 1 returned CHANGES REQUIRED (6 items - the four-to-five-minute question unanswered, the COLD run dropped along with the corrected number, the GM's named techniques not made requirements, no lessons audit, FR-001 forbidding what the GM invited, and two unsourced numbers); all six applied. Round 2 verdict FAITHFUL. Implementation proceeds.

## The GM's request (verbatim, the thing this is graded against)

> "Now I think it's time that we do another pass on efficiency. Have we added enough things to make quick,
> to make it slower than we want? I ask not because I have any specific reason to think that this has
> happened, but because this general thing has happened in the past. So it's worth asking about now. Also,
> how long is the previously four to five minutes worth of tests now? what efficiency improvements remain?
> What things are we currently doing which are computationally expensive in our tests? which we could
> probably hack away at. I mean, you mentioned that some of the tests take ten minutes to run. That feels
> like something that we could probably get down. And I don't even know that we have even attempted to take
> an optimization pass on that particular set of tests, have we? can you do an audit and see if you are able
> to apply any of the lessons that we have used in our last several rounds of performance improvements?
> things like caching rather than recomputing every time or running on a smaller suite that does not have
> many thousands of polygons or things to overlap with. or running on way more random seeds than what we
> actually need in order to get decent test coverage. I don't know. Stuff like that. We've made a whole lot
> of performance improvements, and I feel like we should be able to apply the same techniques we already
> have to get that ten minutes down to something much, much more reasonable. So go ahead and open another
> feature for this and then start with an audit, and I will take acceptance as the final task of the feature
> because it is likely that I will add new tasks after your initial findings."

## The audit, measured before any change (2026-08-29, this clone, 8 workers)

| what | tests | wall |
|---|---|---|
| the cheap loop (testmon selection) | varies | **26.3 s** |
| the cheap loop, ALL=1 | 2,006 | **28.9 s** |
| **THE GATE - the run the GM's "previously four to five minutes" names - WARM** | 2,386 | **13 s** |
| **THE GATE with every roll FORCED - the state a session is in after an engine edit** | 2,386 | **110 s** |
| whole tree, FULL env, no coverage, map rolls DESELECTED | 2,347 | **12 s** |
| whole tree, FULL env, no coverage, map rolls included | 2,417 | **262 s** |
| the full sweep (coverage + the three floors), WARM | 2,417 | **234 s** |
| **the full sweep COLD** (generation cache wiped - 145 MB) | 2,417 | **383 s** |
| the `rolls_map` tests alone, FULL env, no coverage | 69 | **166 s** wall / ~430 s CPU |

**Which target is the GM's "previously four to five minutes"?** The gate. `CLAUDE.md` recorded it at
"~4.5 min unlocked" on 2026-08-26 and at 21.7 s warm after feature 135. Measured here: **13 s warm, 110 s
when every roll is forced.** That question is now answered, and it is a different target from the 234 s full
sweep - the sweep is not what a push runs. The first draft of this spec measured only the sweep and called
it "the pre-push sweep", which was wrong twice over.

**WARM AND COLD ARE DIFFERENT RUNS, AND THE COLD ONE IS THE ONE THE GM NAMED.** Re-basing "ten minutes" to
234 s warm is only half an answer: a session that has just changed the engine has invalidated every cached
roll, and that is precisely when the gate must run before a push. Measured, that state costs 110 s at the
gate and 383 s at the full sweep. This feature therefore targets BOTH, and a reduction that only helps the
warm case is reported as such rather than counted as the answer.

**Two corrections to what the GM was told.** The "ten minutes" figure quoted during feature 146 was a COLD
run taken straight after heavy engine edits, when every cached roll had been invalidated; warm, the same
target is 234 s. And the cheap loop has NOT drifted - it is inside its own 60 s budget with room to spare.

**Where the 234 s goes.** Essentially all of it is map rolls; coverage instrumentation is not the story
(the same tree without coverage but with the rolls is 262 s). Ranked, from the durations profile:

| test | wall |
|---|---|
| `gate/hamletgen/test_driver.py::test_a_rolled_cohort_passes_the_whole_gate` | **155 s** |
| `full/test_villages.py::test_a_map_is_immune_to_an_upstream_change_in_the_number_of_random_draws` | **105 s** |
| `full/pipeline/test_gencache.py::test_the_real_pool_round_trips_through_the_cache` | 32 s |
| `full/hamletgen/test_driver.py::test_the_fan_out_agrees_with_the_serial_path` | 22 s |
| `gate/hamletgen/test_driver.py::test_a_re_roll_that_does_not_help_is_not_kept` | 18 s |
| **31 x `gate/test_scripted_fixtures.py::test_*_fires_*`** | **~14 s EACH** (~430 s CPU) |

**The named waste.** Feature 141 designed a scripted negative fixture as *"a cached roll plus one deliberate
break"* - roll once, then mutate the manifest. The cache does not serve under the FULL run, and for a good
reason recorded in `pipeline/rollcache.py`: *"a served roll executes nothing the coverage floors could see"*.
The consequence nobody costed is that all 31 fixtures then re-roll THE SAME reference hamlet from scratch,
one after another, and the coverage floors only ever needed one of those rolls to execute.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - the GM asks for a small change (Priority: P1)

The GM asks for a one-line change and the session must prove it merges clean. What a push actually runs is
the GATE: 13 s when nothing the rolls execute has changed, and 110 s once the change touches the engine -
which a change worth pushing usually does. The full sweep (234 s warm, 383 s cold) is what a session owes
once at the end. The GM's stated goal is that a five-minute change does not become a half-hour of machine
time, and it is the ENGINE-EDIT cost, not the unchanged-content cost, that decides whether that holds.

**Acceptance**: the full sweep proves exactly what it proves today - every pool map gated, the cohort
ratchet, the determinism guarantee, every kept check firing on a negative fixture, and a 100% hamlet-path
coverage floor - in materially less wall time.

### User Story 2 - a session adds a scripted negative fixture (Priority: P2)

A session adds a check and must prove it fires. Today that adds ~14 s to the sweep for a roll identical to
the thirty already there, so the marginal cost of proving a check has teeth grows without bound.

**Acceptance**: adding one scripted fixture costs the sweep the mutation and the gate, not another roll.

### User Story 3 - the numbers stay honest (Priority: P3)

The timings quoted in the docs are what future sessions plan against, and a cold figure recorded as if it
were warm sends them chasing the wrong thing - which is exactly what happened here.

**Acceptance**: every timing this feature records says whether it is COLD or WARM and on what hardware.

### Edge Cases

- A shared roll must not let one test's mutation leak into another's - a fixture that breaks the manifest it
  was handed would silently disarm every fixture after it.
- The coverage floors must still SEE a real roll execute. If sharing means only one roll runs, that one roll
  must still execute every line the floor is derived from, or the floor silently stops proving anything.
- A cheaper corpus or a smaller seed set must not quietly drop a case that is the only one exercising a rule.
- The cheap loop must stay inside its budget; nothing here may move cost from the sweep INTO it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** The suite MUST still PROVE everything it proves today: every kept check still fires on a
  negative fixture, every live pool map is still gated, the determinism guarantee and the cohort pass-RATE
  ratchet both still hold, and the hamlet-path coverage floor is still 100%. This is a floor on the
  PROPERTIES, deliberately not on the inputs - today's seed counts, corpus size and map count are NOT
  inviolable, because reducing them is a technique the GM named. Where a property can be proven by fewer
  seeds, a smaller map or a shorter corpus, taking that is the feature working, and FR-005 governs how the
  reduction is recorded. What this forbids is retiring a PROPERTY: a saving bought by proving less is a
  scope reduction, and this feature does not have that mandate.
- **FR-002** The 31 scripted negative fixtures MUST share ONE roll of their common spec per worker process
  rather than each rolling it, with each test receiving geometry it can mutate without affecting any other.
- **FR-003** The shared roll MUST still execute under the coverage floors, so the floor's derivation and its
  100% bar are unaffected. Where sharing would hide execution from coverage, the sharing is not taken.
- **FR-004** The five named single tests (cohort 155 s, determinism 105 s, pool round-trip 32 s, fan-out 22 s,
  re-roll 18 s) MUST each be examined and either cut, reduced to the smallest input that still proves the
  property, or KEPT with a written statement of what its time buys.
- **FR-005** Every reduction in seeds, corpus size or map count MUST record what was dropped and the argument
  that the dropped case proved nothing the kept cases do not.
- **FR-006** Each of the THREE techniques the GM named MUST be examined across the whole suite, not only
  within the five named tests, and each MUST produce a written finding whether or not it yields a change:
  (i) **caching rather than recomputing every time**; (ii) **running on a smaller input** rather than one
  carrying many thousands of polygons and overlap candidates; (iii) **seed counts** - for every test that
  rolls more than one seed, how many it rolls and how many are actually needed for decent coverage. Technique
  (iii) had no examination requirement in the first draft, and it is the one the GM named most specifically.
- **FR-007** The prior performance rounds MUST be enumerated (features 135, 138, 140, 141, 146 and any
  others the record shows) and, for each technique they produced, this feature MUST state whether it applies
  to the expensive tests here and why or why not. It MUST also answer the GM's direct question - whether this
  set of tests has ever had an optimization pass - rather than leaving it implied.
- **FR-008** The cheap loop MUST stay inside its 60 s budget, and no cost may be moved from the sweep into it.
- **FR-009** Timings recorded by this feature MUST state COLD or WARM. The docs' existing figures that are
  now known to be cold MUST be corrected.
- **FR-010** The audit's before/after numbers MUST be recorded in the feature's research so the next
  efficiency pass starts from measurements rather than from a fresh profile.

### Key Entities

- **the roll cache** (`pipeline/rollcache.py`) - serves a recorded roll when nothing it executes changed;
  bypasses SERVING under the FULL run so coverage sees real execution.
- **the scripted fixture corpus** (`tests/gate/test_scripted_fixtures.py`) - 31 tests, one roll plus one
  deliberate break each.
- **the cohort ratchet** and **the determinism test** - the two most expensive single tests.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** The full sweep completes in materially less wall time than its measured baselines, WARM (234 s)
  and COLD (383 s), with both achieved figures recorded. **The provisional target is under 90 s warm, and it
  is derived rather than asserted**: the same tree with the map rolls deselected is 12 s and the rolls are
  166 s wall, so removing the ~29 redundant rolls of two specs should land the group near the cost of one
  roll each - about 12 s of tree plus 30-60 s of irreducible rolling. It is the session's provisional
  quantification of "much, much more reasonable", NOT a stopping condition: if cheaper reductions remain
  identified below it they are reported rather than skipped, and the real bar is the GM's at acceptance.
- **SC-001b** The COLD sweep and the ENGINE-EDIT gate (383 s and 110 s measured) each improve, or the reason
  they cannot is written down for the GM. A reduction that helps only the warm case does not satisfy this.
- **SC-002** The scripted-fixture group costs about one roll in total rather than 31.
- **SC-003** The gate and the cheap loop are no slower than the baselines in THIS feature's audit table -
  the gate at 13 s warm and 110 s rolls-forced, the cheap loop at 26.3 s against its standing 60 s budget
  (`tests/CLAUDE.md`, pre-existing project law rather than a number invented here).
- **SC-004** The hamlet-path coverage floor is still 100% and every test still passes.
- **SC-005** Each of the five named expensive tests has either a measured reduction or a written defense.

## Decisions Recorded

This feature changes no map. Every decision it records is about what the SUITE proves and what it costs;
each one lands next to the test it governs, and any case dropped from a corpus or a seed set is recorded
with the argument that it proved nothing the kept cases do.

## Assumptions

- The GM's acceptance is the final task; more tasks are expected after these findings.
- "Materially less" is given a provisional figure in SC-001 so the criterion is measurable, but that figure
  is a floor on ambition rather than a ceiling on effort: anything cheaper found below it is reported, and the
  bar that decides the feature is the GM's at the acceptance task.
- The measurements are from this clone on 8 workers; another machine will differ in absolute terms but the
  RATIOS between the rows are what this feature acts on.
