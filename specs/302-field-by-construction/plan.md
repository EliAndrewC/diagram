# Implementation Plan: the comb field built by construction

**Branch**: none (main, clone `diagram-performance`) | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

## Summary

Phase 0 builds the field-by-construction method as a prototype in `specs/302-field-by-construction/` and times it against the
current `fit_field` on the same captured inputs (`harness.py`). Phase 1 - only on GO - moves the method into the engine,
retires the seam repair and the acreage prediction for comb fields, and re-gates the pool. Phase 1's design is written as an
amendment to this plan once Phase 0 has measured which parts of the prototype survive; the decisions below that already bind
it are marked.

## Technical Context

**Language/Version**: Python 3.14, shapely 2, numpy. **Testing**: pytest through `make`; the Phase 0 harness through `make
spec-harness`. **Target**: the scripted hamlet generator's comb field (`hamletgen/water/fit.py`, `waterfields/`).
**Constraints**: maps may move within the rules (GM 2026-09-30); `100%` coverage; the 1,000-line bar.

### The baseline, measured (research R1)

`fit_field` per recorded input, fastest of three (observed 2026-10-01, method: `harness.py` `timed_fit`, load ~7): Inashiro 1.05 s, Kashikawa 1.10, Mizuguchi
0.57, Sawada 2.39, Inashiro at 10 households 0.82, at 20 1.26. The seam repair `close_seams` is 47-70% of each; the acreage
prediction `planted_area` 11-18%; the plot cutting `_carve` 8-15% across 2-4 trial carves; the skeleton (canals, threads,
march, drain) under 4%; the dry hem and beans 2-12%.

## Performance bookends (constitution VI)

| | label | total | notes |
|---|---|---|---|
| before | `302-start` | 15.3 s (median 3.9, worst 4.4) | unmodified code, before the first engine edit (`dev/perf-log/20261001T201403Z-302-start-diagram-performance.json`) |
| after | `302-end` | | before the push, Phase 1 only |

## Phase 0 design (the prototype)

- **D1 The inputs are captured, not rebuilt.** The harness rolls each recorded input to its field stage and captures
  `fit_field`'s arguments; both methods run on fresh deep copies of them. The prototype reuses the engine's skeleton steps
  (`_comb_skeleton` through `round_channel_joints`, exactly as `carve_comb` calls them) - they are the inputs, under 4% of the
  time, and not what is being replaced.
- **D2 The planted region is the command area less its water.** Per trial size: the envelope `carve_comb` would build
  (`_comb_floor_and_winding`'s ring: the canal, the outer threads, the drain, the floor trim), less `_water(channels)`, less
  `_outside_command(...)` - the same three geometries `close_seams` and `planted_area` take as the ground to be planted. Its
  area is the acreage (FR-007); no plots are cut during the search. Each trial is scored as today on (illegal, acreage error):
  its water's legality is `fan_legal` asked of the region's outline in place of the plots' (the two predicates that read the
  plots, `tail_dangles` and `flanks_commanded`, read only their extent, which the region's outline carries) and the channels.
- **D3 The partition.** On the winning size, the region is cut by the row and column bunds: per sector between adjacent
  threads, the row lines at the carve's row falls (row step rolled as today) and the column lines at the carve's `nsub`
  divisions, both with the carve's contour wobble and row wander, each line drawn across its sector and clipped to the region;
  the threads themselves bound the sectors. The cells are `polygonize` of the noded union of the region's boundary and the
  cut lines, kept where they lie in the region - every edge shared by construction.
- **D4 Rules at construction: merge or split, as the repair resolves them today.** Each cell is judged by `ring_violations`
  in `fan_context`'s context (the engine's own) and by the toe discipline `_comb_toe_and_hem` drops by (thinness, area, apex,
  chevron). A staircase is split on its hops by the repair's own `_split_steps` (`seams/close.py`); any other violating cell
  is merged into the adjacent cell (shared bund) whose union holds the rules, the longest shared bund first, and a merged
  cell that is left a staircase is split in turn. A cell that neither fixes is LEFT BARE, as the repair leaves it
  today (`hold_ring_rules`' third way, "the odd corner left unpaddied"), held under SC-003's bare-ground bound.
- **D5 Everything after the plots runs as today.** The dry hem and the beans (`_comb_dry_and_beans`) and the net's assembly run
  on the prototype's plots, so their cost is in the prototype's time (SC-004).
- **D6 The verdict is computed by the harness.** Both methods fastest of three, back to back per input; totals; each method's
  spread (largest difference between its three runs' totals); GO when current - prototype > the larger spread (SC-001); the
  validity checks of SC-003 printed per input: acreage band, bare ground (region minus the union of plots, as a share of the
  region), unshared bunds (a plot edge not covered by a neighbor or the region boundary), `ring_violations` count.

## Phase 1 design (binding decisions; the rest amended in after GO)

- **D7** The partition replaces `_carve`'s plot cutting, `_comb_toe_and_hem`'s drop, `close_seams` and `planted_area` for
  comb fields; what of the seam machinery nothing else calls is deleted with its tests, each rule it held carried by a test of
  the construction (FR-011). Polder and hill engines unchanged.
- **D8** The fit scores each trial size on its region - its acreage and its water's legality (D2) - and `fan_admissible`
  judges the built net, as today.
- **D9** The smaller levers: the union prediction is retired with what it predicted (FR-010: no longer applies); the number of
  trial sizes is re-measured once the region makes a trial cheap and kept or cut by that measurement.

## Constitution Check

- **I, II**: N/A - no UI in this repository.
- **III, IV, V, VII, VIII, IX**: N/A - no pool content written by hand, no SOURCE blocks, no in-world prose, no setting detail.
- **VI. Verify before reporting done**: Phase 0 - the harness run and its verdict in `research.md`. Phase 1 - `make quick`
  while iterating, Inashiro regenerated first, then the pool (`make maps`), then `make done`; the bookends above; the review
  checks the delta's occasions owe (the field's placement rule substantially changes: a glyph-check of the paddy fabric on
  Inashiro, declared in `tasks.md` `## Occasions`).
- **X. Python discipline**: ruff, ruff format, pyrefly, `100%` coverage, the 1,000-line bar; the prototype lives in `specs/`,
  outside the engine and its coverage.
- **XII. Historical grounding**: the fabric's form (every scrap planted, every bund shared, toe slivers taken into a neighbor)
  is unchanged and already recorded (`research/contents.json#fields`, cited in `seams/close.py`); this feature changes how it is reached.
  Each research pointer that names `close_seams` is re-aimed at what replaces it in Phase 1.
- **XIII. No known regressions**: the baseline is the harness's base run and the pool at this feature's base; every pool map
  stays green.
- **XIV. Fix defects where found**: in scope as found.
- **XVI. Build what was asked**: the spec is FAITHFUL at round 2; any exception goes to `spec-fidelity`.

## Project Structure

```text
specs/302-field-by-construction/
  request.md  spec.md  plan.md  research.md  tasks.md
  harness.py      # Phase 0: capture, the current fit timed, the prototype timed, the verdict
  prototype.py    # Phase 0: the field by construction, importing the engine read-only
```

Phase 1 touches `l7r/diagram/waterfields/` (a new module for the partition; `comb.py`, `carve.py`, `seams/`) and
`l7r/diagram/hamletgen/water/fit.py`, with their tests.

## Amendment 1 (2026-10-01): Phase 1's design, after the GO (research R2)

Phase 0 measured GO (6.558 -> 2.414 s over the six inputs, 2.72x, spread 0.05 s). The engine takes the prototype's method as
R2 records it, every dead end R2 lists left out.

- **D10 Three engine modules, each under the 1,000-line bar.** `waterfields/partition.py` - the planted region of a carve
  (D2), the sectors and their pieces, each sector's lattice (rows with the wander, columns with the wobble, thinning where it
  narrows, a narrow sector's rows spaced for it, the outer strip's lattice), the hug filter, and `cut` (the noded union and
  `polygonize`). `waterfields/settle.py` - the rules at construction (D4): the snap to the recorded grid, `_split_steps` (moved
  from `seams/close.py`, with `_cut_on_hop`), the merge (opened by 0.3 px; clusters grow), the scraps left bare.
  `waterfields/tint.py` - the carve's `low` marking and FLOODED sample, and `close_seams`' tint judgment moved verbatim (its
  six clauses, the promotion of the most basin-like low plot when the sample comes back empty).
