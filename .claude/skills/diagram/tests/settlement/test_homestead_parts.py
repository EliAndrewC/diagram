"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

from l7r.diagram import check_village
from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement, _nuc_village, _scatter_base_points, _town


def test_village_grove_fills_an_irregular_polygon_and_records_it():
    s = _nuc_village()  # field to the EAST (x >= 640)
    poly = [(150, 350), (260, 330), (280, 640), (160, 660)]  # an irregular quad WEST of the field (open ground)
    n = s.village_grove(poly, role="windbreak")  # dense belt -> many overlapping clumps
    assert n > 0
    vg = s.M["village_groves"]
    assert len(vg) == 1 and vg[0]["role"] == "windbreak" and len(vg[0]["poly"]) == 4


def test_village_grove_over_the_paddy_draws_and_records_nothing():
    s = _nuc_village()  # field at [(640,150),(1120,150),(1120,780),(640,780)]
    poly = [(700, 250), (900, 250), (900, 450), (700, 450)]  # a footprint ENTIRELY inside the paddy
    assert s.village_grove(poly, role="copse", dense=False) == 0  # every clump skipped (on crops) -> nothing
    assert s.M["village_groves"] == []  # ... and nothing recorded


def test_village_grove_scatter_skips_houses_and_fills_the_open_gaps():
    s = _nuc_village()
    s.M["houses"] = [{"x": 300, "y": 400, "w": 46, "h": 29}]  # one house inside the scatter region
    n = s.village_grove([(200, 300), (500, 300), (500, 500), (200, 500)], role="copse", dense=False)
    assert n >= 1  # bamboo/fruit clumps settle into the gaps
    assert s.M["village_groves"][0]["role"] == "copse"


def test_village_grove_skips_clumps_on_a_lane():
    s = _nuc_village()
    s.M["lanes"] = [{"pts": [[300, 300], [300, 600]], "w": 6}]  # a lane straight down x=300
    s.village_grove([(250, 300), (350, 300), (350, 600), (250, 600)], role="copse", dense=False)
    vg = s.M["village_groves"][0]
    assert vg["clumps"]  # drew clumps in the gaps beside the lane
    for cx, _cy in vg["clumps"]:  # ... but none on the lane tread + clump radius (mirrors the check)
        assert abs(cx - 300) >= 3 + vg["r"]


def test_corridor_buffers_gathers_lanes_streets_and_road():
    s = _nuc_village()
    s.M["lanes"] = [{"pts": [[0, 0], [10, 0]], "w": 6}]
    s.M["town_streets"] = [{"pts": [[0, 0], [10, 0]], "w": 10}]
    s.M["road"] = [[0, 0], [10, 0]]
    corr = s._corridor_buffers(4)
    assert [b for _, b in corr] == [3 + 4, 5 + 4, 15 + 4]  # lane 6/2, street 10/2, road 30/2 (feature 144), each + extra


def test_village_grove_skips_clumps_in_a_yards_sun_corridor():
    poly = [(200, 380), (360, 380), (360, 560), (200, 560)]
    n_open = _nuc_village().village_grove(poly, role="copse", dense=False)  # baseline, no yard
    s = _nuc_village()
    s.M["threshing_yards"] = [{"x": 300, "y": 420, "w": 30, "h": 6}]  # a thin yard: its SOUTHERN sun-corridor
    n_yard = s.village_grove(poly, role="copse", dense=False)  # ... removes a clump beyond the occ keep-out
    assert n_yard < n_open  # the sun-corridor skip fired
    vg = s.M["village_groves"][0]
    r = vg["r"]
    se = 420 + 3  # yard south edge
    for cx, cy in vg["clumps"]:  # ... and none left in the sun-strip (mirrors the check)
        assert not (abs(cx - 300) < 15 + r and se - r < cy < se + 22 + r)


