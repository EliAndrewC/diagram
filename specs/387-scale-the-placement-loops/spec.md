# Feature Specification: Scale the placement loops - judge what changed, build once, ask an index

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=387-scale-the-placement-loops`)

**Created**: 2026-10-18

**Status**: Draft

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

1. **"Re-checking everything after each addition"** names three sites: **the way tree** (each candidate household way is
   admitted by judging the whole tree with it), **the web's settling passes** (each pass re-checks the whole lane network),
   **the cell merges** (each paddy-cell merge re-runs every ring rule). The GM: *"I don't think we need to re-check everything
   after each addition"* - at each site an addition is judged on what it can change, not by re-checking everything.
2. **"Rebuilding things that don't change"** names two: **the house layout geometry** (a household's bundle geometry, rebuilt
   for every reach check) and **the sun keep-outs** (rebuilt for every grove). Each is built once for the inputs it depends on
   and reused while those inputs stand.
3. **"One straight scan with no index"** names one: **the bamboo strip check** - a candidate strip is tested against the placed
   boxes, houses, fixtures and lanes NEAR it, found by a spatial index built once, not by walking all of them.

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
| the house layout geometry | rebuilt per call when it could be built once | its rolls (yard size, garden jitter, bed split, the fixtures laid round it) are keyed on the seat asked (feature 276 D10): 771 reach checks at 771 seats; the layout is already cached per seat (2,049 of 4,346 asks served) | NO - each seat's layout is a different layout |
| the sun keep-outs | rebuilt per grove | the sun boxes are remembered per plot set, but each of 1,816 asks rebuilds the plot list and its key from every yard and bed (159,808 `plot_box` calls) and filters every box | YES - the key, not the boxes |
| the bamboo strip check | a straight scan, no index | each of 1,102 candidates walks every placed box, house, fixture, lane segment and crown | YES |

## Requirements

- **FR-001 The way tree.** Admitting a candidate household way judges the way against the tree it joins and the rules the
  addition can break, not the whole tree again; the verdict equals the whole judgment's on the same tree and way.
- **FR-002 The web's settling.** The settle runs 2-3 rounds at every size (seed 4: 3 at 10 households, 2 at 40), so the
  rounds are not what grows; the growth is INSIDE steps (spec-fidelity round 1, measured 2026-10-18): the field way's candidate
  runs (`field_runs`: every sampled point of the network measured to the worked ground, 0.32 -> 1.21 s for its one call at 10 ->
  40 households) and the knots' judgments (none at 10 households, 22 calls and 0.83 s at 40). Each such step finds its candidates
  without measuring every point or re-judging every knot for each one: the work it does per candidate kept does not grow with the
  network. Not the withdrawn R12 lever (feature 297: rounds that ran only the steps the law named broken, slower and withdrawn) -
  no round is narrowed and no law is asked first.
- **FR-003 The cell merges.** Each merge judges only the union it would make; what grows is its neighbor search (spec-fidelity
  round 1, measured 2026-10-18: 3.3 shared-bund measurements per merge at 10 households, 15.7 at 40; 2.06 s of the merges'
  3.80 s), which queries an index of the cells built before any merge and measures the shared bund of every stale entry before
  duplicates are dropped. A merge measures each live neighbor once, from an index that stays current as cells absorb each other,
  so the bund measurements per merge do not grow with the household count.
- **FR-004 The house layout geometry - withdrawn as measured.** The layout is a function of the seat it is asked at (feature 276
  D10) and is already built once per seat; making it once per household would change the rolls 276 decided, not the cost of
  re-building one thing. The measurement stands in the premises table and the report; nothing is changed here.
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

- **SC-001** (FR-001, FR-002, FR-003) The work done per addition is COUNTED at each re-check site at 10, 20 and 40 households,
  seed 4, before and after - the tree lanes judged per candidate way, the network points measured per field-way candidate kept
  and the knots judged per settle, the shared-bund measurements per merge - and after the change none grows with the household
  count; the counting command and the counts are recorded in `measurements.json`.
- **SC-002** (FR-001 - FR-006, FR-009) Each site's time (the five kept, FR-004 withdrawn) at 40 households, seed 4, is reported before and after; the
  end bookend's 40-household total is reported against the start's, with both loads.
- **SC-003** (FR-007, FR-008) `make cohort` and the landing cohort pass with no seed newly failing against main; the pool
  hamlets regenerate and pass their gate; each equivalence test is green.
- **SC-004** (FR-010) `dev/performance.md` carries the three rules with their numbers.

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
