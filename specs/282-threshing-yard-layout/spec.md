# Feature 282 - what is in a threshing yard, and where

**Feature**: 282-threshing-yard-layout | **Created**: 2026-09-28 | **Status**: Draft
**Input**: the GM's request, verbatim in [`request.md`](request.md).

## Summary

Every threshing yard on a settlement map is drawn the same way (`settlement/homestead_parts/yards.py`,
`_draw_threshing_yard`): a tamped floor rolled to the household's size, ONE straw mat of a fixed 14 x 9 ft at its
center, and a rack as wide as the yard along its SOUTH edge (observed 2026-09-28; method: read from the code at
c13a6ebe6; research.md R1). The yard's size is researched (homesteads 020, 030);
its interior is not, and its modal calls it accurate. The record already contradicts it: the yard-size source says
mats were spread over the whole yard at harvest, 40 to 60 of them, each 3 by 6 ft (Kitamoto; Imaishi); entry 500
says racks stood mainly on the paddies and only in some regions, as tall racks, by the house; and a rack on the
yard's south edge stands in the sun corridor entry 030 keeps clear.

The GM asked for a research pass on what was in the yard and where, then the glyph changed to match: mats drawn
over the whole yard, fewer than the real count so the drawing stays legible, with the modal saying so; a rack by the
house only in a settlement whose roll gives one, placed where the research puts it and never on the yard's south
side; and the research to say whether a rack by the house was a village's custom or the environment's (so that two
neighboring villages do not differ if every village in one environment did the same). Seasons are out of scope: the
GM ruled the map's look in other seasons future work (paddies, dry crops, snow, frozen ponds), and this feature's
baseline draws the yard as the harvest leaves it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The research is on the record (Priority: P1)

A reader who opens the threshing yard's modal, and its references, finds what was in the yard and where: the mats
and how they lay, where threshing was done, what else stood there, where a rack by the house stood, and what decided
whether a place had one - each with a quoted footnote or an absence note, each rule labeled.

**Independent test**: the new questions are on the homesteads page with their footnotes; every source they cite is
registered, read (source-reader), quoted verbatim (quote-check), judged applicable (source-applicability) and
checked for its reader (record-format).

**Acceptance**:
1. **Given** the homesteads page, **When** a reader looks for the yard's layout, **Then** a question answers how the
   mats lay over the yard and what else stood in it, with what the sources say and where they are silent.
2. **Given** the homesteads page, **When** a reader looks for racks by the house, **Then** a question answers where
   at the house a rack stood, and whether the choice was a village's custom or followed the environment (climate,
   paddy type, terrain), and how strong that evidence is.
3. **Given** entry 500 and entry 020, **When** they touch the yard's contents, **Then** they point at the new
   questions rather than restate them.

### User Story 2 - The yard is drawn as the research says (Priority: P1)

The GM, looking at any settlement map, sees each threshing yard covered in straw mats laid as the research
describes, fewer of them than the real count, and a rack at the house only on a map rolled for one, never on the
yard's south side. Clicking the yard, the modal explains the mats' drawing convention with the real count.

**Independent test**: on the pool hamlets, every drawn yard carries several mats at their researched size, spread
over the yard, and none at its old fixed center; a rack stands only where the map's knob says so, placed per the
research and off the yard's south edge; the `threshing yard` class's docstring says the mats drawn are fewer than
the real 40-60 and why.

**Acceptance**:
1. **Given** a yard of any rolled size, **When** it is drawn, **Then** its mats are tiled over the yard's area at the
   researched mat size, so a larger yard carries more mats, and the drawn count is below the count that would fill
   it (the legibility convention).
2. **Given** a map whose knob gives no rack at the house, **When** its yards are drawn, **Then** no rack is drawn in
   or beside any yard.
3. **Given** a map whose knob gives a rack at the house, **When** its yards are drawn, **Then** each household's rack
   stands where the research places it, and never along or across the yard's south edge.
4. **Given** the yard's modal, **When** the GM opens it, **Then** it says the mats covered the whole yard (40-60 of
   them, 3 by 6 ft), that the map draws fewer so they read, and labels the rack by the house with its knob.

### User Story 3 - The knob a scripted settlement rolls (Priority: P2)

A session scripting a hamlet or village finds the rack-by-the-house knob declared with its forms, what constrains
it, and how it is pinned, so that neighboring settlements in one environment can be given the same value.