def test_village_grove_keeps_the_windbreak_out_of_a_plots_west_sun_lane():
    """Feature 133 T10: with `west_sun_lane` on, a windbreak clump never stands in the lane (50 ft
    in the generator; any value here) west/southwest of a yard or bed; a copse is exempt, and the
    rule is off by default."""
    # A NARROWER BAND (feature 158): a dense belt's cost is its AREA, and this test's question is
    # whether one fixed lane strip is kept clear. x is narrowed to 250..400 and y to 320..580, which
    # still leaves planting ground on both sides of the strip (the "and the belt still stands" arm),
    # for a little over half the clumps.
    poly = [(250, 320), (400, 320), (400, 580), (250, 580)]
    plot = {"x": 380, "y": 420, "w": 30, "h": 20}  # west edge 365, y 410..430

    def lane_hit(s):
        return [(cx, cy) for g in s.M["village_groves"] for cx, cy in g["clumps"] if 365 - 75 - g["r"] < cx < 365 + g["r"] and 410 - g["r"] < cy < 430 + 75 + g["r"]]

    off = _nuc_village()
    off.M["threshing_yards"] = [plot]
    off.village_grove(poly, role="windbreak")
    assert lane_hit(off), "off by default: the belt plants right up to the yard"
    on = _nuc_village()
    on.M["threshing_yards"] = [plot]
    on.west_sun_lane(75)
    n_on = on.village_grove(poly, role="windbreak")
    assert n_on > 0 and not lane_hit(on), "the lane is clear, and the belt still stands"
    copse = _nuc_village()
    copse.M["gardens"] = [plot]
    copse.west_sun_lane(75)
    copse.village_grove(poly, role="copse", dense=False)
    assert lane_hit(copse), "a copse is the dooryard's own trees and is not held to the belt's lane"


def test_village_grove_keeps_every_clump_and_set_view_decides_which_are_on_the_page():
    """The page decides, and it is only known at the crop (feature 152 T02).

    THIS TEST USED TO PIN THE OPPOSITE and was right to, until the thing it pinned turned out to be
    wrong. `face_margin` trimmed at SEATING time against a stand-in for the page - the belt's own inner
    face plus 48 ft - and this test asserted that a 300 px band's deep side is "beyond any 48 px
    margin", which it is. What the test could not see is that the stand-in is only the page when the
    BELT is what sets the frame's edge: let a field or a marsh hold the frame open wider and the proxy
    under-estimates it and deletes canopy a reader can see. Measured over the pool against each map's
    real `meta.view`, Kashikawa discarded 61 clumps of which ALL 61 were wholly inside the rendered
    view, and it was one of three maps with farmhouses standing beyond their belt's ends.

    So seating keeps everything the `within` window admits, and `set_view` - the first moment the page
    exists - partitions the record. That is what this now tests."""
    poly = [(100, 300), (250, 300), (250, 450), (100, 450)]  # half the band of feature 152's version: the partition is a property, not a size (feature 158)
    s = _nuc_village()
    s.M["houses"] = [{"x": 700, "y": 450, "w": 46, "h": 28}]
    n = s.village_grove(poly, role="windbreak", face_margin=48)
    g = s.M["village_groves"][0]
    assert n > 0 and len(g["clumps"]) == n, "seating keeps every clump the window admits"
    assert g["clumps_offpage"] == [], "nothing is off the page until there IS a page"

    # a crop that takes in the whole belt leaves every clump on it...
    s.set_view(0.0, 0.0, 1000.0, 1000.0)
    assert len(g["clumps"]) == n and g["clumps_offpage"] == []

    # ...and one that cuts the band in half moves exactly the clumps it cuts off, and no others
    s.set_view(0.0, 0.0, 180.0, 1000.0)  # cuts the narrowed band roughly in half
    r = float(g["r"])
    assert g["clumps"] and g["clumps_offpage"], "a crop through the band must split the record"
    assert len(g["clumps"]) + len(g["clumps_offpage"]) == n, "no clump is lost by the partition"
    assert all(cx - r < 180.0 for cx, _cy in g["clumps"]), "every drawn clump reaches the page"
    assert all(cx - r >= 180.0 for cx, _cy in g["clumps_offpage"]), "every off-page clump is WHOLLY off it"

    # the partition is a function of the view, not a one-way door: widening it brings them back
    s.set_view(0.0, 0.0, 1000.0, 1000.0)
    assert len(g["clumps"]) == n and g["clumps_offpage"] == []


def test_grove_fits_rejects_a_belt_over_a_dry_strip():
    # the windbreak's canopy stays out of the barley exactly as it stays out of the paddy
    s = _crop_settlement()
    s.dry_polys.append([(300, 300), (500, 300), (500, 380), (300, 380)])
    assert not s._grove_fits(400, 340, 60, 30, own=[])
    assert s._grove_fits(400, 500, 60, 30, own=[])


