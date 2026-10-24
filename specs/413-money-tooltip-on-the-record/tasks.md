# Tasks - feature 413, a tooltip converting every historical amount of money in the record

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [ ] T01 The vendored table and its refresh; the build reads, refuses and writes the box text; the tests (D1, D2, D3, D4, D7; FR-001 to FR-005)
      research: rendering
      verify: the money tests green and each red with its change removed; make money-conversions CHECK=1 exits 0; make record CHECK=1 green
- [ ] T02 The hover in record.js and record.css (D5; FR-004)
      research: rendering
      verify: a built question page with a marked amount shows the box (opened by hand, the figures read back)
- [ ] T03 The back-fill of every amount in the record's fragments (questions, drawing pages and their notes) in the two built eras (D6; FR-006)
      research: rendering
      verify: make money-candidates CHECK=1 exits 0 (every listed amount marked or named in backfill.md with its reason); make record-owed names nothing for the marking
- [ ] T04 The reply on #14 (D8; FR-007)
      research: rendering
      verify: the comment's URL
- [ ] T05 Close: report and land
      research: rendering
      verify: landed on the gated route
- [ ] GM review (make gm-reviewed F=413) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
