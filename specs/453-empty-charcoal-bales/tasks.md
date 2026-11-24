# Tasks - feature 453, what an empty charcoal bale cost

The question task is `research: physical` with its five boxes; the rest are `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [ ] T01 S1+C1: the empty bale (D1; FR-001, FR-002, FR-005, FR-006, FR-007)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
      verify: `make record-owed` names no unit of the new question or of 0279; `make record CHECK=1` passes
- [ ] T02 The implementation check, the reply on #23 and the report (D2; FR-001, FR-003, FR-004)
      research: rendering
      verify: `make impl-check F=453` reports nothing missing; the reply is on diagram#23
- [ ] GM review (make gm-reviewed F=453) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