def test_commons_keeps_scrub_off_dry_plots_and_the_crop_margin():
    # GM 2026-08-15: scrub scattered over dry hatake plots and right up against crop edges. The
    # scatter must skip DRY PLOTS (read from dry_polys, which every dry-crop path registers) as
    # well as paddies, and keep _CROP_MARGIN_FT of clearance off EVERY crop edge - the bund/balk
    # plus one cut swath (settlements/vegetation.md "Scrub stands off the crops"). Tall glyphs
    # (scraggly pines, woodland crowns) stand their own drawn reach further back, so no tip leans
    # over the crop; base points alone are asserted here (the lean is engine-side headroom).
    s = _nuc_village()  # paddy at [(640,150),(1120,150),(1120,780),(640,780)]
    quad = [(200, 300), (400, 300), (400, 500), (200, 500)]
    s.dry_polys.append(quad)
    s.block_polys.append(quad)  # both registries, as every dry-crop path does
    clr = s.px(s._CROP_MARGIN_FT) - 0.06  # 0.1-rounding slack, as in the halo tests
    for role in ("grazing", "woodland"):
        before = len(s.out)
        s.commons([(100, 150), (700, 150), (700, 650), (100, 650)], role=role)  # over the dry plot AND the paddy's W edge
        pts = _scatter_base_points(s.out[before:])
        assert pts
        for gx, gy in pts:
            assert not (200 - clr <= gx <= 400 + clr and 300 - clr <= gy <= 500 + clr), (role, gx, gy)  # dry plot + margin
            assert gx < 640 - clr, (role, gx, gy)  # paddy edge + margin


def test_commons_keeps_scrub_off_drawn_channels():
    # GM 2026-08-16 (Inashiro): grass tufts stood ON the open water of the comb's head-race.
    # _on_watercourse read M['channels'] - the hairline TOPOLOGY connectors (w 2.5) - while the
    # comb's real drawn laterals live in M['drawn_channels'], up to 14 wide on their own filleted
    # post-clip polylines. The "same manifest source" trap: the scatter must skip the DRAWN water
    # band - uniform strokes at w0, tapered runs at each piece's own width (field_channel's 7-piece
    # w0 -> w1 ladder). Base points asserted, as in the crop-margin test above.
    def _clear_of(pts, poly, half):  # min point-to-polyline distance stays outside half + pad
        for gx, gy in pts:
            for (ax, ay), (bx, by) in zip(poly, poly[1:], strict=False):
                dx, dy = bx - ax, by - ay
                t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((gx - ax) * dx + (gy - ay) * dy) / (dx * dx + dy * dy)))
                assert ((gx - ax - t * dx) ** 2 + (gy - ay - t * dy) ** 2) ** 0.5 >= half + 2 - 0.15, (gx, gy)

    s = _nuc_village()
    s.field_channel([(300, 100), (310, 700)], "#6C9CBE", 14.0, 14.0)  # a wide UNIFORM supply lateral
    s.field_channel([(120, 120), (200, 680)], "#6C9CBE", 14.0, 5.0)  # a TAPERED head-race
    uniform, taper = (ch["pts"] for ch in s.M["drawn_channels"])
    before = len(s.out)
    # role="pasture" keeps the scatter to tufts + dots (no pines/crowns, whose highlight/shadow ink
    # is offset from the base point _sparse tests) so every element is base-tested - the same idiom
    # as the urban-halo tests.
    s.commons([(60, 60), (560, 60), (560, 760), (60, 760)], role="pasture")  # laid over both laterals
    pts = _scatter_base_points(s.out[before:])
    assert pts
    _clear_of(pts, uniform, 14.0 / 2)
    _clear_of(pts, taper, 5.0 / 2)  # conservative: every piece of the taper is at least w1 wide


