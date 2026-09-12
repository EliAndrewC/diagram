# Audit: `settlements/fields.md` (68.5 KB) against `research/fields.html`; `settlements/archetypes.md` (54.9 KB) against `research/archetypes.html`

Independent Opus reader, 2026-09-12. Classes as in `homesteads.md`.

## fields.md - unit table

| unit (line) | class | justification | engine (B) / anchor (A) |
|---|---|---|---|
| Header + load-when (1-9) | C | | - |
| Paddy cell size intro, `paddy_grain(ftpx, target_acres=)` (11-13) | B | | `waterfields/palette.py:31`, `:28` `PADDY_CELL_ACRES` |
| Target 0.05 acre + Bray / Buck / se / tan derivation (15) | B | page has none of it | `palette.py:10-28` verbatim, same sources |
| What changed - villages/cities pulled down (16) | B | | `palette.py:24-25` |
| Population invariant untouched (17) | B | rests on a deleted check | `palette.py:26-28` |
| Grain fidelity `grain=2/ftpx` (18) | B | | `waterfields/comb.py:257` |
| Leveled-cell principle governs HILL-RICE archetypes (19) | E | unscripted archetypes | `waterfields/hill.py:12,140` |
| Ratchet test note (20) | C | | `tests/settlement/test_core.py:260` |
| Paddy TRACT size ladder 8 / 20 / 50-90 acre (22-24) | A | | `#tract-sizes---no-settlement-class-cap` |
| `town_has_field_off_edge` (24) | F | NOT FOUND | - |
| Terrain-following outlines, bunded mosaic, per-plot row angles (28-30) | A | | `#paddy-plots---irregular-patchwork-and-why-the-grid-is-anachronistic` |
| Field arrangement village-specific (31) | E | | - |
| Every field ringed; `fallow_implies_abandoned` (32) | B | knob no pool map uses | hamletgen `field_ringed` |
| No paddy on hills (33) | A | | `#where-dry-hatake-crops-go---the-topographic-catena` |
| Strip-allocation ~2-3 glebe plots, gated by check_village (34) | F | | NOT FOUND |
| Fallow / abandoned rendering, corridors (36) | B | | `settlement/fields/paddy.py` |
| Near ring packed; one field off the edge (37) | E | | - |
| NEAR-RING PADDY IS COMB FIELDS ONLY + two REJECTED fillers (38-39) | D | GM 2026-07-23; 013/014 fillers rejected "so they are never reinvented" - the functions still exist in `settlement/land/nearring.py` with docstrings arguing FOR them | - |
| PADDY-FIRST samurai estates; estate DRIVEWAYS not drawn (40) | D + E | "driveway" appears nowhere else in the repo | - |
| Check calibrations 0.12 / 0.28 floors, 800 ft sampler (41) | F | | NOT FOUND |
| Tax-free plots `taxfree_plots_in_range` (42) | F | only `taxfree=` param survives | `paddy.py:55` |
| Every comb fan has a FIELD FLOOR (43) | B | live | `settlement/fields/comb.py:52`; `paddy_fan_has_floor` |
| Comb HEAD ground quilted (44-45) | E + F | city tier; check survives as a comment | `overlap/matrix.py:210` |
| Dry parcels to scale 46/36 px, 0.25-acre ceiling (46) | B | ceiling enforced nowhere | `waterfields/carve.py:659` |
| The check's shape 20/34/48 ft, 20% bare (47) | F | | NOT FOUND |
| A comb fan wastes no commanded ground (48) | B | | `waterfields/seams/close.py:37` |
| Why the leftover pass, shared bunds (49) | A | | `#bunds-are-shared-and-the-fabric-is-continuous` |
| What it replaced `_fill_wedges` (GM 2026-08-17) (50) | A | | same |
| Why the ditch net draws in a LATE water block (51) | B/C | failure story only here | `comb.py:358-368` |
| Tolerance bund-scale, ditches count as cover (52) | B | | `banks.py:288` comment |
| Paddy tiles COMPLETELY (53-54) | A/B | duplicate of 43 | |
| In-field features ARCHETYPE-GATED (56) | A | | `#in-field-features---flat-flooded-paddy-hosts-obstacles-least` |
| What we DON'T redraw (57) | A | | same |
| Honest limits - pond ~55%, rock 1-3, grave island ~30% (58) | B | | `settlement/fields/features.py:86` |
| Plot grain + irregular patchwork (60-61) | A | anchor BROKEN | |
| Size at BOTH grains `plot=34/46` (62) | B | record gives a different band | `paddy.py:55` |
| Bund stroke `AZE`, 5-color ladder, spring/summer departure (63) | D + B | GM 2026-07-24 chose `#6E4520` over chestnut `#7A5230` | `palette.py:55-72` verbatim |
| NOTE patchwork draws from shared RNG (64) | C | | - |
| Crop mix ~85% wet rice (66) | B | 85% nowhere in the record (national 55-60) | `carve.py` |
| One stage, not a rainbow ~6% flooded, ~5% gold (67) | B | | `_geom/base.py:63-65` |
| Surface flooded not rows; the UNMADE decision (68) | A + D | jittered-grid mottle for ordinary combs deliberately unmade | `#why-ruled-rows-waited-for-meiji`; `landuse.py:293` |
| Water-first v1 SUPERSEDED (69) | A | | `#water-first-v2---pond-distribution-and-the-three-layout-modes` |
| Water-first v2 warp-thread, wip -> pool (70) | B/C | | `waterfields/` |
| Delivery-ditch SPACING `min_gap = 2*plot_across` (72) | A + B | | `comb.py:498` |
| Ditches TAPER `w_tail < 0.85*w` (73) | A + B | | `frame.py` |
| A collector STARTS as a thread `w = 1.5*grain` (74) | D | GM 2026-07-25, two derivations agree, two exceptions | `comb.py:630-642` verbatim |
| Cascade tagoshi 4-5 / 8-11 (75) | A + B | | `carve.py` |
| Drain akusui, blue closing rank (76) | A + B | | `#the-wettest-plots-are-their-own-kind-of-ground...` |
| Drain's two ENDS (77) | B | | `hamletgen/sink.py` |
| Water SOURCES from the map EDGE (78) | B | | `pond_fed_from_edge` live |
| Drainage matches SLOPE, `field_fall` (79) | B + C | | `hamletgen/water.py:92` |
| Collector CROSS-slope; three checks; DECLINED readability fixes (80) | D + B | "do NOT add a rule forcing drains within X deg"; topo lines and flow arrows priced and declined; brook curve gated at 65 deg adopted | `hamletgen/sink.py` |
| Connectivity ROLE-aware (81) | B + F | | `field_ditches_reach_source_and_sink` live |
| Crop + COLOR body UNIFORM + RNG-stream trick (82) | D | | `palette.py:44-50` verbatim |
| NOT terraces - bunds not risers (83) | A | | `#minimum-basin-size...` |
| Dry plots RECTANGLES against the CANAL (GM 2026-07) + rejected first fix (84) | D + B | oriented to the CANAL not the paddy | `carve.py` `_dry_fields` |
| Dry plots never lap a paddy `hem_on_paddy` (85) | B | | `comb.py:231` |
| Slope is a KNOB `down_deg`; Ueda (86) | B + E | | `_census.py:52` |
| ONE field vs MANY + village roster (87) | E | | - |
| Dry fields + azemame intro (88) | A | anchor BROKEN | |
| `dry_band` a per-map KNOB (89) | A + B | | same |
| Crop structure `DRY_CROPS` (90) | A + B | | |
| Dry FURROWS vary per plot + wrong first rationale (91) | D + B | ridge-along-contour was a steep-slope measure; GM caught it | `carve.py:637` |
| Azemame SYMBOLIC, bead color ladder (92) | A + D | declined hunter `#355E3B` and forest `#1F4A28` | `palette.py:79-84` |
| A bead sits on a bund the paint SHOWS (93) | B | | `carve.py` |
| `plot_rings` is a PAINT-ORDER STACK (GM 2026-08-17) (94) | D | rings lap, 0.4-2.5% double count; two alternatives declined | `comb.py:440-457` verbatim; `future-work/closed.md:19` |
| The fan's toe is a headland (97-123) | A + B | | `#a-basin-never-tapers-to-a-point---the-fan-toe-truncates`; `banks.py:290` `_TOE_MIN_THICKNESS` |
| A basin too small is taken into the one beside it (125-156) | A | | `#minimum-basin-size---there-is-no-absolute-floor-and-the-real-floor-is-a-ratio` |
| The field hems onto the collector's BANK (158-200) | D + B | GM 2026-08-08 Hoshizora; two causes; `bank_chord` residue accepted; check tests position not angle | `frame.py:296-316`, `carve.py:151-158` verbatim |

