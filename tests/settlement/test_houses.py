"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import json
import math
import random

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement
from tests._scope import full_or
from tests.settlement._builders import _crop_settlement, _nuc_village, _pos_where, _town, _village


# --- farmsteads(): the deferred draw giving EVERY farmhouse a yard (nudge / drop / bound branches) -----
def test_try_place_defers_the_farmhouse():
    # try_place reserves + records the farmhouse but does NOT draw it yet (farmsteads draws it with its yard)
    s = _town()
    assert s.try_place(500, 500, "plain")
    assert len(s.M["houses"]) == 1 and len(s.M["threshing_yards"]) == 0  # deferred, no yard yet


def test_farmsteads_yard_on_the_sunny_south_front():
    s = _town()
    assert s.try_place(500, 500, "plain")
    assert s.farmsteads() == 1
    y = s.M["threshing_yards"][0]
    assert y["of"] == [500, 500] and y["y"] > 500  # the yard sits on the house's south/front (+y) side


# --- dooryard kitchen garden: every farmstead also gets a saien on a sunny side --------------
def test_farmsteads_garden_on_a_sunny_side():
    s = _town()
    assert s.try_place(500, 500, "plain")
    assert s.farmsteads() == 1
    gd = s.M["gardens"][0]
    assert gd["of"] == [500, 500] and gd["y"] >= 500 - 5  # never the shady north back


def test_dry_polys_block_a_footprint_margin_not_just_the_center():
    # dry crop plots are FOOTPRINT-aware no-build cropland: block_polys test only a candidate's
    # CENTER, which let a house centered just off a hem strip stand half its footprint on the crop
    s = _crop_settlement()
    s.dry_polys.append([(300, 300), (500, 300), (500, 380), (300, 380)])
    assert not s._fits(400, 340, 20, 14)  # centered inside the strip -> blocked
    assert not s._fits(510, 340, 20, 14)  # centered 10px OUTSIDE: the footprint would overlap -> still blocked
    assert s._fits(560, 340, 20, 14)  # well clear of the 12px margin -> fits


def test_a_keepout_index_sees_a_registry_mutated_after_its_first_query():
    """The behavioral half of the same rule, at the level a map would notice: query, MUTATE, query
    again. A stale index answers the second query from the first query's world - which is how
    Minami and Nagahara lost every garden on 2026-08-03 - so this walks a point in and out of a
    keep-out by appending and clearing."""
    s = _crop_settlement()
    box = [(480.0, 480.0), (520.0, 480.0), (520.0, 520.0), (480.0, 520.0)]
    assert not s._in_blocked(500, 500)  # builds and caches the index over an empty registry
    s.block_polys.append(box)
    assert s._in_blocked(500, 500), "the index did not see an appended keep-out"
    s.block_polys.clear()
    assert not s._in_blocked(500, 500), "the index did not see the registry emptied"
    # and a corridor, the other indexed registry
    assert not s._near_corridor(300, 300)
    s.corridors.append(([(200.0, 300.0), (400.0, 300.0)], 20.0))
    assert s._near_corridor(300, 300), "the corridor index did not see an appended corridor"


def test_indexed_grid_falls_back_when_a_registry_is_rebound_to_a_plain_list():
    # farm_wells swaps field_polys out and back; anything rebinding a registry to a PLAIN list must
    # still get correct answers, just uncached - the fallback that makes this safe to adopt
    s = _crop_settlement()
    s.block_polys = [[(480.0, 480.0), (520.0, 480.0), (520.0, 520.0), (480.0, 520.0)]]
    assert not isinstance(s.block_polys, settlement.Indexed)
    assert s._in_blocked(500, 500)
    assert not s._in_blocked(300, 300)


def test_garden_beds_undivided_is_the_common_case():
    s = _nuc_village()
    x, y = _pos_where(lambda x, y: Settlement._hjit(x, y, 8.0) >= 0.26)
    beds = s._garden_beds(x, y, 23, 14, x + 20, y, 20, 20, "E", 3)
    assert beds == [(x + 20, y, 20, 20)]  # one undivided plot


def test_garden_beds_opposite_flank_puts_the_house_between_two_beds():
    s = _nuc_village()
    x, y = _pos_where(lambda x, y: Settlement._hjit(x, y, 8.0) < 0.26 and Settlement._hjit(x, y, 9.0) < 0.5)
    beds = s._garden_beds(x, y, 23, 14, x + 20, y, 20, 20, "E", 3)
    assert len(beds) == 2 and min(b[0] for b in beds) < x < max(b[0] for b in beds)  # flanking E and W