def test_commons_keeps_scrub_a_cut_bank_off_the_channels_but_not_the_streams():
    # GM 2026-08-16 (Inashiro, second pass): after the drawn-width fix above, tufts still seeded in
    # the 10-16 ft berm strip between the dry hem plots and the supply channels - legal under the
    # drawn-width skip (2 px pad) + the 6 ft crop margin, which between them left a bare sliver
    # mid-strip. Decision: IRRIGATION channels (M['channels'] + M['drawn_channels']) hold a
    # maintained CUT-BANK margin of _BANK_MARGIN_FT beyond the drawn water edge - the bank is
    # walked for sluice work and scythed for fodder, the same economics as the crop margin
    # (research/vegetation.md "The cut bank"). STREAMS deliberately get NO margin: a natural bank
    # is vegetated to the water's edge, and a sterile halo on the brook is the defect the
    # settlement-review pass warned against. Base points asserted, as in the tests above.
    def _min_dist(gx, gy, poly):
        best = 1e18
        for (ax, ay), (bx, by) in zip(poly, poly[1:], strict=False):
            dx, dy = bx - ax, by - ay
            t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((gx - ax) * dx + (gy - ay) * dy) / (dx * dx + dy * dy)))
            best = min(best, ((gx - ax - t * dx) ** 2 + (gy - ay - t * dy) ** 2) ** 0.5)
        return best

    s = _nuc_village()
    s.field_channel([(300, 100), (310, 700)], "#6C9CBE", 14.0, 14.0)  # a wide UNIFORM supply lateral
    s.field_channel([(120, 120), (200, 680)], "#6C9CBE", 14.0, 5.0)  # a TAPERED head-race
    uniform, taper = (ch["pts"] for ch in s.M["drawn_channels"])
    m = s.px(s._BANK_MARGIN_FT)
    before = len(s.out)
    s.commons([(60, 60), (560, 60), (560, 760), (60, 760)], role="pasture")  # laid over both laterals
    pts = _scatter_base_points(s.out[before:])
    assert pts
    for gx, gy in pts:  # every base clears drawn half-width + the cut-bank margin (w1 conservative on the taper)
        assert _min_dist(gx, gy, uniform) >= 14.0 / 2 + m - 0.15, (gx, gy)
        assert _min_dist(gx, gy, taper) >= 5.0 / 2 + m - 0.15, (gx, gy)

    s2 = _nuc_village()  # ... and the SAME scatter over a natural stream keeps grass to the bank
    stream = [[300, 100], [310, 700]]
    s2.M["streams"] = [{"poly": stream, "w": 8}]
    before = len(s2.out)
    s2.commons([(60, 60), (560, 60), (560, 760), (60, 760)], role="pasture")
    pts2 = _scatter_base_points(s2.out[before:])
    assert pts2
    assert all(_min_dist(gx, gy, [tuple(p) for p in stream]) >= 8 / 2 + 2 - 0.15 for gx, gy in pts2)  # still off the water itself
    assert any(_min_dist(gx, gy, [tuple(p) for p in stream]) < 8 / 2 + 2 + m for gx, gy in pts2), "no tuft near the stream bank - the no-margin-on-streams half of the rule has lost its witness"


def test_attach_garden_draws_and_records_two_beds():
    s = _nuc_village()
    s._attach_garden(500, 500, [(486, 500, 10, 12), (520, 500, 10, 12)])
    beds = s.M["gardens"]
    assert len(beds) == 2 and all(b["of"] == [500, 500] and len(b["poly"]) == 4 for b in beds)


def test_garden_fits_rejects_a_spot_outside_the_bound():
    s = Settlement(1000, 1000, seed=1)
    s.bound = [(0, 0), (600, 0), (600, 1000), (0, 1000)]  # only x < 600 is inside
    yard = (500, 540, 32, 20)
    assert s._garden_fits(700, 500, 24, 16, 500, 500, yard) is False  # x=700 is outside the bound


def test_yard_fits_skips_own_house_and_rejects_a_neighbor():
    s = Settlement(1000, 1000, seed=1)
    s.placed.append((500, 500, 40, 28))  # the OWN house footprint -> the loop skips it
    s.placed.append((520, 540, 40, 28))  # a neighbor where the yard would land -> rejected
    assert s._yard_fits(520, 540, 32, 20, 500, 500) is False


def test_garden_fits_skips_own_house_and_rejects_a_neighbor():
    s = Settlement(1000, 1000, seed=1)
    s.placed.append((500, 500, 40, 28))  # the OWN house footprint -> the loop skips it
    s.placed.append((545, 500, 40, 28))  # a neighbor where the garden would land -> rejected
    assert s._garden_fits(545, 500, 24, 16, 500, 500, (500, 560, 32, 20)) is False


