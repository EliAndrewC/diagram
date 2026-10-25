# Inventory - rest (Explore agent on sonnet, 2026-10-25, plan D10; its reply verbatim)

All paths below are under `D = /diagram/.clones/diagram-backlog/l7r/diagram`. Line numbers are from the files as read. Classes: P1 = rule not asked before placing, P2 = placed then repaired, P3 = finished-map check run inside the generator, P4 = drop, relax, ship a shortfall or refuse where room is the remedy. The five searches interleave, so I report by file, with the cohort audit first.

## 0. What the generator runs and what judges it

- **The roll never judges itself.** `D/hamletgen/driver.py:generate (370)` returns `Report(plan=plan, failures=[], ...)` at 416, so `failures` is always empty.
  - `D/tools/cohort_audit.py:_reference_ok (380)` gates on `rep.failures`, which is that empty list. The reference-map gate therefore sees only a raised refusal.
- **`s.standing.strict = True` (`driver.py:build 268`)** turns every registry record into a check. That is the only in-roll enforcement of the matrix.

## 1. `D/tools/cohort_audit.py`: every check it runs

None of these functions is called by any placer under `l7r/`. Grep finds only comments naming them.

- `roll_how (103)` / `refused_verdict (79)`: `refused:<Name>` for any exception from `roll_or_refusal`.
  - Class: P4 (the refusals are `SeatRefused`, `SinkRefused`, `SiteRefused`, `WebRefused`, `BrookRefused`, `FieldRefused`, `OverlapRefused`, `UndeckableCrossing`).
  - A refusal is a seed's verdict, not an engine retry.
- `scatter_frame_breach (132-135)`: reads `meta.scatter_frame_breach`. The generator itself writes that key (see `finish._record_scatter_frame`), so the audit only re-reads a P3 record.
- `households_seated (140-143)`: `int(_placed) < households`, from `meta.roll_placed`.
  - No placer asks "all households seated". The seating refuses a short count with `SiteRefused` in `hamletgen/homesteads/stages.py` (outside my scope).
- `farmstead_across_brook (144-147)` via local `parts_across_brook (49)`: TWICE.
  - `_cross`/`_o` re-code a segment crossing, with its own part list `_PART_KEYS`.
  - The engine's one predicate is `D/settlement/_geom/water_index.py:crosses_a_stream (65)`. Its docstring says the finished-map test calls it too, but the audit does not.
  - Placers that call `crosses_a_stream`: `rolling/fit.py:_parts_across_stream (423)`, `shrines_wells/byres.py:356,596`, `hamletgen/homesteads/fixtures.py:505`, `homesteads/bamboo.py:302`.
- `features_do_not_overlap (148-155)`: `matrix_violations(manifest)`. Shared predicate underneath: `pair_forbidden` and `element_extents` are what `Standing.conflicts` uses at record time. See section 2.
- `lane_knots (160-165)`: `hamletgen/ways/knots.py:lane_knots`. Only the audit calls it; the knot search (`knots`) is the placer side.
- Five `grove_rules` checks, called only from the audit: `grove_sides_missing`, `groves_off_windward`, `gardens_east_shaded`, `groves_crossed_by_lanes`, `fixtures_on_groves`.
  - `gardens_east_shaded` is TWICE with `settlement/rolling/farmsteads.py:_east_trees (144)` plus `_relax_gardens_south (179)`. Both hard-code a 22 px / `bscale` east band.
  - `fixtures_on_groves` is "the same boxes" as `hamletgen/homesteads/fixtures.py:474` and `rolling/fit_index.py:47` per their comments, but is not the same function.
- `row_rules`, `water_rules`, `bamboo_mismatch` (`hamletgen/homesteads/row_rules.py`): no placer calls them. `homesteads/farm_water.py:258` and `homesteads/bamboo.py:145` only mention them in comments and set the meta they read.
- `trees_shading_plots (176)` and `bamboo_shading_plots (177)`: partly shared.
  - `trees_shading_plots` calls `crown_shades`, which placers also call (`rolling/fit.py:856,872,887`, `farmsteads.py:30`).
  - Placers otherwise reach it through `_sun_keepouts`; the audit has its own list-walking wrapper.
  - `bamboo_shading_plots` uses `box_shades`. Bamboo placers ask `_sun_keepouts(..., BAMBOO_SHADE_FT)` (`hinterland/bamboo.py:237`, `homesteads/bamboo.py:125`) rather than calling it.
- Cohort-level `row_knob_value_never_rolled (290)` and `knob_value_never_drawn (295)` count knob values. They are not map rules.
- Cohort structure: `generate` is run once (never `build`). Seeds come from a hard-coded 10+ (seed*7)%11 household ladder plus six pinned rows. Verdicts go to `dev/cohort-log` via `write_record`.

