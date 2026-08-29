# Implementation Plan: Cut the Cost of the Hamlet-Tier Test Suite (feature 158)

**Spec**: [`spec.md`](spec.md) | **Request (authority)**: [`request.md`](request.md)

## Constitution Check (the gate at plan time)

| principle | how this feature satisfies it |
|---|---|
| **III** everything through `make` | every measurement is a make target (`quick`, `test`, `test-full`, `durations`, `check-census`); nothing bare |
| **VI** verification before "done" | a measured baseline before, the same three measurements after, and one green `make done` at the end |
| **X** 100% coverage on pure-logic packages | FR-010: the three floors are the hard bar. A cut that drops a floor is reverted or replaced with a direct unit test |
| **XII** research before a ruling | this is a TOOLING feature - no physical claim about how a place was built - so every task is `research: rendering`. The one physical-adjacent judgment (does the engine still guarantee X) is answered by READING the placer, not by guessing |
| **XIII** no known regressions | a detached worktree baseline at HEAD is not needed for the SUITE's content (tests are being deliberately deleted), but every pool manifest must stay byte-identical (FR-011/SC-006) and the gate must be green |
| **XIV** fix defects where you find them | an audit over 2,500 tests will turn up defects; they are fixed in this work |
| **XVI** the spec is reviewed before implementation | done - two rounds recorded in the spec's Review history |
| **XVIII** a guard has a test companion | no new guard is added; guards whose tests get cheapened keep their companions |

## The measured baseline (2026-08-29, this clone, 8 workers, warm)

| tier | command | tests | wall |
|---|---|---|---|
| **1 - quick** | `make quick ALL=1` | 2,206 | **41.4 s** |
| **2 - the gate's test phase** | `make test` (coverage on) | 2,583 | **116 s** |
| **2 - the same tree, no coverage, no map rolls** | `make durations N=45` | 2,390 | **45 s** |
| **3 - the full sweep** | `make test-full` | ~2,600 | measured below |

## Where the time actually is (from `make durations`)

1. **ONE test is 39.2 s of the 45 s non-rolling suite** -
   `tests/hamletgen/test_seed_branches_147.py::test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied`.
   It runs `fit_field` on a 600x600 envelope with `target_acres = 500` so every aspect saturates:
   5 aspects x 2 probe carves + 9 refinement carves on the best aspect, ~2 s per carve. It sits in
   `tests/` unmarked, so it is the critical path of `make quick` as well - which is why quick has
   drifted from the 28.9 s feature 147 measured to 41.4 s.
2. **`test_a_saturated_aspect_stops_after_the_probe...`** (`tests/hamletgen/test_water.py`) is the
   same shape at 5-8 s.
3. **Coverage instrumentation roughly doubles tier 2**: 45 s of tests becomes 116 s with the tracer.
   The project runs coverage 7.15.2 on Python 3.14 with LINE coverage only (no `branch = true`), which
   is exactly the configuration `COVERAGE_CORE=sysmon` was built for.
4. A tail of 1-5 s tests: `test_a_linear_hamlet_strings_its_houses_along_the_connector` (4-5 s, seats
   15 households twice), three `village_grove` tests (1.8-4.5 s), `test_a_belt_vertex_in_the_title_pocket`
   (1.5-2 s).
5. The full tier adds the pool sweep, the four-seed cohort and the Playwright page test.

## The approach, in order

### Phase A - the audit (US1)

A1. Baseline all three tiers, measured (above), and the per-test duration profile for the gate tree
and the full tree.
A2. Re-run `make check-census` on today's engine (feature 141's ledger is one label-phase move old)
and produce this feature's own ledger.
A3. Classify every fixture in `pool/regressions/` by tier and by whether a generator alive today can
produce it.

### Phase B - retire the checks the placer guarantees (US2)

B1. For every mechanical RETIRE-CANDIDATE, read the PLACER and ask the question the census cannot:
does the placer GUARANTEE the fact, or does it do its best and fall back? A placer with a
"keep what we have rather than nothing" arm does NOT guarantee, and its check stays. (Worked
example found during planning: `place_kosatsuba` can return `None`, and `stage_notice`'s re-seat
has an explicit `keep the engine's seat rather than none` fallback - so the three kosatsuba checks
are KEEPs that the mechanical census called candidates.)
B2. Retire what survives that reading: the segment function, its check-name fixture entry, its unit
tests, its scripted negative fixtures, its frozen fixtures.
B3. Record each retirement's disposition per FR-005.

### Phase C - the corpus (US3)

C1. Delete every frozen fixture whose manifest is a hand-authored legacy-tier map.
C2. Delete every fixture whose only `fires` are retired checks.
C3. Where a KEPT check loses its only proof, add a scripted negative fixture.

### Phase D - the cheapening (US4)

D1. `COVERAGE_CORE=sysmon` for every coverage-tracing target, with the coverage TOTALS proved
identical before and after.
D2. The 39 s test and the 5-8 s test: shrink the envelope (the subject), keeping the saturation
branch and both assertions. Prove the branch is still reached.
D3. The 1-5 s tail: smaller subjects (household counts, polygon sizes) with the break demonstrated.
D4. Anything else the durations profile turns up once D1-D3 land.

### Phase E - close

E1. Re-measure all three tiers; write the before/after into the ledger.
E2. `make done` green; every pool manifest unchanged.
E3. Push.

## Decisions Recorded

- **The census's verdict is a CANDIDATE, not a ruling.** The mechanical test ("no later stage changes
  an input") cannot see a placer that fails softly. Every retirement in this feature is a hand
  reading of the placer on top of the mechanical verdict, and the ledger records both.
- **The label checks are KEPT even where the census calls them candidates**, because the GM named
  them as the archetype of a check that earns its keep: *"in cases where, for example, we place a
  label and then later on things are added to the map, then an automated check to see whether the
  label's placement is still valid is an example of a useful automated check"* (feature 141). Feature
  157 moved the label phase late, which is what makes them look mechanically settled; the GM's own
  example is the stronger authority.
- **Coverage measurement mode is a TOOLING change, not a test change.** It alters no assertion, so it
  is proved by showing the coverage totals are identical, not by re-arguing the tests.