def test_grove_fits_rejects_a_spot_outside_the_bound():
    s = Settlement(1000, 1000, seed=1)
    s.bound = [(0, 0), (600, 0), (600, 1000), (0, 1000)]  # only x < 600 is inside (a city-style bound)
    assert s._grove_fits(700, 500, 30, 24, [(500, 500)]) is False  # x=700 is outside the bound


def test_on_watercourse_detects_stream_and_channel_beds():
    s = Settlement(600, 600, seed=1)
    s.M["streams"] = [{"poly": [[100, 100], [400, 100]], "w": 8}]
    s.M["channels"] = [{"poly": [[100, 300], [400, 300]], "w": 4}]
    assert s._on_watercourse(250, 100) and s._on_watercourse(250, 300)  # on the stream / channel bed
    assert not s._on_watercourse(250, 200)  # clear ground between them


def test_village_grove_keeps_copse_out_of_a_garden_east_sun_lane():
    # the copse must not scatter a clump directly EAST of a kitchen garden (it would block the morning sun).
    # Teeth: a clump lands in that lane with NO garden present, and is skipped once the garden is there.
    poly = [[260, 240], [420, 240], [420, 360], [260, 360]]

    def lane_clumps(gardens):
        s = Settlement(700, 700, seed=3)
        s.meta(name="V", scale="village", ftpx=2)
        s.M["gardens"] = gardens
        s.village_grove(poly, role="copse", dense=True)
        cs = [c for g in s.M["village_groves"] for c in g["clumps"]]
        return [c for c in cs if 311 < c[0] < 345 and abs(c[1] - 300) < 13]  # the garden's east sun-lane

    without = lane_clumps([])
    with_garden = lane_clumps([{"x": 300, "y": 300, "w": 20, "h": 18, "rot": 0, "of": [280, 300]}])
    assert without and not with_garden


def test_yard_fits_rejects_dry_crop_plots():
    # the threshing yard is footprint-checked against dry_polys exactly like the house in _fits:
    # a hem strip is cropland, and a yard straddling it (center off, footprint on) must be
    # rejected (the Tango-hems class of defect, extended to yards via the town comb conversion)
    s = Settlement(W=1000, H=1000, seed=1)
    s.meta(name="Yd", scale="town", ftpx=1)
    assert s._yard_fits(500, 500, 40, 26, 460, 460)  # open ground: fits
    s.dry_polys.append([(490, 480), (620, 480), (620, 560), (490, 560)])
    # center 14px OUTSIDE the hem (so the center-based _in_blocked test passes it) but the 40px
    # footprint still laps the plot - only the rect test can catch this one
    assert not s._yard_fits(476, 500, 40, 26, 440, 500)


def test_fit_helpers_reject_out_of_bounds_spots():
    # the shared 55/88px canvas-margin early-outs of the appurtenance fit helpers (previously
    # exercised by the towns' legacy farmstead pass; the towns now run the bundle path)
    s = Settlement(W=1000, H=1000, seed=1)
    s.meta(name="Eb", scale="town", ftpx=1)
    assert not s._yard_fits(20, 500, 40, 26, 60, 500)
    assert not s._garden_fits(20, 500, 30, 22, 60, 500, (60, 540, 40, 26))
    assert not s._grove_fits(20, 500, 60, 30, [(60, 500)])


def test_village_grove_copse_skips_dry_crop_plots():
    # a copse clump never lands in a hem strip (the barley) - the dry_polys skip in village_grove
    s = Settlement(W=800, H=800, seed=2)
    s.meta(name="Vg", scale="village", ftpx=2)
    s.dry_polys.append([(300, 300), (500, 300), (500, 500), (300, 500)])
    s.village_grove([(280, 280), (520, 280), (520, 520), (280, 520)], role="copse", dense=False)
    for g in s.M["village_groves"]:
        for cx, cy in g["clumps"]:
            assert not (312 <= cx <= 488 and 312 <= cy <= 488)  # nothing deep inside the plot


