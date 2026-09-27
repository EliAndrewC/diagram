# Feature 273 - hamlet graveyards: where a hamlet's dead lie, and the village's funerary grounds drawn by the generator

**Feature Branch**: `273-hamlet-graveyards` (no branch; `export SPECIFY_FEATURE=273-hamlet-graveyards`)

**Created**: 2026-09-27

**Status**: specified; awaiting spec-fidelity

**Input**: the GM's answer of 2026-09-27 to feature 272's item on village cremation, verbatim in [`request.md`](request.md).

## Summary

The GM ruled that a VILLAGE - the main settlement of a village district, where the headman and the country monk live
- carries the district's shrine, the headman's house and a cremation ground, and a HAMLET (a settlement too small for
a headman, about half a dozen to a district) carries none of them; monks perform the funerary rites in the countryside.
The GM is unsure whether a hamlet keeps a graveyard of its own, sends its dead to the village's, or brings the bones
home from the village's cremation ground to inter near the hamlet, and asked for a research pass: if the history points
one way, the maps follow it; if it does not, the choice is a knob rolled per hamlet. The record is changed to carry the
ruling, the question is researched, and the generator draws what the answer says. Feature 269 handed this feature its
owed burial-generator change (the village's burial ground in the shrine or temple yard or apart, and its siting), which
is designed here with the hamlet rule as one change.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The ruling is in the record (Priority: P1)

A reader of the record finds that a village has a cremation ground and a hamlet has none, that the monk performs the
rites, and that the village alone keeps the shrine and the headman's house - as the GM's ruling, not the record's
reading.

**Acceptance Scenarios**:

1. **Given** religion-and-death 530 and the tier table 210, **When** read, **Then** the village's cremation ground and
   the hamlet's lack of one are stated as the GM's ruling of 2026-09-27.

### User Story 2 - Where a hamlet's dead lie (Priority: P1)

A reader finds, in a new question, whether a hamlet kept a graveyard of its own, used the village's, or interred bones
brought back from the village's cremation ground near the hamlet - each form attested or not, in Japan and China - and
what the maps do about it: one rule where the history agrees, a per-hamlet knob where it does not.

**Acceptance Scenarios**:

1. **Given** the research pass, **When** the evidence points one way, **Then** the question states the rule and every
   hamlet follows it; **When** it supports more than one form, **Then** the question names each form, cited, and the
   knob's odds (sourced or labeled a guess).

### User Story 3 - The generator draws it (Priority: P1)

A generated hamlet draws a graveyard of its own, or none, as the rule or its rolled knob says; a generated village draws
its cremation ground (religion-and-death 530) and its burial ground seated as 269's research says (280: in the shrine or
temple yard or apart; 270: a ground apart downstream, beyond the last house) - with the ruling that a hamlet draws no
cremation ground and no shrine.

**Acceptance Scenarios**:

1. **Given** a rolled hamlet, **When** the knob or rule says it keeps a graveyard, **Then** it draws one seated by the
   researched siting; **When** it does not, **Then** it draws none; the manifest records which.
2. **Given** a rolled village, **When** drawn, **Then** it carries a cremation ground and a burial ground seated by the
   researched rules, and no hamlet carries a cremation ground.

### Edge Cases

- 269's sections 270 and 280 are not yet on main: the village burial ground's seat (US3's second half) lands once they
  are; if 269 is still hours away when the rest is ready, the hamlet part lands first and the village part is a later
  task of this feature.
- The GM's canon governs the setting; the history is reported against it.
- The field graves two hamlets carry today (Kashikawa, Mizuguchi) are a separate feature (the in-field grave island);
  this feature says whether the new rule changes them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: religion-and-death 530 and 210 MUST state the GM's ruling of 2026-09-27 (a village has a cremation ground,
  a hamlet has none; monks perform the rites; only the village keeps the shrine and the headman's house).
- **FR-002**: A new question in religion-and-death MUST answer where a hamlet's dead lie (its own graveyard, the
  village's, or bones brought home), in Japan and China, cited or recorded silent after the search, citing 269's 170,
  270, 280 and 271's 400 rather than restating them; it MUST end in a rule or a knob with its odds.
- **FR-003**: The hamlet generator MUST draw a hamlet's graveyard, or none, per FR-002's rule or knob, recording which
  in the manifest; the village generator MUST draw a cremation ground (530's rule) and a burial ground seated by 280's
  knob and 270's siting, and no hamlet MUST draw a cremation ground.
- **FR-004**: Every new or changed entry MUST pass the record's checks (source-reader, quote-check, record-format,
  source-applicability, entry-drift); every source only a human can fetch goes on the GM's download list.
- **FR-005**: Every pool map whose layout moves MUST be reviewed (settlement-review) and `make done` green.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): 530 and 210 carry the ruling as the GM's.
- **SC-002** (FR-002): the new question answers the three forms with citations or absence notes, and names a rule or a
  knob with odds.
- **SC-003** (FR-003): a roll test shows a hamlet with a graveyard and one without (a knob) or every hamlet alike (a
  rule), a village with its cremation and burial grounds, and no hamlet with a cremation ground.
- **SC-004** (spec-wide; FR-004, FR-005): the record's checks applied; `make done` green; reviews ledgered.

## Assumptions

- "Hamlet" and "village" are the generator's two to-scale tiers of the same names (roll.py: "a hamlet needs no
  headman/shrine/cemetery, a village adds them").