## 2. `D/overlap/`

- `registry.py:Standing.record (316)` / `refuse (323)` / `StandingList.append (495)` / `StandingManifest._wrap (571)`: KEPT backstop and refusal.
  - Quoted: `raise OverlapRefused(k, other, (x, y))` (332). On a non-strict registry `refuse` returns silently (329); hamlets set strict.
  - Class: P4 (refuse). A forbidden record is refused by name; nothing makes room.
- `registry.py:Standing.conflicts (262)` vs `matrix.py:matrix_violations (24)`: shared predicate, two drivers.
  - Both use `element_extents` and `pair_forbidden`. The registry adds `reserved.conflicts`; the matrix does not.
  - Reported as shared, not as a drift.
- `matrix.py:matrix_violations (24)`: P3 when called. Inside `l7r/` only `tools/cohort_audit.py` calls it.
- TWICE (mirrors): `matrix.py:forest_reveal_x (126)`, `FOREST_REVEAL_FT (141)` and `CANOPY_STRUCT_KEYS (145)` are commented "Mirror ... keep in sync". `matrix._mx_clamp (42)` repeats `registry.Standing._clamp (251)`.
- `registry.py:Standing.resync (380)` / `rerecord (372)`: P2/P3 backstop.
  - Run after every stage in `driver._run_stages (302, 315)` and in `finish (589)`.
  - "A record whose drawn extents moved is recorded again - and raises where the matrix forbids what it now covers".
- `registry.py:Kept.__setitem__ (458)`: KEPT at write. `conflicts(...ignore=self)` then `refuse`.
- `registry.py:refuse_unadmitted (422)`: one-candidate writers ask once and refuse. Callers are `sink.drain_run`, `water.stream`, `water.round_stream`, `lanes.lane`, `features.pond`, `moat.sluice_gate`, `comb.py:682,803,939`. No alternatives are tried; refusal is the only remedy.
- `registry.py:forbidden_segment (408)`: KEPT for linear placers.
- `reserved.py:Reservations.conflicts (133)`: KEPT. Corridors and wood seats are asked through `admits`.
- `reserved.py:release_seats_along (194)`: P4. It "gives up" reserved copse seats that a connector's way comes within the lane buffer of.
- `reserved.py:release_corridors_to (181)` and `release_corridors (186)`: reservations dropped when the placer ends.
- `taxonomy.py:_MATRIX_PERMISSIVE (497)`, `_MX_NOT_GEOMETRY (681)`, `_MATRIX_SAME_PARENT_OK (727)`: classes and keys the matrix never asks.
  - COVER, OVERLAY, VEGETATION, RING_ROAD, RECORD, PADDY_RECONSTRUCTED, and keys such as `tree_crowns`, `footbridges`, `wet_plots`.
  - The code says VEGETATION and RING_ROAD are "governed by" other rules (canopy keep-out, `ring_road_kept_clear`), so those are rules coded elsewhere on purpose.
  - Vegetation, cover and records are never refused by the matrix.

## 3. `D/hamletgen/` top-level

**`driver.py`**
- `build (262)` / `_run_stages (296)`: KEPT backstop (strict registry, resync per stage).
  - `WebRefused` is re-raised with a manifest dump (277); P4.
- `generate (370)`: P3 by absence. `failures=[]` is returned at 416, and `meta.roll_placed` is set at 404 for the audit to read.
- `cluster.py:seat_cluster (163)`: KEPT.
  - Predicates asked of each margin before it is a seat: `back_fouled > 0.30`, band on the canvas, `toe`/`wet` containment, `off > BELT_ROOM_MAX_OFF`, and `seat_has_dry_exit`.
  - `SeatRefused (349)`: P4. "no field margin turns its back to the ... wind ... the site has no seat".
  - Remedy elsewhere is room: `plan.seat_room` grows the canvas, and `fall_backs_the_wind` narrows the rolled fall. Both are asked before the seat.
- `cluster.py:belt_off_canvas (94)`: TWICE. It hard-codes the belt bands `36.0, 90.0, 146.0` that `hinterland/belt.py` derives from `BELT_NEAR_FT`, `BELT_DEPTH_FT` and `BELT_FAR_RAG_FT`.
- `cluster.py:seat_has_dry_exit (110)`: TWICE with the connector's `dry_exit` (called inside it, so shared fill) and `ways/track.connector_dry_exit`. The walls are rebuilt here "as `connector_dry_exit` walls it".
- `cluster.py:_fork_spur (473)`: P2. A spur that crosses an arm is cut so it starts at the crossing. The bounded loop is `for _pass in range(8)`.
- `cluster.py:_arm_crossing_accidental (455)`: a rule on clipped arms, applied after the arms are clipped.

