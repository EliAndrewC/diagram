# Feature Specification: cut the cost of the test suite

**Feature**: 147-test-suite-cost
**Created**: 2026-08-29
**Status**: DRAFT - audit complete, awaiting `spec-fidelity` before implementation

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
| whole tree, FULL env, no coverage, map rolls DESELECTED | 2,347 | **12 s** |
| whole tree, FULL env, no coverage, map rolls included | 2,417 | **262 s** |
| the full sweep (adds coverage + the three floors), WARM | 2,417 | **234 s** |
| the `rolls_map` tests alone, FULL env, no coverage | 69 | **166 s** wall / ~430 s CPU |

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

The GM asks for a one-line change and the session must prove it merges clean. Today the pre-push sweep costs
234 s warm; the GM's stated goal is that a five-minute change does not become a half-hour of machine time.

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

- **FR-001** The suite MUST prove everything it proves today. No check loses its negative fixture, no pool
  map goes ungated, the determinism guarantee and the cohort ratchet both stay, and the hamlet-path coverage
  floor stays at 100%. A saving bought by deleting a proof is not a saving; it is a scope reduction, and this
  feature does not have that mandate.
- **FR-002** The 31 scripted negative fixtures MUST share ONE roll of their common spec per worker process
  rather than each rolling it, with each test receiving geometry it can mutate without affecting any other.
- **FR-003** The shared roll MUST still execute under the coverage floors, so the floor's derivation and its
  100% bar are unaffected. Where sharing would hide execution from coverage, the sharing is not taken.
- **FR-004** The five named single tests (cohort 155 s, determinism 105 s, pool round-trip 32 s, fan-out 22 s,
  re-roll 18 s) MUST each be examined and either cut, reduced to the smallest input that still proves the
  property, or KEPT with a written statement of what its time buys.
- **FR-005** Every reduction in seeds, corpus size or map count MUST record what was dropped and the argument
  that the dropped case proved nothing the kept cases do not.
- **FR-006** The cheap loop MUST stay inside its 60 s budget, and no cost may be moved from the sweep into it.
- **FR-007** Timings recorded by this feature MUST state COLD or WARM. The docs' existing figures that are
  now known to be cold MUST be corrected.
- **FR-008** The audit's before/after numbers MUST be recorded in the feature's research so the next
  efficiency pass starts from measurements rather than from a fresh profile.

### Key Entities

- **the roll cache** (`pipeline/rollcache.py`) - serves a recorded roll when nothing it executes changed;
  bypasses SERVING under the FULL run so coverage sees real execution.
- **the scripted fixture corpus** (`tests/gate/test_scripted_fixtures.py`) - 31 tests, one roll plus one
  deliberate break each.
- **the cohort ratchet** and **the determinism test** - the two most expensive single tests.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** The full sweep WARM completes in materially less wall time than the 234 s baseline, with the
  achieved figure recorded. The target is under 90 s; anything above it is reported with its reason.
- **SC-002** The scripted-fixture group costs about one roll in total rather than 31.
- **SC-003** The gate and the cheap loop are no slower than their measured baselines (52 s pytest / 26 s).
- **SC-004** The hamlet-path coverage floor is still 100% and every test still passes.
- **SC-005** Each of the five named expensive tests has either a measured reduction or a written defense.

## Decisions Recorded

This feature changes no map. Every decision it records is about what the SUITE proves and what it costs;
each one lands next to the test it governs, and any case dropped from a corpus or a seed set is recorded
with the argument that it proved nothing the kept cases do.

## Assumptions

- The GM's acceptance is the final task; more tasks are expected after these findings.
- "Materially less" is quantified as the SC-001 target rather than left to judgment.
- The measurements are from this clone on 8 workers; another machine will differ in absolute terms but the
  RATIOS between the rows are what this feature acts on.
