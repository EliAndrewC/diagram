# Tasks - feature 427, call-volume refactors

## Occasions

- none for T01 (a diagnostic; no map, sheet, glyph or placement changes). Each engine task filed after the survey names its own.

## Tasks

- [x] T01 `make perf-fanout`: the call-volume survey - per-stage call totals and growth, the multiplier chains by anchor, the fastest growers, the report in dev/perf-log (D1; FR-001, FR-002, SC-001; `l7r/diagram/tools/perf_fanout.py`, Makefile, `tools/CLAUDE.md`)
      research: rendering
      verify: DONE. landed: make perf-fanout: 8 tests red without it, 100% of tools/perf_fanout.py; run on the current engine it gives 24,140,034 calls @20 and 62,648,969 @40 against the hand survey's 24,140,555 and 62,798,345 (research/survey-t01.md); lane_wells 22.6M @40, growth exponent 2.24
- [ ] T02 Call counts in `make perf`: a counting pass per seed and size, each stage's Python calls and the snapshot's versions recorded, its overhead measured (D2; FR-006; `tools/perf_snapshot.py`)
      research: rendering
- [ ] T03 The call counts are what is watched: the push refuses an unaccepted increase over the line, naming the arbiter command; timings printed only; the arbiter's and perf-audit's agent files, Principle VI and the docs (D3; FR-006, SC-005; `tools/perf_review.py`, `tools/perf_bands.py`, `scripts/sync-with-main.sh`, `.claude/agents/`, the constitution)
      research: rendering
- [ ] GM review (make gm-reviewed F=427) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