**Independent test**: the hamlet generator's plan carries the knob, pinnable from the spec, and either set from the
environment (the fact the generator models, or the environment input the spec states) or rolled from the seed, as
FR-002 finds (FR-005); its declaration names the research question it rests on.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The research record MUST gain, on the homesteads page, a question on what lay in a farmhouse's work
  yard at harvest and where: the straw mats (how many, how laid, what dried on them), where threshing was done, and
  what else stood in the yard. Each claim carries a quoted footnote or an absence note; each rule a label.
- **FR-002**: The research record MUST gain, on the homesteads page beside entry 500, a question on the rack by the
  house: where at the house it stood, its form, and what decided whether a place had one - a village's custom, or
  the environment (climate, paddy type, terrain) such that every village in one environment did the same - saying
  how strong the evidence is either way.
- **FR-003**: Every new source MUST be registered (what it is; why it applies and its limits) and pass
  source-reader, quote-check, source-applicability and record-format before its content reaches the map or a rule.
- **FR-004**: The yard MUST be drawn with straw mats tiled over its area, each at the researched mat size in real
  feet, laid as FR-001 finds (or, where the sources are silent on the arrangement, in rows, labeled a guess); the
  number drawn MUST be fewer than would cover the yard, as a map drawing convention recorded with the real count,
  and MUST still read as a yard covered in mats: the drawn mats spread over the whole yard (every quarter of it
  carries mats) and the drawn count is tied to the yard's area - between one third and two thirds of the count
  that would cover it, so a 60 sq m yard (about 36 mats to cover) draws 12 to 24. Each drawn mat MUST keep bare ground
  around it and room to lie askew - at least a `1 ft` gap to its neighbors on the lattice: a yard that cannot hold a
  third at that gap draws as many as fit at it, and never fewer than four (amended 2026-09-28, after the
  settlement-reviews ruled edge-to-edge mats, and mats at a `0.5 ft` gap, read as paving - research.md R4). The single fixed central mat MUST go.
- **FR-005**: The yard's rack MUST be drawn only where the settlement's rack-by-the-house knob gives one; the knob
  MUST be pinnable from the settlement's spec. Where FR-002 finds the choice followed the environment, the knob MUST
  be SET from that environmental fact, never rolled free: from the fact itself where the generator models it, and
  otherwise from an environment input the settlement's spec states (so neighboring settlements in one environment are
  given the same value), and its declaration MUST say so. Only where FR-002 finds it a village custom, or is
  inconclusive, is it a free per-settlement roll from the seed (the GM's stated fallback, 2026-09-28). Where entry
  500's drying-method knob (four forms, "where the roll gives tall racks") covers the same choice, the two MUST be one
  knob, not two that can disagree.
- **FR-006**: A rack drawn by the house MUST stand where FR-002 places it, and MUST NOT stand on the yard's south
  side: neither in the yard's southern half nor anywhere in the sun corridor entry 030 keeps clear south of the yard
  (`39 ft` deep, the yard's width - research homesteads 030's derived figure, research.md R2). "South" is MAP south, not the glyph's local lower edge (the glyph is turned by its
  house's rake). Where the sources are silent on its place it is seated off the south side and labeled a guess.
- **FR-007**: The `threshing yard` interactive class's docstring MUST be rewritten from the new questions: the mats'
  convention stated in the GM's form ("we can't render dozens of mats and have that be legible"; the real count and
  size given), the rack's knob, and a label per claim; its `Entry:` MUST name the new questions.
- **FR-008**: The pool hamlets whose yards change MUST be regenerated, and the settlement-review pass the gate owes
  for a moved layout MUST run.

### Out of scope

- How the map looks in any other season (growing rice vs stubble, racks standing on the reaped paddies, snow, frozen
  ponds): the GM's ruling of 2026-09-28, "known future work". Racks on the paddies (entry 500) are part of that work.
- Hand-authored legacy maps: they are not regenerated (GM 2026-09-28 on generator work).

## Success Criteria *(mandatory)*

- **SC-001** (FR-004): No drawn yard carries the old central mat (`14 x 9 ft`, research.md R1); every drawn yard's mat
  count lies between one third and two thirds of the count that would cover its area (where the yard cannot hold a third at a `1 ft` gap, as many as fit at it and at least four), and each quarter of the yard
  carries at least one mat (measured by test on the regenerated pool hamlets and on the yard sizes the roll makes).