def test_garden_beds_stacked_when_same_side_south_garden():
    s = _nuc_village()
    x, y = _pos_where(lambda x, y: Settlement._hjit(x, y, 8.0) < 0.26 and Settlement._hjit(x, y, 9.0) >= 0.5 and Settlement._hjit(x, y, 10.0) < 0.5)
    beds = s._garden_beds(x, y, 23, 14, x, y + 30, 20, 20, "SE", 3)  # a SOUTH garden -> may stack above/below
    assert len(beds) == 2 and beds[0][0] == beds[1][0] and beds[0][1] != beds[1][1]  # same x, different y


def test_garden_beds_side_by_side_when_same_side_not_stacked():
    s = _nuc_village()
    x, y = _pos_where(lambda x, y: Settlement._hjit(x, y, 8.0) < 0.26 and Settlement._hjit(x, y, 9.0) >= 0.5 and Settlement._hjit(x, y, 10.0) >= 0.5)
    beds = s._garden_beds(x, y, 23, 14, x, y + 30, 20, 20, "SE", 3)  # not stacked -> side by side
    assert len(beds) == 2 and beds[0][1] == beds[1][1] and beds[0][0] != beds[1][0]  # same y, different x


def test_garden_beds_too_narrow_falls_back_to_one_bed():
    s = _nuc_village()
    x, y = _pos_where(lambda x, y: Settlement._hjit(x, y, 8.0) < 0.26)  # a split is WANTED
    beds = s._garden_beds(x, y, 23, 14, x, y + 12, 8, 8, "SE", 3)  # ... but the plot is too small to split
    assert beds == [(x, y + 12, 8, 8)]


def test_bundle_geom_nucleated_records_a_gardens_list_spanning_the_bbox():
    s = _nuc_village()
    x, y = _pos_where(lambda x, y: Settlement._hjit(x, y, 8.0) < 0.26 and Settlement._hjit(x, y, 9.0) < 0.5)
    geom = s._bundle_geom(x, y, 46, 28, "E")  # a big house so the flank split clears its gate
    assert len(geom["gardens"]) == 2
    bx, by, bw, bh = geom["bbox"]
    for gx, _gy, gw, _gh in geom["gardens"]:  # every bed lies inside the bundle bbox
        assert bx - bw / 2 - 1 <= gx - gw / 2 and gx + gw / 2 <= bx + bw / 2 + 1


def test_bundle_parts_turn_about_the_house_center_with_its_rake():
    # GM 2026-09-26: a yard turned only about its own center slid up to 3 ft along the house front. The yard
    # stays centered on the house's own axis at the gap it was laid at - in the HOUSE's frame, not the map's.
    s = _nuc_village()
    x, y = _pos_where(lambda x, y: abs(s._house_rot(x, y)) > 3.0)
    geom = s._bundle_geom(x, y, 46, 28, "E", shed=True)
    th = math.radians(s._house_rot(x, y))
    for part, sign in ((geom["yard"], 1.0), (geom["shed"], -1.0)):
        dx, dy = part[0] - x, part[1] - y
        along, across = dx * math.cos(th) + dy * math.sin(th), -dx * math.sin(th) + dy * math.cos(th)
        assert abs(along) < 1e-6 and across * sign > 0, "the part sits on the house's own axis, on its side of the house"
    gx, gy = geom["garden"][0] - x, geom["garden"][1] - y
    assert abs(-gx * math.sin(th) + gy * math.cos(th)) < 1e-6, "an east-wall bed stays level with the house in its frame"
    bx, by, bw, bh = geom["bbox"]
    assert bx - bw / 2 <= geom["yard"][0] - geom["yard"][2] / 2 and geom["yard"][1] + geom["yard"][3] / 2 <= by + bh / 2 + 1e-6


def test_nucleated_bundle_returns_none_when_boxed_in():
    # a bound admitting the seed but no room for even the compact house+yard+garden bundle -> no placement
    s = _nuc_village()
    s.bound = [(495, 495), (505, 495), (505, 505), (495, 505)]
    assert s.try_place(500, 500, "plain") is False


