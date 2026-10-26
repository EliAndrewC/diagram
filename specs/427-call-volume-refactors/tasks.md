# Tasks - feature 427, call-volume refactors

## Occasions

- none for T01 (a diagnostic; no map, sheet, glyph or placement changes). Each engine task filed after the survey names its own.

## Tasks

- [x] T01 `make perf-fanout`: the call-volume survey - per-stage call totals and growth, the multiplier chains by anchor, the fastest growers, the report in dev/perf-log (D1; FR-001, FR-002, SC-001; `l7r/diagram/tools/perf_fanout.py`, Makefile, `tools/CLAUDE.md`)
      research: rendering
      verify: DONE. landed: make perf-fanout: 8 tests red without it, 100% of tools/perf_fanout.py; run on the current engine it gives 24,140,034 calls @20 and 62,648,969 @40 against the hand survey's 24,140,555 and 62,798,345 (research/survey-t01.md); lane_wells 22.6M @40, growth exponent 2.24
- [x] T02 Call counts in `make perf`: a counting pass per seed and size, each stage's Python calls and the snapshot's versions recorded, its overhead measured (D2; FR-006; `tools/perf_snapshot.py`)
      research: rendering
      verify: DONE. landed: make perf records each stage's Python calls per seed and size (a counting pass after the timed rolls, sys.monitoring PY_START on the first free tool id) and the interpreter/numpy/shapely versions; tests red without it (counts deterministic per seed, a refusal keeps earlier stages); the pass costs 12.4 s for the 4 reference seeds against 11.4 s timed (about 1.09x a plain roll, snapshot 20261026T172151Z-adhoc)
- [x] T03 The call counts are what is watched: the push refuses an unaccepted increase over the line, naming the arbiter command; timings printed only; the arbiter's and perf-audit's agent files, Principle VI and the docs (D3; FR-006, SC-005; `tools/perf_review.py`, `tools/perf_bands.py`, `scripts/sync-with-main.sh`, `.claude/agents/`, the constitution)
      research: rendering
      verify: DONE. landed: the push watches call counts: tests red without it (perf_calls 5, perf_review 28, sync suite 132); US5's test on a scratch worktree - a 300,000-call loop in stage_sink refused the check naming make arbiter-ask SUBJECT=999-calls-<commit>, the timing's +8.6% printed as information only (research/us5-t03.md); Principle VI 2.33.0, the arbiter's and perf-audit's agent files and the docs; perf_fanout registered
- [x] T04 US2, the contained wins: the cheap wins C1-C3 and C5 and the single-site recomputations R2, R3, R5 and R6 (research/hotspots-cheap-wins.md, research/hotspots-recompute.md), each scoped against the T01 survey (research/survey-t01.md) with its chain's count before and after (FR-002, FR-003, US2)
      research: rendering
      verify: DONE. landed: the contained wins (C1 C2 C3 C5 R2 R3 R5 R6): at seed 39, 40 households, set.add in the windbreak 1,052,833 -> 0, _falls' to_uf chain gone (to_uf 513,948 -> 83,038, all from _f_at_u), the ring_index and pts_key generators 361k / 229k, the crop's 122k, _near_a_house 56k, the union-find's find 109k and getpixel 36k all under the survey's 50k (research/t04-contained-wins.md); the pool unchanged against HEAD after both batches; scipy 1.16.3 declared; claims 2 IN-STEP
- [x] T05 US3, the wells without the cubic term: the shared wells seated with kept state (R1), lane_wells' 22.6M calls at 40 households (research/survey-t01.md) to under 100k (FR-003, US3)
      research: rendering
      verify: DONE. landed: the wells without the cubic term; arbiter accept on the 0.5 s GUESS
- [x] T06 Carried by the claims gate (385 FR-013): findings on code the change left unchanged - fix the code or the claim and re-check each: l7r/diagram/hamletgen/homesteads/wells.py::seat_wells#PAIR_LOOK = 40: how many first-well seats nearest the share's middle are re-ranked by whether a second well would keep both at ten (search breadth, a GUESS) [lands-open]
      research: rendering
      verify: DONE. landed: PAIR_LOOK's claim relabeled GUESS
- [x] T07 US4, the homestead parts family: the homesteads stage's pairwise chains (research/hotspots-pairwise.md) with R8 (research/hotspots-recompute.md), each chain at least tenfold down (FR-003, US4); R4 moved to its own task, T12
      research: rendering
      verify: DONE. landed: homestead parts family's chains tenfold down (R4 to T12); pool unchanged but Kuwabata (kura/byre 3 ft, 0081)
- [ ] T08 US4, the ground cover family: the hinterland and windbreak stages' pairwise chains (research/hotspots-pairwise.md), each at least tenfold down (FR-003, US4)
      research: rendering
- [ ] T09 US4, the water family: the field settle (R7, research/hotspots-recompute.md) and the brook and partition chains (research/hotspots-pairwise.md), each at least tenfold down (FR-003, US4)
      research: rendering
- [ ] T10 US4, the lane web and the lane law, after feature 417's lane conversions (request.md 5): the web stage's pairwise chains (research/hotspots-pairwise.md), each at least tenfold down (FR-003, US4)
      research: rendering
- [ ] T11 The 427-end bookend and the report: SC-002 and SC-003 measured against 427-start (FR-005), make feature-report F=427 WRITE=1
      research: rendering
- [x] T12 US4, R4 on its own: household_reach without laying four whole homesteads per candidate, the per-seat rolls kept (feature 297 R9), its chain at least tenfold down (FR-003, US4)
      research: rendering
      verify: DONE. landed: R4 4.8x down, arbiter accept (ask:427-T12-r4); pool unchanged
- [x] GM review (make gm-reviewed F=427) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
