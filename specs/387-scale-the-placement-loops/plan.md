# Implementation Plan: scale the placement loops (feature 387)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-18

## Summary

Five placement sites stop redoing work that does not change between the questions they ask. Each change is held to the verdict of
the code it replaces (FR-007) by EQUIVALENCE tests at two tiers. A unit test per site (`tests/`, built inputs, no roll) asks the
old form and the new on cases built to hit each branch, the old form kept in the test module as the oracle, never in the engine.
And a soak test, `tests/soak/test_scale_equivalence_387.py` (the tier for rolls past the gate's floor, `tests/soak/CLAUDE.md`;
run by `make soak` in T06, never by the gate - it cannot come from the roll cache, which serves a roll without executing it),
rolls the reference spec and four cohort seeds at 40 households (beyond the band, as the perf snapshot does) with each new
function wrapped so every call also asks the old form, and asserts the same answer on every call. Counts of the work per
addition (SC-001) are read from `make perf-profile` call counts at 10, 20 and 40 households, seed 4, before and after, into
`measurements.json`.

## Technical Context

Python 3.14, shapely 2, the hamlet generator (`l7r/diagram/hamletgen/`, `l7r/diagram/settlement/`, `l7r/diagram/waterfields/`).
Tests: pytest through `make test-file` / `make quick` / `make done`. **Single-artifact target**: the reference hamlet,
`pool/hamlets/inashiro/inashiro.gen.py` (`make map GEN=...`, ~10 s), then the cohort (`make cohort`, ~50 s) and the pool
(`make maps`); the landing cohort (`make cohort-landing`) before the gated push. **Every step is two steps**: each task proves
its change on the reference map and its equivalence test, then T06 sweeps the cohort and the pool.

## Performance bookends

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `387-start` | 19.4 s | 4.8 s | 5.4 s | taken 2026-10-18 on unmodified `2976fd8bf` (the spec commit), SCALING=1: 40 hh 19.8 / 15.5 / 14.4 / 14.9 s |
| after | `387-end` | | | | taken before the push, back to back with a re-take of the start where the load allows |

## Constitution Check

- I-V, VII-IX, XI: N/A - no UI, no pool content, no SOURCE block, no setting prose, no kanji.
- VI: each task lists its verification; T06 runs the cohort, `make maps` and `make done`, T07 the landing cohort.
- X: ruff, ruff format, pyrefly, 100% coverage held. Every change is the efficient form clause 15 asks for (an index built once
  and asked per candidate; nothing walks every item per candidate). No function grows past 100 statements (`admits` is split into
  the base tree and the candidate's own questions, D1); no file past 1,000 lines - `ways/tree.py` is 780 and gains ~60, so the
  base-tree cache goes in a new `ways/tree_base.py` (D1).
- XII: no element of the world changes; every task is `research: rendering` (a change in HOW a verdict is computed, not in what
  is drawn). The research claims of each touched function keep their pointers; a new helper carries `Research: plumbing - NONE`.
- XIII: the regression baseline is main's own cohort record (the landing cohort rolls main's in a detached worktree when it has
  none, feature 386); zero new failures at merge. A site whose equivalence test cannot hold (FR-007) says so in its decision and
  its moved maps are judged by the cohort and the gate.
- XIV: a defect found on the way is fixed or recorded (D3 records one).
- XVI: built as the spec's FRs; FR-004's withdrawal is the spec's, on its measurement.

## T01 - the way tree (FR-001)

**D1 - the base tree built once per tree state, the candidate judged on what it adds.** `ways/tree.admits` today rebuilds, for
each candidate, every tree record (`tree_records`), every run's host (`hosts`), every lane's laid and drawn form (`lanes_of`,
1,886 `lay` calls on 126 asks at 40 households), and the whole tree's fronting ends (29,540 end-way pairs on 44 asks). None of
that depends on the candidate: a candidate is appended LAST, its host is the earliest run it stands on (`hosts`), and every
earlier lane's drawn form depends only on its own run and its own host's (`lanes_of`). So `tree_base.TreeBase` holds, for one
state of the tree, the records, the root, their hosts, the laid lanes (whole tree), and the fronting ends with, for each free end,
the junction test's answer; it is keyed on the CONTENT it is built from (the access corridors' points, the houses' and yards'
records, the lanes' points, the water `laid_run` already keys on) - never on a count or an identity (`indexes.Indexed`'s
lesson). The candidate then costs: its own host (one `_on` scan of the runs), its own laid lane, its chain's lanes (taken from
the base), and: `law_(new)` as today (already the candidate against what it meets); fronting ends as the base's ends minus
those the new lane now joins (an end within `JOIN_TOL` of it) plus the new lane's own ends tested against every way; the needle
faces, `as_joined`, `way_out_once`, `tree_shadows` and `walked_shadows` as today (each already asks the new lane against the rest,
or is one shapely call - `needle_loops` 0.12 s of the 1.84 s profiled, kept whole: a face is not local to the lanes near the new
one, and an incremental face test would trade an exact answer for a guess). **Equivalence**: `admits` and the old whole-tree
form on every candidate the gap pass asks, the same booleans. **Counted** (SC-001): `lanes_of`'s `lay` calls and
`fronting_ends`'s pairs per candidate.

## T02 - the web's field way and the knots (FR-002)

