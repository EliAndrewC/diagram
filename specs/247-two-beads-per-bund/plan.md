# Plan - 247 two beads per bund

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I**: the maps are re-rolled and the settlement-review dispatched beside the gate (`make verify`),
  since every hamlet manifest moves; the GM reads the reference hamlet.
- **VI**: `make map` on Inashiro first, then `make maps` over the pool, then the gate once, backgrounded,
  its notification acted on.
- **X**: no new module; `carve.py` and `comb.py` stay under 1,000 lines; the lifted helper that keeps
  runs of two is a plain function over lists, tested with lists.
- **XII**: a rendering convention by the GM's own words; no research pass, no source; the record's
  convention paragraph and the modal say the convention and state no finding.
- **XIII**: the baseline is the last green `make done` in the run log; the gate's own water-honesty test
  and every other test must stay green on the re-rolled pool.
- **XVI**: spec-fidelity MODE 2 before code; this plan reviewed (MODE 4) before any tick.
- **Route**: `l7r/diagram/waterfields/carve.py`, `l7r/diagram/settlement/fields/comb.py`, the five
  hamlet manifests and the class docstring are engine content - GATED (LOCAL-GATED, `remote off`).

## Design

- `waterfields/carve.py` `_bund_beans`: the shuffle and `R.randint(1, 2)` unchanged (spec D2 of round
  1, FR-003). Per chosen edge: `nd = int(dist / spacing)`; `nd == 2` becomes 3 (two beads at the thirds,
  FR-002); the beads at `t / nd` for `t` in `1..nd-1` as today, each tested by `buried`/`wet` as today;
  the survivors are split at every dropped position and each part of two or more beads is a run
  (FR-001). A module-level `_bead_runs(beads, alive)` does the split-and-judge over a list of points and
  a predicate, with `MIN_BEADS_PER_RUN = 2` and the GM's reason beside it - the one place the rule
  lives, used here and at the draw site. The function returns the runs (`list[Poly]`).
- `waterfields/comb.py` `_comb_dry_and_beans` returns the runs; `build_comb`'s net carries
  `bund_bean_runs` (the runs) and `bund_beans` (the runs flattened). `hill.py` and `polder.py` nets gain
  `bund_bean_runs: []` beside their empty `bund_beans`.
- `settlement/fields/comb.py` `_comb_drop_drowned_beads`: the pond and recorded-ditch tests become one
  predicate over a bead; `_bead_runs` is applied to each run of `net["bund_bean_runs"]`; the kept runs
  are written back and `net["bund_beans"]` re-flattened from them, so the draw and the record read one
  list. The field record is unchanged in shape (spec D3).
- Tests: `tests/settlement/test_core.py` - `_bead_runs` over plain lists (a middle drop splits, a part
  of one is dropped, a part of two survives); a short edge yields two beads at its thirds and a long edge
  the spacing; the two existing drop tests re-asserted on runs; the random state after `_bund_beans`
  equals the previous code's on the same input (the old laying reproduced inline in the test).
  `tests/settlement/test_fields.py` - the draw-site pond drop removes a part left with one bead and
  keeps a part of two; the record's flat list equals the kept runs flattened. `tests/gate/
  test_bunds_and_dikes.py` - parametrized over the shipped hamlet generators (`pool/hamlets/*/*.gen.py`, the sweep's own
  list, Kuwabata with no bead-bearing field among them), each manifest read through `_pool.obtain` so the
  sweep's one roll serves it: the segments derived from `plot_rings` + `bund_beans` by the R1 method all hold two
  or more, and a map with no beads is skipped, not passed.
- The record: `research/fields.html` convention paragraph gains one sentence; the `BundBeans` class Note
  gains the same; `make glossary CHECK=1` / `make citations CHECK=1` confirm nothing stale.
- The maps: `make map GEN=pool/hamlets/inashiro/inashiro.gen.py`, look at it, then `make maps`, then
  `make verify` in the background and the settlement-review beside it; R1's script re-run over the
  regenerated manifests for SC-001.
