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
  takes the diagonal its flank makes (N with the W flank = NW). In every frame but the unchanged NW one the canonical
  east garden would land where the house takes its sun - on the north wall under a turn, on the west wall (no morning
  sun) under the NE mirror - so every other frame lays its garden beside the yard instead (the canonical frame's
  southeast, at the yard's far end), where the yard keeps its sky open to the south - as at Tonami, where the garden
  stood with the entrance on the east front (`homesteads/046`). Until now every dispersed bundle drew its L on the
  north and west whatever the map declared - on no pool map, since none declares a wind, but wrong on any that would.
- **D4 - the bands** (FR-008, FR-010). The deep bands keep today's `1.57 * hh`. A thin band is ONE CROWN deep -
  `2 * CANOPY_R_FT` = 17 ft (the record's mean crown, `vegetation/`'s "Forest density and crown size") - a GUESS for
  the depth, and far thinner than a deep band (44 ft at the median house). It stands outside the ground the farm
  works, clear of what that ground needs: an east band beyond the garden's morning-sun reach (the same `22 * bscale`
  band `_east_trees` reads), a front band beyond the yard's 22 px southern sun corridor (`_yard_sun_conflict`'s strip).
  The N and S bands (canonical frame) run the whole width, the W and E bands between them, so the corners close.
- **D5 - the way in** (FR-007 four sides). A ring round the house must let the house be reached; the front band is
  broken once, at the yard's center, for a way in about 36 ft wide (`WAY_IN_FT`: the router keeps a footpath's gap and
  most of its cell off each band, and at 12 ft - two treads - no lane could be laid through; homesteads/715) - a
  physical necessity with its width a GUESS (`vegetation/620`: no old page gives an opening's width; the
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
- **D8 - the city path** (FR-005, FR-010). The house-first path (`_solve_homestead`, `_find_grove_arms`) plants every
  face `grove_faces` names on a farm that has a grove: `_grove_room` asks room for the minimal footprint of EVERY rolled
  face (deep and thin), `_solve_homestead` takes only a seat with that room for a grove farm - its old fallback to a
  yard-and-garden-only seat goes, so a farm with no such seat within its nudges is not seated, as a to-scale farm whose
  bundle does not fit is not - and `_find_grove_arms` plants each face (the deep ladder as now; a thin face at the thin
  depth, its run shortened as the deep ladder does where a neighbor is close). Whether a farm has a grove at all stays
  the in-wall rule's and `grove_prevalence`'s, as now.
- **D9 - drawing**. A thin band draws with `_draw_grove(..., mix="dooryard")` - fruit and flowering broadleaf, no
  conifer (Tonami's east side: flowering trees, persimmon, fig; its west-to-north side hackberry and alder) - the mix a
  GUESS for the full ring. Deep bands keep the windbreak mix. A band is drawn as clumps of at most one clump's size
  (`band_clumps`: `_draw_grove` caps a clump at 28 crowns, and a deep band drawn as one clump was sparser than the thin
  band), inset one crown radius on the house side so the canopy's edge meets the band's inner edge, off the service
  strip; its bamboo is drawn only where the farm rolled a household bamboo stand (`_farm_rolls_bamboo`, the bamboo pass's
  own positional roll; FR-019).
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

- **D14 - the row's line** (FR-013). A new module `hamletgen/homesteads/rows.py`. `row_line(plan)` is the site's or
  the roll's: `flood_ground` gives `edge`; otherwise `knob_rng(seed, "row_line")` at even odds between `street` and
  `edge`, or `HamletSpec.row_line` pinned; recorded `meta.row_line`. A line is a polyline: `edge` - the field
  envelope buffered outward (shapely) to the street's offset, its exterior ring cut to an arc centered on the seat's
  projection (the row curves with the margin); `street` - a straight segment through that same projection along the
  arc's chord, a surveyed road. The row's length along the line is what its farms need, `n_side x frame`, centered on
  the seat, clipped to the canvas less the frame. A linear hamlet's canvas is 1.5 times `canvas_for`'s (`LINEAR_CANVAS`,
  a drawing convention - the unused ground is cropped): sized for a cluster, the canvas ran each street off the sheet
  after a few lots and cohort seed 12 seated 13 of 17 on six streets.
- **D15 - the seats** (FR-014, FR-015, FR-016). `row_sides(plan)` the same way (knob `row_sides`, `one`/`both`,
  `meta.row_sides`). The frame is the dispersed bundle's `_frame` at the largest house (grove, ground and the lane's
  room); farms step one frame width along the line. ONE side: the street at the field's standoff, the farms beyond it
  (away from the field) at half a frame depth past the street's half-width. BOTH: the street one frame depth plus the
  standoff out from the field, a near row between the street and the field and a far row beyond. Each seat goes to
  `try_place` (one computed move), in center-out order alternating the two ends. When a line is full or refused,
  `row_streets` offsets the next street parallel, one row set further out (FR-016), and the rows continue there. The
  front-row, rank and rescue passes do not run for a linear hamlet. The streets are kept on `s._row_streets` for the web.
- **D16 - the far row's holding** (FR-015). On BOTH, each far-row farm's holding is BEHIND its lot (away from the
  street): on `street` a strip one frame wide and three frames deep, cut in plots of the near ring's cell (the planned
  row's order: house lot, then field, then woodland - homesteads/156); on `edge` one frame deep, compact and near the
  house. It is RESERVED when the farm is seated - `seat_rows` offers a far-row seat only where its holding's box is clear
  of the ground and of every placed box, and registers it (a `placed` box and a `block_polys` ring) - so the woods, the
  copse and the later placers keep off it; a far-row farm whose holding has no room is not seated there, as a farm
  whose grove has no room is not (D6). The plots are drawn at the end of the homestead stage, as the dry plots every later way and the woods treat
  as crop (`dry_plots`, furrowed, `dry_polys`) - drawn after the track, the connector ran across one. Only a strip clipped at the canvas edge (a sheet shows only the near end,
  homesteads/156) or a single plot on water or a lane is dropped, never the whole holding. Depth and crop a GUESS.
- **D17 - the streets** (FR-017). `_lay_street` lays each of `s._row_streets` as one lane, width 6 (the connector's; web
  lanes are 3-5), `street: True`, clipped to its farms' extent plus a lot, routed only where a straight leg is blocked,
  and joined at its nearer end to the connector (or to the previous street). A linear hamlet with planned streets lays no
  skeleton arms and no web cuts; the stragglers still run. EACH ROW FARM'S WAY ENDS ON ITS OWN STREET: `lay_door_paths`
  is given, for a row farm, its own street as the target (not the nearest way), and routes from the front door round the
  farm's grove when the street lies on its windward side (the front is the wind's, D3); the path records the farm it
  serves. The door-to-door street it replaces goes.