def test_every_roofed_feature_is_a_canopy_keepout():
    """THE RATCHET behind "no tree is drawn on a roof". The canopy keep-out was a hand list until a
    reviewer found scrub on a theater stage; settlement.py cannot import check_village (circular),
    so the roofed set is written out - and this holds it against the real overlap registry. Every
    solid feature must be either a canopy keep-out or explicitly named open-air ground, so a new
    feature cannot silently fall outside both the way `theater_stage` did."""

    classified = set(Settlement._CANOPY_STRUCT_KEYS) | set(Settlement._CANOPY_OPEN_AIR_KEYS)
    missing = sorted(k for k in check_village._OVERLAP_STRUCTS if k not in classified)
    assert not missing, (
        f"solid feature(s) {missing} are neither a canopy keep-out nor declared open-air ground - add them to Settlement._CANOPY_ROOFED_KEYS (a tree may not stand on a roof) or to _CANOPY_OPEN_AIR_KEYS with the reason"
    )


def test_reclist_reads_a_singleton_record_as_well_as_a_list():
    """A few features are stored as a bare dict, not a list - which is why their keys are singular.
    Iterating one blindly yields its string KEYS and `o["w"]` then raises TypeError; that is exactly
    how adding `theater_stage` to the keep-out lists crashed every gen until this helper existed."""
    s = _town()
    s.M["theater_stage"] = {"x": 10, "y": 20, "w": 30, "h": 40}
    assert s._reclist("theater_stage") == [{"x": 10, "y": 20, "w": 30, "h": 40}]
    s.M["houses"] = [{"x": 1, "y": 2, "w": 3, "h": 4}, {"x": 5, "y": 6, "w": 7, "h": 8}]
    assert len(s._reclist("houses")) == 2
    assert s._reclist("no_such_key") == []


# ---- feature 145: the refusal branches on the hamlet path that no roll happened to take -----------


def test_yard_fits_rejects_a_basin_VERTEX_inside_the_yard() -> None:
    """The other direction of the two-source paddy test (`_yard_fits`, 2026-08-18): no yard CORNER is
    inside the basin, but a basin vertex is inside the yard - which is what the check tests too."""
    s = Settlement(1000, 1000, seed=1)
    s.M["fields"] = [{"kind": "paddy", "outline": [[495, 495], [505, 495], [505, 505], [495, 505]]}]  # wholly inside the yard
    assert s._yard_fits(500, 500, 60, 40, 500, 440) is False
    s.M["fields"] = [{"kind": "paddy", "outline": [[900, 900], [960, 900], [960, 960], [900, 960]]}]  # far away
    assert s._yard_fits(500, 500, 60, 40, 500, 440) is True


def test_garden_fits_rejects_a_spot_on_its_own_threshing_yard() -> None:
    s = Settlement(1000, 1000, seed=1)
    yard = (500, 560, 32, 20)
    assert s._garden_fits(500, 560, 24, 16, 500, 500, yard) is False  # centered ON the yard


def test_grove_fits_rejects_a_belt_over_the_flooded_paddy() -> None:
    s = Settlement(1000, 1000, seed=1)
    s.field_polys.append([(300, 300), (700, 300), (700, 700), (300, 700)])
    assert s._grove_fits(500, 500, 60, 30, own=[]) is False  # the whole grove inside the basin
    assert s._grove_fits(120, 120, 60, 30, own=[]) is True


def test_bamboo_stand_that_draws_nothing_records_nothing() -> None:
    s = Settlement(1000, 1000, seed=1)
    assert s.bamboo_stand([(500, 500), (500, 500), (500, 500)]) == 0  # zero area: no culm lands, so nothing is drawn
    assert s.M.get("bamboo_stands", []) == []  # (the key is pre-initialized on the manifest; nothing was appended)


def test_watercourse_segs_reads_a_uniform_width_channel() -> None:
    """`field_channel`'s uniform branch records w0 == w1; the segs helper takes the single stroke."""
    s = Settlement(1000, 1000, seed=1)
    s.M["drawn_channels"] = [{"pts": [[100, 100], [400, 100]], "w0": 6.0, "w1": 6.0}, {"pts": [[500, 500]], "w0": 6.0, "w1": 6.0}]
    segs = s._watercourse_segs()
    assert any(abs(hw - (6.0 / 2 + 0.0)) < 3.0 for _pl, hw in segs), segs  # the uniform stroke, its half-width plus pad


def test_corridor_buffers_reads_the_alleys_the_ring_road_and_the_road() -> None:
    """Feature 146: every trodden tread is a keep-out for cover, not only the lanes."""
    s = Settlement(1000, 1000, seed=1)
    s.M["alleys"] = [{"pts": [[10, 10], [90, 10]], "w": 8}]
    s.M["ring_road"] = [[100, 100], [300, 100]]
    s.M["road"] = [[400, 400], [600, 400]]
    got = {round(half) for _pts, half in s._corridor_buffers(4.0)}
    assert {round(8 / 2 + 4), round(20 / 2 + 4), round(30 / 2 + 4)} <= got, got


