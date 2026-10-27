# T57 - why a 40-household roll takes 18 million calls, and what would cut it

Feature 417 T57, written 2026-10-27 for the GM's check-in (his words, `request.md`, "The approach checked"): *"another round
of in-depth analysis on why we are making so many millions of function calls to place such a small number of things"*.
Nothing here is built; the ranked list at the end is for the GM to choose from.

**How the figures were taken.** Seed 39, the reference spec at 40 households.
- *Measured* figures are `make perf-fanout LABEL=417-T57` (`dev/perf-log/20261027T121422Z-fanout-417-T57.txt`), each
  (size, stage) job in a fresh process, and `make perf-profile SEED=39 STAGE=<stage> HOUSEHOLDS=40` for eight stages,
  measured 2026-10-27.
- *Estimated* savings are the share of a stage's profiled time a function holds (cumulative), applied to the stage's
  calls. In pure Python calls track time closely, but these are estimates, labeled so, until a change is measured.

## 1. Where SC-009 stands

| when | calls at 40 households |
|---|---|
| feature 427's start (2026-10-26) | 62.6M |
| feature 417's start | 29.7M |
| now, after T70 | **18,364,392** |
| SC-009's bound | 6.3M |

SC-009 is **not met**: T57 ends on its red exit, the miss recorded here. Wall time at 40 households is about 6-7.5 s a
seed (`make perf LABEL=417-speed SCALING=1`, `dev/perf-log/20261027T121020Z-417-speed-diagram-backlog.json`).

A measurement defect, fixed in this task: the fanout reused worker processes, and caches a job left behind made a later
job count fewer calls. The 40-household homesteads stage counted 4,798,222 calls after its worker had rolled the
20-household stage and 5,204,554 in a fresh one (measured 2026-10-27). Every job now runs in a fresh process, so
fanouts compare. Earlier fanouts in `dev/perf-log/` may be low by up to about 8% on the stages that ran second in a
worker.

Unrelated to speed, noted so it is not mistaken for a regression: seed 4 at 40 households is refused
(`WebRefused`, `joins_short`) in every snapshot since feature 427's start.

## 2. What each stage costs per thing it places