- **D11 The carve lays the skeleton and the region; the finish lays the plots.** `carve_comb` keeps its signature and body up
  to `round_channel_joints`, then builds the envelope and the region and returns a `CombCarve` with `region` and no plots;
  `CombCarve.net` hands the fit's scorers the region's outline in place of the plots (D2/D8); `finish_comb` partitions,
  settles, tints, runs the dry hem and the beans, and assembles the net exactly as today. `build_comb` stays
  `finish_comb(carve_comb(...))`, so the village roll (`settlement/rolling/roll.py`) builds its comb fields the same way.
- **D12 The fit reads the region's area.** `_fit_at_aspect` scores each trial on `carve.region.area` (FR-007);
  `CombCarve.planted_area` and its union are deleted (FR-010: the area-sum lever no longer applies - there is nothing left to
  predict). The number of trial sizes is unchanged: a trial now costs the skeleton and three shape operations (0.02 s), so
  fewer trials would buy little and the probe's record (feature 284) says cutting them moved maps out of the rules.
- **D13 Retired, with the rule each held carried by a test of the construction (FR-011).** From `carve.py`: `_carve`,
  `_carve_plots`, `_carve_sector`, `_hem_pass`, `_spills_drain`, `_bank_chord`, `_above_canal`, `_supply_index`,
  `_clear_supply`, `_quad_in_supply`, `_edge_in_supply`, `_extend_span` (`_bnd` and `_root_f` stay - the partition's bounds);
  `sector_rows.py` whole; from `comb.py`: `_comb_toe_and_hem` and the plot half of `_comb_floor_and_winding` (the envelope half
  stays); from `seams/`: `close_seams` and every function only it reached (`pockets._absorb` and the pocket geometry,
  `plots._plant`/`_tab_cut`/`_unjog`/`_trade`, `_visible_parts`, `_repair_crossing_rings`, `_shed_necks`) - `hold_ring_rules`
  and `_weld_within_rules` stay, because `settlement/fields/features.py` re-holds the rules after a grave is cut from a plot,
  with what they import. Each test of a deleted function is deleted with it; the rules they held are the ring rules
  (`ring_rules.py`, unchanged, its tests unchanged), the toe discipline (now asked in `settle.py`, tested there), and the seam
  sharing (a new test: a finished comb net leaves no bare ground in its region beyond its scraps and shares every bund - SC-007).
- **D14 What the prototype left open is judged on the maps, not guessed.** A few cells came out larger and longer than the
  carve's, and three inputs carry 10-30% fewer plots (R2). After Inashiro and the pool regenerate, the gate judges every rule,
  the paddy glyph check (the Occasions line) judges the fabric on Inashiro, and a finding is fixed in the lattice before the
  push (constitution XIV).
- **D15 The red-green order.** Each new module lands with its unit tests first (plain inputs: a hand-built sector, a hand-built
  cell list), then the switch in `comb.py` and `fit.py`, then the deletions, then the coverage floor; Inashiro is regenerated
  first, then the pool.
