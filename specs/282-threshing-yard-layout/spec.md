# Feature 282 - what is in a threshing yard, and where

**Feature**: 282-threshing-yard-layout | **Created**: 2026-09-28 | **Status**: Draft
**Input**: the GM's request, verbatim in [`request.md`](request.md).

## Summary

Every threshing yard on a settlement map is drawn the same way (`settlement/homestead_parts/yards.py`,
`_draw_threshing_yard`): a tamped floor rolled to the household's size, ONE straw mat of a fixed 14 x 9 ft at its
center, and a rack as wide as the yard along its SOUTH edge. The yard's size is researched (homesteads 020, 030);
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
  that would cover it, so a 60 sq m yard (about 36 mats to cover) draws 12 to 24. The single fixed central mat
  MUST go.
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
  (39 ft deep, the yard's width). "South" is MAP south, not the glyph's local lower edge (the glyph is turned by its
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

- **SC-001**: No drawn yard carries the old 14 x 9 ft central mat; every drawn yard's mat count lies between one
  third and two thirds of the count that would cover its area, and each quarter of the yard carries at least one
  mat (measured by test on the regenerated pool hamlets).
- **SC-002**: No rack is drawn on a map whose knob gives none; on a map whose knob gives one, no rack's footprint
  enters the yard's southern half or the 39 ft corridor south of it, taken in map coordinates (measured by test on a
  pinned hamlet).
- **SC-003**: The two new questions pass quote-check, record-format and source-applicability with no open finding.

## Decisions Recorded

- **D1 - the baseline draws the harvest yard.** The GM ruled seasons out of scope and asked for mats over the yard;
  the yard is drawn as the harvest leaves it while the paddies stay as they are drawn now. Class: this project's
  decision (GM 2026-09-28).
- **D2 - fewer mats than the real count.** A map drawing convention, the GM's own form: the real yard was covered
  (40-60 mats); the drawing thins them so each reads as a mat. The band of one third to two thirds of a full cover
  is this project's decision (spec-fidelity round 1: a floor tied to area, so the impression of a covered yard holds).

## Review history

- Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - the south side widened from the edge to the sun corridor in
  map coordinates; the environment-driven knob set from a stated input, never a free roll; a mat-count floor tied
  to area. All three applied.
- Round 2 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - US3's test line still said "rolled from the seed"; rewritten
  to FR-005's rule. The three round-1 items confirmed fixed.
- Round 3 (spec-fidelity-verify, 2026-09-28): FAITHFUL - the US3 line resolved; no new drift.
