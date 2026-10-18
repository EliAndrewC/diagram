# Feature Specification: Scale the placement loops - judge what changed, build once, ask an index

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=387-scale-the-placement-loops`)

**Created**: 2026-10-18

**Status**: Done 2026-10-18 - T01-T07 ticked; make done green; landing cohort 54/54 (fresh 6 of 48); spec accepted by the round arbiter at its round cap, plan CLEAR; FR-004 withdrawn as measured

**Approved**: the GM, 2026-10-18, "I don't think we need to re-check everything after each addition, and you've already proposed fixes for the others, so please file a feature for this and then make it happen."

**Affects**: hamlet

**Input**: `request.md` - the GM's question, the session's profile of a 40-household roll and its three-bullet diagnosis, and
the GM's approval, verbatim. "All of this" is the three bullets quoted there.

## Why

At 40 households the reference hamlet's stages take 15-20 s a seed, and 10 -> 40 households grows ~5x (observed 2026-10-18;
method: `make perf SCALING=1` and `make perf-profile ... HOUSEHOLDS=40`, `request.md`). No single function is hot; the cost is
in the SHAPE of five loops. The hamlet band stops at 20 households (research question 0001), so 40 is the measuring roll's
size, not a map anyone draws; it matters because the village, town and city tiers will run these same placers at their sizes.

## The three bullets, read literally

This section reads the GM's words; what the code was measured to do at each site is the premises table below, and where a
premise did not hold the requirement is restated on the measurement (FR-002, FR-003) or withdrawn (FR-004).

1. **"Re-checking everything after each addition"** names three sites: **the way tree**, **the web's settling passes** and
   **the cell merges**. The GM: *"I don't think we need to re-check everything after each addition"* - at each site the work
   done for one addition does not re-do what that addition cannot change.
2. **"Rebuilding things that don't change"** names two: **the house layout geometry** and **the sun keep-outs** - built once
   for the inputs they depend on, and reused while those inputs stand.
3. **"One straight scan with no index"** names one: **the bamboo strip check** - a candidate strip is tested against what
   stands NEAR it, found by a spatial index, not by walking everything.

The session's own estimate in the diagnosis ("should cut the 40-household time by well over half") is an estimate, not a bar
the GM set; this feature measures and reports what each change bought (SC-002).

## User scenarios

### User story 1 - a bigger settlement costs in proportion to its size (P1)

The GM asks for a larger settlement and the time it takes grows with its size, not with its size squared.

**Acceptance**: at 10, 20 and 40 households, the work each re-check site does per addition - counted, not timed - does not grow
with the household count (SC-001).

### User story 2 - the maps keep their rules (P1)

Faster placement draws maps held to the same rules: nothing is loosened, coarsened or skipped to buy speed.

**Acceptance**: the cohort and the pool hamlets pass as they did on main (SC-003); where a site's new judgment can give a
different answer from the whole check, the difference is shown on the cohort and recorded at the point of change.

## The premises, measured before planning (2026-10-18)

The diagnosis the GM approved was read off one cProfile table. Before any plan, each site's premise was checked against the code
and the call counts (`make perf-profile SEED=4 STAGE=<stage> HOUSEHOLDS=40`, callees read from the raw profile). The GM's goal
is the one in the bullets - a placer's cost should grow with what it is asked, not with everything already on the map - and
where a premise did not hold, the requirement below is the form of that goal the code admits, or a withdrawal with its measurement.

| site | the premise | what the code does | holds? |
|---|---|---|---|
| the way tree | each candidate way re-judges the whole tree | `ways/tree.admits` rebuilds every lane's drawn form (`lanes_of`) and asks the whole tree for needles, fronting ends, doubled bands and walked shadows - pairs and faces no candidate touches - for each of 88 candidates | YES |
| the web's settling | 36 passes, each re-checking the whole web | 2-3 rounds of the 18 settle steps at every size (36 step calls = 2 x 18); the growth is inside steps - the field way's candidates measured from every network point, the knots judged | NO as stated; the re-done work is inside two steps |
| the cell merges | each merge re-runs every cell's ring rules | each merge judges only the union it would make (`Fabric.merge` -> `verdict`); its NEIGHBOR SEARCH grows - an index built once and never updated, every stale entry's shared bund measured before duplicates drop (3.3 measurements a merge at 10 households, 15.7 at 40) | NO as stated; the re-done work is the neighbor search |
| the house layout geometry | rebuilt per call when it could be built once | its rolls (yard size, garden jitter, bed split, the fixtures laid round it) are keyed on the seat asked: 771 reach checks at 771 seats; the layout is already cached per seat (2,049 of 4,346 asks served); keying it per household was tried and withdrawn (297 R9) | NO - each seat's layout is a different layout |
| the sun keep-outs | rebuilt per grove | the sun boxes are remembered per plot set, but each of 1,816 asks rebuilds the plot list and its key from every yard and bed (159,808 `plot_box` calls) and filters every box | YES - the key, not the boxes |
| the bamboo strip check | a straight scan, no index | each of 1,102 candidates walks every placed box, house, fixture, lane segment and crown | YES |

## Requirements

- **FR-001 The way tree.** Admitting a candidate household way judges the way against the tree it joins and the rules the
  addition can break, not the whole tree again; the verdict equals the whole judgment's on the same tree and way.
- **FR-002 The web's settling.** The settle runs 2-3 rounds at every size (seed 4: 3 at 10 households, 2 at 40), so the
  rounds are not what grows; the growth is INSIDE steps (observed 2026-10-18; method: spec-fidelity round 1, `make perf-profile SEED=4 STAGE=web HOUSEHOLDS=<10|40>` under cProfile): the field way's candidate
  runs (`field_runs`: every sampled point of the network measured to the worked ground, 0.32 -> 1.21 s for its one call at 10 ->
  40 households) and the knots' judgments (none at 10 households, 22 trials and 0.83 s at 40, each trial asking the whole web's counts again).
  The field way finds its candidates without measuring every point: the work it does per candidate kept does not grow with
  the network. A knot's trial gather moves only the lanes it edits, so of the whole web's five counts (`_WHOLE_RULES`) the trial
  re-asks only where an edit can change them: `doorstep_ends` (the free ends at each house - an edit changes its own ends and
  the junctions of ends within the touch gap of the edited lane's old or new LINE, since `fronting_ends` tests an end against the
  whole way), `doubled_tails` and `shadows` (pair by pair - an edit changes only the pairs it is in) and `needle_loops` (a face
  that meets no edited lane's old or new line is the same face before and after the edit, so only the faces that meet one are
  judged; the web is still noded and polygonized whole, one shapely call). One stays whole: `way_outs` (each household's way out
  is a route through the whole web, which one moved end can re-route anywhere). Not the withdrawn R12 lever (feature 297: rounds
  that ran only the steps the law named broken, slower and withdrawn) - no round is narrowed and no law is asked first.
- **FR-003 The cell merges.** Each merge judges only the union it would make; what grows is its neighbor search (spec-fidelity
  round 1, measured 2026-10-18: 3.3 shared-bund measurements per merge at 10 households, 15.7 at 40; 2.06 s of the merges'
  3.80 s), which queries an index of the cells built before any merge and measures the shared bund of every stale entry before
  duplicates are dropped. A merge measures each live neighbor once, so the bund measurements per merge do not grow with the
  household count. The index is NOT made current: a cell a staircase split makes is one it never held, so indexing it would find
  merges the current code cannot and move maps against FR-007 - recorded as a defect found and reported (SC-005).
- **FR-004 The house layout geometry - withdrawn as measured.** The layout is already built once for the inputs it depends on:
  its template is cached on a key that includes the seat it is asked at (`bundle._bundle_template`), and the rest of
  `_bundle_geom` (the turn, the turned boxes, the persimmon) depends on that position - so each reach check is a different
  layout. Keying it on the household instead was TRIED AND WITHDRAWN (feature 297, plan C, research R9, recorded at
  `place.py`'s `_place_bundle`): the yard's size rolled once per household lost the per-seat rolls that fit a large-yard
  household into a tight spot, and seed 3 seated 9 of 10 households and had its site refused. Nothing is changed here.
- **FR-005 The sun keep-outs.** The plots' sun boxes and their key are built once for each state of the yards, beds and placed
  homesteads they read (invalidated by the registries' own versions, never by a count or identity guess), and a grove's ask is
  answered from a spatial index of them, not a filter over all.
- **FR-006 The bamboo strip check.** A candidate strip asks spatial indexes, built once per pass and kept current as things
  are placed, for what stands near it; the verdict equals the straight scan's.
- **FR-007 Equivalence first (this governs FR-001 - FR-006).** Each change is proved verdict-equivalent to the code it replaces - by a test that runs both on
  the same inputs - unless it cannot be; a change that alters an answer says so at the point of change and in the plan, and the
  maps it moves are judged against the rules (cohort, pool hamlets), never byte-identity (`l7r/diagram/CLAUDE.md`,
  "Performance").
- **FR-008 No rule loosened.** No check is removed, coarsened, sampled or given a wider tolerance to buy speed
  (`dev/performance.md`: a slow check is INDEXED, never coarsened).
- **FR-009 Measured.** Bookends `make perf LABEL=387-start SCALING=1` before the first engine edit and `-end` after the last,
  taken back to back on a quiet machine where possible, each with its load; per-site profiles at 40 households before and after.
- **FR-010 Recorded.** `dev/performance.md` gets the general rule each site illustrates (judge the addition, build once,
  index the scan), with its measurement.

## Out of scope

- The hamlet household band (10-20, research question 0001) stays; the CLI keeps refusing 40 households. The GM: *"I don't
  want to contradict the research."*
- Rendering the scaling legs (the GM declined: "No thanks").
- Hot spots the three bullets did not name (the commons byres' clearance checks, open-ground patches, grove index inserts): noted
  in the report as the next candidates, not changed here.
- The memory trades in `dev/performance.md` "Time traded for memory" are not undone.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003) The work done per addition is COUNTED, before and after, from profiles at 10, 20 and 40
  households, seed 4 (`m:counts-before` and its after): the tree lanes judged per candidate way, the network points measured per
  field-way candidate kept and the shared-bund measurements per merge - after the change none grows with the household count;
  and, at 40 households (the only size seed 4 makes knot trials at: 0 at 10 and 20), the ends, lane pairs and faces (those whose width is tested) re-asked per
  knot trial are fewer than the web's total ends, pairs and faces. The counting command and the counts are recorded in
  `measurements.json`.
- **SC-002** (FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-009) Each site's time (the five kept, FR-004 withdrawn) at 40 households, seed 4, is reported before and after; the
  end bookend's 40-household total is reported against the start's, with both loads.
- **SC-003** (FR-007, FR-008) `make cohort` and the landing cohort pass with no seed newly failing against main; the pool
  hamlets regenerate and pass their gate; each equivalence test is green.
- **SC-004** (FR-010) `dev/performance.md` carries the three rules with their numbers.
- **SC-005** (FR-002, FR-003, FR-004) The landing report to the GM names FR-004 as withdrawn, with its measurement and 297 R9,
  says that FR-002's and FR-003's premises were restated from the diagnosis the GM approved, each with what was measured, and names FR-003's
  split-part defect.

## Assumptions

- The five stages are profiled on the reference spec (nucleated, pond), the one the bookends time; the other forms run the
  same placers and are covered by the cohort.

## Review history

- **spec-fidelity round 1 (2026-10-18): CHANGES REQUIRED, 4 items.** (1) FR-003's premise was wrong: a merge judges only its
  union; the growth is the stale neighbor index (3.3 -> 15.7 bund measurements a merge) - FR-003 restated on it. (2) FR-002's
  premise was wrong: 2-3 rounds at every size; the growth is inside `field_runs` and the knots' judgments, and R12 was unmentioned -
  FR-002 restated on the measured steps, and set apart from R12. (3) SC-001 counted judgments per addition, which the quadratic
  shape passes at 1 - restated as the work per addition, counted. (4) "the diagnosis did not name" -> "the three bullets did
  not name". Its note on FR-001 vs FR-007: FR-007 now says it governs. The session's own premise checks (the premises table,
  FR-004 withdrawn as measured, FR-005 restated on the key) were made in the same pass.
- **spec-fidelity round 2 (2026-10-18): CHANGES REQUIRED, 3 items.** (A) SC-001's knots count was per settle, which grows with
  the knots - now the ends re-asked per knot trial, FR-002's own bar. (B) "The three bullets, read literally" still restated the
  premises the table marks NO - it now reads the GM's words and points at the table. (C) FR-004's withdrawal ruled faithful on
  two conditions: its reason cites 297 R9 (keying per household tried and withdrawn, seed 3 lost a household), not 276 D10; and
  the report to the GM is required - SC-005. With them, FR-003's "an index that stays current" was taken out (the plan keeps the
  index as it was, D3) and the split-part defect is reported under SC-005.
- **spec-fidelity round 3 (2026-10-18): CHANGES REQUIRED, 3 items.** (1) FR-002's knots sentence promised more than the plan:
  it now names which whole-web counts a trial re-asks locally (`doorstep_ends`, `doubled_tails`, `shadows`) and which stay
  whole, with why (`way_outs`, `needle_loops`). (2) The knots count could not be judged across sizes (trials only at 40 on seed 4)
  - the bar is now at 40 households, re-asked against the web's totals. (3) SC-005 had no task - plan and tasks T07 carry it.
- **spec-fidelity round 4 (2026-10-18): CHANGES REQUIRED, 2 items.** (1) `doorstep_ends`' local set named too few ends: a gather
  moves a lane's middle (`teed_onto`, `contracted`) and `fronting_ends` tests an end against the whole way - now the ends within
  the touch gap of the edited lane's old or new LINE. (2) SC-001's knots clause had no failing case - now "fewer than the web's
  totals", and "none grows" covers only the three-size counts. Its note on the needle test (plan D1 local, FR-002 whole): made
  one - both judge only the faces that meet a changed lane, the arrangement polygonized whole; `way_outs` alone stays whole.
- **spec-fidelity round 5 (2026-10-18): CHANGES REQUIRED, 1 item** - tasks T02 named three of FR-002's four local counts; it now
  names `needle_loops` too, `way_outs` whole. Its note on SC-001's faces: the faces counted are those whose width is tested.
  The round cap reached, the arbiter's ruling follows.
- **round-arbiter (2026-10-18), trigger round:spec-fidelity|387-scale-the-placement-loops#1@6: ACCEPT** - the review converged
  (4, 3, 3, 2, 1 items, none repeated, round 5's a stale task line, applied); the spec stands as round 5 left it. Its tooling fix
  (the arbiter bundle carries each round's verdict file with each finding marked) is an open item of this feature.
