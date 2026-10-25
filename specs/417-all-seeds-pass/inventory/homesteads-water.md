# Inventory - homesteads-water (Explore agent on sonnet, 2026-10-25, plan D10; its reply verbatim)

Inventory below. All paths are relative to `/diagram/.clones/diagram-backlog/l7r/diagram/`. I read the four `CLAUDE.md` files first, plus `waterfields/seams/CLAUDE.md`. I did not read `settlement/rolling/*` or `ways/*` bodies. Where they came up I cite them only as callers or as second sites of a rule.

## A. Who calls the finished-map rules (search 2)

- **`tools/cohort_audit.py` is the only non-test caller.** Lines 166-175 call `grove_sides_missing`, `groves_off_windward`, `gardens_east_shaded`, `groves_crossed_by_lanes`, `fixtures_on_groves`, `row_rules`, `water_rules`, `bamboo_mismatch`, `trees_shading_plots` and `bamboo_shading_plots`. It also calls `matrix_violations` (line 154), `lane_knots` (line 148) and its own `parts_across_brook`.
- **The `tests/` hits were not opened.** Per the CLAUDE.md files the same rules are also read by gate and soak tests. These are the only `row_rules` / `grove_rules` / `bamboo_mismatch` hits outside `tests/`, so no generator code calls them.
- **`waterfields/trunks.py:outfall_rise` (71), `sharpest_turn` (81):** no callers in the generator. Construction (`DRAIN_MIN_LEG`) stands in for them; tests ask them.
- **`waterfields/furrows.py:tract_seams` (94):** only gate tests call it. The generator calls `settle_tract_seams` instead.
- **`homesteads/row_rules.py:row_rules` (71), `water_rules` (152), `bamboo_mismatch` (196):** P3 does not apply (never called in the run), so class P1. `bamboo_mismatch` is the clearest case: `bamboo.py:145` writes `meta.household_bamboo_in_grove_farms` only so this rule can read it later.
- **`brook_violations`** (`hamletgen/water/brook.py:262`) is called in the run by `feed_brook` and by `hamletgen/sink.py:448`. It is asked of a candidate before it is taken, so it is KEPT, not P3.

## B. Per-file entries

### hamletgen/homesteads/

**row_rules.py** (module comment: "read off a finished manifest")
- `row_rules (71)` | P1 | Checks `farm_off_its_street`, `farm_behind_another`, `street_not_drawn`/`street_broken`, `holding_not_drawn` and `farm_not_on_its_street` only on the finished manifest. `rows.seat_rows` asks only `frame_refused` and `holding_clear`.
- `water_rules (152)` | P1 | Checks `farm_beyond_a_shared_well`, `farm_without_its_channel`, `farm_without_its_well` and `well_in_the_way_in` on the manifest. `wells.grove_water` / `farm_water.farm_channels` build the water but never ask this.
- `bamboo_mismatch (196)` | P1 | `return [("draws_unrolled", k) ...] + [("rolled_undrawn", k) ...]`, read off the manifest only.
- `continuous (50)` | P1 | The "one continuous street" test, asked only inside `row_rules`.

