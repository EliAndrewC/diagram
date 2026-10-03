# Implementation Plan: bamboo held out of a yard's or bed's sun

**Branch**: none (`main` in the clone; `SPECIFY_FEATURE=315-bamboo-in-the-sun`) | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: the accepted spec, the GM's words in `request.md`, `research.md` R0-R2.

## Summary

Bamboo is held to the sun rule feature 310 set for canopy trees, at a reach worked out from the timber bamboos' least
height (R2: the same 50 ft). The culm marks take the sun boxes their clump's crowns already take, the two stand placers
refuse a seat in a plot's sun, every drawn mark is recorded, and the map check counts bamboo beside the trees.

## Technical Context

**Language/Version**: Python 3.14 (`.claude/skills/diagram/l7r/diagram/`)

**Testing**: pytest via `make`; 100% coverage over the engine

**Scale/Scope**: the five pool hamlets and the 24-seed cohort

**Single-artifact target**: `pool/hamlets/kuwabata/kuwabata.gen.py` (the most culm marks), then the pool and the cohort.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `315-start` | on the unmodified engine (main at the claim), before D1 |
| after | `315-end` | before the push; `make perf-report AGAINST=315-start` |

## Decisions

- **D1 Bamboo's reach is its own constant**: `tree_shade.BAMBOO_SHADE_FT`, derived beside it from the timber bamboos' least
  cited height (R2) - 50 ft, the canopy reach's value by the same derivation, never an alias of `CANOPY_SHADE_FT`.
- **D2 `_sun_keepouts` takes the reach**: `_sun_keepouts(bbox, reach=CANOPY_SHADE_FT)`; every existing caller unchanged.
- **D3 The culm marks take the sun boxes** (`_draw_grove`): the mark's test reads the clump's keep-outs plus
  `_sun_keepouts(..., BAMBOO_SHADE_FT)` over the clump's padded box, with the mark's own reach (`_mark_r`) and the crowns'
  pad; each inked mark is recorded in `M['bamboo_marks']` as [x, y, r] (r the mark's reach). The `ksun` comment that names
  the GM's "maybe bamboo" is rewritten.
- **D4 The stands refuse a seat in the sun**: `household_bamboo` refuses a candidate strip whose rectangle meets a plot's sun
  box at bamboo's reach (the next side is tried, as for any other refusal); `bamboo_seats` adds the sun boxes to the boxes its
  `BambooObstacles` index refuses, built once per pass (clause 15). A stand refused everywhere is not drawn (spec Edge Cases).
- **D5 The map check counts bamboo**: `tree_shade.bamboo_shading_plots(M, reach)` over `bamboo_marks` (discs) and
  `bamboo_stands` (their outlines' boxes), beside `trees_shading_plots`; `tests/gate/test_canopy_sun.py` asserts both zero on
  the five hamlets, with non-vacuity (marks and stands found), and that the record's mark count equals the culm marks parsed
  from the SVG (SC-002); `tools/cohort_audit.py` reads it. The new key is classified in the overlap taxonomy
  (`_OVERLAP_EXEMPT`, `_MX_NOT_GEOMETRY`) and `land/cover.py` `_BARE_SKIP`, as `scrub_pines` was.
- **D6 The record**: the sun page's bamboo bullet rewritten - bamboo held at its own reach, the heights footnoted to the
  pages R0 read (new registry entries through `make reserve`), yadake placed; `tree_shade.py`'s docstring; the ThreshingYard
  and Garden modals ("bamboo is left out", "leaving bamboo out of it"); the bamboo modals and the bamboo drawing page checked by
  `entry-drift` where their section moves. Record checks as the record gate owes them (feature 311).

- **D7 (amendment, the regressions feature 310 shipped)**: a bed slid south after the groves stand keeps its sun ground clear of
  standing crowns, promised persimmons and bamboo marks (`farmsteads.beds_sun_clear`); a grove farm's bed stands wholly south of
  the front wall, and a band in a turned bed's east reach is cut back a pixel clear of it (`dispersed.clear_east_of_beds`).
- **D8 The persimmon** (research R3): held to its dooryard (`fixture_seats.PERSIMMON_DOORYARD_FT`, none where no seat); on a grove
  farm free to stand in its own grove's bands (`lay_fixtures` `fruit`; `_fixtures_in_bands` passes it in its own band only);
  its template judged at its seat's own rake; and dropped, where its homestead is laid, if it stands in its own or a placed
  neighbor's plots' sun (`fit._settle_persimmon`, called in `_bundle_geom` - the placer re-lays a chosen seat's homestead).
- **D9 A walled-in gateway** leaves along the exit strip's end, else from the first bearing turned off the downslope whose sweep
  is dry (`track.gateway_track`, `turned_gateway_track`, `track_from_the_strip_end`).
- **D10 A shared row well is not dug in the street's bend** (`wells.street_turns_at`, `BEND_WELL_DEG`), and a row street is laid
  through `_unjog` (`street.lay_row_streets`).

## Constitution Check

- **I, II, III, IV, V, VII, VIII, IX**: N/A - no UI, pool content kind, SOURCE block, in-world prose or setting detail.
- **VI**: `make quick`, `make test-file`, Kuwabata then the pool, `make cohort N=24`, `make done`, the bookends. Occasions:
  none for a glyph or a whole map - no pool bamboo moves (R0: none of 3 stands and 329 marks in a plot's sun), so no element
  is new, redrawn or re-placed on a pool map; the rule is held by the gate test (D5). If a pool map's bamboo does move when
  regenerated, the occasion `placement-changed` for bamboo on that map is declared then.
- **X**: red-green - D5's gate test written first and shown red on a planted mark; unit tests of D2-D4; 100% coverage;
  clause 15 per D4.
- **XII**: R0 is the opening bookend; every decision is in the spec's table; the closing bookend re-reads the rendered
  Kuwabata and Kashikawa bamboo against R0.
- **XIII**: the cohort baseline in a detached worktree at the claim's commit (`make cohort N=24`); zero new failures.

## Project Structure

```text
specs/315-bamboo-in-the-sun/          request, spec, research, plan, tasks
.claude/skills/diagram/l7r/diagram/
├── settlement/homestead_parts/tree_shade.py   D1, D5
├── settlement/homestead_parts/keepouts.py     D2
├── settlement/homestead_parts/groves.py       D3
├── hamletgen/homesteads/bamboo.py             D4
├── hamletgen/hinterland/bamboo.py             D4
├── overlap/taxonomy.py, settlement/land/cover.py   D5 (the new key)
├── tools/cohort_audit.py                      D5
└── interactive/classes/homestead.py           D6
.claude/skills/diagram/tests/gate/test_canopy_sun.py   D5
.claude/skills/diagram/research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html   D6
```

## Complexity Tracking

None.