**`plan.py`**
- `plan_site (456)`: KEPT. Asks "room" in advance via `seat_room (421)` and `canvas_for`.
  - The rolled fall comes from the falls that pass `fall_backs_the_wind (439)`.
  - A declared `down_deg` is taken as written, and `SeatRefused` fires only if no seat exists.
- `SitePlan.__post_init__ (150-201)` and `plan.py:504` raise `ValueError` for bad declared values. Input errors, not room; I note them only because they are refusals.

**`sink.py`**
- `stage_sink (544)` / `lay_sink (598)`: KEPT for the chosen route.
  - `route_refusals (238)` is one predicate per term; the search tries alternatives.
  - `drain_admitted (133)` asks the matrix.
  - `confluence_keeps_the_brook (442)` asks `brook_violations`; this is P3 (a finished-brook rule asked inside the roll) used as a pre-filter.
- Fallbacks, all P4:
  - Pond to off-map: `plan.water_sink = "offmap"; stage_sink(s, plan)` at 795, 806 and 822.
  - Dike-crossing, brook-crossing or matrix-forbidden pond becomes an off-map drain.
  - The pond `clamped` branch (799-808) undoes the solve and falls back.
  - Three refusals, all P4: `SinkRefused` at 754, 758 and 761 ("the drain's constructed route lies where the overlap matrix forbids it").
- `sink.py:hull_route (273)`: a constructed route replaces a searched one. Not a repair, but a fall-through.
- `sink.py:pond_seat (509)`: sways across the fall until the ditch is legal. Candidate adjustment before recording; KEPT.
- TWICE:
  - `pond_setback (164)` inlines the two tests of `pond_clear_of_crop (152)`; its docstring says so.
  - `_through_the_crop (354)` (0.3 lead exemption) and `route_refusals`'s `"field"` term (first leg exempt) are two codings of the crop rule.
  - `GATE_FLOW_SPAN = 40.0 (62)` and `JUNCTION_TURN_MAX_DEG (232)` mirror numbers of retired gate checks.
- `sink.py:stage_sink (595)` calls `round_the_brooks` (in `water/`, other session): a post-hoc reshaping of the drawn brook.
- Backing off the drain start (`for back_off in (0.0, 12.0, 24.0, 40.0, 60.0)`, 671): P2/P4. It moves the start until "the point is genuinely inside" so a later gate-style trim does its job.

**`washing.py`**
- `shared_places (120)` / `each_house_places (174)`: KEPT, `s.admits("washing_places", rec)` across `BANK_SHIFTS_FT`.
- `no_seat (167)` and the `else: no_seat(s.M)` branches: P4. A group with no seat "keeps none", counted in `meta.washing_no_seat`.

**`burial.py`**
- `stage_burial (30)`: nothing placed. `ValueError` (51) for an unattested pinned value.

**`clearance.py`**: spatial indexes only (`FabricIndex.fouled` vs `fouled_brute`). `fouled_brute` is the test oracle.

**`frame.py`**
- `stage_crossings (25)`: P1/P2 by design. Docstring: "the crossing is legal because this stage will deck it". `s.bridges()` decks what the web drew; the rule is not asked at the web (the web is outside my scope), and `UndeckableCrossing` is the last resort. See `city/bridges.py`.
- `stage_notice (65)`: KEPT. `place_kosatsuba` applies every board rule once. The docstring records that a second siter was deleted.
- `stage_frame (127)`: P3 and P2.
  - `frame_for(s, plan) != plan.view` writes `meta.view_drift`. The view is "still the decided one"; drift is recorded, not repaired.
  - `waterward_to_the_frame (204)` rewrites a placed strip: `rec.update(poly=ring, ...)` and `s.M["marshes"].pop()`. P2.
- `stage_labels (261)`: the label phase. See section 5.

**`pondbank.py`**
- `seat_free (77)`: KEPT. Each tree is tested against `_canopy_keepouts`, `_sun_keepouts`, `_on_a_tread`, crop, marsh and streams.
- `stage_pond_bank (149)`: `if seat_free(...) and all(...)` else the tree is not drawn. P4: "a planted bank with no free seat draws no tree" (`meta.pond_bank_trees`).
- It does not use `s.admits`. `pond-bank tree` crowns are in `_MX_NOT_GEOMETRY`, so the matrix does not govern them.

**`pondstock.py`**
- `reserve_sty_seat (103)`: KEPT. `sty_on_near_half`, `sty_in_reach`, `pond_fixture_fits`.
- `stage_pond_stock (156)` re-asks the same three rules (209, 232) after the houses stand. TWICE: reserve time versus stage time; `seat_faults (249)` is a third coding for diagnosis.
- P4: no seat in reach, no sty. `stock["none_why"]` records it; `n_sty` is a target, not a guarantee.