- **SC-002** (FR-005, FR-006): No rack is drawn on a map whose knob gives none; on a map whose knob gives one, every
  yard carries a rack and no rack's footprint enters the yard's southern half or the `39 ft` corridor south of it
  (research.md R2), taken in map coordinates (measured by test on the pool's changeable-weather hamlet and on the
  placement for any rotation).
- **SC-003** (FR-001, FR-002, FR-003): The two new questions pass source-reader, quote-check, record-format and
  source-applicability with no open finding.
- **SC-004** (FR-007): The `threshing yard` modal's registry entry carries the convention label, the real mat count and
  size, and names both new questions in its `Entry:` (measured by the interactive registry tests).
- **SC-005** (FR-008): Every pool hamlet whose yards change is regenerated, and the settlement-review the gate owes
  for this change is a row in the review ledger.

## Decisions Recorded

- **D1 - the baseline draws the harvest yard.** The GM ruled seasons out of scope and asked for mats over the yard;
  the yard is drawn as the harvest leaves it while the paddies stay as they are drawn now. Class: this project's
  decision (GM 2026-09-28).
- **D2 - fewer mats than the real count.** A map drawing convention, the GM's own form: the real yard was covered
  (40-60 mats); the drawing thins them so each reads as a mat. The band of one third to two thirds of a full cover
  is this project's decision (spec-fidelity round 1: a floor tied to area, so the impression of a covered yard holds).
  EXCEPTION (amended 2026-09-28; the first form, for yards under `400 sq ft`, ruled LEGITIMATE by spec-fidelity, then
  broadened): a yard that cannot hold a third at a `1 ft` gap draws as many as fit at it, never fewer than four - a map
  drawing convention, since mats edge to edge or at a `0.5 ft` gap read as paving (research.md R4). To go to the GM at
  hand-back, per the exception procedure.

## Review history

- Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - the south side widened from the edge to the sun corridor in
  map coordinates; the environment-driven knob set from a stated input, never a free roll; a mat-count floor tied
  to area. All three applied.
- Round 2 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - US3's test line still said "rolled from the seed"; rewritten
  to FR-005's rule. The three round-1 items confirmed fixed.
- Round 3 (spec-fidelity-verify, 2026-09-28): FAITHFUL - the US3 line resolved; no new drift.
- Amendment round (spec-fidelity-verify, 2026-09-28): CHANGES REQUIRED - SC-005 required a settlement-review per
  regenerated hamlet, beyond FR-008 and against plan D6; reworded as the review the gate owes.
- Amendment round 2 (spec-fidelity, 2026-09-28): FAITHFUL - SC-005 now reads "the settlement-review the gate owes",
  matching FR-008; no new drift. Plan review round 4 CLEAR (D3 matches the code, D6 names the five reviews owed).
