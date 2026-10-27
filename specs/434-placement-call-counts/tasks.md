# Tasks - feature 434, call counts on the placement-stages page

## Occasions

- none: no map, sheet, glyph or placement changes (tooling; the engine is untouched)

## Tasks

- [ ] T01 The measurement: `make phase-calls` rolls one 40-household hamlet stage by stage, each stage under cProfile and each listed step under its own profiler while it is the innermost listed step running, and records per stage `calls`, `own` and `steps` in `dev/phase-calls.json`, newest per map type (D1, D2, D3, D6; FR-001, FR-002, FR-005, FR-006; `tools/phase_calls.py`, `Makefile`)
      research: rendering
- [ ] T02 The page: each stage heading carries the reference's calls and share (another type beside it as D4 says), and a last section after "Features this map does not have" tables every stage, each row opening on a click to its steps and its own work with calls, share of the stage and share of the roll (D4, D5; FR-003, FR-004, FR-005; `tools/placement_calls.py`, `tools/placement_stages.py`)
      research: rendering
- [ ] T03 The reference hamlet at 40 households measured and its counts checked against `make perf-fanout`; the row, dispersed, polder and dike-pond types measured where a 40-household roll of them stands; the page regenerated (SC-001 to SC-004)
      research: rendering