## 4. `D/hamletgen/hinterland/`

- `stages.py:stage_hinterland (78)`: runs `s.thin_planted_trees()` (121), `settlement/homestead_parts/keepouts.py:301`.
  - P2. Planted dike trees were drawn in the field stage and are removed later for a plot's sun: `keep = [... not self._crown_covers(...)]`. Returns the number dropped.
  - It runs `s.fill_the_holes(plan.view, ...)` (165): P3 (see `land/cover.py`).
  - `plan.belt` is recomputed (147) after the scrub's first predicted pass. Prediction then recompute.
- `stages.py:woodland_on_the_sheet (58)` / `woodland_offsheet (39)`: P4. No parcel found means "recorded beyond the sheet" in `meta.woodland_offsheet`.
- `stages.py:stock_woodland (230)`: P3 and P4, and TWICE.
  - `if len(s.woodland_room(patch)) < WOODLAND_MIN_CROWNS:` the parcel is drawn as grazing and recorded in `meta.woodland_regraded`.
  - The same `woodland_room` rule is asked at the scan in `open_ground_patches (741)` and again at the draw.
- `stages.py:plant_the_belt (272)` / `dent_around (257)`: P2 and P4.
  - Belt vertices inside the title pocket are pushed out 6 px (`dent_around`).
  - `village_grove(... within=..., keep_off=reserved_seats(s))` drops clumps. The comment says the polygon "is not moved - the CLUMPS are held inside the frame instead".
- `stages.py:stage_windbreak (373)`: the copse is trimmed to a rolled goal via `copse_goal`/`_goal_for`, then `s.standing.reserved.release_seats()` (472).
- `stages.py:homestead_wood_drawn (512)`: "THE ONE PREDICATE" of the wood floor. It only records `meta.homestead_wood_ft2.drawn`; the floor is not enforced here. P3-style record.
- `parcels.py:open_ground_patches (323)`: KEPT predicate `_ok (488)`, with relaxations.
  - Quoted: `for _sb_normal, _sb_sunny in ((80.0, 180.0), (40.0, 100.0)):` (437); P4 (set-back relaxed).
  - Shrink ladder: `size, size*0.8, 0.64, 0.5`; `fit_square_parcel (113)` shrinks 0.9 to 0.6. Parcels "FEWER, never smaller".
  - Dropped parcels (`continue` at 715, 727, 733, 738, 742, 749); parcels not offered when no seat is across the field (`_beyond_the_fields`).
  - `follow_the_bounds (874)` pulls ring vertices in, then `lot_follows_its_bounds (842)` asks the rule. Shape then ask, before recording.
- TWICE in parcels: `parcel_bbox_ok (70)`, `parcel_inside_share (98)`, `_ok` (0.8) and the gate (0.7) are three codings of the frame-share rule. `_crop_refuses (964)` is now only re-exported; `open_ground_region (909)` is the live set-back.
- `belt.py:belt_polygon (201)`: P4. The ladder `for span_f, back in ((1.0, 0.0), (1.0, 22.0), (1.0, 44.0), (0.88, 44.0), (0.74, 60.0), (0.6, 60.0)):` (371) stops at the first non-fouled belt.
  - If no rung is clean, the last rung (0.6, 60.0) is returned and the loop falls through unconditionally. The belt may ship fouled.
- `bamboo.py:bamboo_seats (172)`: KEPT, `nearest_fitting (106)` over `_fits`.
  - P4: "a stand that fits nowhere is dropped ... draws none".
  - `bamboo_blocked (37)` vs `bamboo_blocked_indexed (77)` is an oracle pair.
- `frame.py:title_pocket (299)` / `pocket_clear_of_features (258)`: KEPT predicate, with a P4 ladder.
  - 300x190 pocket, then placard-size, then outside the content (four corners with 0/16/32/48 shifts), then `plan.title_pocket = (x0, y0, x0, y0)` (383), a degenerate pocket reserving nothing.
- `frame.py:frame_for (121)` / `frame_bounds (188)` / `scatter_frame (195)`: predicted before the view is decided. Breach is checked later in `finish._record_scatter_frame`.
- `paddy_grass.py:seat_paddy_grass (85)`: KEPT. `open_seat` then `clear_of_plot`/`above` re-asked "held as seated: the seat search may slide it". P4: `"no seat"` recorded.
- `crossing.py`, `wood_rank.py`: predicates only.

## 5. `D/settlement/`

