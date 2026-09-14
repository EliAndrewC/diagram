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

- `waterfields/carve.py` `_bund_beans`: after `R.shuffle(order)`, keep only edges whose
  `int(dist / spacing)` is at least 3 (two interior beads at the spacing), then take `[: R.randint(1, 2)]`
  of those - the draws are the same as before (spec D2). Each chosen edge's surviving beads form a run;
  a run with fewer than two after the burial and ditch drops is not kept. The function returns the runs
  (`list[Poly]`); a module-level `_bead_runs_kept(runs)` keeps runs of two or more and is the one place
  the minimum lives (`MIN_BEADS_PER_RUN = 2`, with the GM's reason beside it and R2/R3 pointed at).
- `waterfields/comb.py` `_comb_dry_and_beans` returns the runs; `build_comb`'s net carries
  `bund_bean_runs` (the runs) and `bund_beans` (the runs flattened). `hill.py` and `polder.py` nets
  gain `bund_bean_runs: []` beside their empty `bund_beans`.
- `settlement/fields/comb.py` `_comb_drop_drowned_beads`: the pond and recorded-ditch filters apply per
  bead within each run of `net["bund_bean_runs"]`, then `_bead_runs_kept`, then `net["bund_beans"]` is
  re-flattened from the kept runs, so the draw and the record read one list. The field record adds
  `"bund_bean_runs": [len(run) for run in runs]` beside `bund_beans` (spec D3).
- Tests: `tests/settlement/test_core.py` - a run left with one bead by a later plot is dropped whole; a
  run left with one under the ditch net is dropped whole; an edge shorter than three spacings yields no
  beads while a longer edge of the same plot does; the random state after the call equals the old
  function's on the same input (the old choice logic reproduced inline in the test). `tests/settlement/
  test_fields.py` - the draw-site pond drop removes a run left with one; the record's run lengths sum to
  the bead count. `tests/gate/test_bunds_and_dikes.py` - every shipped manifest's runs hold two or more
  and sum to the count.
- The record: `research/fields.html` convention paragraph gains one sentence; the `BundBeans` class Note
  gains the same; `make glossary` / `make citations CHECK=1` confirm nothing stale.
- The maps: `make map GEN=pool/hamlets/inashiro/inashiro.gen.py`, look at it, then `make maps`, then
  `make verify` in the background and the settlement-review beside it; R1's script re-run over the
  regenerated manifests for SC-001.