- **D18 - water** (FR-018). A dispersed farm's own well is seated in its dooryard by `own_wells`: a ring round the house
  out to the frame, nearest the work yard first, tested by footprint against every reserved box, never on the way in
  (the line from the house through its yard). A well seat reserved in the bundle's layout was built and MEASURED: every
  seat beside the yard widened the turned frames, and cohort seed 19 seated 10 of 11 households against 11 without it
  (FR-010 forbids that), so it is not used. The guarantee is the check: `water_rules` fails any dispersed farm without
  its own well, on every cohort roll and the gate's grove maps - a farm is never silently left dry. A linear hamlet
  rolls `row_water` (`own`/`shared`, even odds, pinnable, `meta.row_water`): `own` the same; `shared` seats wells beside
  each street, in the lane's room between two lots, SPACED FROM THE REACH - one at least every `floor(reach / frame)`
  farms along the street, the reach the watering rule's (`WATER_REACH_FT`) - so every farm of every row and street, near
  and far, stands within reach of one.
- **D19 - the checks** (SC-007, SC-008). `grove_rules` gains `row_rules(M)` (every house within a frame depth of a
  street; no house behind another on its side; each street one lane; every far row farm with its holding behind it; every
  row farm joined by a way to its own street) and `water_rules(M)` (every dispersed farm with its own well, not in its
  way in; a linear map's `row_water` drawn - own wells, or every farm within reach of a shared well), and the door and
  bamboo predicates (`doors_unreached`: every grove farm's front door within the door reach of a way; `bamboo_mismatch`:
  the farms drawing grove bamboo exactly the farms that rolled it). The cohort audit runs all of them on every roll and,
  beside its 24 seeds, rolls a PINNED linear spec for each value of `row_line`, `row_sides` and `row_water` (four
  line-by-sides specs, water alternating), so both values of each knob are asserted to appear, not left to the roll; the
  gate test runs them on the linear pool maps.

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