**`core.py` / `houses.py` / `hard_ground.py`**
- `core.py:admits (326)`: KEPT.
- `houses.py:_fits (261)`: P1 in part. Documented asymmetry in `shrines_wells/seats.py:_footprint_clear (26)`: `_fits` tests only a candidate's CENTER against `bound`, `block_polys` and corridors.
- `hard_ground.py:_hard_clear (58)` sweeps a fixed 5 degree tilt "decided elsewhere". A rule tested on a footprint other than the drawn one (P1).
- `houses.py:_try_place_bundle (421)`: for `kind == "abandoned"` (426) it uses `_fits` only, no `admits`. P1; `M["houses"].append` is the backstop.
- `houses.py:_try_place_bundle (462-465)`: `ValueError` for an over-long farmhouse is an input error.

**`finish.py`**
- `finish (437)` runs `settle_beads (443)` and `flush_tree_stands`/`flush_mark_groups`/`flush_covers`: P2.
  - Beads are dropped after the last water, and crowns are not drawn where they would cover a structure.
  - `_record_scatter_frame (606)`: P3 record. Quoted: `self.M["meta"]["scatter_frame_breach"] = _over`. No repair.
  - `self.standing.resync()` at 589 is the last backstop.
  - `RuntimeError` at 551 is a stream-alignment invariant, not room.
- `finish.py:_caption_lines (295)` / `label (212)`: TWICE with `labels/placer.place`. A second wrap-and-clear judgement against `label_blocker_quads`; "when none is clear the one-liner is" drawn, which is P4.

**`title.py`**
- `title (51)`: P4 ladder, but the final rung is room. The rungs are pocket, blank, cover, four corners, then `_title_band (157)`, which grows the sheet (`set_view(... vh + band)`).
  - "A band inside the map is map, and its bare ground is clothed" via `refill_the_view`.
  - Notable: this is the one ladder that ends in "more room", and it is not a refusal.

**`rolling/`**
- `place.py:_place_bundle_dispersed (143)` / `_slide (96)`: KEPT. `_seat_refused` / `_bundle_refused` / `_bundle_fits` are re-asked per step.
- `place.py:_place_bundle_nucleated (178)`: KEPT. The "one computed move" shifts an overlapping envelope once and re-tests; the nudged `geom` is re-asked.
- TWICE: `place.py:_seat_refused (53)` and `_bundle_refused (72)` restate conjuncts of `fit.py:_bundle_fits (559)` and `_envelope_blocked` "so a YES here is the fit test's NO". `_house_box_refused (310)` repeats `_envelope_blocked`'s margin tests.
- `fit.py:_bundle_fits (559)`: KEPT, ending in `bundle_admitted (lot.py:267)`.
- `fit.py:_settle_persimmon (860)` / `fit_index.py:drop_persimmon (81)`: P4/P2. "Dropped rather than moved" from an already-laid `geom`.
- `fit.py:_yard_sun_conflict (891)`: "A SEATING PREFERENCE", labeled as not the sun rule; the sun rule is `_sun_keepouts`.
- `fit.py:_parts_across_stream (423)`: see TWICE with cohort_audit.
- `farmsteads.py:_relax_gardens_south (179)`: P2 / P1.
  - A garden "left with a NEIGHBOR'S grove hard against its EAST" is nudged south after the groves are recorded. "Best-effort: a garden boxed in ... stays put" (flagged only by `gardens_east_shaded`).
  - Beds move via `geom["gardens"] = shifted` without `s.admits`; they are checked by `_garden_beds_clear`, `beds_sun_clear`, `_rect_blocked` instead.
  - TWICE with `grove_rules.gardens_east_shaded`.
- `farmsteads.py:_farmsteads_bundle (67)`: `_draw_grove` thins crowns off walls "by one rule rather than by z-order"; P2-ish.
- `gap_ways.py:lay_the_ways (398)` / `pinch (379)`: the household way is deferred to after the last house.
  - P4: "a household no way reaches is pinched across its nearest reached neighbor's yard" (`reached_across`, `passage_kind = "pinch"`). Relaxes the access rule; labeled CANON.
  - `rec.pop("reached_across")` / `passage_depth` / `passage`: passages "ended" once a way reaches them (P2).
- `access.py:access_corridor (450)` / `admitted (496)` / `tree_admits`: KEPT (corridor and whole tree lawful). `passage.py:passage_of (270)` / `opens (95)`: the rule asked at seat time (`SeatRegion.opens`) and again later by `gap_ways`/ways (`unreached_houses`, outside my scope). TWICE.
- `lot.py:bundle_admitted (267)` / `bundle_records (249)`: KEPT.