def test_fits_steers_off_a_grove():
    # groves are out of `placed` (so they may merge), but `_fits` still keeps the wells off them
    s = Settlement(1000, 1000, seed=1)
    s.grove_rects.append((500, 500, 40, 40))
    assert s._fits(505, 505, 20, 20) is False


def test_abandoned_ruin_draws_as_a_lone_house_and_big_glyph_renders():
    # the geom-less lone-house path in _farmsteads_bundle now serves ONLY abandoned ruins - the dispersed
    # headman that used to share it gets a full bundle since 2026-07-21 (the Hikari fix). The ruin must
    # survive farmsteads() as a bare house (no yard/garden/grove), riding through _relax_gardens_south's
    # geom-less skip. The "big" minka glyph (storeroom wing) renders via a direct draw.
    s = Settlement(800, 800, seed=5)
    s.meta(name="Ruin", scale="village", ftpx=2, toscale=True)
    assert s.try_place(400, 400, "abandoned")
    assert s.try_place(560, 400, "plain")  # a bundle placed AFTER the ruin: the shading scan skips the geom-less rec
    assert s.farmsteads() == 2
    assert s.M["houses"][0]["kind"] == "abandoned"
    assert len(s.M["threshing_yards"]) == 1 and len(s.M["gardens"]) == 1  # the plain bundle's, not the ruin's
    s.house(200, 200, 46, 28, "big", 0)  # the big-minka glyph branch (the storeroom wing)


def test_a_farmstead_belt_is_immune_to_an_upstream_change_in_draw_count():
    # THE RATCHET for the whole positional-randomness discipline (GM 2026-08-08). A caption resize
    # in a city's temple quarter re-rolled farmland 700 px away and dropped a farm shed on a garden,
    # because a farmhouse's rake and its storehouse were STREAM draws: consume one more random
    # number anywhere upstream and every homestead in the map re-rolled. They are position-seeded
    # now (the convention _hjit's own docstring describes), so this holds.
    def belt(perturb):
        s = _town()
        for _ in range(perturb):
            random.random()
        for x in (400, 500, 600, 700, 800):
            s.try_place(x, 500, "plain")
        s.farmsteads()
        return {k: json.dumps(s.M[k], sort_keys=True) for k in ("houses", "gardens", "threshing_yards", "farm_sheds")}

    a, b = belt(0), belt(1)
    assert a == b, f"an upstream draw re-rolled: {[k for k in a if a[k] != b[k]]}"


# ---- house: the ABANDONED-ruin glyph -------------------------------------------------------
def test_house_abandoned_draws_the_collapsed_roof_glyph():
    s = _village()
    s.house(300, 300, 46, 28, kind="abandoned")
    svg = "".join(s.out)
    assert '#6E6452' in svg  # the collapsed-roof debris polygon
    assert 'stroke-dasharray="5,3"' in svg  # the derelict outline dash


# ---- try_place: the LONE ABANDONED ruin (no homestead bundle) ------------------------------
def test_try_place_abandoned_places_a_lone_ruin_without_a_bundle():
    s = _nuc_village()  # a to-scale village; the west half (x < 640) is open ground
    assert s.try_place(300, 300, "abandoned") is True
    ruin = [h for h in s.M["houses"] if h["kind"] == "abandoned"]
    assert len(ruin) == 1 and ruin[0]["shed"] is False  # a lone derelict, no kura


# ---- try_place: an abandoned ruin that does not FIT is rejected ----------------------------
def test_try_place_abandoned_rejects_a_ruin_off_the_canvas_edge():
    s = _nuc_village()
    assert s.try_place(20, 300, "abandoned") is False  # x < 55 -> _fits fails, no ruin placed
    assert not [h for h in s.M["houses"] if h["kind"] == "abandoned"]


# ---- cluster_shape knob: shape-aware seed generation (feature 005, US1) -------------------------


