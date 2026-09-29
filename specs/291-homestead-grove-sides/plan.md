# Plan - feature 291, how many sides a homestead grove takes

Spec: [`spec.md`](spec.md) (FAITHFUL, round 3). Request: [`request.md`](request.md).

## What the measurement found first

- **The per-house grove is drawn in the scripted tier by the DISPERSED BUNDLE** (`settlement/rolling/bundle.py`
  `_bundle_layout`): an L of two bands, `grove_n` and `grove_w`, hard-wired to the north and west whatever the map's
  windward key, each `1.57 * hh` deep (the grove ~6x the house; at Inashiro's median house, 50 x 28 ft, a 44 ft band -
  several crowns). Linear hamlets take the same bundle (`_nucleated` is true for the nucleated form alone). The
  `_find_grove_arms` ladder (`homestead_parts/groves.py`) serves only the non-to-scale (city) path and the frozen
  legacy maps.
- **Restoring the form weights alone, the cohort was 24/24** (seeds 1-24, 2026-09-29) - but that gate no longer runs
  the grove rules: feature 166 retired the check battery that measured feature 126's defects, and the cohort's own
  verdict is the roll's failures, the reach count and the households seated. Adding `features_do_not_overlap` (the
  matrix, which classifies `groves` as VEGETATION against every structure and lane) to the cohort audit, the same 24
  seeds rolled dispersed 7, linear 6, nucleated 11: no overlap on any non-nucleated seed; two on NUCLEATED seeds
  (17: `dry_plots` on `lanes`; 20: `lanes` on `gardens`) - the baseline decides whether those are pre-existing (T02).
  The windward, garden-sun and every-side rules are not in the matrix and get manifest predicates (D7).

## Decisions

- **D1 - the knob, in the plan** (FR-005, FR-006, FR-009). `hamletgen/consts.py`: `GROVE_SIDES = (2,)*5 + (3,)*3 +
  (4,)*2` and `GROVE_SIDES_FLOOD = (2,)*15 + (3,)*9 + (4,)*16` (37.5 / 22.5 / 40, the 5 : 3 kept), rolled by the plan's
  `_roll(seed, "grove_sides", table)` like every hamlet knob (independent per name, so no other roll moves).
  `HamletSpec.grove_sides` pins it; `HamletSpec.flood_ground` pins the ground, else `flood_ground = field_archetype in
  POLDER_ARCHETYPES or settlement_form == "dike_top"`. Both on `SitePlan`, both into `meta` (`grove_sides`,
  `flood_ground`), rolled and recorded for a nucleated hamlet too (it draws nothing - its farms carry no grove).
  The generic `Settlement` (city path) reads `meta.grove_sides` when pinned and otherwise rolls the same table from
  its seed (`knob_rng(seed, "grove_sides")`), with `meta.flood_ground` choosing the table.
- **D2 - the faces** (FR-007). One module-level function, `grove_faces(windward, sides, flank)` in
  `homestead_parts/groves.py`, returns `(deep, thin)` as tuples of unit faces: two = the windward pair (a diagonal
  key's two faces; a cardinal key's face and `flank`, the side rolled per settlement from the seed); three adds the one
  face left that is not the FRONT; four adds the front. The FRONT is the lee face where the yard and the way in are:
  in the bundle's own frame that is always the side the yard is laid on (D3).
- **D3 - the bundle turned to its wind** (FR-007; a defect fixed under XIV). The dispersed bundle is laid out in its
  canonical frame (wind from the NW: bands N and W, yard S, garden E) and carried to the map's key by the square's
  symmetry that takes {N, W} to the windward pair and puts the yard on the lee face nearest the south: NW identity;
  NE mirrored east-west (yard S); SW turned a quarter counterclockwise (yard E - Tonami's east front); SE turned a
  half (yard N) is refused in favor of the mirror across the anti-diagonal (yard W, the afternoon sun); a cardinal key
  takes the diagonal its flank makes (N with the W flank = NW). Under a turn the canonical east garden would land on
  the house's north wall, in its shadow, so a turned bundle lays its garden beside the yard instead (the canonical
  frame's southeast, at the yard's east end), where the yard keeps its sky open to the south - as at Tonami, where the
  garden stood with the entrance on the east front (`homesteads/046`). Until now every dispersed bundle drew its L on the
  north and west whatever the map declared - on no pool map, since none declares a wind, but wrong on any that would.