Share: A ~23%, B ~41%, C ~3%, D ~16% (all but two also in engine comments), E ~12%, F ~5%.

### fields.md D items
1. NEAR-RING PADDY IS COMB FIELDS ONLY; 013/014 fillers rejected (GM 2026-07-23). 2. Estate driveways not drawn (GM). 3. AZE color chosen over chestnut; spring azenuri honest, summer bunds green over (GM 2026-07-24). 4. Jittered-grid mottle for ordinary combs deliberately unmade. 5. Collector starts as a thread, two derivations (GM 2026-07-25). 6. Declined drain-angle rule + two declined readability fixes. 7. Uniform paddy body, RNG stream kept (GM). 8. Rejected first dry-plot fix (GM 2026-07). 9. Wrong first furrow rationale (GM caught it). 10. Bead color ladder, two declined (GM 2026-08-15). 11. `plot_rings` paint-order stack, two alternatives declined (GM 2026-08-17). 12. Field hems onto the collector's bank (GM 2026-08-08).

### fields.md B items not encoded
`town_has_field_off_edge`; glebe ~2-3 plots law-bounded (`taxfree_plots_in_range`); near-ring cultivated floors 0.12 city / 0.28 town within ~800 ft; city fan-head bare ceiling 20%; dry-parcel 0.25-acre mean ceiling (reasoning at `carve.py:663`); estates >=1 visible, capital-facing half-planes, >=200 px dispersion; `field_outline_matches_planting`, `population_consistent_with_housing`; `comb_fans_record_their_design_cell`.

