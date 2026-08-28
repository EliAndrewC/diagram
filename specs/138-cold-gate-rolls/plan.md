# Implementation Plan: The Cold Gate - Faster Rolls, and a Cache Warmed While Idle

**Branch**: none (`SPECIFY_FEATURE=138-cold-gate-rolls`) | **Date**: 2026-08-28 | **Spec**: [spec.md](spec.md)

## Summary

A profile of the seed-19 polder (110 s) put 57 s in `stage_web` and 22 s in `stage_track`, none of it in
field fitting. Both are brute-force inner loops: `_route` builds a free-lattice by calling `clear_runs` once
PER CELL (165,611 calls; each re-derives every polygon's bounding box and then measures `seg_dist` against
every polygon that survives - 36 million calls), and `path_violations` counts pairs of water crossings within
a deck length by comparing every pair (170 million `hypot` on a polder whose grid ditches produce thousands
of crossings). The plan: (1) a **fabric index** built once per `_route`/`clear_runs` call - per-polygon
bounds computed once, a coarse cell grid over the routing box mapping cells to the obstacle/tight/line
candidates whose bounds reach them - so a sample's clearance test measures only its cell's candidates;
(2) the **crossing sweep** - sort the hits along one axis and compare only within the deck length; (3)
prove **byte identity** on every gate roll and live pool map against the baseline taken before the first
edit; (4) perf bookends; (5) the idle run verified to warm every cache the interactive gate reads; (6) the
budget comment corrected.

## Technical Context

Python 3.14; pure-Python geometry (`settlement/_geom/primitives.py`); no new dependency. **Single-artifact
target**: the seed-19 polder (`stage_web` 57 s / `stage_track` 22 s) - proven first, then every gate roll
and the live pool by manifest byte-identity (`make maps` covers the reference and the pool tier). **Every
step is two steps**: polder, then pool.

## Performance bookends

| | label | notes |
|---|---|---|
| before | `138-start` | taken on unmodified code in the background at feature open |
| after | `138-end` | before the push; `make perf-report AGAINST=138-start`; a slower seed is diagnosed in writing |

## Constitution Check

- I/II/III/IV/V/VII/VIII/IX: N/A - no UI, no pool content, no SOURCE, no prose.
- VI: every task names its verification; byte-identity sweep + `make done` + `make maps` + bookends. PASS.
- X: ruff/mypy strict; red-green: a test that plants a segment the brute-force scan finds and the index
  must find (a superset property test on random fabric), 100% on the touched modules. PASS.
- XII: no world assertion changes - byte identity is the proof. Record-the-why: the budget comment is
  corrected with the measured cause (FR-008). PASS.
- XIII: baseline manifests + timings on unmodified code before the first edit; zero diffs; XIV: defects
  found are tasks. PASS.

## Design decisions

1. **An index, not a smarter scan.** The bbox prefilter already exists per call; the waste is that it is
   redone 165k times and that after it every surviving polygon is still measured. A grid over the routing
   box (cell = the clearance margin or larger) filled once, with each polygon/line inserted into every cell
   its inflated bounds cover, makes a lookup O(candidates in the cell). It returns a SUPERSET of what the
   bbox scan returns (same inflation, coarser cells), so the verdict cannot change - byte identity holds by
   construction, and the sweep proves it.
2. **The lattice's free map is computed by one index, not 90,000 `clear_runs` calls.** `_route` calls
   `clear_runs` with a two-point degenerate polyline per cell; it becomes one `fouled(q)` against the index
   built for the whole box.
3. **The sweep is exact.** Pairs within 46 px in Euclidean distance are a subset of pairs within 46 px in
   x; sorting by x and comparing while `dx < 46` visits every Euclidean pair and no other count changes.
4. **No sampling change.** Coarser samples in `clear_runs` would move verdicts; declined for this feature
   (the GM: byte identity is the bar).
5. **Warming needs no new mechanism unless measured otherwise.** `make idle-tests` = `make done`, which
   stores every roll and corpus verdict; T30 measures that a post-sync idle run leaves the next gate warm.