def test_cluster_seeds_shapes_generate_and_record():
    import random as _r

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="Cs", scale="village")
    for shape in ("round", "elongated", "crescent", "split"):
        pts = s.cluster_seeds(shape, 500, 700, 150, 220, 60, _r.Random(4))
        assert len(pts) == 60
        assert s.M["meta"]["cluster_shape"] == shape

    # elongated is taller than wide (stretched along the margin); round is broader across
    rnd = s.cluster_seeds("round", 500, 700, 150, 220, 200, _r.Random(9))
    elo = s.cluster_seeds("elongated", 500, 700, 150, 220, 200, _r.Random(9))
    rw = max(p[0] for p in rnd) - min(p[0] for p in rnd)
    ew = max(p[0] for p in elo) - min(p[0] for p in elo)
    assert ew < rw  # elongated is narrower across the margin

    # split forms two lateral lobes -> the x-distribution is bimodal (few points near the center line)
    spl = s.cluster_seeds("split", 500, 700, 150, 220, 300, _r.Random(9))
    near_center = sum(1 for p in spl if abs(p[0] - 500) < 30)
    assert near_center < 0.15 * len(spl)  # a gap between the two sub-hamlets


def test_cluster_anchor_places_each_position_on_the_right_dry_margin():
    # cluster_position resolves against the field bbox + down_deg into an anchor off the paddy. Check each
    # value lands on the expected side of the field center relative to the fall (down_deg=90 -> downhill = +y).
    import math as m

    s = Settlement(2000, 2000, seed=1)
    s.meta(name="Ca", scale="village")
    fb = (600.0, 400.0, 1400.0, 1200.0)  # a field, center (1000, 800)
    fcx, fcy = 1000.0, 800.0
    dd = 90.0
    dx, dy = m.cos(m.radians(dd)), m.sin(m.radians(dd))  # (0, 1)
    ux, uy = -dy, dx  # (-1, 0)

    def along(pos):  # signed along-slope offset of the anchor (>0 = downhill of center)
        cx, cy, _ex, _ey = s.cluster_anchor(pos, fb, dd)
        return (cx - fcx) * dx + (cy - fcy) * dy

    def lateral(pos):
        cx, cy, _ex, _ey = s.cluster_anchor(pos, fb, dd)
        return (cx - fcx) * ux + (cy - fcy) * uy

    assert along("high_margin") < -400 and abs(lateral("high_margin")) < 30  # uphill, centered
    assert along("valley_head") < -400 and lateral("valley_head") != lateral("mid_margin")  # both high, opposite flanks
    assert along("mid_margin") < -400
    assert abs(lateral("flank")) > 400 and abs(along("flank")) < 30  # off to a cross-slope side
    assert along("valley_mouth") > 0 and abs(lateral("valley_mouth")) > 400  # low end, but on the dry shoulder
    assert along("on_rise") < -300  # a high-corner knoll
    # the anchor center sits OFF the paddy footprint (never inside the field bbox) for the margin positions
    for pos in ("high_margin", "valley_head", "mid_margin", "flank", "valley_mouth"):
        cx, cy, _ex, _ey = s.cluster_anchor(pos, fb, dd)
        assert not (fb[0] < cx < fb[2] and fb[1] < cy < fb[3])
    # extents are positive and the lateral (along-margin) axis is the broader one for a top margin (runs E-W)
    _cx, _cy, ex, ey = s.cluster_anchor("high_margin", fb, dd)
    assert ex > ey > 0
    with pytest.raises(ValueError):
        s.cluster_anchor("nowhere", fb, dd)


def test_plot_texture_drives_build_comb_grain():
    from tests.waterfields._builders import lay_comb

    s = Settlement(1400, 1800, seed=1)
    s.meta(name="Pt", scale="village", ftpx=2)  # ftpx>=2 -> the real-feet calibration branch (the ft/px=1 hamlet legacy branch is covered by honda/shimizu)
    # small_irregular vs large_block must produce visibly different plot counts on the SAME field
    a_small, step_small = s.plot_texture("small_irregular", "organic")
    a_large, _step_large = s.plot_texture("large_block", "organic")
    assert a_small < a_large  # smaller plot_across = smaller paddies
    # ONE fan each (T20, GM 2026-08-26): the property is "smaller plot_across -> more plots on the same field", which any fan shows; two 5-fan combs cost 4 s for it
    net_small = lay_comb(900, 1100, (360, 160), full_or(1, 3), down_deg=90, field_fall=500, offtakes_a=(0.5,), offtakes_b=(), plot_across=a_small, row_step=step_small)
    net_large = lay_comb(900, 1100, (360, 160), full_or(1, 3), down_deg=90, field_fall=500, offtakes_a=(0.5,), offtakes_b=(), plot_across=a_large)
    assert len(net_small["plots"]) > len(net_large["plots"])  # small paddies -> more plots
    # grid tightens the row-step spread vs organic
    _a, org = s.plot_texture("medium", "organic")
    _a2, grid = s.plot_texture("medium", "grid")
    assert (grid[1] - grid[0]) < (org[1] - org[0])
    # the knobs are recorded
    assert s.M["meta"]["plot_size"] == "medium" and s.M["meta"]["plot_regularity"] == "grid"
    for bad in (("huge", "organic"), ("medium", "checkerboard")):
        with pytest.raises(ValueError):
            s.plot_texture(*bad)