### fields.md inbound and disagreements
Inbound: `settlements.md:14,37`; `research/README.md:17`; `pending-enclosed-fan-floor.md:6,32,60` ("Paddy TRACT size" - page has it); `tests/tooling/test_docs_match_the_mechanism.py:41`; `tests/waterfields/test_hill.py:39`; `future-work/farming-communities.md:1604`; `.claude/agents/settlement-review.md:49`.
Disagreements: 2 of 4 anchors broken (`---`); plot size stated three ways (0.19 acre at plot=46 vs page's 0.1-0.15 vs 0.05 cell target); crop ratio 85% prose-only.

## archetypes.md - unit table

| unit (line) | class | justification | engine (B) / anchor (A) |
|---|---|---|---|
| Scripted dike-pond hamlet (feature 150) rules head (3-7) | B | | `hamletgen/consts.py:292-293,306` |
| No threshing floor, `work_yards: false` (9-10) | B | | `hamletgen/water.py:60,65` |
| Knobs `pond_layout`, `manure_form`, `dike_crop`, `leftover` (11-14) | B | | `consts.py` |
| Fry ponds one in ten, GUESS (15-16) | B | | `pondstock.py:68` |
| Sluice gates at every dike cut (17-18) | B | | `frame.py:54` |
| Pond stock pig sties / duck pens GUESS (19-20) | B | | `pondstock.py:56` |
| Not drawn by the GM's ruling: creek, boats, landing (21) | A | | `#what-stands-on-a-dike-pond-hamlet-that-a-paddy-hamlet-lacks---the-audit` |
| Header + load-when (24-30) | C | | |
| Archetype knobs, overlays PERMANENT (32) | A + B | anchor BROKEN | `#why-rape-油菜-was-tried-and-removed` |
| Two-term rule; `fraction` share of ELIGIBLE (34-44) | A | anchor BROKEN | `#overlay-extent---a-calibrated-liberty-disclosed`; `landuse.py:78-100` |
| A check written and REMOVED for having no teeth `dikeponds_are_clustered` (50) | D | nowhere else | |
| Five archetypes catalog (50) | B + E + F | terrace/ribbon unscripted; three validators NOT FOUND | `hill.py`, `polder.py:20` |
| Polder PARCEL fabric patchwork, 110/160 ft modules (52) | A + B | | `#polder-parcels-were-a-private-tenure-patchwork`; `consts.py:306-309` |
| Perimeter dike 14-40 ft band (54) | A + B | | `#the-perimeter-dike-followed-the-natural-water-edge` |
| Perimeter dike planting (56) | A | | `#why-dikes-were-planted-and-what-the-row-spacing-rests-on` |
| Ring canal on INNER toe (58) | A + B | anchor BROKEN | `#the-ring-canal-runs-on-the-inner-toe---一河围田` |
| Ring canal second pass - eight GM observations (60) | B + D | item 5 keep-out registration, item 7 footbridge `seg_caps` 41 -> 8 | `polder.py`; `water.py` |
| Third pass - five items, six dead fixture paths (62) | B + F | | `polder.py:163-168` `edge_wander` |
| Watercourses JOIN not cross - perpendicular measure (64) | A + D | the measurement rationale only here | `#wet-rice-hydrology-has-no-crossings-to-draw`; `polder.py` `_onto` |
| Mosaic vs grid knob, why NO gate check (66) | A + D | anchor BROKEN | `#grid-vs-mosaic---the-arrangement-differed-by-system`; `polder.py:33` |
| Fourth pass - crown density 6 -> 4.4 px, +5 px bank caught (68) | B + D | | `landuse.py:293-297` |
| Mulberry clear of canals; edge-grazing passes deliberately (70) | B + D | | `landuse.py:330,346` |
| Dike-pond sluices (72) | A + B | | `#a-dike-pond-is-fed-and-drained-through-sluice-gates`; `landuse.py:391` |
| Polder network CONNECTED ~0.62x span (74) | B + F | reasoned reconstruction; fixture stale | `polder.py:77` |
| Polder siting Q&A (76) | A | anchor BROKEN | `#polder-siting---full-enclosure-fluctuating-water-and-where-the-village-sits` |
| Waterward fringe + dike-top housing (78) | A + B | | `land/dikes.py:270`, `land/wet.py:209` |
| Fifth pass - gap only as wide as what runs in it; hand-piled earth never ruled (80a) | A + B + D | `split_gap` decision engine-only | `palette.py:87-104`; `polder.py:31` |
| Extended to SHARED-BARRIER archetypes (GM 2026-07-25) - additive not subtractive (80b) | D | | `comb.py:104` `bund_junctions` |
| Sixth pass - regularity was in the LATTICE, four decisions, two traps, teeth revised (80c) | D + B | | `polder.py:34` `line_wander=0.10`; `rolling/roll.py:305` |

Share: A ~24%, B ~42%, C ~2%, D ~20%, E ~5%, F ~7%. Line 80 alone is 12.6 KB (23% of the file).

### archetypes.md D items
1. `dikeponds_are_clustered` written and REMOVED - an even random scatter passed it; testable only with a 2-D eligible region. 2. Junction measure is PERPENDICULAR to the other stroke, not run-length (GM 2026-07-24 Enokida); a run-length rule cannot separate a shallow Y-offtake from a poking T. 3. Mosaic knob, NO gate check - every aggregate metric tried overlapped `edge_wander`; `pond_layout` became a ninth twin axis instead (GM 2026-07-22). 4. Fourth-pass crown density 6 -> 4.4 px, ~1 bush per 23 sq ft vs attested low end, "the remaining gap is the price of the crowns reading as separate plants"; the +5 px bank draft caught in 72 places. 5. Edge-grazing passes deliberately (GM 2026-07-24): trunk-center 3.5 px, ~1.5 px graze is the toe line clipping the rim. 6. Fifth pass extended to shared-barrier archetypes (GM 2026-07-25): polder rounding SUBTRACTIVE, comb junctions ADDITIVE; node 4-6 ft, never inflated; no manifest check (comb records no outlines). 7. Sixth pass (GM 2026-07-25: "make the lines less straight generally"): per-line wander 0.10 module, per-row fall drift tapering to zero at head and closing rank, corner reach long-tailed triangular floor ~0.12x, quadrant fillets ~a quarter bare; two traps (roughness scales to the feature; sampling density follows size); `polder_parcels_are_organic` reads the COUNT of square corners (>=12 vertices, <=2.5 square per parcel). 8. `split_gap`: intra-bay split lines at full 8 ft were "a promise of water that is not there".

### archetypes.md B items not encoded
`contour_terraces_are_stepped_bands` + `terrace_bunds`; `ribbon_is_long_and_narrow`; `dikepond_corners_rounded`; `land_use_overlay_drawn`; `dikepond_is_ponds_in_a_block`, `dikeponds_fed_and_drained`, `dikepond_water_within_banks`, `mulberry_banks_clear_of_channels`, `polder_parcels_vary`, `polder_parcels_front_water`, `polder_parcels_are_organic`, `dike_top_houses_on_the_dike`, `overlays_on_wet_ground_only` (rules live in placers, named verification gone); sixteen dead fixture paths across the two files.

### archetypes.md inbound and disagreements
Inbound: `settlements.md:24,49`; `research/README.md:9`; `hamletgen/water.py:705` (`Research/archetypes.md 'Polder siting'` - page has it); `kuwabata.notes.md:51,71` (feature-150 rule block has no home on the page); `settlements/water.md:16`.
Disagreements: (1) L42 still cites the STRUCK Shunde "townships past 50%" claim as evidence for the `fraction` design; (2) L68 states mulberry density as attested where the page labels it GUESS; (3) L52 gives the 0.4-0.6 ha / 6-10 m figures without the page's summary-only caveat (`consts.py:299-301` carries it); (4) 7 of 13 anchors broken.

## Verdicts
**fields.md**: almost nothing operative lost; the constants live in the engine with their why. Lost: four orphan decisions (rejected fillers, driveways, unmade mottle, declined drain-angle rule) and eight un-enforced rules. **archetypes.md**: sharper losses - the withdrawn-check record, the perpendicular measure, the no-gate-check record, the additive-vs-subtractive ruling, the two jitter traps, `split_gap`; 7% actively wrong. The feature-150 "rules" block is a summary of `consts.py` and belongs in `hamletgen/CLAUDE.md` or derived.