- **D4 - the bands** (FR-008, FR-010). The deep bands keep today's `1.57 * hh`. A thin band is ONE CROWN deep -
  `2 * CANOPY_R_FT` = 17 ft (the record's mean crown, `vegetation/`'s "Forest density and crown size") - a GUESS for
  the depth, and far thinner than a deep band (44 ft at the median house). It stands outside the ground the farm
  works, clear of what that ground needs: an east band beyond the garden's morning-sun reach (the same `22 * bscale`
  band `_east_trees` reads), a front band beyond the yard's 22 px southern sun corridor (`_yard_sun_conflict`'s strip).
  The N and S bands (canonical frame) run the whole width, the W and E bands between them, so the corners close.
- **D5 - the way in** (FR-007 four sides). A ring round the house must let the house be reached; the front band is
  broken once, at the yard's center, for a way in 12 ft wide (two 6 ft treads, the width the lane fabric sizes every
  lane at) - a physical necessity with its width a GUESS (`vegetation/620`: no old page gives an opening's width; the
  old entrances stood on the grove's open side, which a four-sided grove does not have).
- **D6 - the bundle carries a list** (FR-010). `geom["groves"]`, a list of `(cx, cy, w, h)`, with `geom["grove_faces"]`
  beside it (`((dx, dy), "deep"|"thin")`), replaces `grove_n` / `grove_w` in every reader - `house_extent`,
  `_bundle_fits` (blocked ground and treads), `_yard_sun_conflict`, `_bundle_refused`, `_relax_gardens_south` and its
  `_east_trees` (own thin east band INCLUDED in the east test: only the deep arms are exempt, which sit off the garden
  by construction), and the flush in `_farmsteads_bundle`. The manifest's `groves` records carry `face` as now plus
  `depth`. The bbox and `_frame` cover every band. A farm is seated only where its whole rolled grove fits, so every
  farm carries every side (FR-010's no fallback).
- **D7 - the rules as predicates, and the cohort reads them** (FR-010, SC-005). New module
  `settlement/homestead_parts/grove_rules.py`, manifest-level, pure: `grove_sides_complete(M)` (every farm of a
  non-nucleated map has one band per rolled side, on the faces `grove_faces` names), `groves_windward(M)` (each deep
  band on a windward face of its own house), `gardens_east_clear(M)` (no grove band within the east shade reach across
  a garden's height). `cohort_audit` runs them and the matrix on every roll, and prints the forms and side counts it
  rolled. A gate seed test runs them on any pool roll that is non-nucleated.
- **D8 - the city path** (FR-005). `_find_grove_arms` plants `grove_faces`' deep faces as now and each thin face at
  the thin depth, fit-tested; it is the frozen legacy maps' path and runs on no live generator.
- **D9 - drawing**. A thin band draws with `_draw_grove(..., mix="dooryard")` - fruit and flowering broadleaf, no
  conifer (Tonami's east side: flowering trees, persimmon, fig; its west-to-north side hackberry and alder) - the mix a
  GUESS for the full ring. Deep bands keep the windbreak mix.
- **D10 - the forms back on** (FR-011). `SETTLEMENT_FORMS = _SETTLEMENT_FORMS_WHEN_GROVES_WORK` and the comment block
  above it rewritten from "why off" to the measurement that put them back.
- **D11 - the pool** (FR-012). The five hamlets regenerate from their unchanged specs; each takes its seed's form and
  side count; `settlement-review` on each whose layout moved.
- **D12 - the record** (FR-001-FR-004). Two write sessions from briefs in a second clone
  (`/diagram/.clones/diagram-readability-2`, so a headless session never writes into the tree the engine work is in):
  R1 = homesteads 010, 710, 480; R2 = vegetation 030, 620. Then check-and-apply sessions (`quote-check`,
  `record-format`, `source-applicability` on `irie-2020-igune` for its new use). The modal docstrings written from
  those entries are checked by `entry-drift` and rewritten (FR-004); the grove kind's modal states the side count
  (FR-009).
- **D13 - the two nucleated overlaps** (XIV). If the baseline shows seeds 17 and 20 fail on main too, they are
  defects found in this work and are fixed here; if they do not, they are regressions of this change and are fixed.
  Either way, fixed.

## Indexing

The bands are fit-tested through the existing bundle tests (`_rect_blocked`, `_house_on_a_tread`, the free-ground
index, the placed-box reach index); no new per-candidate scan is added. The predicates in D7 run once per map over
its manifest and bucket the bands by house (`of`).

## Constitution Check

- XII: every number labeled - the weights and the flood table the GM's ruling (GUESS), the thin depth, the mix and the
  way-in width GUESSES, the flood ground this project's decision; the record carries each.
- XIII: the cohort baseline on main (detached worktree) against the same seeds with the matrix and the predicates.
- XIV: D3 (the unturned bundle) and D13 fixed here.
- XVI: no farm without its rolled grove; no exception carved (spec rounds 1-3).
