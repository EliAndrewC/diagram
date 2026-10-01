# Feature 297 - placement by construction

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-09-30
**Status**: Accepted - FAITHFUL at round 3 (2026-09-30)
**Request**: [`request.md`](request.md) - the GM's words verbatim: Inashiro's times are "much higher than I'd expect" (">1s is a
lot to place 15 farmhouses ... it's hard to believe that's actually necessary"; "1.9s to generate the interactive HTML map
seems like a lot"; "12,000 drain-bank clearance checks"; "roughly 100,000 spatial-index lookups for the hinterlands ...
instead of drawing a box and then filling it in with a much simpler algorithm"), and then: "Yes, please build and implement
all of that as a spec-kit feature, working it from start to finish" - "all of that" being the session's three levers (the
house seats from a precomputed reachable-and-buildable region with the lane test once per seat; the marsh, village grove and
open-ground fill as region-then-fill; the lane rules kept true as the lanes are laid rather than checked afterward), the
page's Python work run alongside its picture (the side question), and the GM's own two counts.
**Predecessors**: 284 (the fourth hotspot pass, its harness re-based here), 287 (the placer guarantees: every placement rule
asked at its placer - this feature changes WHEN and HOW OFTEN those rules are asked, never which rules).

## Summary

Inashiro regenerates in about 7.5 s: the stages about 5.0 s, the finish about 1.9 s (research R1; observed 2026-09-30, method: `make map PROFILE=1` with scratch phase marks). The time is not spent placing
what the map shows; it is spent building candidates in full and refusing them. The seating offered 734 seats for 15 houses,
built 2,716 garden-side layouts and then ran 902 part-rule tests on them, and asked for a lane corridor 477 times, and 348 of those asks
found no corridor candidate at all - a property of where the house stands, asked only after its four layouts were built
(research R2, R6). The
hinterland asks each marsh tuft, grove crown and woodland candidate of every keep-out one at a time; the web lays lanes, then
re-asks the whole lane law of the whole web every round and drops what breaks it. This feature turns each into construction:
the region a thing may occupy is computed once from what stands, candidates are proposed only from it, and what is laid is
lawful when it is laid. The page's own Python work runs while its picture renders.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The reference hamlet regenerates much faster, and is still the place it was (Priority: P1)

**Why this priority**: the whole point - the GM's numbers.

**Independent Test**: the harness (research R1), the base worktree and the clone back to back, fastest of three.

**Acceptance Scenarios**:

1. **Given** Inashiro, **When** it is regenerated, **Then** its stages take at most half the base's time (SC-001) and its
   `make map` regeneration is faster end to end.
2. **Given** any pool map, **When** it regenerates, **Then** every gate rule passes and it keeps its households, form, kinds
   and acreage band (SC-009).

### User Story 2 - A house is seated by asking where it can stand, not by refusing where it cannot (Priority: P1)

**Acceptance Scenarios**:

1. **Given** the standing map and its access tree, **When** the seating looks for the next seat, **Then** it is offered seats
   only from the region where a homestead can stand and a door can reach the tree, computed once per change to what stands.
2. **Given** a seat, **When** it is judged, **Then** the questions that depend only on where the house stands are asked once,
   before any of its garden-side layouts is built, and a seat that fails them builds none.
3. **Given** a homestead's threshing yard, **When** its mats are laid, **Then** they fill the yard's free ground directly.

### User Story 3 - Ground cover is region-then-fill (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a marsh, a village grove or the woodland search, **When** it fills its ground, **Then** the region it may use is
   computed once from every keep-out it reads, and each glyph or candidate is read against that region - not tested against
   each keep-out in turn - with the same keep-outs and the same densities.

### User Story 4 - The lanes are lawful as they are laid (Priority: P1)

**Acceptance Scenarios**:

1. **Given** the web's construction, **When** a lane is laid, **Then** it is admitted against the lane law then - the rules
   that read it alone, and the rules that read it with the lanes it meets - and refused or reshaped at that moment, so the
   web has nothing left to repair afterward.
2. **Given** a finished web, **When** the stage ends, **Then** no whole-web repair round and no whole-web re-asking of the law
   runs; the web's refusal of a broken result (`WebRefused`) reads the verdicts kept as the lanes were laid.

### User Story 5 - The page and the field ask less (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a finished map, **When** its page is written, **Then** the page's Python work that its picture does not need
   runs while the picture renders.
