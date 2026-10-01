# Implementation Plan: every finished-map rule guaranteed by its placer

**Branch**: none (main, clone `diagram-performance`) | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)
**Input**: [spec.md](spec.md), [research.md](research.md) (R1-R3), [request.md](request.md), the five area designs
(`design/design-{water,ways,homes,woods,labels}.json`: 175 distinct rules, each with its owner, mechanism, fallback, later
stages, unit test, retirements and risk) and their one-row-per-rule index [plan-rules.md](plan-rules.md). A rule is named
`area:id` below (`ways:W01`), since three designs number from W01.

## Summary

The three censuses (R1-R3: 118 finished-map rules, 31 breaking fallbacks, 58 open violations) resolve to 175 distinct rules
across five areas. 17 or more are already guaranteed by construction and need only their placer test; the rest need a
placer change. The designs agree on nine shared mechanisms (below) that carry most of the work; each rule's own mechanism is
its design row. The work runs in phases, each landing its guarantees with their unit tests and retiring the tests they make
unnecessary, so the gate never pays for both at once.

## Technical Context

**Language/Version**: Python 3.14, shapely 2, numpy (bound on first use). **Testing**: pytest through `make`; each guarantee's
unit test on constructed inputs beside its placer's module test; the acceptance sweep (`sweep/harness.py`, SC-003) as a
spec harness. **Constraints**: 100% coverage; files under 1,000 lines; `make done` green per landing; no roll may re-roll
after M3 lands.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `287-start` | total 20.9 s, median 5.2 s, worst 5.8 s (observed 2026-09-29, method: `make perf LABEL=287-start` in the clone before any 287 engine change, load 1.3) |
| after | `287-end` | before the push; `make perf-report AGAINST=287-start` |

The gate's test phase before (SC-005): 5,258 tests in 57.13 s (observed 2026-09-29, method: `make durations`; the slowest listed in
`research.md` R4).

## Constitution Check

- **VI**: bookends above; SC-005 measures the gate. **X clause 15**: every new predicate that tests a candidate against
  standing geometry asks an index built once (the lane law, the ring rules, the overlap registry). **XII**: every task is
  `research: rendering`; a task that turns on a new physical fact (a fallback form the research must decide) is marked
  `research: physical` with its boxes. **XIII**: the cohort before and after; zero failing seeds is the bar (SC-004).
  **XIV**: defects found in the work are fixed in it. **XVI**: every FR as written; the items below that could read as
  "X except Y" are listed under Decisions for review.

## The shared mechanisms

