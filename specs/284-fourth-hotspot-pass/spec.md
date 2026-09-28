# Feature 284 - the fourth hotspot pass

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-09-28
**Status**: Accepted - FAITHFUL at round 5 of 5 (2026-09-28)
**Request**: [`request.md`](request.md) - the GM's words verbatim: take every lever 281's report priced, and in general
"look at what is slow and then be willing to let things of that nature change if those changes would allow it to be
significantly faster".
**Predecessors**: 281 (the third pass; its residue table in `dev/performance.md` priced these levers), 278, 276.

## Summary

The same exercise as 276, 278 and 281, with one difference the GM ruled: a lever is taken when its map change is of the
kind the GM named - a lane taking the other of two equally short routes, plot boundaries shifting within tolerance, a
tied seat resolving the other way, clumps sitting a little differently. The five pool hamlets roll in 32.168 s between
them (m:before-pool-roll-s; research R1). The levers, from the profile and the GM's table: the router searches toward its
goal, pulls its string with one index per route and runs on the coarsest lattice that strands no house; the field's size
search stops carving the largest fan blind and its rows are computed as arrays; the page is built from the structured
primitives the engine already makes; the notice board fits only the seats that can still win, on a coarser lattice; the
bamboo search walks outward; the whole-ring distance scans and the brook toll ask indexes; and the other slow stages the
profile names - the windbreak, the seam closing, the commons, the blade flush and the threshing yards' mats - are taken
too.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The pool rolls significantly faster, and every map is still the place it was (Priority: P1)

**Why this priority**: the whole point.

**Independent Test**: the harness, the base worktree and the clone back to back, fastest of three.

**Acceptance Scenarios**:

1. **Given** the five pool hamlets, **When** they roll, **Then** their summed roll time is well under the base's.
2. **Given** any moved map, **When** it regenerates, **Then** every gate rule passes and it keeps its households, forms,
   kinds and field acreage band.

### User Story 2 - The router does less and draws equally short ways (Priority: P1)

**Acceptance Scenarios**:

1. **Given** any start, goal and ground, **When** the router runs, **Then** on the same lattice A*'s path costs no more
   than Dijkstra's, every drawn link passes the same clearance test, and the new router's drawn path - A* and the
   coarser lattice together - is within the recorded bound of today's.

### User Story 3 - The field is sized without its costliest carve (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a field whose first guess falls short, **When** it is sized, **Then** it is not carved at the largest fan
   unless the carves show the fan saturating, and it lands within the same tolerance of its target acreage.

### User Story 4 - The page reads each string once (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a finished map, **When** its page is written, **Then** the page is byte-identical to today's.

### User Story 5 - The board, the bamboo, the scans and the other slow stages ask less (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a map, **When** the board, the bamboo seats, the fabric scans and the toll run, **Then** each asks a fraction of
   today's questions and every rule each enforces still holds.

### Edge Cases

- A route with no path: the search toward the goal explores every reachable cell, as now, and returns [].
- A field that genuinely saturates (the envelope clamps it): it is still detected, and the bracket's top still tried.
- The board's lazy caption test on a given candidate set: the same seat as the full evaluation (the coarser candidate
  lattice changes the set itself, FR-007).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 The router searches toward its goal.** An admissible, consistent heuristic (the straight-line distance, never
  more than any path's cost - the step is `hypot * cell` plus a toll that is never negative) orders the search, so the
  lattice path it returns costs no more than Dijkstra's; where two lattice paths cost the same it may return the other.
- **FR-002 The router's string-pull asks one index per route**: the link test's fabric index is built once for the route,
  not its memo key rebuilt per link. The pull still takes, from each point, the farthest point whose link is clear - the
  same search as now, so for a given lattice path the drawn path is exactly today's.
- **FR-003 The router's lattice is coarsened where the gaps allow.** The cell is raised from 10 toward the width of the
  narrowest gap a way must thread (`MIN_WEB_GAP`; the docstring's rule: "a lattice coarser than the gap cannot see
  the gap"), with the plan's half-diagonal clearance kept, and it is taken at the largest cell under which every pool map,
  the rescue-rounds scenario, the toys and the cohort keep every house reached - a house left without a way breaks the
  one rule a roll reports on, so a cell that strands one is not taken, and the measurement saying where it bites is
  recorded.
- **FR-004 The field's size search does not carve the largest fan blind.** After a first guess that falls short it carves
  at the predicted size; it probes the bracket's top only when a carve shows the fan saturating (its acreage not growing
  with its size), so a clamped fan is still found. The fit lands within the same tolerance of the same target; the
  plots may differ.
- **FR-005 The carve's rows are computed as array operations** - each sector's row-by-column bund vertices and their
  pushes off the supply banks, and the plot tests, as numpy arrays - with the plots allowed to shift within `fit_field`'s
  tolerance. It is judged by the field stage's wall time, fastest of three (281's lesson: calls removed are not time
  saved); if it does not pay it is recorded as tried with that measurement and withdrawn.