def test_cluster_seeds_record_false_and_bad_shape():
    import random as _r

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="Cs2", scale="village")
    s.cluster_seeds("round", 500, 500, 100, 100, 5, _r.Random(1), record=False)
    assert "cluster_shape" not in s.M["meta"]  # record=False leaves meta untouched
    with pytest.raises(ValueError):
        s.cluster_seeds("spiral", 500, 500, 100, 100, 5, _r.Random(1))


def test_hard_polys_footprint_test_refuses_what_the_center_test_allowed():
    """The split that fixes center-vs-footprint: `hard_polys` (crop, pond, bog, a field's own
    ditches) is tested against the WHOLE footprint, while `block_polys` keeps the center test its
    soft reservations - caption bands, aprons, fence standoffs - were tuned for."""
    s = _town()
    plot = [(500.0, 500.0), (600.0, 500.0), (600.0, 600.0), (500.0, 600.0)]
    s.block_polys.append(plot)
    assert s._fits(490, 550, 46, 28)  # center (490) is outside the plot, so the center test allows it...
    s.hard_polys.append(plot)
    assert not s._fits(490, 550, 46, 28)  # ...but the footprint runs to 513, well inside it
    assert s._fits(300, 300, 46, 28)  # well clear, still fine


def test_the_way_a_row_FRONTS_does_not_refuse_it_its_own_tread():
    """`skip` means the same thing to the tread test as it does to `_near_corridor`, and for the same
    reason: a frontage row lines the way it fronts, so that way's own surface must not be what
    refuses it. Matched by GEOMETRY as well as identity - a frontage written as a fresh two-point
    list over a sub-stretch is the shape that once cost the pool two thirds of its shop frontage."""
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="Front", scale="hamlet", ftpx=1, toscale=True, households=12)
    way = [[200.0, 700.0], [1200.0, 700.0]]
    s.lane(way, width=16, clearance=22)
    x, y, w, h = 700.0, 706.0, 62.0, 56.0  # a footprint squarely over the tread
    assert s._on_a_tread(x, y, w, h), "the fixture must actually sit on the tread, or it proves nothing"
    assert not s._on_a_tread(x, y, w, h, skip=way), "the very polyline registered must be skipped"
    assert not s._on_a_tread(x, y, w, h, skip=[[400.0, 700.0], [900.0, 700.0]]), "a SUB-STRETCH of the way is the same ground"
    assert not s._on_a_tread(x, y, w, h, skip=[[[400.0, 700.0], [900.0, 700.0]]]), "a LIST of fronted stretches is accepted too"
    assert not s._on_a_tread(x, y, w, h, skip=[[100.0, 700.0], [1300.0, 700.0]]), "a stretch LONGER than the way is the same ground too"
    assert s._on_a_tread(x, y, w, h, skip=[[700.0, 200.0], [700.0, 1200.0]]), "a way merely CROSSING must still refuse"
    assert s._on_a_tread(x, y, w, h, skip=[[700.0, 700.0]]), "a degenerate one-point skip excuses nothing"


def test_the_tread_test_measures_the_RAKE_a_house_will_be_drawn_at():
    """A farmhouse is drawn raked by `_house_rot` (+/-5 deg), and the rake pushes a corner OUTSIDE
    the axis-aligned rect the placer clears - up to 2.56 px, measured across the pool. `_on_a_tread`
    used to pass 0.0 unconditionally, so its "exact" footprint test measured a square-on rect and
    the map then drew a raked one (feature 121).

    THIS TEST HAS TEETH BY CONSTRUCTION: the seat below is clear of the tread when measured
    square-on and ON it once raked, so an implementation that ignores `rot` fails the third
    assertion. That is the whole defect, in one fixture."""
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="Rake", scale="hamlet", ftpx=1, toscale=True, households=12)
    s.lane([[200.0, 700.0], [1200.0, 700.0]], width=16, clearance=22)
    x, y, w, h = 700.0, 728.5, 62.0, 30.0  # a LONG minka (the 1.35x length jitter), just clear square-on (of the 4 ft TREAD_WALL_FT, feature 294)
    assert not s._on_a_tread(x, y, w, h), "square-on, this seat clears the tread - so the rake is the only thing under test"
    assert not s._on_a_tread(x, y, w, h, rot=0.0), "an explicit zero rake must agree with the default"
    assert s._on_a_tread(x, y, w, h, rot=-5.0), "RAKED, the same seat puts a corner on the tread and must be refused"