**D2a - the field way's candidates best-first.** `corridors.field_runs` measures every sampled point of the network to the
worked ground (`run_on_target`, 8,552 calls at 40 households) and keeps the `limit` shortest per ground. Every run from `q` -
straight, or over a ford - is at least `q`'s distance to the ground's edge, so the points are taken in that distance's order
(the distance asked of the ground's ring index, `RingIndex.edge_within`/its outline) and the search stops once `limit` runs are
in hand and the next point's distance exceeds the longest kept. Ties keep the old order: the kept runs are sorted by (length,
the point's place in `samples_along`), the old `sorted` being stable on that place. **Equivalence**: `field_runs` old and new on every
call, the same list. **Counted**: `run_on_target` calls per kept run.

**D2b - the knots' whole-web counts.** `knots.settle_knots.judge` asks, for each trial gather, `memo.count` of each of the whole
web's rules on the WHOLE trial web (`_WHOLE_RULES`; `way_outs_crossing` and `doorstep_ends` re-walked whole, 0.30 s of its
0.83 s). A gather moves the ends of the lanes in `edits` only. `doorstep_ends` is a sum over each house of the free ends near it:
the trial's count is the web's count minus the edited lanes' old ends plus their new ends, each end's junction test asked against
every way (it is only the junction an end meets that can change, and an edited end can newly join another lane's end, so the
ends of every lane within `JOIN_TOL` of an edited end are re-asked too). `way_outs_crossing` is a route through the whole web:
kept whole - an edit can change any household's route, and a local answer would be a guess. **Equivalence**: each trial's
counts old and new, the same numbers. **Counted**: ends re-asked per
trial. Not R12: no round narrowed, no law asked to pick steps.

## T03 - the cell merges (FR-003)

**D3 - each live neighbor measured once.** `Fabric.neighbors` queries the index built in `Fabric.__init__`, maps each hit to its
live owner (`find`) and measures the shared bund (`shared_length`, a shapely buffer and intersection) for EVERY hit before the
set drops duplicates: 15.7 measurements a merge at 40 households against 3.3 at 10. The hits are mapped to their owners first,
deduplicated, then each measured once. **Equivalence** is exact by construction (the same owners, the same measure of each, the
same sort) and is tested on every merge of the rolls. **The index kept current - not done, a defect recorded**: a cell a `split` makes
gets a new id the index never held, so a neighbor that is a split part is never found (`split` deletes the cell and adds its
parts; `find` of the old id returns an id no longer alive). Indexing the parts would find merges the current code cannot and
move maps; FR-007 holds this feature to the old verdicts, so it is recorded at `neighbors` and in the report to the GM as a
defect found (XIV), with its measurement of how often a split part neighbors a failing cell. **Counted**: `shared_length` calls
per merge.

## T04 - the sun keep-outs (FR-005)

**D4 - the plots taken once while the grove is drawn, the sun boxes indexed.** `_sun_keepouts` rebuilds its plot list and key
from every yard and bed on each of its 1,816 asks (159,808 `plot_box` calls), then filters every sun box. Its callers in the
windbreak stage (`village_grove` -> `_draw_grove`) add crowns, never yards, beds or homesteads. A scope, `s.plots_stand()`, set
by `village_grove` around its drawing, builds the plots, their sun boxes and a `PointGrid` of the boxes once; inside it
`_sun_keepouts` answers from the grid (the boxes whose cell range meets `bbox`, then the same overlap test, returned in the
plots' order so a caller iterating them sees the same order). Outside the scope it is unchanged. **Exactness held by a
check, not assumed**: under the test suite (`L7R_CHECK_SCOPES=1`, set by `tests/conftest.py`) the scope re-takes the plot list
when it closes and raises if it changed - so a later stage that adds a plot inside the scope fails the suite instead of
answering stale. **Equivalence**: every ask's answer, old and new, the same list in the same order. **Counted**:
`plot_box` calls per grove.

## T05 - the bamboo strip check (FR-006)

**D5 - the strip asks an index of what stands.** `household_bamboo` builds, once per pass, a `PointGrid` (cell 128 px) of: the
placed boxes, the houses' turned boxes, the wells / kosatsuba / byres / farm sheds / retirement houses, each lane segment's box
padded by its half-width, and the tree crowns. `_strip_blocked` takes the index as an optional argument (`near`); with it, each
straight scan becomes a scan of the grid's candidates for the strip's box padded by the largest margin that scan uses (2, 6 ft
and the lane's half-width), then the SAME test on each; without it (the fixtures' caller, `homesteads/fixtures.py`), it scans
as now. What the pass adds while it runs (the strips it seats are walls to one another) is appended to the index as it is
seated, through the one function that records a seated strip. The same scope check as D4 guards the pass's inputs under the
suite. **Equivalence**: every candidate's verdict, old and new. **Counted**: items tested per candidate.

## T06 - measure, sweep and record (FR-009, FR-010, SC-001 - SC-004)

The counts at 10/20/40 households, seed 4, before (taken now, on `2976fd8bf`) and after, into `measurements.json` with the
command; `make cohort`, `make maps` and `make done`; the end bookend; `dev/performance.md` gains "Judge the addition, build once,
index the scan (feature 387)" with each site's before/after. A seed newly failing blocks (XIII).

## T07 - land (SC-003)

`make cohort-landing`, then the gated push (`scripts/sync-with-main.sh done`), the feature report.

## Project Structure

New: `l7r/diagram/hamletgen/ways/tree_base.py` (D1), `tests/hamletgen/ways/test_tree_base.py`, one equivalence test per site
beside that site's tests, and `tests/soak/test_scale_equivalence_387.py` (the rolled shadow comparison). Changed: `ways/tree.py`, `ways/corridors.py`, `ways/knots.py`,
`waterfields/settle.py`, `settlement/homestead_parts/keepouts.py`, `hinterland/stands.py` (the scope), `homesteads/bamboo.py`.

## Complexity Tracking

None.