- **FR-006 The page is built from the structured primitives the engine already makes, and parses the rest once.** The
  scrub's and the marsh's ink - the grass and reed blades, the brush dots, the tint and glint marks - is made as tuples with
  their coordinates and extents (`_blade_groups`, `_mark_groups`) and flattened to SVG strings at the finish, and those two
  classes - the scrub's marks region included - are about 83% of the page's parsing (observed 2026-09-28, method: research
  R2's probe and the review's re-measurement); the page takes those structures as they are, not the strings. Every other record string is parsed once, and every page pass that
  reads its elements (the off-map cull, the merge, the marks' regions, the hit layer) reads that parse - every other class
  is 5% of the parsing or less, about 17% together (research R2), spread over every producer of drawing code. The page is
  byte-identical.
- **FR-007 The notice board fits only the seats that can still win.** Its final choice ranks by caption level first; the
  caption level is asked in that ranking's order and the asking stops at the first seat that holds the best level possible
  and stands in the open - exact, the same seat. And its candidate lattice along a route is coarsened (from `12` to `24` px
  between samples), so the board may stand a few feet along its verge from today's - kept only if the notice stage,
  fastest of three, is faster with it than without (the GM allowed such changes where they make things faster).
- **FR-008 The bamboo seat search walks outward from its target** and stops at the first seat that fits - the nearest, as
  the whole-square scan found it, ties broken in the old scan's order. Exact. This takes the table's bamboo lever ("sampled
  more coarsely") by removing the same wasted tests without moving a clump. Only if SC-006's floor is not met by it is the
  coarser sampling taken as well - a MOVING change then, under 276's FR-006 condition, with its own Decisions row.
- **FR-009 The whole-ring distance scans ask ring and segment indexes**: `_crosses_fabric`, `_trim_to_service`,
  `push_clear_of_fabric` and the comb's bead test (`_dry`, every segment of every water line per bead) measure a point
  against the nearby edges only, deciding as now. Exact.
- **FR-010 The brook toll reads a bitmap of the cells near the band** before any sample, deciding as now. Exact.
- **FR-011 The other slow stages are taken too - those the before-profile names and whatever the after-profile shows.** The
  before-profile names five more (research R1, R3): the windbreak's grove (`village_grove`, its draw and its gap fill), the
  seam closing (`close_seams`), the commons' scatter, the finish's blade flush, and - arrived with main's feature 282 as this
  work was re-based - the threshing yards' mats (`mat_cells`, `_lay_by_hand`), which made the homesteads stage about 3.7 to 5.1 times slower on Inashiro,
  Kashikawa and Sawada (research R3). The mats are made exactly: the same mats, found by array operations and a box prefilter. For each of them, and for anything the
  after-profile shows slow, a lever of the allowed kind is taken where one would make it significantly faster; only what
  cannot be made significantly faster without a fundamental change or a broken rule is left.
- **FR-012 What is left is written down** in `dev/performance.md`: only what FR-011 could not take, each with the measurement
  that shows why.
- **FR-013 Every moved map keeps its invariants**: 276's FR-006 condition in full (SC-011).

### Key Entities

- **The harness** (`harness.py`, `counts.py`, `measure.py`): 281's, re-based at `5f15c65bd`, with this pass's buckets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

Every ratio below is a FLOOR set with no projection behind it (the counts are measured; the fraction each lever
removes is not predicted), and every stage figure is the fastest of three with the load recorded.

- **SC-001** (spec-wide): the five pool hamlets' summed roll time is at least `1.25x` less than the base's, back to back
  (32.168 s at the start, m:before-pool-roll-s; research R1). Whether that is "significantly faster" is the GM's to judge;
  the report states the figure.
- **SC-002** (FR-001, FR-002, FR-003): the router bucket's calls are at least `2x` fewer on Kashikawa (6698373,
  m:before-kashikawa-b-router-total) and Sawada (4816914, m:before-sawada-b-router-total); a test over recorded route
  requests shows, on the same lattice, A*'s path costing no more than Dijkstra's, every drawn link clear, and the new
  router's drawn path - A* and the coarser lattice together - at most `5%` longer than the old router's for the same
  request, a bound recorded under Decisions.
- **SC-003** (FR-004, FR-005): the field bucket's calls - the size search and its carves, the seam closing counted apart
  (buckets nest exclusively) - are at least `1.3x` fewer on Inashiro (1474667, m:before-inashiro-b-field-total) and Sawada
  (2459714, m:before-sawada-b-field-total), every field within its tolerance,
  a test shows a saturating fan still probed, and FR-005 is kept only if Sawada's field stage (2.939 s,
  m:before-sawada-stage-field-s) is faster with it than without.
