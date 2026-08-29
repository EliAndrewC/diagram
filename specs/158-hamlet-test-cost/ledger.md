# Feature 158 - the audit ledger

Every cut and every cheapening this feature made, with what it cost, what carries its guarantee now,
and - where a lever was tried and did not work - what the measurement said. The census of the check
battery is the machine-generated `ledger.json` / the table this file's "The checks" section reads
from; this file is the decisions.

## 1. The three tiers, before and after

See `research.md` R1 for the baseline's conditions. Warm-versus-warm comparisons only: the
non-rolling profile (`make durations`) and `make quick` never touch the roll cache, so those two are
the fair unit-test numbers.

| tier | before | after |
|---|---|---|
| **1 - `make quick ALL=1`** (pytest half) | 40.6 s, 2,206 tests | see §6 |
| **the non-rolling suite** (`make durations`, no coverage) | 45.2 s, 2,390 tests | see §6 |
| **2 - the gate** | see §6 | see §6 |
| **3 - the full sweep** | 390.6 s, 2,794 tests (1 pre-existing failure) | see §6 |

## 2. The checks - what was retired, and what carries it now

The census (`make check-census`, run on today's engine, `ledger.json`) returned **154 check names,
130 KEEP, 13 RETIRE-CANDIDATE, 10 NO-SCRIPTED-EXECUTOR, 1 VACUOUS-ON-SCRIPTED**. The mechanical
verdict is a CANDIDATE, never a ruling: it can see whether a later stage changes an input, and it
cannot see a placer that fails softly. So every candidate got a hand reading of its placer.

### Retired (3 checks, 19 segments)

| check | why it went | what carries it now |
|---|---|---|
| `bridges_align_with_their_way` | it re-derived the way x water crossings from the SAME shared source `settlement.bridges()` places from (`city/bridges.py` says so in its own docstring) and then asked whether the deck it had been handed sat on the crossing it had just computed - the same measure of the same fact. Its whole evidence in the record is two decks a person placed BY HAND on Minami and Nagahara in July 2026, on maps no generator can produce. Every deck `s.bridges()` has ever solved landed 0.0-1.0 px and 0.0-1.0 deg off its crossing | `settlement.bridges()`, which computes the deck's seat and rotation FROM the crossing - there is no path by which it can produce a crooked one |
| `bridges_seat_on_water` | fired exactly once in the whole record, on Shiro Daika's hand-authored towpath plank | the same placer: a deck exists because a crossing was found, and the crossing is on water by construction |
| `bridges_clear_of_houses` | never fired anywhere, on any map, ever - no frozen fixture, no cohort pin, no waiver | accepted loss of rigor (*"It is okay if the tests become slightly less rigorous"*). A plank is placed on a ditch crossing, and no farmhouse stands on a ditch |

Their whole derivation subgraph went with them - **19 segments** (0334-0338 and 0341-0344 in `06a`,
0360-0363 in `06b` were restored for the KEEP below, 0416-0419 in `07a`), including `_seg_0338`'s
ways x waters double loop, which the gate had been running on **every map** to feed a single retired
verdict. The cut was proved **closed** before it was made: a script compared every name a surviving
segment declares as an input against every name only a deleted segment writes, and the intersection
was empty.

### A candidate KEPT against the mechanical verdict, and why

**`bridges_span_their_water`** measures the same family and the census called it a candidate on the
same grounds. It is kept. The reason is in the engine's own comments: `hamletgen/ways.py` records it
catching the **scripted** placer four separate times on oblique crossings ("a 7 px stream at 17
degrees, and `bridges_span_their_water` failed the deck it produced"). A placer with four recorded
misses does not guarantee the fact; this is exactly the case feature 141's doctrine describes as
"its placer only does its best". Its derivations (0360-0363) were deleted and then restored when
this reading came in - recorded here because it is the single most useful thing in this audit: **the
census's dataflow verdict and the record of what has actually fired disagree, and the record wins.**

### The 10 NO-SCRIPTED-EXECUTOR names are a NAMING ARTIFACT, not a cut

`capital_has_kosatsuba`, `city_has_kosatsuba`, `town_has_kosatsuba`, `village_has_kosatsuba` and the
four `*_has_no_headman` are not separate checks. They are ONE segment each, emitting
`check(f"{scale}_has_kosatsuba", ...)` and `check(f"{scale}_has_no_headman", ...)` - the hamlet
variant is live and proved, and the others are the same line seen at a scale nothing currently
rolls. There is no code to delete and no time to save; retiring them would mean adding a branch, not
removing one. Recorded so the next audit does not chase them again.

### Six segments that were ALREADY dead (Principle XIV - a defect fixed where it was found)

`_seg_0187__wall`, `_seg_0285_008__yards`, `_seg_0285_024__sheds`, `_seg_0286_000__cems`,
`_seg_0286_007__wall`, `_seg_0286_008___inside`. Each computes a value that **no** surviving segment
declares as an input, so the gate has been executing them on every map for nothing. Found by the
closure analysis written for the retirement above. Deleted.

## 3. The stored bad maps

**26 frozen fixtures deleted** - every one in `pool/regressions/` whose manifest declares a legacy
tier (town, city, capital, village). These are the GM's category exactly: *"there is no reason to see
what would happen if we encountered a type of map, which is literally impossible to produce any
longer"*. Four more went with the retired bridge checks. The corpus is **134 -> 104**.

**One of the 26 was ALSO the full-gate coverage SENTINEL, and deleting it broke a test** - caught by
the closing full-tier run, fixed rather than reverted.
`settlement_wells_fire_on_a_village_with_no_wells.json` was a hand-authored Kikuta village with its
wells taken out, picked by feature 022's greedy line-coverage search, and
`tests/full/test_coverage_carriers.py` loaded it by name. Its remaining job was to keep full-mode
`gate()` - no `only=`, every segment, the shared derivations end to end - under test inside the
suite, and a REAL ROLL does that better: the sentinel is now the cached reference hamlet through the
whole gate, asserted clean, plus one deliberate break (its wells removed) that the gate must still
name. Recorded because the lesson generalizes: **a fixture's tier tells you whether it is a hand-era
map; it does not tell you what else is holding on to it.**

**What was NOT deleted, deliberately**: the 35 fixtures that declare no tier at all. Those are
synthetic manifests captured from unit tests - hand-BUILT minimal manifests, not maps from the
hand-placement era - and feature 141 kept them for that reason.

**Three hamlet-relevant checks lost their only proof** to the tier cut and got the post-141
replacement instead of a record of the loss: `water_channels_obtuse_turns`, `field_ditches_terminate`
and `paddy_fan_has_floor` now have scripted negative fixtures in `tests/gate/test_scripted_fixtures.py`
- a cached roll and one deliberate break. `field_ditches_terminate` had to point at the POLDER rather
than the reference hamlet: only the polder grid draws `lateral` ditches (8 on seed 19; Inashiro has
none), so a break on Inashiro would have proved nothing. That is the kind of vacuity a fixture hides
and a scripted break exposes.

**A correction to a figure the spec review reported.** Round 2 of `spec-fidelity` counted 42
registered checks with "no firing proof of any kind". That count looked only at the scripted fixtures
and the frozen corpus; it did not count `tests/check_village/test_segments_*.py`, where most checks
are proved to fire on a hand-built manifest. Measured properly: before this feature, **10 of 154**
had no firing proof anywhere; after the corpus cut and the three new scripted fixtures, **13 of 151**
- and 6 of those 13 are the naming artifact above.

## 4. The cheapenings

Each is FR-009-bound: the test still fails when the behavior it names is broken.

| test | before | change | how it is still honest |
|---|---|---|---|
| `test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied` | **39.2 s** | the carve runs on a coarse plot grid: `plot_across` 46 -> 138, `row_step` (26,30) -> (78,90), so the largest fan is 257 plots instead of 1,985 | `make cov-file` proves the branch it exists for (`fit_field`'s re-search, `water.py` 128-135) is still executed; the acreage error is unchanged at 0.891 and the same aspect wins |
| `test_a_saturated_aspect_stops_after_the_probe_instead_of_bisecting_a_fan_it_cannot_grow` | 5.1-8.2 s | the same coarse grid | its two assertions (`not bad and err > 0.5`, a non-empty fan) hold on the measured values |
| `test_a_linear_hamlet_strings_its_houses_along_the_connector` | 3.9-4.8 s | 10 households instead of 15 (the floor `HamletSpec` accepts) | the assertion counts seated households and still fails if the frontage loop drops one |
| `test_village_grove_keeps_the_windbreak_out_of_a_plots_west_sun_lane` | 3.9-4.5 s | the band narrows in x to 250-400 and in y to 320-580 | narrowed only where the lane strip is not - the "and the belt still stands" arm still has ground on both sides of the strip, and it is asserted |
| `test_village_grove_keeps_every_clump_and_set_view_decides_which_are_on_the_page` | 1.8-2.3 s | half the band; the cutting crop moves with it (260 -> 180) | the assertions are about the PARTITION, not the size: no clump lost, every drawn one reaches the page, every off-page one wholly off |
| `test_a_windbreak_reseating_round_a_house_stays_inside_the_within_box` | 4.3 s | half the band, same house, same `within` box | `0 < narrow < wide` still holds |
| `test_village_grove_skips_the_dike_bank` | 2.3-2.6 s | a 1,600 px dike ring instead of 3,000 px | a NEW precondition asserts the earthwork still runs through the belt's footprint, so the skip cannot pass for the wrong reason |
| `test_a_belt_vertex_in_the_title_pocket_is_pushed_out_of_it` | 1.5-2.0 s | 10 households, so the derived canvas is smaller | the dent is measured against the title pocket, which is derived, not fixed |
| `test_a_comb_hem_is_registered_as_CROPLAND_not_only_as_no_build_ground` | 5.6 s | canvas 1800 -> 1200, fall 800 -> 520 | the test already carried its own guard: *"the fixture must actually draw a dry hem, or it proves nothing"* |
| `test_a_map_is_immune_to_an_upstream_change_in_the_number_of_random_draws` | **214 s** (the full tier's largest item) | TWO Kashikawa rolls instead of three - the perturbed roll runs FIRST, so the clean one runs last and leaves the committed manifest as it should be | the claim needs one perturbed roll and one clean roll; the third only restored a file |

## 5. Two levers MEASURED AND REJECTED

Recorded because the next session will reach for both.

**Shrinking the test settlement does nothing for the 39 s test.** The obvious reading of the GM's
own example - *"reducing the size of the test fixture settlement"* - was tried first. Taking
`plan.envelope` from a 600 px square down through 400, 300, 200 and 150 leaves the drawn fan at
**1,985 plots and an acreage error of 0.891 at every single one**: the envelope is not what clamps
this fan. What clamps it is the canvas, which is derived from the household count, and what costs the
seconds is the PLOT COUNT, which is set by the two arguments the test passes. Full table in
`research.md` R3.

**`COVERAGE_CORE=sysmon` is SLOWER here, not faster.** Python 3.14 plus coverage 7.15 with line-only
coverage is exactly the configuration `sys.monitoring` was built for, and the tracer looked like half
of tier 2. Measured, on the same tree, same selection: **ctrace 16.2 s wall / 1 m 30 s CPU; sysmon
20.1 s wall / 1 m 59 s CPU**, with the coverage tables byte-identical. Rejected. The tracer also
turned out not to be half of tier 2 at all - the 116 s baseline had a cold roll cache in it, and the
coverage overhead on a warm tree is small. A hypothesis this feature would have shipped on
plausibility alone, and the measurement killed it.

## 6. The closing measurements

Filled from the verification run - see the "after" section appended below.

## 7. Ledgered, NOT fixed by this feature

**A pre-existing failure in the full tier, measured on the merge base before any change:**

    FAILED tests/gate/hamletgen/test_driver.py::test_a_rolled_cohort_passes_the_whole_gate
    REGRESSION seed 42: farmhouses_reach_a_way - not in the pinned baseline

The merge-scope gate rolls seed 41 only and is green; the drift is on seed 42, which only the full
tier rolls. It is NOT this feature's (constitution XIII: pre-existing failures stay ledgered and are
not fixed under someone else's feature) and, more importantly, the only way to make the full tier
green would be to ADD a pin - which would silence a real map defect rather than fix it. That is the
GM's call, not a session's.