**stages.py**
- `seat_every_household (272)` | P4 | `if placed < want: raise SiteRefused(... "no house is taken back")`. If a margin seats some but not all households, the site is refused. Only a margin that seated zero houses falls to the next rung of `margin_ladder` (`for margin in ladder if placed == 0 else ()`).
- `_seat_households_as (444)` | P4 | `if len(s.reserve_commons_byres(...)) < want: raise SiteRefused("the seat band holds no ground for ... shared byres")`. `if _out is None: return 0, 0` gives up a margin with no lawful way out.
- `_seat_households (424)` | P1 / P4 | For dispersed forms it deep-copies the settlement (`trial = copy.deepcopy(s)`), seats the single-file line on the copy, and keeps it only if `>= households` stand. Otherwise it seats in ranks.
- `_seat_rank_rounds (802)` | P4 | Seven rounds, `wlat = lat*(1+0.22*attempt)`. The band widens (more room), but after round 4 `if hypot(...) > bound and attempt >= 4: continue` drops the candidate and the exhaustive pass follows.
- `_ground_push (382)` | P2 | Moves a front-row candidate seat by `push` (corridor / brook reach) before it is offered. This moves a candidate, not a placed house.
- `stage_homesteads (80)` | P2 | `lay_the_ways(s)` returns `passage_revoked` / `pinch_passages`. A passage is "ended in place" and a household no way reaches is "reached across the nearest neighbor's yard". The code is in `settlement/rolling/gap_ways.py` (not opened); it runs after the houses stand.
- KEPT: `stages.py:_offer_seat (360)` (`region.offer([(x, y)])[0]`, the seat-region predicate) and `corridor_ground (345)` (the ways' own `on_lawful_ground`).

**capacity.py**
- `unseat_to (169)` | P2 | `del s.M["houses"][h:] ... del s.hard_polys[hp:]` takes back a margin's registries. It counts houses in `meta.houses_taken_back`, which is held at 0 by gate.
- `margin_ladder (140)` | P4 | Supplies the next-ranked margin when the chosen one seats no house.
- `seat_the_rest (103)`, `offer_seats (121)` | P4 (give-up) | `since >= dry` with `DRY_SPELL = 400` gives up a margin after 400 offers in a row seat no one.
- `class SiteRefused (43)` | P4 | The refusal type.
- KEPT: `offer_seats` — each candidate goes through `s.try_place(q[0], q[1], "plain")`.

**growth.py**
- `settled_seat (146)` | P4 | Returns None after `SETTLE_TRIES` moves, or when `refused(q)`. The candidate is dropped.
- `grow_the_margin (361)` | P4 | `if level >= len(GROW_LEVELS) and not queued: break  # ...the ground is full`. It widens (8, 12, 16 directions, more rings), which is more room. It stops when no new seat is queued and ships `placed < want` to the caller's refusal.
- KEPT: `seat_refused (191)` (asked "before laying out any part": `_house_box_refused`, `rect_refused`), `keeps_its_distance (167)`, `keeps_every_gap (225)` (each pair clears the gap), `settled_seat` (reach rolled at the seat).

**persimmon_reseat.py**
- `give_way (101)` | P2 | After a persimmon is placed it deletes the farm's own grove crowns under it from `tree_crowns`, from `_conifer_crowns`, and from the SVG strings (`s.out[:] = [drop(o) ...]`).
- `reseat_persimmons (136)` | P1 / P4 | A tree a household "could not keep" is handed to another household, fixing the count after the seating (`laid >= short`). Placement went wrong first, then the count was repaired.
- KEPT: `persimmon_for (35)` — `clear(lx, ly, r)` asks sun, conifer and neighbor-shade for every seat tried.

**fixtures.py**
- `_draw_pending (401)` | P4 (fallback) | `else: draw_laid_fixture(s, h, f, forms)`. A field pit with no clear spot falls back to the seat laid for it.
- KEPT: `under_a_lane (451)` (`over_a_fixture`, the one predicate), `_flexible_clear (462)` (`_strip_blocked`, `across_the_brook`), `across_the_brook (497)` (`crosses_a_stream`), `across_a_lane (508)`.

**bamboo.py**
- `household_bamboo (73)` | P4 | "A farmstead with no room keeps none." The loop ends with no candidate and nothing is placed.
- `seat_strips (336)` | P4 | `meta.household_bamboo_no_room = want - len(strips)` ships the shortfall as a recorded count.
- KEPT: `strip_refused (276)` (`_strip_blocked`, `in_belt`, `parts_hit`, `stand_spares_seats`, `in_the_sun`, `crosses_a_stream`, `across_a_lane`), `_strip_blocked (524)`.

**retirement.py**
- `retirement_houses (136)` | P4 | "A household with no room passes its turn to the next one." `meta.retirement_houses = seated` can be less than `retirement_target`.
- KEPT: `s._byre_clear_of_all_but(...) and s.admits("retirement_houses", rec)`.

**sties.py**
- `stage_sties (128)` | P4 | `s.M["meta"]["sty_short"] = target - drawn`. The hamlet ships the shortfall.
- KEPT: `sty_seat (97)` — `s.admits("farm_fixtures", rec) and not any(fixture_on_band(rec, g) ...)`. This is the model case: it uses the check's own predicate before placing.

**wells.py**
- `reach_wells (745)` | P3 / P4 | Calls `dry_households(s, houses)` on the placed map and adds wells until none is dry: `if not dry_households(s, houses) and not busy: break`. It ends in `meta.dry_households` (shipped) and `meta.well_fallback`.
- `dry_households (735)` | P3 | The finished-map "within `WATER_REACH_FT`" check, run inside the generator.
- `lane_and_fallback_wells (809)` | P4 | A fallback rung: "among three houses, then two, at the 95 ft... marked `fallback`".
- `record_over_ten (791)` | P4 | `meta.wells_over_ten = over`. A well serving more than ten households stands and is only recorded.
- `seat_cluster (666)` | P4 | Reach widens (190, 300, 520, 760 ft), then "three, then two... only where fewer than five households need the communal wells". The ladder relaxes the neighborhood count.
- `stage_lane_wells (710)` | P4 | Seats owed wells after the lanes. The seating that came first (`place_wells`) is repaired later.
- KEPT: `seat_wells (384)` (`s.well_at`, the 170 px apart test, `extent_past`, the wood-floor disc), `own_well_clear (172)`.

**rows.py**
- `draw_holdings (336)` | P2 | `if band.is_empty or band.area < 1.0 or any(band.intersects(g) for g in lanes + water): continue`. The holding was reserved at seating (`holding_clear`) and cells are cut away at draw time.
- KEPT: `frame_refused (321)` (`door_clear`, the frame crossing a street, `frame_on_holdings`), `holding_clear (256)`, `door_clear (288)`, `best_row_line (490)`.
- `seat_rows (535)`: places only through `frame_refused` and `try_place`. A far-row seat whose holding does not fit is "passed over". Short farms go to the next margin, so the refusal is in `seat_every_household`.

**farm_water.py**
- `farm_channels (256)` | P4 | `dry.append(h)`: a farm no channel reaches is given a well instead (`grove_water`), not more room.
- KEPT: `farm_channel (172)` — `routes += [p for p in found if ... not crosses_other_water(p, water, ...)]`.

**boundary.py, region.py, seat_geometry.py, seats.py, household_ways.py, well_seats.py, holds.py**
- KEPT (ground predicates asked before a seat): `boundary.py:FreeGround.rect_refused (447)`, `UnreachableGround.refuses (488)`, `region.py:SeatRegion.offer (155)`. No repair or refusal logic found.

### settlement/homestead_parts/

**belt_law.py**
- `settle_the_belt (421)` | P2 + P3 + P4 | Plants the belt, then reads it as a finished map (`BeltReading(...)`, `rd.thin()`, `rd.holes()`) inside the run. A "repair" phase deepens and closes; an "end" phase removes crowns: `seated = _cut(rd, seated, v1, v2)  # keep the longer side`. The module header says "read and repaired where the belt is planted".
- `_cut (407)` | P4 | `keep_left = left >= right` — drops the shorter side of the belt.
- `_deepen (369)`, `_close (387)` | P2 | Add crowns to an already-seated belt.
- `reading_of (329)`, `belt_depths (342)`, `belt_holes (348)` | P3 / P1 | The finished-manifest readers (W16, W17). The same `BeltReading` is used by the placer inside `settle_the_belt` and by the tests.

**stands.py**
- `village_grove (203)` | P2 + P4 (mixed with KEPT) | Per-seat chain is KEPT (see below). After it comes the repair block: `close_belt_gaps`, `settle_the_belt`, `trim_to_the_wind`, `stocked_copse(...)`, `trim_to_goal(...)`. Those drop or add already-seated crowns.
- `trim_to_the_wind (81)`, `_trim_ends (101)` | P2 + P4 | `del out[far]`. End crowns come off until the belt bears on the wind. The result is `[]` (no belt) if it still bears off: `return out if off <= ... else []`.
- `belt_bearing_and_subtense (65)` | one predicate, asked after planting.
- KEPT: `_seat` inside `village_grove` — `blocks.taken_by`/`exact_taken_by`, `_near.too_near`, and a re-seat re-asked (`blocks.static_clear`/`exact_clear`).

**stocking.py**
- `stocked_copse (18)` | P2 + P4 | `del out[max(loose, ...)]` drops the farthest clumps until `grove_stocked`.
- `main_stand (53)`, `stocked_box (72)` | P2 / P4 | Split the clumps and keep the larger part, or shrink the recorded extent to the main stand.
- `grove_stocked (10)` | one predicate (W15). It is applied after planting in the three functions above.

**wood_goal.py**
- `trim_to_goal (78)` | P2 | Trims the copse back to the rolled goal by dropping seats from the end of the run.

**grove_fill.py**
- `reseat_clump (235)` | P2 (candidate level) | Moves a refused clump up to 2.2 steps. Other refusals are dropped: "a clump refused by the crop, open water or a dike bank is dropped, not re-seated".
- `close_belt_gaps (349)` | P2 | Fills interior gaps after the belt is seated.
- KEPT: `grove_blocks (27)`, `grove_blocks.py:GroveBlocks.taken_by (164)`.

**keepouts.py**
- `thin_planted_trees (301)` | P2 | `self.out[z] = "".join(p for p, kept in zip(pieces, keep) if kept)`. Dike trees laid in the field stage are removed once yards and beds exist. Called from `hamletgen/hinterland/stages.py:121`.
- KEPT: `_sun_keepouts (234)`, `_crown_covers (357)`, `_canopy_keepouts (319)`.

**tree_shade.py**
- `trees_shading_plots (131)`, `bamboo_shading_plots (119)` | P1 | Finished-manifest checks, run only by gate and `cohort_audit`.
- KEPT: `crown_shades (41)`, `crown_in_ground (59)`. The same predicate is asked before placing by `fixture_seats._persimmon`, `rolling/fit._persimmon_sun_conflict` and every crown placer, per the module docstring.

**groves.py**
- `_draw_grove (437)` | P4 (drops) | Inner `seat()` runs `_crown_covers`, `_crown_seat_clear`, `over_a_conifer`, and a persimmon-crown test, then `return`s. The refused crown is not drawn and the grove ships sparser (`TOPUP_TRIES` bounds the retry). The same goes for a bamboo mark under a crown (`continue`).

**yards.py**
- `_lay_by_hand (394)` | P4 (relax) | Ladder `((x+dx, y+dy, a), (x, y, a), (x, y, a/2), (x, y, 0.0))`. The last rung is accepted unasked: `if ja == 0.0 or (fits(q) and ...)`.
- `mat_cells (81)`, `thin_evenly (424)` | P4 | `thin_evenly(best, cap)` drops mats evenly to the cap. A yard "that cannot hold a third... draws as many as fit at 1 ft".

**fixture_seats.py**
- KEPT: `lay_fixtures (347)`. A fixture with no seat raises `class FixtureUnlaid(ValueError) (128)` (a bath room "refused rather than walked out"), and the bundle fit refuses that household's seat. The check runs before the household is placed.
- KEPT: `_persimmon (786)` (sun rule inside the seat search).

**wood_share.py**
- KEPT: `WoodShares.seat_barred (297)` ("THE ONE PREDICATE of a reserved seat"), `WoodShares.share (325)` (returns None, so the homestead is refused its seat).

**bamboo_keepout.py**
- KEPT: `stand_spares_seats (36)`.

**grove_rules.py** (all finished-manifest)
- `grove_sides_missing (65)`, `groves_off_windward (83)`, `groves_crossed_by_lanes (102)`, `gardens_east_shaded (131)`, `fixtures_on_groves (154)` | P1 | Read only from `cohort_audit`.
- `fixture_on_band (169)` | shared predicate, KEPT (see TWICE).

**grove_sides.py**
- `grove_faces (104)` / the roll table raises `ValueError("a farmstead grove takes 2, 3 or 4 sides...")` — a type guard, not a room matter.

### hamletgen/water/

**brook.py**
- `settle_course (458)` | P2 | `out = unfold(axes_off(clear_of_field(out, ...)), BROOK_MAX_TURN_DEG, hold=[sluice]); out = axes_off(bend_runs(out, ...))` up to `SETTLE_PASSES`. It moves and bends a candidate course to make it legal.
- `clear_of_field (431)`, `axes_off (303)`, `bend_at (343)`, `bend_runs (369)` | P2 | Components of the repair: push segments out of the field, tilt axis-aligned segments, insert bends.
- `feed_brook (517)` | P2 / P3 / P4 | Each candidate is repaired by `settle_course`, then kept only `if not brook_violations(course, plan, sluice, ditches): return course`. After bearings and routes round the field fail, `raise BrookRefused(... "keeps every rule of the brook")`.
- `brook_skirt (90)` | P4 (relax) | "A crop ring reaching within one skirt of the fan's head is left out of the profile." "Crop clearance wins... never below `floor`."
- KEPT: `brook_violations (262)` ("empty for a course the placer may take"). Also called from `sink.py:448`.
- `approach_legs (473)` | KEPT: returns None where the chord crosses the envelope.

**brook_course.py**
- `unfold (154)` | P2 | Deletes vertices turning past `limit_deg`.
- `_off_the_axes (313)` | P2 | Nudges the far end of an axis-aligned segment by up to 11 px.
- `exit_legs (40)` | construction (guaranteed off-canvas mouth, W07).

**brook_rules.py**
- KEPT: `level_runs_along_frame (62)`, `axis_segments (140)`, `crosses_mid_run (190)`, plus `monotone_down`, `course_enters`, `ends_off_canvas`, `reserved_box`. All are single predicates shared by placer and tests.

**fit.py**
- `fit_field (45)` | P3 + P4 | Carve, then `_finish_first_admissible` judges the finished net. If none is admissible: `raise FieldRefused(... "no fan at any of ... aspects is legal ... and lands ... acres within ...")`. It widens the aspect search first (more room).
- `_finish_first_admissible (126)` | P3 | `net = finish_comb(carve); if fan_admissible(net, ...): return net`. A finished-net check inside the run.
- `fan_legal (159)`, `tail_dangles (357)`, `flanks_commanded (395)`, `net_bends_acutely (425)` | P3 | Finished-net legality, asked of the finished net rather than before placing.
- KEPT: `field_acres_in_band (151)` — "the ONE predicate the fit decides by and a test reads".

**polder.py**
- `fit_polder (334)` | P3 + P4 | Candidates are cleaned and measured on the drawn block: `clean_polder_parcels(best); ... if polder_acres_in_band(final, ...): return best`. Failure: `raise ValueError(f"no polder grid of ... lands ... acres within ...")`.
- `_polder_candidate (437)` | P4 (relax) | `for wander in (0.5, 0.4, 0.3, 0.2, 0.12):` — the edge wander is "walked down until the block reads as one block". The rule is relaxed until the bbox fill reaches 0.86.
- `gaps_for_courses (144)` | P2 | `while hits := course_breaches(...): out.append(hits[0])`. Dike gaps are added wherever a course still breaches the crest, after the dike was gapped once.
- `inlet_to_rim (119)` | P2 | Moves the feeder's last point.
- KEPT: `walk_pond_uphill (57)` — "a solved seat, not a bounded walk", asks `reservoir_clear_of_crop (33)` and `reservoir_uphill_of_field (48)` at each step. `dike_gaps_at_channels (82)` is also shape-checked before drawing.
- KEPT: `polder_acres_in_band (428)`.

### waterfields/

**settle.py**
- `settle_cells (272)`, `Fabric.merge (253)`, `takes (144)` | P2 + P4 | The partition is cut first, then `verdict()` judges each cell. Failing cells merge into a neighbor; "what neither makes lawful is LEFT BARE". `scraps = [fab.alive[k] for k, v in fab.fails.items() if v]`.
- `verdict (64)` | KEPT-style: `ring_violations(ring, ctx)` plus the toe test, asked of each cut cell.

**seams/close.py**
- `hold_ring_rules (62)` | P2 + P3 + P4 | Its one caller is `settlement/fields/features.py:155` (the grave cut). Splits, welds or leaves bare a ring that "breaks one": `bad = [k for k in ... if held_faults(...)]`.
- `blunt_points (123)`, `_weld_within_rules (174)`, `_split_steps (205)` | P2 | Cut off points, weld scraps, split staircases.
- `held_faults (156)` | P3 / TWICE | `ring_violations` plus the placer's lines (see TWICE).

**ring_rules.py**
- `ring_violations (472)` | rule set asked after the cut (by `settle.verdict` and `held_faults`) and by the finished-map gate. The module's own account: refused "any candidate for which `ring_violations` is non-empty". In the run it is asked of cells already cut, so P1 for the cut itself.
- `narrow`, `dart` | recorded, not asked ("recorded rules, not enforced").
- `simple_outline (165)` | P2 | `make_valid` drops the fold from a ring after it was built.
- KEPT: `crosses_pond_rim (383)`, `under_island (394)`.

**furrows.py**
- `settle_tract_seams (126)` | P2 + P4 | Turns whole tracts after the hem is laid, or merges: `ps[i]["tract"], ps[i]["theta"] = ps[host]["tract"], ps[host]["theta"]`. Called from `hem.py:102`.
- `tract_seams (94)` | P1 | The finished-map rule, read only by tests.
- `tract_ways (40)` | KEPT: construction-time "a tract that would come out within `TRACT_SEAM_MIN_RAD` of the one before takes the other way".

**twins.py**
- `drop_twin_deliveries (130)` | P2 | `del channels[k]`: deliveries already drawn are deleted afterwards (called at `comb.py:759`). The module docstring says the predicate is asked "by the comb as it draws"; in practice it runs on `channels[first:]` after `_comb_canal_pieces` has appended them.
- `twin_run_ft (68)`, `twins` | one predicate.

**trunks.py**
- `anchor_trunk_ends (123)` | P2 + P4 | Clips unanchored ends back; "A trunk no point of which is anchored... is dropped": `drop.append(k)` then `del channels[k]`. Called at `comb.py:209`.
- `drop_stub_pieces (167)` | P2 + P4 | Deletes sub-8 px remainders after the canal was cut (`comb.py:192`).
- `outfall_rise (71)`, `sharpest_turn (81)`, `end_anchored (95)` | P1 (first two), KEPT (`end_anchored` is what `anchor_trunk_ends` asks).

**tint.py**
- `judge_tint (108)` | P2 | A flooded plot that is a needle or tapers "goes back to rice green"; if none survives, the most basin-like plot is tinted. This edits the fill of an already-cut plot.

**polder.py (waterfields)**
- `_plots_clear_of_channels (666)` | P2 | Re-projects parcel outlines off the ditch after the lattice is laid.
- `unpoint_parcels (916)` | P2 + P4 | Re-hems pointed rings, then drops them: `plots[:] = kept`. "A ring left pointed... is dropped from the crop and left as bank ground".
- `_polder_close (812)` | P2 | Pops trailing acute channel stubs; lifts vertices with `hem_to_bank`.
- `clean_polder_parcels (864)` | P2 | Re-runs the cleanup on the winner and re-measures acreage.
- `end_on_centerline (875)` | KEPT, a shared predicate (the "toe snap" at 183 moves ends, then this tests them).

**banks.py**
- `hem_to_bank (284)`, `hem_rings_to_bank (353)` | P2 | A terminal pass: "it enforces one physical invariant on geometry those engines have finished with". Also the shared `drain_bank_clearance (73)` predicate (KEPT) is what it reads.
- `round_channel_joints (676)` | P2 | Moves already-built channel vertices.
- KEPT: `drain_bank_clearance (73)`, `supply_bank_clearance (113)`, `floor_overhang (254)` ("ONE predicate, shared by the comb builder's envelope trim and by the gate"), `hem_on_paddy (648)`.

**comb.py**
- `_comb_envelope (762)` | P2 | Pulls envelope vertices "back up-fall onto" the drain line after the ring is built.

**carve.py**
- `_dry_fields (62)` | P4 | Drops cells: `if any(p[0] < 12 ...): continue`, `if blocked(cx, cy): continue`, `if _quad_in_berm(quad): continue`. "Dropping the cell keeps the shared-seam invariant". The test is asked of the candidate cell before it is appended.

**partition.py**
- `keep_far (334)`, `keep_rows (320)` | P4 | Bund pieces "wholly within `lim` of the ground's edge" are not cut.
- `recut (359)` | P2 | A cell over `RECUT_OVER` design cells is recut after `polygonize`.

## C. TWICE: a rule judged at two places

- **Fixture inside a grove band.**
  - `settlement/homestead_parts/grove_rules.py:fixtures_on_groves (154)` / `fixture_on_band (169)`; used by `hamletgen/homesteads/sties.py:sty_seat (97)`.
  - `settlement/rolling/fit.py:_fixtures_in_bands` (~571) with `fit_index.py:recorded_box (46)`, which re-implements the box "as `fixtures_on_groves` reads its record".
  - `hamletgen/homesteads/fixtures.py:_flexible_clear (462)`: an inline axis-aligned overlap with no `rot`. Its comment says "the same boxes".
  - `hamletgen/homesteads/persimmon_reseat.py:persimmon_for (35)`: another inline neighbor-grove overlap with no `rot`.
- **A way does not cross a grove.** `groves_crossed_by_lanes (102)` uses a stroked quad and `poly_gap`. `hamletgen/ways/serve.py` (~474) uses grown `rot_rect` bands as walls for routing. Two codings.
- **Farmstead part across a stream.** `settlement/_geom/water_index.py:crosses_a_stream (65)` is the single predicate, and its docstring says a third copy was folded in. `tools/cohort_audit.py:parts_across_brook` still has its own `_cross` / `_o` line-intersection test.
- **Ring rules at two margins.**
  - `ring_rules.ring_violations (472)` is the gate's line: needle under 15 degrees, area at 0.20 of the cell.
  - `seams/close.py:held_faults (156)` adds the placer's own lines: `pointed_ring` at 25 degrees, 0.25 cell, `is_chevron`.
  - `settle.verdict (64)` adds the "toe" test: `_TOE_MIN_THICKNESS`, `_TOE_MIN_AREA`, `pointed_ring`, `is_chevron`.
  - `tint._needle`/`judge_tint` (45, 108) and `polder.unpoint_parcels` (916, `POLDER_APEX_DEG = 25`) each code the needle again.
- **Hairpin / acute turn.** `hamletgen/water/fit.py:net_bends_acutely (425)` (cosine < 0) and `waterfields/polder.py:_polder_close (812)` (`_ang >= 90.0` inline) and `trunks.sharpest_turn (81)` (`SHARP_TURN_DEG = 100`).
- **Screen-axis segment.** `brook_rules.py:axis_segments (140)`; `brook.py:axes_off (303)` and `brook_course.py:_off_the_axes (313)` each hold their own `min(deg, 90.0 - deg) < eps` test.
- **Dike crest crossing.** `hamletgen/water/polder.py:dike_gaps_at_channels (82)` (ring-edge `segments_cross` with a 30 ft merge) and `gaps_for_courses (144)` (via `settlement/land/dikes.py:course_breaches`).
- **Seam between dry tracts.** `furrows.py:tract_ways (40)` uses `TRACT_SEAM_MIN_RAD = 0.35`. `settle_tract_seams (126)` uses its floors. `tract_seams (94)` uses `SEAM_READS_RAD = 0.10`. One rule, three thresholds in three functions.
- **Within reach of a well.**
  - `row_rules.water_rules (152)` uses `WATER_REACH_FT` for the shared-well case.
  - `wells.dry_households (735)` and the `served` calculations in `wells.grove_water (299)` code the same distance test.
  - `wells.record_over_ten (791)` re-codes `most_served_after (142)` (`WELL_SERVES_MAX`).
- **Copse keep-outs.** `wood_share.py:copse_keepouts (84)` / `ground_blocks (152)` mirror `grove_fill.py:grove_blocks (27)` ("The figures are `village_grove`'s; the placer holds them `BAR_MARGIN_PX` stricter").
- **Persimmon vs crowns.** `persimmon_reseat.give_way (101)` removes crowns after the fact. `groves.py:_draw_grove (437)` checks the same thing with `_trees` before drawing a crown.
- **Dispersed seat refusal.** `growth.seat_refused (191)` repeats the placer's first tests ("Its own questions, asked as it asks them").
- **Door reach.** `rows.py:door_clear (288)` uses `FOOTPATH_DOOR_OUT_FT` (12 ft). `row_rules.py:row_rules` uses `serve.front_door` (`DOOR_STEP_FT`) and `street_arrives`. The module comment records the 8 ft vs 12 ft difference.

## D. KEPT summary

- `homesteads/sties.py:sty_seat` - `s.admits(...) and not any(fixture_on_band(rec, g) ...)`.
- `homesteads/fixtures.py:under_a_lane` / `across_the_brook` - `over_a_fixture` / `crosses_a_stream`.
- `homesteads/bamboo.py:strip_refused` - footprints, belt, parts, copse seats, sun, stream, lane.
- `homesteads/growth.py:keeps_every_gap` / `keeps_its_distance` / `seat_refused` - gap and ground tests before the layout.
- `homesteads/rows.py:frame_refused` / `holding_clear` / `door_clear` - frame, holding and door ground.
- `homesteads/farm_water.py:farm_channel` - `crosses_other_water` before drawing.
- `homesteads/wells.py:seat_wells` - `s.well_at`, spacing, crop-past, wood-floor disc.
- `homesteads/boundary.py` / `region.py` - `rect_refused`, `refuses`, `offer`.
- `homestead_parts/wood_share.py:WoodShares.seat_barred`, `share` - reservation test per seat.
- `homestead_parts/stands.py:village_grove._seat` - rejection chain per clump.
- `homestead_parts/fixture_seats.py:lay_fixtures` - `FixtureUnlaid` refuses the bundle.
- `homestead_parts/tree_shade.py:crown_shades` - one predicate asked by placers.
- `homestead_parts/bamboo_keepout.py:stand_spares_seats`.
- `hamletgen/water/brook.py:brook_violations` (candidate courses).
- `hamletgen/water/brook_rules.py` - level / ruled / axis / enters / crosses / monotone.
- `hamletgen/water/fit.py:field_acres_in_band`.
- `hamletgen/water/polder.py:reservoir_clear_of_crop`, `reservoir_uphill_of_field`, `polder_acres_in_band`.
- `waterfields/banks.py:drain_bank_clearance`, `supply_bank_clearance`, `floor_overhang`, `hem_on_paddy`.
- `waterfields/frame.py:_drain_bank` - hems onto the bank by construction.
- `waterfields/trunks.py:end_anchored`.
- `waterfields/polder.py:end_on_centerline`.
- `waterfields/furrows.py:tract_ways` - construction-time seam turn.