# ---- feature 146: one test per refusal reason the rolls have not happened to hit ----------------------


def test_yard_fits_rejects_a_yard_whose_corner_is_inside_a_basin() -> None:
    """The FIRST direction of the two-source paddy test (the second is covered above): a yard CORNER inside a
    drawn basin outline, which is what `harvest_yards_clear_of_paddies` measures."""
    s = Settlement(1000, 1000, seed=1)
    s.M["fields"] = [{"kind": "paddy", "outline": [[520, 480], [900, 480], [900, 900], [520, 900]]}]
    assert s._yard_fits(500, 500, 60, 40, 500, 440) is False  # the yard's east corners reach into the basin
    assert s._yard_fits(200, 200, 60, 40, 200, 140) is True


def test_garden_fits_rejects_a_bed_on_the_paddy_and_near_its_edge() -> None:
    """A kitchen garden is DRY ground: inside a paddy, or within its own radius of one's edge, is refused."""
    s = Settlement(1000, 1000, seed=1)
    s.field_polys.append([(400, 400), (700, 400), (700, 700), (400, 700)])
    yard = (200, 260, 32, 20)
    assert s._garden_fits(550, 550, 24, 16, 200, 200, yard) is False  # in the basin
    assert s._garden_fits(390, 550, 24, 16, 200, 200, yard) is False  # off it, but inside the radius + 4
    assert s._garden_fits(200, 200, 24, 16, 200, 200, yard) is True


def test_grove_fits_rejects_a_belt_on_a_lane_tread() -> None:
    """A grove may stand at the paddy's edge (the field set-back is for buildings) but never on a trodden way."""
    s = Settlement(1000, 1000, seed=1)
    s.corridors.append(([(100.0, 500.0), (900.0, 500.0)], 20.0))  # a lane's cleared band, as the placer registers it
    assert s._grove_fits(500, 500, 60, 30, own=[]) is False  # centered on the tread
    assert s._grove_fits(500, 300, 60, 30, own=[]) is True


def test_draw_grove_draws_a_mixed_stand_at_its_seat() -> None:
    """Feature 146: the clump draws conifer and broadleaf crowns at its own seat. It does NOT draw bamboo -
    the threshold that would select it is 0.0 in both mixes, so that arm was unreachable and is gone."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1)
    before = len(s.out)
    s._draw_grove(300.0, 300.0, 120.0, 80.0, face=(0, -1), mix="windbreak")
    ink = "".join(str(o) for o in s.out[before:])
    assert "<circle" in ink and "translate(300,300)" in ink
    assert "#BBD06A" not in ink, "no culm: the bamboo arm was unreachable and was removed"


def test_a_kitchen_garden_is_refused_a_seat_on_the_paddy():
    """A garden is DRY ground. The refusal is by footprint plus a 4 px hair, so a seat whose center
    stands clear but whose corner laps the bund is refused too."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.field_polys.append([(100.0, 100.0), (400.0, 100.0), (400.0, 400.0), (100.0, 400.0)])
    # 18 px OUT from the field edge: past `_in_blocked`'s own 14 px setback, which answers first for
    # anything nearer and would leave the garden's own rule (its half-diagonal plus 4) untested.
    assert not s._garden_fits(418, 250, 22, 24, 900, 900, (900, 900, 30, 20)), "its corner laps the bund"
    assert s._garden_fits(700, 700, 22, 24, 900, 900, (900, 900, 30, 20)), "and dry ground is fine"