def test_the_drawn_rake_has_ONE_definition_shared_by_placer_and_renderer():
    """`_house_rot` exists so the placer cannot disagree with the renderer about the rake. The
    expression was written out at both farmhouse record sites and nowhere in the bundle placer,
    which is how the bundle path came to clear an axis-aligned rect for a raked house."""
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="Rake", scale="hamlet", ftpx=1, toscale=True, households=12)
    for cx, cy in ((100.0, 200.0), (713.5, 918.25), (1200.0, 40.0)):
        assert s._house_rot(cx, cy) == s._hjit(cx, cy, 11.0) * 10.0 - 5.0
        assert -5.0 <= s._house_rot(cx, cy) < 5.0, "the rake stays inside the +/-5 deg band the glyph is drawn in"
    assert s._house_rot(100.0, 200.0) == s._house_rot(100.0, 200.0), "position-seeded: same seat, same rake, no stream draw"


def test_a_house_is_refused_a_seat_whose_DRAWN_corner_lands_on_a_lane():
    """THE RATCHET for the engine's "placement tests a different footprint than the one drawn" debt,
    at the lane (this skill's CLAUDE.md, "CENTER vs FOOTPRINT" item 3).

    `_near_corridor` measures a candidate's CENTRE against a way's soft clearance, so a homestead
    whose drawn steading is wider than the placer assumed could stand a legal distance off by its
    center and still put a corner on the road - which `houses_clear_of_lanes` reports as a house in
    the lane. The tread is now tested against the FOOTPRINT, so the same center is legal for a
    narrow building and refused for a wide one. Both halves are asserted: a test that refuses
    everything decides nothing."""
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="Tread", scale="hamlet", ftpx=1, toscale=True, households=12)
    s.lane([[200.0, 700.0], [1200.0, 700.0]], width=16, clearance=22)
    cx, cy = 700.0, 734.0  # 34 px off the centerline: clear of the 22 px clearance by its center
    assert s._fits(cx, cy, 46.0, 28.0), "the base footprint stands clear of the lane and must be allowed"
    assert not s._fits(cx, cy, 62.0, 56.0), "the DRAWN footprint puts a corner on the tread and must be refused"


def test_fits_measures_drawn_extents_when_both_are_known() -> None:
    """Feature 146: `_fits` prefers the DRAWN extents of the candidate and its neighbour when both are
    recorded (a raked roof's real reach), and falls back to the half-diagonal circle when they are not."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="F", scale="hamlet", ftpx=1)
    s.placed.append((500.0, 500.0, 60.0, 30.0, None, None, 60.0, 30.0))
    near = s._fits(548.0, 500.0, 60.0, 30.0)
    far = s._fits(700.0, 500.0, 60.0, 30.0)
    assert near is False, "overlapping drawn extents"
    assert far is True


def test_fits_measures_the_exact_box_when_both_sides_declare_what_they_draw():
    """The circumscribed circle is rotation-invariant and refuses seats nothing occupies - 38.7% of all
    refusals on a provincial city - so where BOTH the candidate and the standing feature have declared
    their drawn extent, the exact box is used instead. The candidate declares by passing `rot`."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.placed.append((500.0, 500.0, 40.0, 26.0, 40.0, 26.0))  # a standing feature that knows its rake
    assert not s._fits(510.0, 505.0, 40.0, 26.0, rot=0.0), "the boxes lap"
    assert s._fits(700.0, 700.0, 40.0, 26.0, rot=0.0), "and well clear is clear"