**`shrines_wells/`**
- `wells.py:well_at (106)`: KEPT. `admits("wells", ...)` and `_fits`.
  - TWICE with `_place_wells (180)`: both compute `2*r+14` ("the two must move together").
  - `_place_wells` does not ask `admits`; hamlets do not call it (they call `well_at`).
- `wellground.py:_well_ground_clear (137)`: KEPT (placement half of `wells_clear_of_paddies`, `wells_off_the_wet_toe`).
- `byres.py:reserve_commons_byres (158)`: KEPT with widening rounds. "fewer than asked only where the band has no free ground, which the caller refuses" (`SiteRefused`, `homesteads/stages.py:593`).
- `byres.py:_commons_pocket_clear (202)`: KEPT (`tree.covers_box`, `_fits`, `admits("byres", ...)`).
- `byres.py:draft_byres (403)`: P4 (relaxed form and spread) and P1 (spiral path).
  - Form fall-through: `courtyard` becomes `yard_shed`, then a free shed at rot 0.
  - Spread tier relaxes `for _tier in (0.5, 0.25, 0.0):`. Boxed-in homesteads are skipped.
  - The spiral path asks `_fits`, field edge, `_sep` and `crosses_a_stream`, but not `admits("byres", ...)`. The `M["byres"].append` backstop covers it.
- `woods.py:flush_tree_stands (46)` / `_canopy_seats (137)` / `trees_off_the_treads (23)`: P2/P4. "A crown that would cover [a structure] is simply not drawn: the stand THINS".
- `torii.py:_torii (39)`: KEPT predicate with `ValueError` refusal (P4). `torii_seat_on_wall` is asked and the arch is refused, "so a hand-placed arch is what lands here".
- `seats.py:open_seat (46)`: KEPT, but P1 for `_footprint_clear (26)`, which tightens only `bound`.

**`structures/fixtures/` and `captions.py`**
- `siting.py:place_kosatsuba (134)` / `_route_seats (286)` / `_board_for (417)`: KEPT.
  - `_route_seats (331-347)` asks view, placard, way beds, water, `_fits(..., corridors=False)`, facing and `admits("kosatsuba", ...)`.
- P4 ladder: `board_seat.py:site_board (269)` asks the caption proofs `[proof, lax, loose]`.
  - `terminal_caption (202)` then `fallback_caption (214)` ("Never None, so a board with a roadside seat is never dropped over its caption"). The clean caption is a preference.
  - `_board_for`: `cands = [c ...] or cands`, traffic floor 60%, `choose_board(...) or choose_board(cands, proof)`.
  - Final `return None  # no roadside seat at all`; `resolve_seat (289)` raises `ValueError` for an unsitable pinned placement.
- `board_seat.py:board_caption_seat (165)`: "THE ONE PREDICATE" of the caption rules. The association is "PROVED AGAIN ON THE RECORD" at 0.1 rounding (`recorded_board (190)`), because the map is judged on the manifest.
- `captions.py:place_labels (139)`: drains the queue and seats every caption against the finished map by the one placer.
  - `label_blocker_quads (113)` is TWICE with `label_obstacles (221)`: two collectors of "what a caption must miss".
  - `discard_queued_label (336)`: the undo for a withdrawn feature.

