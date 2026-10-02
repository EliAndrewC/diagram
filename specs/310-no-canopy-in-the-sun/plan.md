# Implementation Plan: no canopy tree in a yard's or bed's sun

**Branch**: none (`main` in the clone; `SPECIFY_FEATURE=310-no-canopy-in-the-sun`) | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: the accepted spec, the GM's words in `request.md`, `research.md` R0-R2.

## Summary

Most drawn canopy crowns pass one test before they are inked - `_crown_covers` against keep-out boxes - and the rest are
seated by their own tests or drawn before any plot exists (research R1). A plot's sun ground is such a box, so the rule is one keep-out
source, `_sun_keepouts`, handed to every `_crown_covers` test and to none of
the bamboo marks', with the reach and the map check generalized from the persimmon's (pushed 2026-10-02) to every crown.

## Technical Context

**Language/Version**: Python 3.14 (`.claude/skills/diagram/l7r/diagram/`)

**Testing**: pytest via `make`; 100% coverage over the engine

**Scale/Scope**: the five pool hamlets and cohort seeds 1-24

**Single-artifact target**: `pool/hamlets/inashiro/inashiro.gen.py` (~8-11 s a roll; copse), then Kashikawa (farm groves),
then the pool (`make maps`) and the cohort.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `310-start` | on the unmodified engine, before D1 |
| after | `310-end` | before the push; `make perf-report AGAINST=310-start` |

## Decisions

- **D1 The reach is one constant for every canopy tree**: `PERSIMMON_SHADE_FT` moves to `tree_shade.py` as `CANOPY_SHADE_FT`
  (the sun page's west-lane reach, the working windbreak tree's), renamed everywhere it is read (code, tests, the record's
  comments). The persimmon's seat keeps its own form (it is seated in its house's frame before the rake, R1).
- **D2 One keep-out source**: `_sun_keepouts(bbox)` on the keep-outs mixin returns, for a map that keeps the sun corridor
  (`_sun_corridor_ft`, the scripted path's opt-in), the sun-ground box of every plot meeting `bbox` - the drawn
  `threshing_yards` and `gardens` and every placed bundle's `yard` and `gardens` (a farm grove's arms are drawn in the flush,
  whose plots may not yet be records). Off on every other map. Indexed as the caller indexes its other boxes: the belt's
  `PointGrid`, the clump's prefiltered list (both built once per stand; clause 15).
- **D3 Every tree site takes it; no bamboo, coppiced-mulberry or tea-hedge site does** (research R1, the whole inventory):
  - the `_crown_covers` sites - `_belt_ranks`, the `_draw_grove` crown test, the woods stand and fringe - take the sun boxes
    in their keep-out list; the culm marks' test keeps the old list (FR-003);
  - the woodland commons' throws and its `woodland_room` fallback grid refuse a crown that `crown_shades` finds in a plot's
    sun (the commons are drawn in the hinterland stage, after every plot);
  - the scrub's hill pines refuse a pine whose branch spread (its crown, the widest branch's reach) stands in a plot's sun, and
    are recorded as `scrub_pines` [x, y, r] so the check sees them (not in `tree_crowns`, which other rules read as canopy
    discs - recording the pines there would move those rules);
  - the perimeter dike's willow row and the fruit dike's trees are drawn in the field stage, before any plot exists: each tree is
    recorded with its planted string's place in the stream (`planted_trees`), and once the homesteads are placed
    (`stage_hinterland`'s start) each string is rewritten without the trees that stand in a plot's sun - the mulberry and tea rows
    unchanged (not canopy, R1);
  - the persimmon already keeps the rule.
  A tree refused is simply not drawn, as a crown over a roof is today (the wood is the remainder - spec Decisions row 5).
- **D4 The copse's west-lane exemption goes** (`homestead_parts/stands.py`: the lane applies to every mix; the comment's
  unsupported justification is removed - FR-006). The lane is now a seat prefilter that D3 also enforces at the crown.
- **D5 The farm grove's seat-time strips stay as seating PREFERENCES** (`fit._yard_sun_conflict`, `_garden_sun_conflict`):
  they refuse a bundle whose grove BAND would stand in a neighbor's sun, which keeps bands whole; they exempt nothing, because
  D3 holds every crown to the full rule whatever seat a bundle takes. Replacing them with the full reach at seat time would
  refuse bundles for crowns D3 thins anyway, and move houses (the spec's Assumption: only trees give way). Every text that
  presents a strip as the sun rule is rewritten as a seating preference under the one crown rule: the `_yard_sun_conflict`
  docstring, `_garden_sun_conflict`'s "by construction", `rolling/dispersed.py`'s and `hamletgen/consts.py`'s comments; no record
  page or modal describes a strip as how a grove keeps a plot's sun.
- **D6 The map check reads every tree**: `tree_shade.trees_shading_plots(M, reach)` over `tree_crowns`, `scrub_pines` and
  `planted_trees` (the persimmon's crown is in `tree_crowns`, so `persimmons_shading_plots` is retired into it). The gate test
  becomes `tests/gate/test_canopy_sun.py` over the five hamlets; the cohort audit reads the same function.
- **D7 The record**: the sun page states the one rule, the bamboo exemption as the GM's choice, and the class of each
  (spec Decisions); the persimmon bullet folds into it. The modals written from it are checked by `entry-drift`.

## Constitution Check

- **I, II, III, IV, V, VII, VIII, IX**: N/A - no UI, pool content kind, SOURCE block, in-world prose or setting detail.
- **VI**: per task - `make quick`, `make test-file`, Inashiro then Kashikawa, then `make maps` and `make cohort N=24`,
  `make done`, the bookends. Occasions: `placement-changed` for the copse on Inashiro and the farm grove on Kashikawa (their
  crowns now keep a new rule); `gm-fix` on Inashiro (the GM's complaint).
- **X**: red-green (D6's gate test red on today's pool first; unit tests of `_sun_keepouts` and each site); 100% coverage;
  clause 15 per D2.
- **XII**: opening bookend `research.md` R0; every decision in the spec's table; the closing bookend re-reads the rendered
  Inashiro and Kashikawa against R0.
- **XIII**: a 24-seed cohort baseline in a detached worktree on the unmodified engine (`make cohort N=24`), after the
  `310-start` bookend; zero new failures.

## Project Structure

```text
specs/310-no-canopy-in-the-sun/       request, spec, research, plan, tasks
.claude/skills/diagram/l7r/diagram/settlement/
├── homestead_parts/tree_shade.py     D1, D6
├── homestead_parts/keepouts.py       D2
├── homestead_parts/groves.py         D3 (belt ranks, clump crowns; not the culm marks)
├── homestead_parts/stands.py         D4
├── shrines_wells/woods.py            D3
├── land/cover.py, land/dikes.py      D3 (the commons, the scrub pines, the dike willows)
├── rolling/dispersed.py              D5 (comments)
├── rolling/fit.py                    D5 (comments)
└── tools/cohort_audit.py             D6
.claude/skills/diagram/tests/gate/test_canopy_sun.py   D6 (replaces test_persimmon_sun.py)
.claude/skills/diagram/research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html   D7
```

## Complexity Tracking

None.