| stage | calls @40 | what it places (manifest) | calls per thing |
|---|---|---|---|
| homesteads | 5,205,031 | 40 houses, 40 yards, 52 gardens, 85 access corridors, the site boundary | ~130,000 per house |
| web | 3,278,818 | 41 lanes | 79,971 per lane |
| field | 2,869,318 | ~335 paddy cells, plots, ditches and channels | 8,565 |
| hinterland | 2,543,420 | 1,069 scrub pines, 42 crowns, 5 commons, a grove | 2,236 |
| lane wells | 1,267,184 | **2 wells** | **633,592 per well** |
| windbreak | 1,119,945 | 3,597 tree crowns | 311 |
| notice | 779,962 | **1 notice board** | **779,962** |
| appurtenances | 494,974 | 121 fixtures, 99 crowns, 33 persimmons, 17 byres, 2 wells | 1,819 |
| seat | 204,913 | (the cluster's seat, not a manifest list) | - |
| woodland | 205,647 | 1,929 tree crowns | 106 |
| crossings | 125,028 | 18 bridges | 6,946 |
| labels | 107,013 | the label layer | - |
| sink | 77,448 | 1 pond and its channels | 11,064 |
| washing | 30,524 | 1 washing place | 30,524 |
| sties | 27,684 | 23 fixtures | 1,203 |
| frame | 18,062 | title and scale bar | - |
| track | 8,548 | 1 lane | 8,548 |
| bamboo | 742 | 7 stands | 106 |
| water frame, waterward, pond stock, burial, pond bank | 131 together | - | - |

The eight stages over 0.49M hold 17.56M of the 18.36M (96%); the other fifteen together hold 0.81M.

For the big four, what multiplies (each a count from the profiles, measured 2026-10-27):
- **homesteads**: 160 placement tries and 2,506 bundle geometries built for 40 houses; 416 reach questions, 3,364
  standing-ground tests and 13,393 way-leg tests for 40 households' ways.
- **web**: 41 lanes; `end_serves` asked 948 times, which asks `ring_within` 70,555 times; the tree's `off_the_needle` 2,460
  and `closes` 4,800 times; `doubled_tails` asks 7,314 pairs.
- **field**: 1,398 cell verdicts and 1,416 ring-rule checks for about 335 cells, 157 merges; 22,427 bank clearances.
- **hinterland**: `open_ground_region` asked 3,541 times and `patches._ok` 4,368 times for 1,069 pines and 5 commons.

## 3. The cross-cutting finding: most calls are arithmetic one value at a time

Across the eight heavy stages' profiles (17.56M calls, measured 2026-10-27):

| kind of call | share |
|---|---|
| Python builtins (`len`, `dict.get`, `max`, `min`, `list.append`, `isinstance`, `math.hypot`, `round`, `math.dist`...) | **58%** |
| generator and lambda bodies (the inner loops themselves) | 10% |
| placement and rule logic (the engine's own functions) | 16% |
| geometry primitives and spatial indexes | 8% |
| libraries (shapely, numpy, PIL) | 7% |
| imports | 1% |

So about two thirds of the calls are a candidate's coordinates being compared, one number at a time, against the
segments, rings and boxes near it. No single loop owns them: the top builtin callers each hold under 3% (`seg_dist`'s
231,765 `hypot`, the spatial index builds' 168,438 + 104,022 `append`, shapely's per-object wrapper's 226,777
`isinstance`). It is the shape of the whole engine, a candidate tested in Python against each thing near it, not one
bad function. That is why the speed lane's function-by-function work has given less each time.

## 4. The patterns behind the multipliers

**A. A lattice of candidates, each fully tested.** The wells try 73,249 seat points (`_seat_ok`) and 1,746 full overlap
admissions (`well_at`) to seat 2 wells in `lane_wells` (and 824 more in `appurtenances`). The notice board runs 1,561
whole house-fit tests (`_fits`) over 42 route-seat searches for one board. The windbreak tests 9,971 seats for 3,597
crowns; the hinterland asks `open_ground_region` 3,541 times. Nothing cheap screens the candidates first.

**B. The whole set re-asked for each candidate.** The households' ways judge each candidate against the whole access
tree (`tree_admits`, 103 calls, about 13% of homesteads); the web's tree settle asks `off_the_needle` 2,460 times and
`closes` 4,800 times, pair against pair; a lane end's service asks `ring_within` 70,555 times. A change touches one or two
lanes, but the whole web is asked again.

**C. The same geometry rebuilt.** A homestead bundle's geometry is built 2,506 times for 40 houses (`_bundle_geom`,
`_bundle_template`: about 63 a house, ~12% of homesteads), though a bundle differs only by its translation, rotation and
fixture roll.

**D. Drawn, then checked, then mended.** The field cuts its cells and then judges and merges them (`settle_cells`: 1,398
verdicts, 157 merges, about 40% of the field); the web's settle (about a third of the web); the windbreak plants its
crowns and then trims back to the wood goal (`trim_to_goal`, about a quarter of the windbreak).

**E. Shapely one object at a time.** 19,272 shapely calls in homesteads, 47,776 in the field, each through its per-call
wrapper - shapely 2 takes whole arrays.

## 5. What would cut it - ranked by estimated saving per cost

Savings are estimates (section's method above); cost is S (one landing, a day or less), M (a task of a few landings),
L (a refactor across modules).

| # | change | stage(s) | est. saving | cost | pattern |
|---|---|---|---|---|---|
| 1 | Wells: one feasibility mask over the seat area (numpy), then the overlap admission asked of the best few seats only | lane wells, appurtenances | ~1.5M of ~1.7M (the 1.7M measured: `seat_wells` is 0.726 of `lane_wells`' 0.732 s and 0.324 of `appurtenances`' 0.353) | M | A |
| 2 | Notice board: screen route seats against an index of houses and yards before the full house-fit test | notice | ~0.6M of 0.78M | S | A |
| 3 | Homestead bundle geometry built once per (form, size, fixtures) and moved into place | homesteads | ~0.5M | S | C |
| 4 | Windbreak planted to its wood goal instead of planted and trimmed; its index filled in one batch | windbreak | ~0.5M | S-M | D, A |
| 5 | The access tree judged incrementally - only the lanes a candidate touches (T54's owed judgment, upper bound 1.2M) | homesteads, web | ~0.7-1.2M | M-L | B |
| 6 | The web's tree pair checks (`off_the_needle`, `closes`) asked box-first, as T61 did for the settle | web | ~0.7M | M | B |
| 7 | Open ground asked of a raster built once, not region by region (with T66's three deferred sites) | hinterland | ~0.6M | M | A |
| 8 | Paddy cells cut by the ring rules, the settle's judge-and-merge gone (T12, in the correctness phase) | field | ~0.8M | M-L | D |
| 9 | The rest of T06 (the settle's remaining repair steps; in the correctness phase) | web | ≤0.78M | M-L | D |
| 10 | The shared geometry layer vectorized: `seg_dist`, `point_in_poly`, ring and segment distance, the spatial index builds and shapely asked on arrays of candidates | every stage | ~3-5M | L | E, and A's inner loops |

**What they add up to** - upper bounds, not a sum of independent cuts: items 5 and 6 both act on the web's tree pair checks (an incremental judgment would take most of what box-first asking saves there), and item 10 vectorizes the same inner loops that items 1, 4 and 7 remove by searching less, so its 3-5M is a share of today's 10.2M builtins, not of what is left after 1-9. The time-share proxy under-counts call-dense subtrees (a builtin costs little time per call), so the wells and notice estimates are, if anything, low. Items 1-4 (the S and M items, about 3.1M) would take the roll to about 15M. With 5-9 (about
3.6-4.1M more, the correctness-phase items among them), about 11M. Reaching SC-009's 6.3M needs item 10 as well:
about two thirds of the calls are the scalar inner loops of section 3 (SC-009's 6.3M is itself an estimate, the session's of 2026-10-26 of what an engine laid by construction reaches, which the GM confirmed - a goal, not a measured floor), and only a change to how those loops are written
- arrays of candidates, one call for many - removes them in bulk. That is the large decision, and the GM's to price.

**What I would do first** (a recommendation, the GM's to decide): items 2, 3 and 1, in that order (cheapest first, about 2.6M together - items 2 and 3 a landing each, item 1 a few -
measured by the fanout; the roll then about 15.7M), then a short spike on item 10 - one predicate
(`seg_dist` over many candidates) vectorized and measured in its hottest caller - to put a measured number on the
large item before committing to it.
