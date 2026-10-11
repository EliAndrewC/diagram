# Feature Specification: Did a village lane ever run between a house and its own grove?

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-08 (filed); specified 2026-10-11
**Status**: In progress - specified

**Affects**: hamlet, research record

**Input**: the GM's request, verbatim in `request.md`: the filed entry (feature 287's woods review, 2026-09-29), the GM's
scoping of 2026-10-10 (*"just do the research and update the implementation's tagging so that it shows up on the claims
report as either something with evidence or which is not implemented in accordance with our research"*) and the go-ahead of
2026-10-11.

## Why

A reviewer of feature 287's woods found dooryard-copse crowns whose nearest farmhouse stood across a lane. The maps settle
it by construction: feature 287 reserves each household's copse seats and keeps every later lane off them (woods W25,
`overlap/reserved.py`, `Reservations.conflicts`), so a lane never runs through a household's own wood share. But no research
page says whether a real village lane ever ran between a farmhouse and its own grove. The question is neither answered nor
recorded as a guess or an absence, so `make open-questions` cannot list it and the code's claim rests on a drawing page
(0071's) that does not ask it.

## User Scenarios & Testing

### User Story 1 - The record answers the question (Priority: P1)

A reader of question 0036 (groves around farmhouses) who wonders whether a lane could pass between a house and its grove
finds the answer: what the sources show, or a stated absence naming what was searched.

**Acceptance Scenarios**:

1. **Given** 0036's findings page, **When** a reader looks for whether a lane ran between a farmhouse and its own grove,
   **Then** the page states it with a footnoted source, or states that no source read says, with an absence note naming
   the search.

### User Story 2 - The claims report shows where the code stands (Priority: P1)

The GM opens `make claims-report` and sees the code that keeps lanes off a household's wood share judged against that
finding: IN-STEP with its evidence, or DRIFTED from it.

**Acceptance Scenarios**:

1. **Given** the code FR-003 lists, **When** `make claims-report` runs, **Then** each of its `Research:` claims cites
   0036's findings page and carries an `impl-drift` verdict, and what no code decides is in `implementation-check.md`.

### Edge Cases

- The sources show both forms (a lane between a house and its grove in some villages, not in others): the record says so,
  and the claim is judged against it; per the project's knob doctrine that is a DRIFTED verdict on code that draws one form
  only, recorded, not fixed.
- The record is silent: the absence note is the finding, and the claim cites it as the code's guess.

## Requirements

### Functional Requirements

- **FR-001 - The research pass.** The archive first (`make archive-find`), then the web, for whether a village lane or path
  ran between a farmhouse and its own homestead grove (yashikirin, a dooryard grove or copse), in Japan and in the setting's
  first reference, China.
- **FR-002 - The finding recorded on 0036.** `research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html`
  gains the answer under a heading a reader would ask, each assertion footnoted to a passage quoted verbatim from a page the
  reader can open, or, where nothing is found, an absence note naming the searches. The record's checks owed by the change
  are answered (`make record-owed`).
- **FR-003 - The claims.** The units whose claims decide the question are found by a recorded search: the claims index's
  keys and notes (`dev/claims-index.json`) and the `Research:` claim text in the code and the procedures, each matched against
  `(wood|woodlot|copse)s?'?[ -]seats?|seat off a lane|lane gap`, kept where the claim governs how a way stands to a
  household's wood seats. On 2026-10-11 they are:
  - `overlap/reserved.py` `Reservations.conflicts` (#wood seats);
  - `hamletgen/homesteads/household_ways.py` `seat_walls` and `seated_parts` (#the track off the wood seats);
  - `hamletgen/homesteads/region.py` `SeatRegion.sync` (#reserved wood seats bar lane ground);
  - `hamletgen/homesteads/stages.py` `reserve_the_seating` (#a lane's buffer about a copse seat);
  - `hamletgen/ways/track.py` `_connector_through` (#gives up a wood seat as last resort);
  - `hamletgen/ways/web.py` `stage_web` (#web lanes routed round the households' reserved wood seats as fabric);
  - `settlement/rolling/gap_ways.py` `Layers` and `lane_layers` (#lane ground);
  - `settlement/rolling/passage.py` `walk_clear` (#walk crosses nothing standing);
  - `settlement/homestead_parts/wood_share.py` `WoodShares.__init__` (#seat off a lane);
  - `hamletgen/homesteads/growth.py` `footprint` (#the household's wood): the seating's placement of a household's seats
    beside its house, the code that may decide whether a lane can come BETWEEN a house and its own seats.
  Left out, each because its rule is not a way's: the bamboo stands' (`hinterland/bamboo.py` `bamboo_seats`,
  `homesteads/bamboo.py` `household_bamboo`), the grove fill's (`grove_fill.py` `grove_blocks`, `reseat_clump`), the seats'
  own pitch (`wood_share.py` #copse seat pitch) and their reservation (`stages.py` #wood seats reserved).
  Each of these claims cites 0036's FINDINGS page and is re-judged by `impl-drift`, so `make claims-report` shows each IN-STEP
  with evidence or DRIFTED from it. Where the finding does not reach a claim's detail (a buffer's distance the sources do not
  give), that claim stays a labeled guess citing 0036's absence. Any part of the question no code decides is recorded as
  implemented nowhere in `implementation-check.md`, with what was searched (feature 378).
- **FR-004 - No map change.** No generator, placer or map changes; a DRIFTED verdict is recorded, not fixed (the GM's scope).
- **FR-005 - The implementation check.** `make impl-check F=352` reports nothing missing.

## Success Criteria

- **SC-001** (FR-001, FR-002): 0036's findings page answers the question or states its absence with the search named, and
  `make record-owed UNANSWERED=1` lists nothing.
- **SC-002** (FR-003, FR-005): `make claims-report` lists every claim FR-003 names citing 0036 with a verdict, and
  `make impl-check F=352` reports nothing missing.
- **SC-003** (FR-004): the delta changes no engine line beyond a docstring's claim, and no map.

## Assumptions

- 0036 is the question the filed entry names; the copse's own drawing question (0071) keeps its claim.
- The research may find nothing; an absence is a finding.

## Decisions Recorded

(none yet)

## Review history

- Round 1 (spec-fidelity, 2026-10-11): CHANGES REQUIRED - FR-003 named one claim where the rule is claimed in seven units,
  several UNRESEARCHED, and `conflicts` does not decide "between". Applied: FR-003 lists the units a recorded command finds,
  each re-judged against 0036's findings, the seating's placement named, and what no code decides goes to
  `implementation-check.md`; US2 and SC-002 reworded to match.
- Round 2 (spec-fidelity-verify, 2026-10-11): CHANGES REQUIRED - the list omitted `gap_ways.py`, which the search returned,
  and the pattern missed the code's own wording ("woodlots' seats", "seat off a lane"). Applied: the search reads the claim
  text too, with a widened pattern; `gap_ways.py` (`Layers`, `lane_layers`), `passage.py` `walk_clear` and `wood_share.py`
  (#seat off a lane) added; `growth.py` named by its claim; the exclusions stated with their reason.
- Round 3 (spec-fidelity-verify, 2026-10-11): FAITHFUL - the search re-run returns exactly the ten listed claims and five stated exclusions. Aside for the plan review: plan.md's Technical Context and Project Structure predate round 2 (the claim-text search; gap_ways, passage, wood_share).