- **M1 One predicate per rule, in the engine.** Each rule's test body is lifted into an engine predicate that its placer
  calls and its test calls (FR-003): `waterfields/ring_rules.py` (every paddy-ring rule: apex, area, width, dart, step count,
  stroke, collector, chevron, pond, grave - water design), `hamletgen/ways/law.py` (every lane rule: bends, ends, service,
  fords at the one 30 ft constant, decks via `_deck_corners_clear` - ways design M1), `labels`' `place(strict=True)` and
  `board_caption_seat` (the board's caption - labels design), and one predicate each where a placer and its test disagree
  today (the wells' spacing, the eave gap on a turned house, the field pond's rim, the flooded tint's ring, the woodland's
  dry-ground sample, the drip lines, the same-bank test written twice as `_parts_across_stream` and `across_the_brook`).
  The acceptance sweep (M9) runs every predicate on a finished map, so the predicates are the one registry of the rules.
- **M2 The final water before anything reads it.** `round_the_brooks` (the brook's rounding) moves to just after
  `stage_sink`; the rounding is lifted into `brook.py:finished_course`, which `feed_brook` scores its candidates against
  (water design), and every bank, ford, corridor and deck test reads the final course (ways M4, homes, woods S1). Ways
  keep routing against the unrounded course where the rounding's docstring records why (rounding early moved every way).
- **M3 The access-corridor tree, replacing the re-roll.** At seating the first corridor is an exit strip from the cluster
  center outward (the connector starts at its outer end); each house is admitted only with a clear corridor from its door to
  the tree, and every later placement refuses to cover a corridor (a keep-out in the shared registry, M8). The web draws
  the corridor for any house its lanes do not reach (ways `settle_the_web`). Why this can succeed where eighteen seat-time
  reach tests failed (`driver.py`'s record; `future-work` on the reach residue): those tests ran while the neighbors'
  fabric was still to be laid, and the corridor is reserved against it. `generate`'s re-roll loop and its machinery are
  removed, with the tests of it (FR-002, FR-007). One corridor also reserves the field path (ways W03).
- **M4 The web settles itself.** `settle_the_web`, the last pass of `stage_web`: a repair loop that only cuts ordinary lanes
  or draws reserved corridors (so it terminates), ending with every lane-law predicate passing; the crossing-squaring moves
  from `stage_crossings` into it, so no stage after the web rewrites a lane (ways M2, M4).
- **M5 A household's parts are the household's.** One quota table keyed on seat order decides each household's house size,
  kura, byre, fixtures and well pocket, closing every count at round(n x share) for the households seated; the guaranteed
  parts (kura, byre, fixtures, the bath's corridor, the well pocket, the access corridor) are laid as parts of the bundle
  inside the homestead envelope, so the existing envelope and parts tests decide whether the household is seated at all
  and no later stage can lose a part (homes design). A part with no room passes to the next seated household.
- **M6 The view decided once.** At the end of `stage_hinterland` the view is fixed and `stage_frame` takes exactly it; the
  rules that read the view (the bare ground, the woodland in the picture, the belt's record against its ink, the waterward
  strip, the scatter gap) are guaranteed against that view (woods S2, water).
- **M7 The recorded marsh is the drawn marsh.** The marsh's recorded outline becomes the ground its reeds are drawn on, and
  every "is this in the marsh" reads it (woods S3; future-work's toe-marsh entry).
- **M8 One registry of what stands, refused at record time.** The overlap matrix (`overlap/`) is read today by one test and
  no placer (R1, group 3). Every footprint is recorded through one indexed registry that answers "may this kind lie on what
  is already here" by the matrix, and a placer offers only candidates it admits (water design W53: overhaul-scale, in scope
  because the GM's "literally any" includes it; phased last among the placer work because every placer consults it).
- **M9 The acceptance sweep.** `sweep/harness.py` rolls the pool and cohort seeds 1-48 plain, and again with feature 284's
  A* and field-search lever applied as probes (neither ships), and runs every M1 predicate on each finished map, counting
  failures and re-rolls (SC-003). It is a spec harness, not a gate test.

## Phases

- **P0 - Measurements owed before building** (the designs name them): the Polder coverage seeds 12 and 19, naming the polder grid's two failures (water
  W48); the board terminal - how many maps of cohort 1-48 and the probes reach "no verge in the view takes a board with a
  clean caption" (labels L4); seed 31's yard over a paddy (homes); the belt cases D8's mechanisms leave (a margin whose belt
  cannot be planted 30 ft deep and whole, over cohort 1-48 and the probes); whether the field pond's count (water W29) is a
  rolled knob (D9); and the seats D2 refuses (households unseated today over cohort 1-48, the probes and the pool).
  Recorded in research R5.
- **P1 - The reorders and the predicates**: M2, M6, M7 and M1's modules, with each predicate's unit test against its old
  test body; no placer changed yet.
- **P2 - Water** (59 rules; `design-water.json`), **P3 - Homesteads** (47; M5 and M3's seat half - measured as it lands,
  before anything else depends on it: the cohort 1-48 and the pool with the corridor rule alone, households seated and seats
  refused per seed, scored by `unreached_houses` itself), **P4 - Ways** (25; M3's web half and M4 - `settle_the_web`'s
  rounds, seconds and lanes cut per pool map measured - then the re-roll removed), **P5 - Woods** (26), **P6 - Labels and the generated Mode A sheets** (18).
  Each area lands its rules in the order of its design, each with its unit test, and retires the tests the design names.
- **P7 - M8, the registry**, then the overlap-matrix rule.
- **P8 - The excuses and the retirements closed**: `ACREAGE_SHORT`, the seed-43 strict xfail and R3's test-side excuses
  removed (FR-006); every test the refactor made unnecessary retired, each with the cost the gate no longer pays (FR-007,
  SC-005); the rolls and roster rows only they needed removed.
- **P9 - Acceptance**: M9's sweep (SC-003); the pool regenerated with every moved map's before and after (FR-009, SC-004);
  `make cohort N=24` with zero failing seeds; the closing census by `census_select.py` and the same judgment (FR-008,
  SC-001); `make durations` and `make audit` against the before (SC-005); `make perf LABEL=287-end` and the report (SC-006).

## Decisions for review

Each of these could read as a narrowing; they are put here rather than decided silently. None records a violation: a
"shortfall", an "unhonored" knob or a dropped rolled feature is the violation, so each is closed by a mechanism instead.

- **D1 A fallback that drops is recorded only where the drop is the rule's own provision.** Where a placer has no legal
  candidate left, the design's fallback is taken when it stays inside the rule (draw it smaller within its researched range,
  or a stated alternative); a drop of a rolled or required feature is never a fallback - it is closed by constraining the
  knob or the candidates beforehand (D4, D9).
- **D2 The seating floor holds where the site is chosen** (homes H14). The limits that bound a settlement's seat band are
  named: H03 (every house within 700 ft of the field outline), the belt band reserved before the hem (D8), the resolved
  cluster shape (D4), the drain (a dwelling above it) and the canvas. Within them, the site is chosen for its capacity by
  the placer itself: `seat_cluster` takes a margin only if the homestead seat pass - the same placer, run on a copy of the
  settlement over that margin's band, with M5's shrink of envelopes within their researched range - seats every household;
  margins are tried in its ranking order, and the seating the chosen margin's pass found is the seating kept (one pass, not
  a second roll). A site where no margin seats every household is refused at `stage_seat`, naming it, as impossible input
  (D7's kind of refusal, before any house exists) - never a shortfall, never a re-roll. P0 counts the seeds of cohort 1-48,
  the probes and the pool that reach it; if any live map or any cohort seed does, it goes to the GM with that count.
- **D3 A fall into the wind is refused only where its geometry admits no wind-facing margin above the drain** (homes H30):
  H30's steps (1)-(3) are kept; at plan time the margins are computed from the envelope and the drain, and a fall - declared
  or rolled - is refused (declared) or constrained (rolled: the fall's value space narrowed to falls with such a margin) at
  spec resolution only when no wind-facing margin above the drain exists. Sawada
  (`down_deg=225`, seed 24, seating all 19 on a wind-facing margin) has one and is untouched.
- **D4 The cluster shape resolves only over the shapes the chosen seat band allows** (homes H05), as labels L1 does for the
  board's seat: the band is chosen, the knob's value space is narrowed to the shapes that band admits (the ones the seat
  placer can draw there), the knob resolves over that space from the map's seed, and the seat placer steers and repairs
  within the resolved shape. The drawn shape is the rolled shape; there is no "unhonored" record.
- **D5 The brook's ruled run is judged by a stricter, view-independent bound** at the brook's placer (water W03), since the
  view is decided later; the placer stricter than the test is the engine's standing convention, so the rule as tested holds.
- **D6 The bare-ground predicate counts every recorded footprint and tread as covered** (woods W11): the rule's own
  grounding is that a hole is "the map admitting it has not decided what is there", and a recorded lane, stream, well or
  clearing is decided ground. Raised with the GM once it works.
- **D7 A generated Mode A program whose caption or building has no legal seat after repair and growth is refused at
  composition, naming it** (labels L15, homes H29a): the composer is seedless, so the refusal is of an impossible input
  before any sheet exists, not a finished-map check.
- **D8 The belt is planted where it can be deep and whole** (woods W16, W17): the belt band is reserved before the hem (H30
  step 2), the canvas is sized for belt room (H31), and `seat_cluster` refuses a margin whose belt band cannot be planted 30
  ft deep and unbroken. P0 measures, over cohort 1-48 and the probes, any case left; only a case shown to be forced goes to
  the GM, with its count.
- **D9 A rolled or required feature is always drawn**: the homestead's wood floor is laid as one of M5's parts inside the
  homestead envelope, so a household is seated only with room for it (woods W25), and D2's capacity ladder supplies the
  room; the hamlet's own burial ground (`burial.py`, `hamlet_burial='own'`) resolves `own` only where the edge seat finds a
  legal seat at resolve time, the knob narrowed to what the site affords as in D4 (the homes design's "for the owning
  area" item, taken here) - a PINNED `own_ground` with no legal seat is refused at resolve time, naming it, as declared
  input the site cannot honor (D7's kind); a field pond that is a rolled count (water W29) is treated the same way if the census of its
  knob confirms it is rolled, and otherwise recorded as not a rule.
- **D10 A caption never overlaps, on any sheet** (labels L13, homes H29c): where the one placer has no free seat, it draws
  the caption on a leader line, and failing that enters it in the sheet's key - on hamlets, generated sheets and hand
  sheets alike. The GM's "we'll treat labels as mandatory" (`labels/standard.py`) is honored without an overlap; the
  least-cost overlapping seat is retired.
- **D11 A village's worked woodland off a tight sheet is recorded off the sheet with its bearing** (woods, R3's woodland
  row): research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html puts the wood on the hill beyond the fields, and the GM's frame rule forbids a parcel
  setting the frame. Raised with the GM once it works.
- **D12 The question for the GM**, after P0's count and through `escalation-check`: the notice board where no verge in the
  view takes a board whose caption clears roofs, lanes, crowns and neighbors (labels L4) - every option breaks one of the
  GM's own rulings: (a) no board, recorded (against "every settlement carries the board", 2026-07-24); (b) a board farther
  off the way than `BOARD_TO_WAY_PX` (against `kosatsuba_by_the_road`); (c) a caption that breaks a caption rule, drawn on a
  leader under D10 (against the caption rules). The count of maps reaching it over cohort 1-48 and the probes goes with the
  question. Work that does not depend on the answer proceeds meanwhile.

## Verification per phase

| phase | unit tests | map proof |
|---|---|---|
| P1 | each predicate against its old test body | the pool unchanged where no placer changed |
| P2-P7 | each rule's placer test with its violating case | the pool regenerated and every predicate run on it; the cohort |
| P8 | the removed excuses' seeds assert the rule | the gate's cost before and after |
| P9 | - | the sweep, the census, the cohort, the bookends |