def test_hard_clear_from_its_box_index_equals_the_scan():
    """Feature 278 (FR-009): `_hard_clear` asks a grid of the hard polygons' boxes instead of comparing every box; over
    random footprints it answers as the scan did (restated here), and the grid is rebuilt when the hard ground grows."""
    import math
    import random

    from l7r.diagram.settlement import Settlement
    from l7r.diagram.settlement._geom import quad_hits_poly

    s = Settlement(900, 900, seed=2)
    s.meta(name="H", scale="hamlet", ftpx=1, toscale=True)
    rng = random.Random(278)

    def blob():
        cx, cy, r, n = rng.uniform(0, 900), rng.uniform(0, 900), rng.uniform(10, 120), rng.randint(4, 12)
        return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]

    def scan(x, y, w, h):
        th = math.radians(5.0)
        w0 = w
        w, h = w0 * math.cos(th) + h * math.sin(th), w0 * math.sin(th) + h * math.cos(th)
        fp = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]
        hard = s._hard_ground()
        return not any(
            quad_hits_poly(fp, hp) for hp, (hx0, hy0, hx1, hy1) in zip(hard, s._poly_bboxes(hard), strict=False) if not (x + w / 2 < hx0 or x - w / 2 > hx1 or y + h / 2 < hy0 or y - h / 2 > hy1)
        )

    for rnd in range(2):
        for _ in range(12):
            s.hard_polys.append(blob())
        clear = 0
        for _ in range(1500):
            x, y, w, h = rng.uniform(0, 900), rng.uniform(0, 900), rng.uniform(10, 60), rng.uniform(10, 40)
            want = scan(x, y, w, h)
            assert s._hard_clear(x, y, w, h) == want
            clear += want
        assert 100 < clear < 1400, f"non-vacuity, round {rnd}"


def test_the_storehouse_is_drawn_in_its_own_gray_not_the_roof_color() -> None:
    """Feature 280 (settlement-review of Sawada): in the house's roof color the storehouse read as a wing of the house."""
    from l7r.diagram.settlement import Settlement
    from l7r.diagram.settlement.houses import STOREHOUSE_GRAY

    s = Settlement(W=400, H=400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.house(200.0, 200.0, 46.0, 28.0, shed=True, shed_side="N")
    assert STOREHOUSE_GRAY in s.out[-1], "the storehouse's fill"


def test_every_corner_stands_seven_ft_off_a_narrow_lanes_middle():
    """0246 (feature 328 wave 48): "a lane's middle keeps at least 7 ft clear of a garden fence". The tread's half-width and
    `TREAD_WALL_FT` held a 3 ft footpath's corners only 5.5 ft off its middle; every corner now stands `LANE_MIDDLE_CLEAR_FT`
    off it, while a wide way still keeps its half-width and the hair."""
    from l7r.diagram.settlement.rolling.access import LANE_MIDDLE_CLEAR_FT, TREAD_WALL_FT

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="Path", scale="hamlet", ftpx=1, toscale=True, households=12)
    s.lane([[200.0, 700.0], [1200.0, 700.0]], width=3, clearance=7)
    w, h = 40.0, 20.0
    assert 1.5 + TREAD_WALL_FT < 6.0 < LANE_MIDDLE_CLEAR_FT, "the fixture's corner stands between the old reach and the page's"
    assert s._on_a_tread(700.0, 700.0 + 6.0 + h / 2, w, h), "a corner 6 ft off a footpath's middle is refused"
    assert not s._on_a_tread(700.0, 700.0 + 7.5 + h / 2, w, h), "and 7.5 ft off it is clear"
    s.lane([[200.0, 300.0], [1200.0, 300.0]], width=16, clearance=22)
    assert s._on_a_tread(700.0, 300.0 + 10.5 + h / 2, w, h), "a wide way keeps its half-width and the hair (8 + 3 ft)"


def test_each_wall_is_measured_whole_not_its_corners_alone():
    """385 T07 (impl-drift on `_on_a_tread`): the corners and the center alone let a footpath run square across a long house
    10 ft off its center - every corner 10 ft off the tread and the center 10 ft off it, all past the 7 ft. Each wall is
    measured whole now, so the crossing is refused; the same path 8 ft clear of the end wall is not."""
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="Across", scale="hamlet", ftpx=1, toscale=True, households=12)
    s.lane([[710.0, 500.0], [710.0, 900.0]], width=3, clearance=7)
    assert s._on_a_tread(700.0, 700.0, 40.0, 20.0), "a path square across a 40 ft house 10 ft off its center is refused"
    assert not s._on_a_tread(682.0, 700.0, 40.0, 20.0), "the same path 8 ft off the house's end wall is clear"