2. **Given** a carved field, **When** its plots are held off the drain, **Then** only the plot corners near the drain are
   measured against it, and every bund still stands off the drain.

### Edge Cases

- A seat region that is empty: the seating moves to the next margin (`margin_ladder`) and past the last refuses the site
  (`SiteRefused`), as now - the region only replaces the offering, never the refusal.
- A seat inside the region that the full placer still refuses (a part-level rule: sun, fixtures, the wood share): it is
  refused as now; the region is a necessary condition, not a sufficient one.
- A lane that cannot be laid lawfully: it is not laid (or is laid in its lawful shape), at the moment of laying; a house the
  web then cannot reach is refused by name as now (`refuse_unreached`).
- A marsh or grove whose region is empty draws nothing and records nothing, as a footprint that drew nothing does now.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 The seat region.** The seating computes, once per change to what stands (each seated house, each reserved
  corridor), the region where a homestead's envelope can stand on buildable ground and a door can reach the access tree on
  lawful ground, and offers the placer seats only from it - every round, the exhaustive pass included. The placer's own rules
  are unchanged and still decide each seat.
- **FR-002 A seat is judged once before its layouts** (the four layouts of a seat share one house and one yard, 558 of 558
  seats measured, research R6, so the seat's own questions decide for all four). The questions that depend only on where a house stands - the reach to
  the field, the water, the corridor to the access tree's nearest points clear of the standing ground - are asked once per seat
  before any garden-side layout is built; a seat that fails them builds no layout, and the four layouts of a seat that passes
  share their answers.
- **FR-003 The threshing-yard mats are a fill** of the yard's free cells, computed once per yard, under the same mat rules.
- **FR-004 Region-then-fill for the ground cover.** The marsh (its tint, tufts and glints), the village grove (its crowns, in
  every role), and the open-ground search for managed woodland each compute the free region they may use once - every keep-out
  they read today, painted into one region - and fill or scan it from that region; per glyph or candidate, only what depends on
  the glyphs already placed (their own spacing) is asked one at a time. The keep-outs, densities and spacings are unchanged.
- **FR-005 The lane law kept true as the lanes are laid.** Every lane the web lays - the skeleton, the web lanes, the access
  tree's lanes, the joins and spurs - is admitted against the lane law when it is laid: the rules that read one lane on its
  own, and the joint rules for the lanes it meets. A lane that would break a rule is reshaped or not laid at that moment. The
  settle's repair rounds and the last resort's whole-web re-sweeps are retired; the verdicts kept as lanes are laid are what the
  end of the stage reads, and a web that breaks the law is still refused by name (`WebRefused`), never shipped.
- **FR-006 The page's Python work runs alongside its picture.** The page's work the picture and the id map do not need (the
  hit regions, the explanations and their data) runs while the picture and the id map render.
- **FR-007 The drain-bank hem measures only the corners near the drain** (a box test first) - the GM's 12,000 checks asked only
  where a corner can be within reach of the collector, every bund still held off the drain.
- **FR-008 What is left is written down** in `dev/performance.md`: for each stage still over half a second on Inashiro after this work,
  and for the page write (the GM: "1.9s to generate the interactive HTML map seems like a lot" - its picture is 1.197 s of it,
  research R1, observed 2026-09-30, method: the scratch phase marks), what its time is spent on and why no change of the allowed kind takes it further.
- **FR-009 Every moved map keeps its invariants** (276's FR-006 condition, as 284 held it): SC-009.

### Key Entities

- **The harness** (`harness.py`, `counts.py`, `measure.py`): 284's, re-based at `c5a631f9b` (main when this feature was claimed),
  every map's spec read from its own generator, with this feature's buckets (seats, corridor, bundle, mats, marsh, grove,
  open_ground, commons, web, law, field, hem, seams, page).
- **The seat region**: the buildable, reachable ground a seat may be offered from, kept current as what stands changes.
- **The free region** of a ground cover: every keep-out the cover reads, painted once.
- **A lane's verdict**: what the lane law says of a lane, kept from the moment it is laid.

## Success Criteria *(mandatory)*

### Measurable Outcomes

Every figure is the fastest of three with the load recorded, taken by `measure.py` from the base worktree and the clone back to
back; every ratio is a floor with no projection behind it. Keys `m:...` are in `measurements.json`.

- The harness's "before" seconds were taken at load 6.4 -> 2.0 and the `make map` figure re-taken at 1.0 -> 1.4 (recorded per key); the
  after-run re-takes the base back to back, and the floors are judged on that pair.
- **SC-001** (spec-wide) (the session's expectation, "well under half", held as a floor - the GM gave no number): Inashiro's stages sum to at most half the base's (5.640 s, the sum of the per-stage keys `before-inashiro-stage-<stage>-s`), and its `make map`
  regeneration (the child with its svg, png and page) is faster than the base's (6.1 s uncached, `m:before-inashiro-regen-s`, re-taken at load 1.0 -> 1.4 back to back with the clone; first read 8.0 s at
  load 2.5 -> 6.1, observed 2026-09-30, `measure.py regen-before`; research R1).
- **SC-002** (FR-001, FR-002): on Inashiro the seats bucket asks at least `3x` fewer calls (2,640,745, `m:before-inashiro-b-seats-total`), the homestead layouts built
  (`_bundle_geom`) are at least `3x` fewer (2,716, `m:before-inashiro-bundle-geom`), and the homesteads stage is at least `2x` faster (1.114 s, `m:before-inashiro-stage-homesteads-s`).
- **SC-003** (FR-003): the mats bucket asks at least `3x` fewer calls on Inashiro (477,299, `m:before-inashiro-b-mats-total`), every
  mat rule still holding.
- **SC-004** (FR-004): the marsh, grove and open-ground buckets each ask at least `3x` fewer calls on the map where each asks most
  (marsh on Sawada 2,039,897, `m:before-sawada-b-marsh-total`; grove on Inashiro 2,212,731, `m:before-inashiro-b-grove-total`; open ground on Inashiro 1,712,847, `m:before-inashiro-b-open-ground-total`), and Inashiro's hinterland stage is at least `2x` faster (1.016 s, `m:before-inashiro-stage-hinterland-s`).
- **SC-005** (FR-005): the law bucket (the last resort and the settle's exit question) asks at least `5x` fewer calls on Inashiro and
  Sawada (3,989,351 and 456,889, `m:before-inashiro-b-law-total`, `m:before-sawada-b-law-total`), no repair round runs on any pool map (`web_settle.rounds` reports none), and Inashiro's web stage is at least
  `2x` faster (1.067 s, `m:before-inashiro-stage-web-s`).
- **SC-006** (FR-006): Inashiro's page write is faster than the base's by at least `0.25 s` (the hit regions' 0.115 s and the
  explanations' 0.207 s, research R1's phase marks), measured by the same marks.
- **SC-007** (FR-007): the hem bucket asks at least `3x` fewer calls on Inashiro (759,058, `m:before-inashiro-b-hem-total`; 12,195 drain-bank clearances, `m:before-inashiro-b-hem-drain-bank-clearance`), every bund held off the drain.
- **SC-008** (FR-008): every stage over half a second on Inashiro after the work, and the page write, has its entry in
  `dev/performance.md`, with the page's remaining parts timed (the picture's render and encode, the id map, the text passes).
- **SC-010** (FR-004, the GM's second count): the spatial-index lookups (`PointGrid.near`) beneath Inashiro's hinterland stage are at least
  `3x` fewer (102,164, `m:before-inashiro-b-hinterland-stage-pointgrid-near`).
- **SC-009** (FR-009, the pool): every live pool map regenerates; `make done` is green at the `100%` floor and every gate rule
  passes; every pool map and `make cohort N=24` seat every declared household (no `SiteRefused` or `WebRefused` newly raised) and
  keep their forms and house kinds; every comb field stays within its acreage tolerance; each moved map's houses, paddies and ways
  are given before and after in research, and a material change is a finding to fix, not a report. No output is held
  byte-identical: the GM, 2026-09-30, "it is perfectly acceptable for maps to change as a result of these optimizations. They do
  NOT need to remain identical in output."

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Seats offered only from the computed seat region; a house may stand at a different seat of the same rules | map drawing convention (the same rules decide; the order of offering changes) | FR-001; the GM allows map changes for speed within the rules | point of change in `hamletgen/homesteads/` |
| Marsh glyphs, grove crowns and woodland patches placed by region-then-fill may sit differently, at the same densities and keep-outs | map drawing convention | FR-004 | points of change in `settlement/land/wet.py`, `settlement/homestead_parts/stands.py`, `hamletgen/hinterland/parcels.py` |
| ~~Lanes admitted lawful as laid~~ - withdrawn (R14); the settle repairs after the web as before, its verdicts kept per lane and a dangling lane its trim cannot mend dropped at the step | map drawing convention (the same lane law) | FR-005, Amendment 1 | `hamletgen/ways/keeper.py`, `settle.settle_dangling` |
| Any other output the levers touch (a seat judged once, the yard's mats as a fill, the hem's prefilter, the page's order of work) may differ where the rules allow | map drawing convention (the same rules; GM 2026-09-30: maps "do NOT need to remain identical in output") | FR-002, FR-003, FR-006, FR-007 | the points of change |

## Amendment 1 (2026-10-01): what the measurements decided

Each lever was built and measured by the wall clock (research R10: cProfile charges calls, and misled twice); what changed from
the accepted spec, each with its evidence:

- **FR-005, the lane law, built as measured (research R11).** The web cannot be lawful at each write: its construction passes lay
  it in pieces and join it later, and ends dangle and are joined from pass to pass, so a lane judged at its write would be refused
  before the pass that completes it; asking the law at every pass costs more than the settle. What was built: the law's pure
  verdicts KEPT per lane (`ways/keeper.py` - a lane unchanged since its last ask is answered from the keeper) and a defect fixed
  (`settle_dangling` never dropped a lane its trim could not shorten, though its docstring said it did; on Inashiro that one lane
  ran the whole last resort, which no longer runs there). A later round asking the law and running only its broken rules' steps
  was built and measured slower on two of three maps (R12), and withdrawn: the rounds are as before.
  `WebRefused` is unchanged. **This is narrower than the GM's lever ("kept true as the lanes are laid, rather than checked
  afterward")**: the law is still asked, and the web still repaired, after it is laid. Plan D2-D4 were built and
  measured over the five pool maps and cohort seeds 1-24 (R14), three ways: at the pass boundary (10 of 23 webs refused, 1.38x
  slower); at each write with every repair (21 of 29 broken or unreached, one raising - a harness bug, fixed); and at each OUTERMOST
  write with the network-wide repairs held to the end as plan D1 and D4 state (16 of 22 webs broken or unreached, two raising
  because the construction passes walk the lane list by index while a repair drops lanes from under them, and the web 1.72x slower).
  Withdrawn under the plan's rule - slower and failing the gate after the fixable failure was fixed; making the web lawful at each
  write means re-writing its construction passes, an overhaul. **The GM is to be told.**
- **FR-002, the seat's own questions, reordered (R10).** The field's reach and the water are asked before any layout; the corridor
  - the costliest question - once per seat, after the four layouts are built and the envelope tested: asked first, it ran on every
  offered seat (325 searches against 166). So "a seat that fails them builds no layout" now holds for the field's reach and the
  water only; a seat that fails the corridor has built its four layouts first. The GM's lever ("the lane test once per seat rather
  than once per orientation") is met. Plan C's second half, the layout keyed per household, was withdrawn: the per-seat yard-size rolls were the seating's only
  way to fit a large-yard household into a tight seat, and seed 3 lost a household (R9).
- **FR-001, the seat region, as built (plan Amendment 1 B1).** The static ground and the access tree's corridors are painted and
  kept current; the seated homesteads are NOT painted (the placer's one computed move rescues a seat lapping one neighbor - painted,
  Inashiro seated no one), so the region is not recomputed for each seated house's box, only for each new corridor.
- **FR-004, the grove, as built (B3, R16).** The fill's region answers "clear"; where it reads taken, the exact families are asked in
  turn to say which (a hard edge drops the clump, a local obstacle re-seats it) - so User Story 3's "not tested against each keep-out
  in turn" holds for the open ground only. The regions-alone form (three rasters by family deciding) was built and withdrawn under
  the plan's rule: it failed woods W25 at the gate (a reserved wood seat refused by a keep-out's margin), for 0.06 s a map.
- **FR-004, the regions painted in C (R10).** Every region paints with PIL's own primitives and a two-cell margin; buffering each
  shape with shapely first was most of a region's cost and made the hinterland slower than the base. The marsh and the grass read
  their keep-out grid as one painted region (`KeepoutGrid.taken_many`).
- **FR-007 (R10)**: the comb's hem asks every plot's corners at once (`hem_rings_to_bank`); asked a ring at a time the array's fixed
  cost made Sawada's field slower; the single-ring hem is the scalar walk again.
- **What the measurements say of each success criterion** (`measure.py after` on the final engine, base `c5a631f9b` and the clone
  back to back; `m:` keys in `measurements.json`):
  - SC-001: Inashiro's stages 4.460 -> 3.730 s, 1.20x - MISSED (the floor was half); `make map` 6.1 -> 5.8 s (`m:before-inashiro-regen-s`,
    `m:after-inashiro-regen-s`) - met. The pool 25.1 -> 22.5 s, 1.12x.
  - SC-002: the seats bucket's calls ROSE, 2,640,745 -> 3,525,463 (the region's own painting and labeling are calls); the layouts
    built 2,716 -> 1,479 (1.84x); the homesteads stage 0.999 -> 0.854 s (1.17x) - MISSED (3x, 3x, 2x).
  - SC-003: the mats' calls 477,299 -> 215,696 (2.2x) - MISSED (3x); every mat rule holds (`test_every_pool_yard_lays_lawful_mats`).
  - SC-004: the marsh on Sawada 2,039,897 -> 257,151 (7.9x) - met; the grove on Inashiro 2,212,731 -> 1,950,264 (1.13x) and the open
    ground 1,712,847 -> 1,200,562 (1.43x) - MISSED; the hinterland stage 0.944 -> 0.798 s (1.18x) - MISSED (2x).
  - SC-005: the law's calls on Inashiro 3,989,351 -> 281,486 (14.2x) - met; on Sawada 456,889 -> 271,242 (1.68x) - MISSED (5x); repair
    rounds still run (the settle is kept, R11-R12) - MISSED; Inashiro's web stage 0.761 -> 0.387 s (1.97x) - just MISSED (2x).
  - SC-006: the page write 1.648 -> 1.462 s, 0.19 s (observed 2026-10-01, method: a scratch timer round `write_html`, best of
    three, both trees) - MISSED (0.25 s).
  - SC-007: the drain-bank clearances asked one at a time on Inashiro 12,195 -> 0 (`m:after-inashiro-drain-bank-clearance`; every
    plot's corners asked at once) - met; every bund held off the drain (the gate).
  - SC-008: `dev/performance.md`, "Placement by construction, and what it bought" - met.
  - SC-009: the gate green at 100%; every pool map regenerates with the same houses, acreage, lanes, wells and crowns (R13); `make
    cohort N=24` 30/30 as the base's - met.
  - SC-010: the hinterland's `PointGrid.near` 102,164 -> 48,830 (2.1x) - MISSED (3x).
  The floors were set with no projection behind them (the spec says so); what each lever reaches is measured above, and what
  is left of each stage is in `dev/performance.md`. SC-002's seats bucket went the WRONG way (2,640,745 -> 3,525,463 calls: the
  region's painting and labeling are calls of their own) even as its stage got faster. **Whether to land at these figures is the
  GM's call**; the session lands them because every lever is faster than the base and no map broke a rule, and reports the misses.

## Assumptions

- The seconds are taken back to back against the base worktree, fastest of three, with the load recorded; the counts are
  load-independent.
- "Well under half" was the session's guess for the stages; SC-001 holds it as the floor of half, the GM's to judge further.

## Review history

- Round 1 (spec-fidelity, 2026-09-30): CHANGES REQUIRED, 5 items - the GM's second count ("roughly 100,000 spatial-index lookups")
  had no criterion and three per-call harness keys read 0 (wrong callee names); the Summary misstated R2's layouts and tests;
  FR-002 was in neither the exact list nor the Decisions; the page's remaining picture time went unaccounted; SC-001 called the session's
  guess "the GM's number". Addressed: the harness's callee names corrected and a whole-stage hinterland bucket added (SC-010), the
  baseline re-taken; the Summary restated; FR-008/SC-008 take the page write; SC-001 relabeled. Between rounds the GM ruled that maps
  need not stay identical (request.md), so every byte-identity requirement was replaced by the rules and invariants, and FR-002's
  move is in the Decisions table.
- Round 2 (spec-fidelity-verify, 2026-09-30): CHANGES REQUIRED, 3 one-line items - the GM's second statement missing from
  request.md, the Summary's funnel order, SC-001 naming `full_s` while citing the `make map` figure and a load bullet true of only
  one figure. Addressed.
- Round 3 (spec-fidelity-verify, 2026-09-30): FAITHFUL. The GM's second statement's guideline edits were made as their own commit
  (5594b7c54: constitution v2.27.0, `dev/performance.md`, `docs/efficiency-tooling.md`, the engine `CLAUDE.md`).