**`water_ways/`**
- `lanes.py:lane (50)` / `reshape_lane (88)`: KEPT backstop. `lane()` calls `refuse_unadmitted(self.M, "lanes", new)`, then `rec = self.standing.kept("lanes", new)`. `reshape_lane` leaves a lane unchanged if `admits` is false.
- `lanes.py:admitted_runs (104)`: P2. The draft polyline "with every segment the overlap matrix forbids ... taken out".
- `water.py:stream (107)`: KEPT at record. `round_stream (153)` / `rerecord`: P2. A recorded stream is rewritten to a rounded course after first drawing, asking `refuse_unadmitted` first.
- `clipping.py:field_channel (216)` / `_clip_to_pond|moat|river|stream`: P2. Mouths are snapped or trimmed at draw, so the recorded `field_ditches` and the post-clip `drawn_channels` "diverge wherever a mouth was snapped".
- `_helpers.py:_pull_back (88)`, `junction_floor (154)`, `_LANE_MIN_FT (37)`: lane trim helpers (callers are in the other session's `ways/`). A lane under 71 ft "is dropped"; ends are pulled back. P2.

**`land/`**
- `cover.py:fill_the_holes (257)` / `refill_the_view (282)` / `bare_cells (189)`: P3.
  - `bare_cells` is "ONE PREDICATE ... the gate's own grid"; `BARE_SHARE_CAP = 0.35` (`margins_form_continuous_ring`).
  - Quoted: `if not total or len(bare) <= BARE_SHARE_CAP * total: break` (276). The roll fills holes with grazing until the finished-map share passes.
- `cover.py:woodland_room (339)`: P3/KEPT, "so the scan that offers a parcel and the commons that stocks it read one answer".
- `wet.py:marsh (316)` / `drawn_ground (247)`: P4. "a marsh with no open ground left ... is None", recorded in `meta.marsh_dropped`.
- `wet.py:trim_off_marsh (486)`: P2. Lane ends are walked back off reeds; a way wholly wet "returns []", dropping it.
- `dikes.py:breaches_any_dike (154)`: KEPT (used by `sink`).
- `dikes.py:dike_gates (340)`: P2. Gates are placed at the cuts the dike made earlier and "SNAPPED onto the recorded watercourse ... when one runs within 20 ft ... else at the cut".
- `dikes.py:dike_top_houses (390)`: P1. Asks only the `gap_clear` and spacing checks, with no `_fits`/`admits`; no in-`l7r` caller was found.

**`fields/`**
- `comb.py:_comb_draw_hem (341)`: KEPT with drop. `_refused` = `hem_on_paddy` or `_hem_on_water` or `not self.admits("dry_plots", ...)`.
  - P4: refused plots are dropped; `_coarse_grain_top_up` / `grain.top_up (grain.py:107)` makes up the area from reserve plots "or every plot the ground offers is in it".
- `comb.py:_comb_drop_drowned_beads (511)` / `settle_beads (569)`: P2, and TWICE (same `bead_drowned`).
  - Beads are dropped at draw, then again after the last water at `finish`.
- `comb.py:935`: `ValueError` for a feed that runs level or uphill. P4.
- `features.py:_plot_pond (358)`: shrinks the pond until it clears the plot ring; below 10x7 px the plot takes none. P4. `pond()`: `refuse_unadmitted(self.M, "pond", ...)`.
- `outfall.py:outfall_run (45)`: tries the standard run, else a fallback curve if `runs_downhill` fails. P4 (relax).

**`city/`**
- `bridges.py:bridges (404)`: `deck_admitted` and `UndeckableCrossing (445)`.
  - P4 (refuse): "no deck seats where a way crosses water". The class docstring says the web's last pass cuts such crossings, so reaching here is "a defect in the engine".
  - `_reseat_to_cover (461)`: P2. A standing deck is lengthened to cover a second crossing.
  - `crossing_deck` is the one predicate shared with `hamletgen/ways/law.py:deck_seats` (outside my scope).
- `bridges.py:channel_footbridges (470)`: KEPT, many candidate predicates ending in `self.admits("bridges", ...)`.
  - A candidate that fails any rule is skipped (`continue`), and no plank is laid if none fits. P4.
  - Rounded inputs are tested to match the gate's recomputation: `_plank_reaches_useful_ground(round(px,1), ...)`. TWICE with the gate's `footbridges_reach_useful_ground`.
- `moat.py:inwall_drain_outfall (75)`: P2. The drain polyline is trimmed back from the ring road before being drawn.

**`_geom/` / `sitegen/`**
- `sitegen/geom.py:pull_clear (56)`: P2. Walks a point back "until it is `margin` clear"; returns the point after `tries=24` steps even if still fouled (used by `hamletgen/ways/track.py:536`).
- `_geom/primitives.py:keepout_ring (269)`: loop of at most `KEEPOUT_GROWTHS` pushes, then `ValueError("no keep-out of ... chords contains its band")`. P4.

## 6. `D/labels/`

- `placer.py:place (409)`: KEPT. Candidates are ranked and free space wins.
  - P4 ladder when nothing is free: fallback search, leader rings, soft least-cost, `moved_inward (550)`.
  - Quoted: `# ...AND WITH NO FREE GROUND AT ALL, THE SEAT COVERING THE LEAST, whatever it covers` (505). "Never dropped".
  - `strict=True` returns `None`; used by `board_caption_seat`.
- `placer.py:nudge (599)`: candidate shifted, each shift re-scored. KEPT. `_strict_seat (523)`: KEPT.
- `placer.py:305`: `ValueError` for a bad subject kind.
- `hand_sheet.py:seat (714)` / `repair (805)`: P2. Greedy placement, then each caption left covering ink is re-placed with one neighbor lifted; the pair is kept if the total cost falls.
- `hand_sheet.py:declared_parts` (~655): `ValueError` for captions that name nothing.

## 7. Pool generators (`/diagram/.clones/diagram-backlog/pool/`)

- The hamlet `.gen.py` files (inashiro, mizuguchi, sawada, kashikawa, kuwabata) only call `generate(HamletSpec(...), out_base=...)`, with spec pins (e.g. `pins={"paddy_rest": "unsettled"}`, `fixtures_min={"shrine": 1}`). No repair, retry or check runs in the gens.
- The magistracy and shrine gens are compound drafts with no engine repair call.

## 8. KEPT (the rule is asked of a candidate before it is placed)

Prefix `D/`.
- `overlap/registry.py:Standing.admits/conflicts` - the matrix `pair_forbidden` plus the `reserved` corridors and wood seats.
- `settlement/core.py:Settlement.admits` - the same, for a candidate record.
- `hamletgen/cluster.py:seat_cluster` - back not fouled by crop, band and belt on the canvas, off toe, wet and brook, and a dry exit.
- `hamletgen/sink.py:route_refusals` and `drain_admitted` - kink, field, uphill, upstream, brook, dike, twin, and the matrix.
- `hamletgen/washing.py:shared_places` / `each_house_places` - `s.admits("washing_places", rec)` per shift.
- `hamletgen/pondbank.py:seat_free` - canopy, sun, tread, crop, marsh and stream keep-outs per tree.
- `hamletgen/pondstock.py:reserve_sty_seat` - `sty_on_near_half`, `sty_in_reach`, `pond_fixture_fits`.
- `settlement/farm_fixtures.py:pond_fixture_fits` - structures and crossings, then `admits("pig_sties", ...)`.
- `hamletgen/hinterland/parcels.py:open_ground_patches` (`_ok`, `parcel_bbox_ok`, `parcel_inside_share`, `parcel_wet_share`, `lot_follows_its_bounds`, `in_a_ruled_line`) and `woodland_room`.
- `hamletgen/hinterland/bamboo.py:bamboo_seats` - `_fits` with `stand_spares_seats` over the sampled stand.
- `hamletgen/hinterland/frame.py:pocket_clear_of_features` / `clear_pocket_spot` - glyph keep-clear plus `reserved.box_covers`.
- `hamletgen/hinterland/paddy_grass.py:seat_paddy_grass` - `open_seat` plus `clear_of_plot` and `above`.
- `settlement/rolling/fit.py:_bundle_fits` - `_bundle_common_fits`, side fits, `_on_the_access`, `_fixtures_in_bands`, `bundle_admitted`.
- `settlement/rolling/lot.py:bundle_admitted` - `admits` for every part of the bundle.
- `settlement/rolling/place.py:_place_bundle_nucleated` and `_slide` - re-ask the fit at each move.
- `settlement/rolling/access.py:access_corridor` / `admitted` / `tree_admits`.
- `settlement/shrines_wells/wells.py:well_at` - `admits("wells", ...)` plus `_fits` plus `_well_ground_clear`.
- `settlement/shrines_wells/byres.py:_commons_pocket_clear` - `tree.covers_box`, `_fits`, `admits("byres", ...)`.
- `settlement/structures/fixtures/siting.py:_route_seats` and `board_seat.py:board_caption_seat` (+ `entrance_seat_ok`) - `admits("kosatsuba", ...)`, view, placard and caption proof.
- `settlement/water_ways/lanes.py:admits_lane` / `reshape_lane` / `lane` (`refuse_unadmitted`) and `Kept`.
- `settlement/water_ways/water.py:stream` / `round_stream` and `settlement/fields/features.py:pond` / `moat.sluice_gate` - `refuse_unadmitted`.
- `settlement/fields/comb.py:_comb_draw_hem._refused` - `admits("dry_plots", ...)` plus `hem_on_paddy`/`hem_on_water`.
- `settlement/fields/paddy.py:252` - `admits("fallow_patches", ...)`.
- `settlement/city/bridges.py:channel_footbridges` - ends in `admits("bridges", ...)`.
- `settlement/_geom/water_index.py:crosses_a_stream` - the same-bank rule, one predicate for the fit, fixtures, byres and bamboo placers.
- `settlement/rolling/farmsteads.py:_garden_beds_clear` and `beds_sun_clear` - asked per nudge step.
- `settlement/land/dikes.py:breaches_any_dike` - used by `sink`.
- `labels/placer.py:place` - free-space-first. Strict mode refuses; non-strict degrades (see section 6).

## 9. Other rule duplicates not covered above

- Vegetation and the canopy keep-out: the matrix abstains for VEGETATION, and the keep-out is coded in `_canopy_keepouts`/`_sun_keepouts`/`crown_shades` (taxonomy lines 497-515).
- `hamletgen/consts.py:539` states that the matrix and grove predicates "are run on every roll by `tools/cohort_audit`", which records that the in-generator rules and the cohort rules were deliberately separate.
- I did not read `settlement/homestead_parts/`, `hamletgen/ways/`, `hamletgen/homesteads/`, `hamletgen/water/` or `waterfields/`. Anything attributed to them above comes from calls, docstrings or comments in the files I did read.