def test_a_windbreak_reseating_round_a_house_stays_inside_the_within_box():
    """A DENSE belt flows around a local obstacle instead of losing the column - it tries eight bearings
    at five radii for a new seat. `within` bounds where those seats may land: a clump that would be
    pushed wholly outside the caller's box is refused there rather than planted off the frame."""
    poly = [(300.0, 320.0), (500.0, 320.0), (500.0, 440.0), (300.0, 440.0)]  # half the band, same house, same question (feature 158)
    s = _nuc_village()
    s.M["houses"] = [{"x": 400.0, "y": 380.0, "w": 90.0, "h": 60.0, "rot": 0, "kind": "plain"}]
    s.placed.append((400.0, 380.0, 90.0, 60.0))
    narrow = s.village_grove(poly, role="windbreak", within=(360.0, 350.0, 440.0, 410.0))  # the house's own box

    s2 = _nuc_village()
    s2.M["houses"] = [{"x": 400.0, "y": 380.0, "w": 90.0, "h": 60.0, "rot": 0, "kind": "plain"}]
    s2.placed.append((400.0, 380.0, 90.0, 60.0))
    wide = s2.village_grove(poly, role="windbreak")
    assert 0 < narrow < wide, "the box bounds the belt without emptying it"


def test_the_allotted_yard_knob_issues_every_household_the_same_yard() -> None:
    """THE THIRD ATTESTED FORM, and the one whose whole point is that the roll does NOT apply.

    `yard_sizes` names which record a map follows. `wet` and `dryfield` differ only in the median the
    lognormal is drawn about, so both vary house to house; `allotted` is the planned-colony form - a
    shinden colony issued every settler an identical homestead (Santome 1696) - and there the yard is
    the median FLAT, with the household's own deviation and the positional draw both discarded.

    That single assignment is the whole knob, and nothing reached it: the pool rolls wet and dryfield,
    so the branch that makes the third form different from the other two was never executed. This
    pins the property rather than the line - four households whose houses differ in size and position
    get the SAME yard under `allotted`, and different yards under `wet`."""
    houses = [(300.0, 300.0, 46.0, 28.0), (700.0, 520.0, 62.0, 34.0), (420.0, 780.0, 38.0, 24.0), (860.0, 240.0, 52.0, 30.0)]

    allotted = Settlement(1200, 1000, seed=7)
    allotted.meta(name="Santome", scale="hamlet", yard_sizes="allotted")
    issued = {round(allotted._yard_area_ft2(*h), 6) for h in houses}
    assert len(issued) == 1, f"a planned colony issues one yard, got {issued}"

    rolled = Settlement(1200, 1000, seed=7)
    rolled.meta(name="Sawada", scale="hamlet")
    varied = {round(rolled._yard_area_ft2(*h), 6) for h in houses}
    assert len(varied) == len(houses), "the rolled forms vary household by household"

    # ...and the allotted figure is the median itself, neither tilted by the house nor jittered
    assert abs(issued.pop() - allotted.YARD_MEDIAN_TSUBO * allotted.TSUBO_FT2) < 1e-3


def test_a_garden_is_refused_on_a_no_build_corridor() -> None:
    """THE PLACER'S GUARANTEE that the retired `gardens_clear_of_channels` check used to re-measure on
    the finished map (feature 166).

    A raised-bed saien sits on dry ground, never in a running feeder channel, field ditch or stream. The
    placer already refuses it: every watercourse registers a no-build CORRIDOR, and `_garden_fits`
    consults `_near_corridor` before anything else about the ground. Asserting it here is the same rule
    measured where it is made."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1, down_deg=90)
    yard = (900.0, 900.0, 30.0, 20.0)  # far away, so only the corridor can refuse
    assert s._garden_fits(500.0, 500.0, 22.0, 24.0, 480.0, 480.0, yard), "open dry ground takes a garden"

    s.corridors.append(([(400.0, 500.0), (600.0, 500.0)], 33.0))  # a watercourse runs through it
    assert not s._garden_fits(500.0, 500.0, 22.0, 24.0, 480.0, 480.0, yard), "and a garden in the channel is refused"


def test_a_watercourse_registers_the_corridor_the_garden_consults() -> None:
    """The other half of the chain, so the pair proves the whole rule rather than half of it: the garden
    refusing a corridor is only the guarantee if a drawn channel actually REGISTERS one. `water_ways`
    appends `(poly, 33)` for a channel and a wider band for a stream - the check this replaces trusted
    that link implicitly, and a test that asserted only the refusal would still pass if channels stopped
    registering."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1, down_deg=90)
    before = len(s.corridors)
    s.channel((200.0, 300.0), (800.0, 300.0), frm={"kind": "stream"}, to={"kind": "field", "name": "f"})
    assert len(s.corridors) > before, "a drawn channel must register a no-build corridor"
    assert s._near_corridor(500.0, 300.0), "and that corridor covers the water it protects"