- Amendment round 3 (spec-fidelity, 2026-09-28; MODE 1 on the small-yard exception, then the spec): the exception to
  FR-004's one-third floor LEGITIMATE - the floor is this project's proxy, not the GM's number, and holding it on the
  smallest yards drew them edge to edge, which the reviews read as paving, defeating the GM's stated aim that the drawn
  mats be legible as mats; bounded to under `400 sq ft`, every quarter still carries mats. CHANGES REQUIRED: (1)
  research.md R4's counts moved - re-measured on the working-tree manifests (2026-09-28), four yards fall short, not five
  (Sawada's `20 x 14 ft` yard now draws 6, its third), and the short yards draw 5 to 6, not 4 to 6; (2) D2 does not
  record the small-yard exception and does not mark it for the GM (the XVI procedure: an agreed exception goes to the GM
  once the implementation works). Plan review round 5 CLEAR (D3-small-yard a narrowing, LEGITIMATE).
- Amendment round 4 (spec-fidelity-verify, 2026-09-28): FAITHFUL - (1) research.md R4 now names four short yards
  (Kashikawa's two `22 x 15 ft` at 6 and 5 of 7, Sawada's `22 x 15` and `24 x 16 ft` at 6 and 6 of 7 and 8), matching
  the working-tree manifests re-read with `jq`; (2) D2 carries the small-yard exception in FR-004's terms, labeled a map
  drawing convention and marked to go to the GM at hand-back. No new drift.
- Amendment round 5 (spec-fidelity, 2026-09-28; MODE 1 on the broadened exception, then the spec): the `1 ft` least gap
  LEGITIMATE (it serves the GM's aim that the drawn mats read as mats; rounds 4-6 read `0.5 ft` as paving); a yard that
  PHYSICALLY cannot hold a third at `1 ft` drawing as many as fit there LEGITIMATE at any size (the `400 sq ft` bound was a
  proxy for that). NOT LEGITIMATE: the floor lowered from four to three, and "cannot hold" decided by the one centered
  lattice the code lays per gap step. On this round's own run (the working-tree SVGs and manifests, 2026-09-28; a shifted,
  unturned `1 ft`-gap lattice of `6 x 3 ft` mats, corners `1 ft` inside the drawn outline, off the rack): of the nine yards
  drawn under a third of their drawn outline's cover, eight hold a third at `1 ft` - Kashikawa's `22 x 15 ft` yard draws 3
  where 6 fit, Sawada's `31 x 22 ft` draws 8 where 12 fit, Mizuguchi's two draw 10 and 11 where 12 and 15 fit; only
  Inashiro's `20 x 14 ft` yard cannot (4 fit, 4 drawn). CHANGES REQUIRED: (1) research.md R4 does not reproduce - eleven
  short yards is neither the nine under a third of the drawn outline nor the sixteen under a third of the manifest's
  `w x h` (the area the code's floor uses), and the fewest-3 yards are two (Kashikawa's, no rack, as well as Sawada's
  `20 x 14 ft`); and it reports what the centered lattice drew, not what fits at `1 ft`, which is the premise FR-004's
  exception turns on - re-measure what fits; (2) FR-004, SC-001 and D2: "never fewer than three" back to four (no
  measured yard holds fewer than four at `1 ft`; three exists only where the code draws half of what fits), unless a
  rolled yard is measured that cannot hold four; (3) SC-001: the exception's test MUST establish "cannot hold a third at
  `1 ft`" independently of the layout under test (the most that fit), so a yard drawn short only by lattice alignment
  fails it. Plan review round 6 BLOCKED (D3's short-yard test and floor).
- Amendment round 6 (spec-fidelity, 2026-09-28; the round-5 items, then the plan re-read whole): (2) confirmed - FR-004,
  SC-001 and D2 say four. (1) and (3) NOT resolved. On this round's own run (a brute-force search over every lattice
  origin on a quarter-foot grid at a `1 ft` gap, corners `1 ft` inside the SVG's drawn outline, off the padded rack; the
  same result with the clearance at `1.05 ft` to cover the outline's 0.1 px rounding), eight of the nine short pool yards
  are fit-limited as R4 says, but Kashikawa's `27.1 x 18.7 ft` yard (manifest x 1036.7, y 886.0, no rack) draws 9 against a
  third of 10 where a 3 x 4 lattice seats 12 - its rows fit in a `0.2 ft` window that `mat_cells`' five offsets per axis
  step over. CHANGES REQUIRED: (1) that yard must draw at least a third, and research.md R4 then lists eight short yards,
  not nine (its "no room for the last mat" is false for this one); (2) SC-001's test: the "27 x 19 ft" case is not the
  pool's outline (the pool's is `(-13.0, -8.4), (13.4, -8.4), (13.0, 8.9), (-12.5, 8.8)`), so the oracle never met the
  yard that fails it - run it on every pool yard that draws under a third, from its drawn outline and rack; (3) the modal,
  025 and the notes say "a mat fewer", but Inashiro's `20 x 14 ft` yard draws 4 of 6 - say "a mat or two fewer". Plan
  review round 7 BLOCKED (D3's lattice search).
- Amendment round 7 (spec-fidelity, 2026-09-28; the round-6 items, then the plan re-read whole): (1) confirmed for the
  yard named - Kashikawa's `27.1 x 18.7 ft` yard now draws 12 against a third of 10; (3) confirmed - the modal, 025 and
  the four rice maps' notes say "a mat or two fewer". (2) NOT resolved, and (1)'s premise does not hold for two more
  yards. On this round's own run (Sawada rolled in memory with `mat_cells` wrapped to capture its exact inputs - the
  unrounded outline and the rack keep-out with its `0.25 ft` pad - then every lattice origin searched on a `0.05 ft` grid
  at a `1 ft` gap and a `1 ft` clearance, at two grid anchors): Sawada's `31.2 x 21.5 ft` yard seats 13, its third, where 12
  are drawn, and its `20.3 x 14.0 ft` yard seats 6, its third, where 5 are drawn. Their fitting lattices lie in windows
  narrower than the quarter-foot step, the round-6 failure at a finer grain (this reviewer's round-6 oracle used the same
  quarter-foot grid and missed them too). The other six short yards are fit-limited at the finer grid. CHANGES REQUIRED:
  (1) those two yards must draw at least a third, and "cannot hold a third at `1 ft`" must be decided by a search that finds
  every lattice that fits, not one sampled at a fixed step; research.md R4 then lists six short yards, and its method line
  says how the search reaches every fit; (2) SC-001's oracle must not share the search's grid - `_brute_fit` enumerates
  exactly the quarter-foot offsets from `-w/2` that `mat_cells` does, so it agrees with it by construction - and the pool
  test must be able to see the two yards above: run it on the exact outline (or a manifest outline recorded finely enough
  that no clearance allowance is needed; the `1.05 ft` allowance alone hides the `20 x 14 ft` yard, which fits to `1.04 ft` on the SVG outline),
  and show it fails on the current code. Plan review round 8 BLOCKED (D3's lattice search).
- Amendment round 8 (spec-fidelity, 2026-09-28; the round-7 items, then the plan re-read whole): (2) confirmed - the pool
  oracle's grid is anchored `0.01 ft` off the search's, runs on the outline to a thousandth with no clearance allowance, and
  its test sees the old counts (`make test-file` on both 282 test files, 48 passed). (1) confirmed for the pool: Sawada's
  `31.2 x 21.5` and `20.3 x 14.0 ft` yards draw 13 and 6, their thirds, and R4's six short yards reproduce against an EXACT
  search on this round's own run (the pool rolled in memory with `mat_cells` wrapped for its exact inputs; every lattice
  size, the origin taken at every vertex of the arrangement of each mat spot's outline and rack constraint lines): 4, 6, 6,
  7, 6 and 8, as drawn. NOT resolved for the rule: the search is still sampled down, on a `0.02 ft` grid. On this round's own
  run (1,000 synthetic yards of the roll's sizes, `19-48 ft` wide at the pool's `h/w`, corners pulled in within the range
  the pool's outlines show, the rack from `rack_segment`), one yard - `25.41 x 17.52 ft` with a rack - draws 7 against a third
  of 9 where a lattice seats 8, which `_exact_lattice` itself finds at a `0.005 ft` step and every mat of which passes
  `mat_cells`' own fit test: the top row fits in a band under `0.02 ft` tall below the rack's end. CHANGES REQUIRED: (1) solve
  the down direction exactly too - the candidate `y0` are the vertices of the arrangement (each row's top or bottom meeting a
  rack limit, `k1 - mh - r ph` and `k3 - r ph`, and the pairwise crossings of the spots' outline constraint lines), each then
  swept exactly across as now - and pin that yard on plain inputs; R4's method line then says so. Plan review round 9
  BLOCKED (D3's search down).
- Amendment round 9 (spec-fidelity-verify, 2026-09-28; the round-8 item and the passages changed since): FAITHFUL. (1)
  resolved - `_exact_lattice` now takes every crossing of the fit conditions' lines on the lattice origin, with no step in
  either direction, and the `25.4 x 17.5 ft` yard is pinned on plain inputs (drawn 8). On this round's own run: the 282 test
  files pass (49); the 1,000-yard sweep of round 8 re-run on four seeds (4,000 yards of the roll's sizes) finds no short yard
  an exact oracle seats more in; 12,000 perturbations of the pinned yard (corners and rack moved up to `1 ft`) find none;
  and `_exact_lattice` agrees with an independent ground truth (every crossing probed a hair round in 16 directions) on 1,260
  yards, with racks from `rack_segment` and with arbitrary keep-out boxes. The regenerated pool's short yards are R4's six
  (4, 6, 6, 7, 6, 8 against thirds of 6, 7, 7, 8, 7, 9). R4's method line and plan D3 describe the exact solve. Aside, not a
  finding: confirming a group of crossings at its centroid is exact only where each seated set's region is convex; a
  keep-out box can cut an L-shaped region, and a hand-built `10 x 7 ft` yard with a keep-out box at its corner and arms
  `0.1 ft` wide draws 0 where one mat fits. No rack and no yard in the roll's range reproduced it. The docstring's "a hair
  to each side of it" would close it. The plan changed since round 9's record, so the plan review is owed to `spec-fidelity`.
