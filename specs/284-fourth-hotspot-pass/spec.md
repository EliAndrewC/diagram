# Feature 284 - the fourth hotspot pass

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-09-28
**Status**: Draft
**Request**: [`request.md`](request.md) - the GM's words verbatim: take every lever 281's report priced, and in general
"look at what is slow and then be willing to let things of that nature change if those changes would allow it to be
significantly faster".
**Predecessors**: 281 (the third pass; its residue table in `dev/performance.md` priced these levers), 278, 276.

## Summary

The same exercise as 276, 278 and 281, with one difference the GM ruled: a lever is taken when its map change is of the
kind the GM named - a lane taking the other of two equally short routes, plot boundaries shifting within tolerance, a
tied seat resolving the other way, clumps sitting a little differently. The five pool hamlets roll in 27.95 s between
them (m:before-pool-roll-s; research R1). The levers, from the profile: the router searches toward its goal and pulls its
string with one index per route; the field's size search stops carving the largest fan blind; the page parses each
record string once; the notice board scores before it fits; the bamboo seats sample coarser; the whole-ring distance
scans and the brook toll ask indexes.

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

1. **Given** any start, goal and ground, **When** the router runs, **Then** it returns a path no longer than the old
   router's, whose every link passes the same clearance test.

### User Story 3 - The field is sized without its costliest carve (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a field whose first guess falls short, **When** it is sized, **Then** it is not carved at the largest fan
   unless the carves show the fan saturating, and it lands within the same tolerance of its target acreage.

### User Story 4 - The page reads each string once (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a finished map, **When** its page is written, **Then** the page is byte-identical to today's.

### User Story 5 - The board, the bamboo and the scans ask less (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a map, **When** the board, the bamboo seats, the fabric scans and the toll run, **Then** each asks a fraction of
   today's questions and every rule each enforces still holds.

### Edge Cases

- A route with no path: the search toward the goal explores every reachable cell, as now, and returns [].
- A field that genuinely saturates (the envelope clamps it): it is still detected, and the bracket's top still tried.
- A tie on the board where the scoring's first criterion alone decides: the same seat as today.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 The router searches toward its goal.** An admissible, consistent heuristic (the straight-line distance, never
  more than any path's cost) orders the search, so the path it returns costs no more than Dijkstra's; where two paths cost
  the same it may return the other.
- **FR-002 The router's string-pull asks one index per route** (the link test's fabric index, built once, not its memo key
  per link) **and finds the farthest clear point by a galloping search** (doubling, then halving between the last clear and
  the first fouled point) rather than by testing every point from the path's end inward. Every link it keeps is tested
  exactly as now; where visibility along the path is not monotone it may keep a nearer point, and `_unjog` still runs.
- **FR-003 The field's size search does not carve the largest fan blind.** After a first guess that falls short it carves
  at the predicted size; it probes the bracket's top only when a carve shows the fan saturating (its acreage not growing
  with its size), so a clamped fan is still found. The fit lands within the same tolerance of the same target; the
  plots may differ.
- **FR-004 The page parses each record string once** and every pass that reads its elements - the off-map cull, the merge,
  the marks' regions, the hit layer - reads that one parse. The page is byte-identical. (This is how "the page built from
  the map's records instead of re-reading the SVG" is met: the records ARE the SVG strings, and the waste is the
  re-reading; if the one parse still dominates the page after this, carrying structured primitives from `add()` is the
  next step, recorded in FR-009.)
- **FR-005 The notice board scores its candidate seats before fitting them**, fitting and captioning a seat only while it
  can still win; where two seats tie on everything the board may stand at the other.
- **FR-006 The bamboo seats sample coarser**, the stands' rules (their keep-outs and their reach from the house) unchanged;
  the clumps sit a little differently.
- **FR-007 The whole-ring distance scans ask ring indexes**: `_crosses_fabric`, `_trim_to_service` and
  `push_clear_of_fabric` measure a point against a polygon's nearby edges only, deciding as now. Exact.
