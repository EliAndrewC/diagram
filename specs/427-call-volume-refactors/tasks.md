# Tasks - feature 427, call-volume refactors

## Occasions

- none for T01 (a diagnostic; no map, sheet, glyph or placement changes). Each engine task filed after the survey names its own.

## Tasks

- [x] T01 `make perf-fanout`: the call-volume survey - per-stage call totals and growth, the multiplier chains by anchor, the fastest growers, the report in dev/perf-log (D1; FR-001, FR-002, SC-001; `l7r/diagram/tools/perf_fanout.py`, Makefile, `tools/CLAUDE.md`)
      research: rendering
      verify: DONE. landed: make perf-fanout: 8 tests red without it, 100% of tools/perf_fanout.py; run on the current engine it gives 24,140,034 calls @20 and 62,648,969 @40 against the hand survey's 24,140,555 and 62,798,345 (research/survey-t01.md); lane_wells 22.6M @40, growth exponent 2.24
- [ ] GM review (make gm-reviewed F=427) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