- **SC-004** (FR-006): the page bucket's calls are at least `1.5x` fewer on Sawada (3517145, m:before-sawada-b-page-total)
  and Kashikawa (3462419, m:before-kashikawa-b-page-total), and every pool page byte-identical.
- **SC-005** (FR-007): the notice bucket's calls are at least `1.5x` fewer on Inashiro (3142767,
  m:before-inashiro-b-notice-total) and Sawada (2240653, m:before-sawada-b-notice-total), and FR-007's coarser spacing is
  kept only if the notice stage, fastest of three, is faster with it than without.
- **SC-006** (FR-008): the bamboo bucket's calls are at least `2x` fewer on Kashikawa (674263,
  m:before-kashikawa-b-bamboo-total) and Mizuguchi (278855, m:before-mizuguchi-b-bamboo-total), the seats identical under
  the outward search (the coarser fallback, if taken, is held to SC-011's moving condition instead).
- **SC-007** (FR-009): the edge-scan bucket's calls, the comb's bead test among them, are at least `3x` fewer on Kashikawa
  (2248774, m:before-kashikawa-b-edge-scan-total) and Kuwabata (1417712, m:before-kuwabata-b-edge-scan-total).
- **SC-008** (FR-010): the toll's cell lookups are at least `2x` fewer on Kashikawa (590253,
  m:before-kashikawa-b-toll-dict-get) and Sawada (374679, m:before-sawada-b-toll-dict-get).
- **SC-009** (FR-011): each of the five named stages asks at least `1.5x` fewer calls on the map where it asks most - the
  grove's fill and draw on Kashikawa (2075676 and 824228, m:before-kashikawa-b-grove-total,
  m:before-kashikawa-b-grove-draw-total), the seam closing on Sawada (2079622, m:before-sawada-b-seams-total), the
  commons on Kashikawa (581710, m:before-kashikawa-b-commons-total), the blade flush on Sawada (1523927,
  m:before-sawada-b-flush-total), the yards' mats on Kashikawa (14288475, m:before-kashikawa-b-mats-total, with the homesteads
  stage at 2.313 s, m:before-kashikawa-stage-homesteads-s) - and is faster in wall time, fastest of three; or the plan's measurement says why
  no allowed change reaches it. The mats are byte-identical.
- **SC-010** (FR-011, FR-012): every stage the after-profile shows slow either has a lever of the allowed kind taken and is
  faster, fastest of three, or is recorded in `dev/performance.md` with the measurement showing that no change of the
  allowed kind makes it significantly faster - and that record holds nothing else; every figure named here is in
  `measurements.json`, the after-figures carrying the command that re-runs them.