- **FR-008 The brook toll reads a bitmap of the cells near the band** before any sample, deciding as now. Exact.
- **FR-009 Anything else the after-profile shows slow**, and a change of the same nature would make significantly faster,
  is taken in this feature or recorded with its price (the GM's general instruction); what is left is written down in
  `dev/performance.md` with its levers priced.
- **FR-010 Every moved map keeps its invariants**: 276's FR-006 condition in full (SC-009).

### Key Entities

- **The harness** (`harness.py`, `counts.py`, `measure.py`): 281's, re-based at `f52ed6aa8`, with this pass's buckets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (spec-wide): the five pool hamlets' summed roll time is at least `1.25x` less than the base's, fastest of
  three, back to back (27.95 s at the start, m:before-pool-roll-s; research R1).
- **SC-002** (FR-001, FR-002): the router bucket's calls are at least `2x` fewer on Kashikawa (6698394,
  m:before-kashikawa-b-router-total) and Sawada (4816861, m:before-sawada-b-router-total), and a test over recorded route
  requests shows every new path no longer than the old one's and every kept link clear.
- **SC-003** (FR-003): the field bucket's calls are at least `1.3x` fewer on Inashiro (2359101,
  m:before-inashiro-b-field-total) and Sawada (4539336, m:before-sawada-b-field-total), every field within its tolerance,
  and a test shows a saturating fan still probed.
- **SC-004** (FR-004): the page bucket's calls are at least `1.5x` fewer on Sawada (3518827, m:before-sawada-b-page-total)
  and Kashikawa (3463026, m:before-kashikawa-b-page-total), and every pool page byte-identical.
- **SC-005** (FR-005): the notice bucket's calls are at least `1.5x` fewer on Inashiro (3142523,
  m:before-inashiro-b-notice-total) and Sawada (2240617, m:before-sawada-b-notice-total).
- **SC-006** (FR-006): the bamboo bucket's calls are at least `2x` fewer on Kashikawa (674263,
  m:before-kashikawa-b-bamboo-total) and Mizuguchi (278855, m:before-mizuguchi-b-bamboo-total).
- **SC-007** (FR-007): the edge-scan bucket's calls are at least `3x` fewer on Kashikawa (1679823,
  m:before-kashikawa-b-edge-scan-total) and Kuwabata (1417401, m:before-kuwabata-b-edge-scan-total).
- **SC-008** (FR-008): the toll's cell lookups are at least `2x` fewer on Kashikawa (590253,
  m:before-kashikawa-b-toll-dict-get) and Sawada (374679, m:before-sawada-b-toll-dict-get).
- **SC-009** (FR-010, the pool): every live pool map regenerates; `make done` is green at the `100%` floor and every gate
  rule passes (the overlap rules among them); every pool map, the rescue-rounds scenario and the 10- and 20-household toys
  seat at least as many houses as today, with no new or larger shortfall, and keep their forms (dispersed or nucleated,
  the headman's house) and house kinds; every comb field's acreage stays within its tolerance of its target; each moved
  map's research entry gives its houses, paddies and ways before and after, and a material change is a finding to fix,
  not a report; and `make cohort N=24` shows no newly failing seed. The exact changes (FR-004, FR-007, FR-008) leave every
  output they touch byte-identical, shown before the moving ones land.
- **SC-010** (FR-009): `dev/performance.md` holds the after-profile's remaining costs with their levers priced; every
  figure named here is in `measurements.json`, the after-figures carrying the command that re-runs them.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The router searches toward its goal; of two equally short routes it may draw the other | map drawing convention (the same clearance rules; a tie resolved differently) | research R1; the GM's request | point of change in `hamletgen/ways/route.py` |
| The string-pull gallops to its farthest clear point | map drawing convention (every link tested as now) | research R1 | point of change in `hamletgen/ways/route.py` |
| The field's size search probes the largest fan only on measured saturation | map drawing convention (the same tolerance and target; the plots may differ) | research R1 | point of change in `hamletgen/water/fit.py` |
| The notice board fits only the seats that can still win | map drawing convention (the same scoring; a full tie may resolve the other way) | research R1 | point of change in `settlement/structures/fixtures/siting.py` |
| The bamboo seats sample coarser | map drawing convention (the same keep-outs and reach) | research R1 | point of change in `hamletgen/hinterland/bamboo.py` |

## Assumptions

- The seconds are taken back to back against the base worktree, fastest of three, with the load recorded; the counts are
  load-independent.

## Review history

(none yet)