- **SC-011** (FR-013, the pool): every live pool map regenerates; `make done` is green at the `100%` floor and every gate
  rule passes (the overlap rules among them); every pool map, the rescue-rounds scenario and the 10- and 20-household toys
  seat at least as many houses as today, with no new or larger shortfall, and keep their forms (dispersed or nucleated,
  the headman's house) and house kinds; every comb field's acreage stays within its tolerance of its target; each moved
  map's research entry gives its houses, paddies and ways before and after, and a material change is a finding to fix,
  not a report; and `make cohort N=24` shows no newly failing seed. The exact changes (FR-002, FR-006, FR-008, FR-009,
  FR-010, the board's lazy caption test) leave every output they touch byte-identical, shown before the moving ones land.
- **SC-012** (FR-014, Amendment 1): a stranding re-roll resumed from the first roll's snapshot gives a manifest, svg and page
  byte-identical to the re-roll built from scratch, on every map the harness finds re-rolling, and is faster (research R8);
  a stand-in-stage test shows the stages before the seats run once and every resume starts from the untouched copy.
- **Counts that move between runs of the same code** (observed 2026-09-28, method: round 1's `make figures` re-run): the
  fabric bucket by tens of thousands (Kuwabata 702611 and 731256, Sawada 776100 and 762559) and anything beneath the
  fabric index by a few calls - the router's (Kuwabata 1134922 and 1134924) and the clip's (Sawada 7390 and 7388) - with
  the id-keyed memo's hits (281's Amendment 1). No floor above is set on the fabric bucket or the clip bucket, and the router's
  moves are far inside its floor.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The router searches toward its goal; of two equally short routes it may draw the other - WITHDRAWN, Amendment 1 (faster, but the moved maps broke gate rules) | map drawing convention (the same clearance rules; a tie resolved differently) | research R1; the GM's request | point of change in `hamletgen/ways/route.py` |
| The router's drawn path may be up to `5%` longer than today's for the same request - where A* picks another lattice path of the same cost, or the coarser lattice (FR-003) draws the way differently - WITHDRAWN, Amendment 1 (the router draws today's paths) | map drawing convention (the same clearance rules; the bound tested, SC-002) | research R1 | point of change in `hamletgen/ways/route.py` |
| The router's lattice cell is the largest that strands no house - measured: 10 px, today's (Amendment 1; observed 2026-09-28, method: `b2/harness.py`) | map drawing convention (measured; a stranding cell is not taken) | FR-003 | point of change in `hamletgen/ways/route.py` |
| The carve's rows as arrays, kept only if faster - WITHDRAWN, Amendment 1 (slower) | map drawing convention (plots within the fit's tolerance) | FR-005 | point of change in `waterfields/sector_rows.py` |
| The field's size search probes the largest fan only on measured saturation - WITHDRAWN, Amendment 1 (faster, but the moved maps broke gate rules) | map drawing convention (the same tolerance and target; the plots may differ) | research R1 | point of change in `hamletgen/water/fit.py` |
| The notice board's candidates sampled every `24` px along a route, not `12`, kept only if faster - WITHDRAWN, Amendment 1 (broke the entrance rule) | map drawing convention (the same rules and ranking; the board may stand a few feet along its verge) | FR-007 | point of change in `settlement/structures/fixtures/siting.py` |
| Bamboo clumps may sit a little differently - taken only if the outward search misses SC-006's floor - TAKEN, Amendment 1 (16 ft) | map drawing convention (the same keep-outs and reach; coarser sampling) | FR-008 | point of change in `hamletgen/hinterland/bamboo.py` |

## Amendment 1 (2026-09-28): what the measurements decided

Each lever the spec made conditional was measured, and the measurements decided it; one lever the after-profile found is
added under FR-011's own rule ("whatever the after-profile shows"). What changed from the accepted spec:

- **FR-003 withdrawn by its own rule** (research R4): on the engine that ships, the first cell tried, 12 px, strands houses
  the 10 px lattice does not (8 unreached over every attempt against 5, on cohort seed 08 and Sawada, each healed by its
  re-roll), and no coarser cell is faster in all, so the largest cell before it is today's 10. The lattice is unchanged, the
  constant named (`ROUTE_CELL`) with the measurement at the point of change.
- **FR-005 withdrawn by its own rule** (research R5): the plot tests' edge walk in arrays is 3.6 times slower than the
  scalar walk over the same 3,310 calls on Sawada (0.312 s against 0.086 s), with the same verdicts; the vertices' pushes
  total 0.024 s scalar, under the loss already measured.
- **FR-006's "parses the rest once" not taken, on its ceiling** (research R7): with the scrub's and the marsh's structures
  carried to the page, the passes that re-read a string the page already read - the off-map cull and the hit copies - cost
  0.051 s of Kashikawa's page and 0.059 s of Sawada's together (observed 2026-09-28, method: `parse/harness.py`, each pass
  timed inside the page write, fastest of three, load 12.5 - a ceiling, since load inflates it); one parse could at most
  remove those, about 1% of a roll. The merge itself (0.17-0.18 s) is work, not a re-parse. The page bucket met SC-004
  without it (1.76x on Sawada, 1.77x on Kashikawa, the final measure.py after).
- **FR-007's coarser lattice withdrawn**: at 24 px the entrance board stood on a straggler at its join, the rule
  `test_an_entrance_board_stands_on_the_approach_and_not_on_a_straggler_at_its_join` enforces, so the spacing stays 12 px
  (the reason at `BOARD_ALONG_STEP_PX`). In its place an exact lever: at the lane tiers the roadside rule keeps only the
  verge band whenever it holds a seat, so the verge band is sampled first and the rest only when it holds none - the same
  candidates, in the same order (`VERGE_FIRST`, tested against the whole-band sampling).
- **FR-008's coarser sampling taken**, as the spec required when the outward walk missed SC-006 on Mizuguchi (1.23x): the
  bamboo seat lattice is 16 ft, not 8 (`BAMBOO_SEAT_STEP_FT`); the Decisions row already covers it.
- **FR-014 (new, under FR-011): a stranding re-roll resumes at the seats.** The after-profile's costliest item that is not a
  stage: a roll that strands a house pays a whole second build (two of the 29 rolls of research R4 at 10 px on the engine
  that ships, six of 29 with the moving levers in). The avoid list a re-roll carries is first read at `stage_homesteads`; the first roll keeps a copy of
  itself before that stage and each re-roll resumes from a fresh copy. Exact: manifest, svg and page byte-identical to a
  re-roll built from scratch on six re-rolling maps, each re-roll 1.1-1.7 s faster (research R8).
- **FR-001 and FR-004 measured faster, and withdrawn on the rules** (research R6): each moving lever was judged by the pool
  and cohort seeds 1-24 rolled whole, against the run-to-run spread measured in the same run. On the engine that ships
  FR-004 was 5% faster against a 1% spread, A* 2.4% against 0.6%, both together 4.8% (344.75 s off against 327.27 s and
  329.37 s on). But the maps they moved failed the gate on the shipped pool - a bund built as a flight of steps, woodland
  parcels in a ruled row, a copse off its house's bank, brook legs on a screen axis, Sawada's seat off the regional wind -
  and the pool itself was no faster (23.76 s with them against 23.89 s without). The GM allowed map changes for speed within
  the rules only; both are withdrawn, the base's router order and field search restored, the reasons at the points of change.
- **A defect found and fixed (constitution XIV)**: a connector the web could not join was deleted as debris by the junction
  pass, and the reach check then passed on the network that was left - cohort seed 15 shipped a hamlet with no way off the
  map (research R6). The pass never drops the connector now; every roll of R6's three runs, 87 rolls each, draws its connector.
- **What the final measurement shows** (measure.py after, the base worktree and the clone back to back, loads 2.0-5.6; the
  pool as research R6's table leaves it - Kashikawa re-rolled once, so its counts from the seats on are two builds' against the
  base's one). **SC-001 met**: 23.764 s against 32.494 s, 1.37x (m:after-pool-roll-s, m:base-rerun-pool-roll-s). Met:
  SC-002 (the router, 2.37x and 6.06x), SC-003 (the field, 2.11x and 2.97x), SC-004 (the page, 2.75x and 1.70x), SC-005 (the
  notice board, 1.58x and 2.00x), SC-006 (the bamboo, 4.65x and 4.02x), SC-008 (the toll's lookups, 590,253 to 11,780 on
  Kashikawa and 374,679 to 4,855 on Sawada), the mats (10.4x, byte-identical) and the blade flush (1.74x). Missed, each with
  why no allowed change reaches it (SC-009's and SC-010's own exit):
  - SC-007's `3x` on the edge-scan bucket (1.78x on Kashikawa over its two builds, 2.39x on Kuwabata): `edge_dist` itself
    fell from 32,850 calls to 912 on Kuwabata (m:after-kuwabata-b-edge-scan-edge-dist); what the bucket still counts is the
    ring indexes' own queries beneath the four entries and the track's push (now box-prefiltered too).
  - SC-009 on the grove fill (1.21x) and draw (0.66x) and the commons (0.48x), all on Kashikawa over two builds, and the seam
    closing on Sawada (0.87x - its field, moved by FR-004, closes 822 pockets where the base's closed 727): research R7 - the
    grove draw is 2-3% of a build and its crown test a fifth of that; the commons and the fill are sums of indexed lookups;
    the seam closing's moving levers are priced there (fewer welds leaves doubled bunds; dropping its `simplify` buys 1-2%).
    The grove draw's crown grid (A6) is exact and its stage no slower; it asks more, smaller calls than the scan it replaced.
- **FR-009 carried one more scan**: the track's `push_clear_of_fabric` asked every polygon's ring at every step; it asks only
  the polygons whose widened box holds the point (exact: tested against the old walk, and on all 72 of Sawada's calls).

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The router's lattice stays 10 px | map drawing convention (measured: every coarser cell tried strands a house; observed 2026-09-28, method: `b2/harness.py`) | research R4 | point of change in `hamletgen/ways/route.py` (`ROUTE_CELL`) |
| The carve's rows stay scalar | map drawing convention (measured: arrays slower) | research R5 | this amendment |
| The board's lattice stays 12 px; its verge band sampled first | map drawing convention (the same board; the coarser lattice broke the entrance rule) | this amendment | point of change in `settlement/structures/fixtures/siting.py` |
| The router and the field search keep the base's forms | map drawing convention (measured: the moving levers broke gate rules on the shipped maps) | research R6 | points of change in `hamletgen/ways/route.py` and `hamletgen/water/fit.py` |
| The junction pass never drops the connector | historically accurate (a hamlet has its way out; the rule the connector already carries) | research R6 | point of change in `hamletgen/ways/touch.py` |
| A stranding re-roll resumes from the first roll's copy before the seats | map drawing convention (exact: the same map) | research R8 | point of change in `hamletgen/driver.py` (`resume_at`, `resume`) |

## Assumptions

- The seconds are taken back to back against the base worktree, fastest of three, with the load recorded; the counts are
  load-independent.

## Review history

- Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - the field's rows-as-arrays and the router's coarser grid were
  missing; the page lever was narrowed to one parse; the comb's `_dry` scan was dropped from the whole-ring scans; the
  galloping pull contradicted "no longer than today's"; the general instruction was weakened and the slow stages the
  profile already names were not taken. Addressed: FR-003 (the coarser lattice, measured against stranding), FR-005 (the
  rows as arrays, kept only if faster), FR-006 (the page from the structured blades and marks, the rest parsed once),
  FR-009 with `_dry`, FR-002 keeps the pull exact and SC-002 bounds the drawn length, FR-011 takes the four named
  stages; the floors are labeled as floors; the moving counts are named.
- Round 2 (spec-fidelity-verify, 2026-09-28): CHANGES REQUIRED - SC-002 compared costs across lattices; FR-006 carried
  structure only for the scrub and marsh with no measurement of the rest; FR-011/FR-012 left the after-profile to be
  recorded; the moving counts understated; the board's edge case and coarser lattice; the bamboo swap unstated; the crown
  bucket counted nothing. Addressed: SC-002 and US2 on the same lattice with the bound on the whole router; research R2
  measures the page's parsing by class (most of it in the two structured classes); FR-011 takes the after-profile
  under the same rule and FR-012 records only what cannot be taken; the moves given with their sizes; the board's edge
  case narrowed and its coarser lattice kept only if faster; FR-008 states the swap; the crown callee named by its
  qualified name.
- Round 3 (spec-fidelity-verify, 2026-09-28): CHANGES REQUIRED - R2 misattributed the scrub's marks region; SC-010 still
  priced what FR-012 now takes, and the after-profile clause had no criterion; the bamboo fallback contradicted "exact";
  SC-005 did not test the keep-if-faster; the counts note implied a clip floor; the crown figures still read 0. Addressed
  (R2 and FR-006 on the corrected share, SC-010 rewritten over the after-profile, the fallback a moving change with its Decisions row,
  SC-005's condition, the note corrected, and the whole base re-taken at `5f15c65bd` - main having merged 282, which moved
  every pool manifest - with the corrected crown callee).
- Round 4 (spec-fidelity-verify, 2026-09-28): CHANGES REQUIRED - the slowdown range, four stages left in three places, the
  harness base in Key Entities, R3's figures unlabeled. Addressed.
- Round 5 (spec-fidelity-verify, 2026-09-28): FAITHFUL.
