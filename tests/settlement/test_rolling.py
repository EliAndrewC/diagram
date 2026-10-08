"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import math

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement, _nuc_village, _town, _village


def test_nucleated_cluster_is_grove_less_with_yards_and_gardens():

    s = _nuc_village()
    s.lane([(300, 180), (322, 620)], width=5, clearance=11, worn=True)  # the WORN (unpaved) lane branch
    assert s.headman(520, 300)  # headman = a LARGER plain farmhouse; its whole envelope (194 x 166) west of the paddy at x=640
    # SEATS ON A LATTICE, as the generator proposes them (feature 227): the placer tests the homestead's whole envelope
    # once and makes no spiral, so a random throw mostly lands on a standing bundle and is refused - the way to seat a
    # cluster is to propose seats at the pitch, which is what `stage_homesteads` does.
    n = 1
    for gx in range(380, 640, 100):
        for gy in range(200, 720, 90):
            if n < 14 and s.try_place(gx, gy, "plain"):
                n += 1
    drawn = s.farmsteads()
    assert drawn >= 10
    assert s.M["lanes"] and s.M["lanes"][0]["worn"] is True  # worn lane recorded
    assert not s.M["groves"]  # nucleated -> NO per-house grove
    assert len(s.M["threshing_yards"]) >= drawn - 1  # each homestead keeps a yard
    assert len(s.M["gardens"]) >= drawn - 1  # ... and an (adaptive-side) garden
    hm = [h for h in s.M["houses"] if h.get("role") == "headman"][0]
    assert hm["kind"] == "plain" and hm["w"] >= 40  # the headman is a plain, larger house
    assert all(h["w"] <= hm["w"] for h in s.M["houses"])  # ... and the largest


def test_rect_hits_detects_a_pure_edge_crossing():
    # the _rect_hits edge-cross arm: a plus-sign where neither shape has a corner/vertex inside the
    # other, but their edges cross - the corner-in / vertex-in fast paths both miss, so only the
    # per-edge segments_cross catches it. Plus a bbox-disjoint poly to exercise the early reject.
    s = _crop_settlement()
    assert s._rect_hits((500, 500, 200, 40), [[(480, 400), (520, 400), (520, 600), (480, 600)]])
    assert not s._rect_hits((500, 500, 40, 40), [[(900, 900), (950, 900), (950, 950), (900, 950)]])


def test_rect_on_water_blocks_a_solid_part_on_an_irrigation_line():
    # the homestead solver rejects a house/yard/garden that lands on a channel/ditch/stream, but NOT the grove
    s = _crop_settlement()
    s.M["field_ditches"] = [{"poly": [(400, 300), (400, 500)], "role": "drain", "w": 6, "field": "f"}]
    s.M["channels"] = [{"poly": [(600, 300), (600, 500)], "w": 2.5}]
    s.M["streams"] = [{"poly": [(800, 300), (800, 500)], "w": 9}]
    assert s._rect_on_water((400, 400, 24, 16)) is True  # garden straddling the drain -> seg_dist branch
    assert s._rect_on_water((360, 400, 100, 10)) is True  # a wide rect an edge of which the ditch CROSSES far from any corner -> segments_cross branch
    assert s._rect_on_water((600, 400, 20, 14)) is True  # on the feeder channel
    assert s._rect_on_water((800, 400, 20, 14)) is True  # on the stream
    assert s._rect_on_water((500, 400, 24, 16)) is False  # dry ground between them -> clear
    # the grove (fields=False) is exempt - it may hug a bund/ditch; the solid parts (fields=True) are not
    assert s._rect_blocked((400, 400, 24, 16), fields=False) is False
    assert s._rect_blocked((400, 400, 24, 16), fields=True) is True


def test_parts_across_stream_refuses_a_garden_on_the_far_bank():
    # feature 261 FR-013: a brook between the house and a part of its homestead refuses the configuration, though
    # no part stands ON the water; the same parts with the brook beyond them all, or with no brook, are clear
    s = _crop_settlement()
    geom = {"house": (400, 400, 24, 16), "yard": (400, 430, 30, 20), "gardens": [(450, 400, 20, 16)], "shed": None}
    assert s._parts_across_stream(geom) is False  # no stream on the sheet
    s.M["streams"] = [{"poly": [(430, 300), (430, 500)], "w": 9}, {"poly": [(0, 0)], "w": 9}]
    assert s._parts_across_stream(geom) is True  # the brook runs between the house and its garden bed
    assert s._parts_fit(geom) is False
    s.M["streams"] = [{"poly": [(520, 300), (520, 500)], "w": 9}]
    assert s._parts_across_stream(geom) is False  # beyond every part
    s.M["streams"] = [{"poly": [(450, 300), (450, 500)], "w": 9}]
    assert s._rect_on_stream(geom["gardens"][0]) is True and s._parts_across_stream(geom) is True  # the bed stands ON the brook


def test_rect_on_water_skips_a_degenerate_course_and_far_ones():
    # the collision pre-filter: a degenerate (<2-point) course is dropped from _water_obstacles (it has no
    # segment and would crash the bbox min/max on an empty poly), and a course whose bbox is nowhere near
    # the rect is skipped without any seg_dist / crossing math.
    s = _crop_settlement()
    s.M["streams"] = [
        {"poly": [(100, 100)], "w": 9},  # degenerate: single point -> skipped
        {"poly": [(1500, 1300), (1500, 1400)], "w": 9},
    ]  # real, but far from the probe rect
    assert s._water_obstacles() == [(s.M["streams"][1]["poly"], 9 / 2 + 5, (1500, 1300, 1500, 1400))]
    assert s._rect_on_water((400, 400, 24, 16)) is False  # far course bbox-rejected -> clear


def test_garden_shaded_detects_a_house_to_the_south():
    s = _nuc_village()
    s.M["houses"].append({"x": 400, "y": 470, "w": 23, "h": 14})  # a house just SOUTH of the garden
    assert s._garden_shaded((400, 450, 22, 12)) is True  # shaded
    assert s._garden_shaded((900, 450, 22, 12)) is False  # open sky to the south -> not shaded


def test_garden_shaded_from_the_index_equals_the_scan_of_every_house():
    """Feature 276: the indexed garden-shade test flags exactly the gardens the scan over every placed house flags."""
    import random

    s = _village()
    rng = random.Random(276)
    for _ in range(80):
        s.M["houses"].append({"x": rng.uniform(0, 600), "y": rng.uniform(0, 600), "w": rng.uniform(20, 50), "h": rng.uniform(14, 30), "kind": "plain"})

    def scan(g):
        gx, gy, gw, gh = g
        return any(r["y"] > gy + gh / 2 - 3 and abs(r["x"] - gx) < (r["w"] + gw) / 2 and (r["y"] - r["h"] / 2) - (gy + gh / 2) < gh + 4 for r in s.M["houses"])

    gardens = [(rng.uniform(0, 600), rng.uniform(0, 600), rng.uniform(10, 30), rng.uniform(8, 20)) for _ in range(400)]
    got = [s._garden_shaded(g) for g in gardens]
    assert got == [scan(g) for g in gardens]
    assert 20 < sum(got) < 380, "non-vacuity: both answers occur"


def test_sun_corridor_covers_a_neighbors_garden_and_this_bundles_gardens():
    """Feature 133 T10: both directions of the garden corridor, and the side split that keeps the
    side-dependent half out of `_sun_corridor_ok` (which `_fits_any_side` runs once for all sides)."""
    s = _nuc_village()
    s.sun_corridor(39)
    # a standing bundle with a bed on its E flank at (440, 400) 22x24 -> bed south edge 412
    s.M["houses"].append({"x": 400, "y": 400, "w": 46, "h": 28, "geom": {"yard": (400, 430, 36, 26), "gardens": [(440, 400, 22, 24)]}})
    under_bed = {"house": (440, 450, 46, 28), "yard": (440, 480, 36, 26), "gardens": []}  # wall 24 ft south of the bed
    assert s._sun_corridor_ok(under_bed) is False  # a new house may not shade a standing bed
    clear = {"house": (440, 500, 46, 28), "yard": (440, 530, 36, 26), "gardens": []}  # wall 74 ft south of the bed, 43 from the yard: past 39 + 2 on both
    assert s._sun_corridor_ok(clear) is True
    # ...and a new bundle's OWN beds against standing houses, side by side, not all-or-nothing
    s.M["houses"].append({"x": 300, "y": 470, "w": 46, "h": 28})  # a house whose wall is at y=456
    assert s._gardens_sun_ok({"gardens": [(300, 430, 22, 24)]}) is False  # bed south edge 442, wall 14 ft off
    assert s._gardens_sun_ok({"gardens": [(300, 380, 22, 24)]}) is True  # 64 ft: clear
    assert s._gardens_sun_ok({"gardens": [(600, 430, 22, 24)]}) is True  # not in the corridor laterally
    s._sun_corridor_ft = 0.0
    assert s._gardens_sun_ok({"gardens": [(300, 430, 22, 24)]}) is True  # off by default, like the yard rule


def test_a_persimmon_keeps_out_of_its_own_and_its_neighbors_yards_and_beds_sun():
    """GM 2026-10-02: a household's persimmon in a yard's or bed's sun - its own as drawn, a standing neighbor's - is dropped,
    and the seat judged without it (feature 315: a dooryard tree never refuses a household); a seat whose plots a standing
    neighbor's persimmon shades is refused; off where the sun corridor is."""
    s = _nuc_village()
    tree = (500, 300, 23, 23)
    assert s._persimmon_sun_conflict({"yard": (500, 330, 36, 26), "gardens": [], "fixtures": {"persimmon": tree}}) is False, "off by default"
    s.sun_corridor(39)
    own = {
        "yard": (440, 300, 36, 26),
        "gardens": [],
        "fixtures": {"persimmon": tree},
        "fixture_notes": {"ft": {"persimmon": (23.0, 23.0), "privy": (24.0, 12.0)}},
        "boxes": {"fixtures": {"persimmon": tree}},
    }
    assert s._persimmon_sun_conflict(own) is False and "persimmon" not in own["fixtures"], "its own yard: the tree is dropped, the seat stands"
    assert own["boxes"]["fixtures"] == {} and own["fixture_notes"]["ft"] == {"privy": (24.0, 12.0)}, "its box and its rolled size go with it"
    assert s._persimmon_sun_conflict({"yard": (500, 400, 36, 26), "gardens": [], "fixtures": {"persimmon": tree}}) is False, "behind its house"
    assert s._persimmon_sun_conflict({"yard": (500, 400, 36, 26), "gardens": []}) is False, "a household with no tree"
    s.M["houses"].append({"x": 420, "y": 260, "w": 46, "h": 28, "geom": {"yard": (420, 300, 36, 26), "gardens": [(470, 260, 22, 24)], "fixtures": {"persimmon": (380, 330, 23, 23)}}})
    near = {"yard": (500, 400, 36, 26), "gardens": [], "fixtures": {"persimmon": tree}}
    assert s._persimmon_sun_conflict(near) is False and "persimmon" not in near["fixtures"], "a neighbor's yard to its east: dropped"
    assert s._persimmon_sun_conflict({"yard": (440, 310, 36, 26), "gardens": []}) is True, "a neighbor's tree in this yard's sun: the seat is refused"
    own_shade = {"yard": (360, 380, 36, 26), "gardens": [], "fixtures": {"persimmon": (360, 340, 23, 23)}}
    assert s._persimmon_sun_conflict(own_shade) is False and own_shade["fixtures"] == {}, "its own tree over its own yard: dropped"
    assert s._persimmon_sun_conflict({"yard": (700, 600, 36, 26), "gardens": [], "fixtures": {"persimmon": (700, 560, 23, 23)}}) is False, "far from both"


def test_headman_refuses_a_non_toscale_map():
    # the legacy (pre-to-scale) headman rec branch was dead code after the Hikari fix and is gone
    s = Settlement(800, 800, seed=5)
    s.meta(name="T", scale="town")
    with pytest.raises(ValueError):
        s.headman(400, 400)


def test_a_hamlet_scale_map_can_draw_no_headman():
    """Feature 287, homes H18: the role's one producer refuses a hamlet - a hamlet has no headman of its own."""
    s = Settlement(800, 800, seed=5)
    s.meta(name="H", scale="hamlet", ftpx=1, toscale=True)
    with pytest.raises(ValueError, match="no headman of its own"):
        s.headman(400, 400)
    assert not any(h.get("role") == "headman" for h in s.M["houses"])


def test_garden_beds_clear_rejects_a_bed_on_a_neighbor():
    # the neighbor-footprint hit branch: a shifted bed landing on an actual drawn structure is rejected
    s = Settlement(800, 800, seed=5)
    s.meta(name="B", scale="village", ftpx=2, toscale=True)
    assert s._garden_beds_clear([(100, 100, 20, 14)], others=[(104, 102, 20, 14)]) is False
    assert s._garden_beds_clear([(100, 100, 20, 14)], others=[(300, 300, 20, 14)]) is True


def test_closest_on_seg_degenerate_segment():
    # a zero-length segment returns its own endpoint (no division by zero)
    assert Settlement._closest_on_seg(0, 0, 5, 5, 5, 5) == (5, 5)


def test_bundle_fits_rejects_a_bundle_spilling_outside_the_bound():
    # a homestead bundle whose grove/garden corner falls outside the settlement bound is rejected
    s = _village()
    s.bound = [(100, 100), (500, 100), (500, 500), (100, 500)]
    assert s._bundle_fits(s._bundle_geom(120, 120, 40, 26)) is False


def test_slide_stops_on_no_target_and_on_arrival():
    # _slide halts when the target function yields None (nowhere to go) and when it is already on target
    s = _village()
    assert s._slide(200, 200, 40, 26, lambda x, y: None, True) == (200, 200)
    assert s._slide(200, 200, 40, 26, lambda x, y: (x, y), True) == (200, 200)


def test_kura_side_flips_to_the_north_wall_when_the_west_is_taken():
    # A legacy farmstead reserves its base rect but DRAWS its west kura past it, so the side is
    # chosen at flush time against the neighbors actually on the ground (Minami 2026-08-08, a farm
    # shed drawn on a garden). West by default, north when the west is taken - and when BOTH are
    # taken the west stands, so the overlap matrix reports a homestead with no room for its kura
    # rather than the engine hiding it.
    s = Settlement(600, 600, seed=1)
    s.meta(name="V", scale="village", ftpx=2)
    rec = {"x": 300.0, "y": 300.0, "w": 44.0, "h": 29.0, "rot": 0.0, "shed": True}
    assert s._kura_side(rec, 44.0, 29.0) == "W"
    s.M["gardens"].append({"x": 300 - 0.64 * 44, "y": 300.0, "w": 10.0, "h": 10.0})  # a neighbor's bed on the west wall
    assert s._kura_side(rec, 44.0, 29.0) == "N"
    s.M["gardens"].append({"x": 300.0, "y": 300 - 0.60 * 29, "w": 10.0, "h": 10.0})  # ...and one on the back wall too
    assert s._kura_side(rec, 44.0, 29.0) == "W"


def test_legacy_dispersed_farmstead_path_still_covered():
    # every POOL map is now to-scale, so keep the legacy (non-to-scale) DISPERSED path covered here: an old-style
    # hamlet (scale!=village, no toscale -> _toscale() False) rings its field with houses and draws farmsteads
    # via _try_place_legacy + _farmsteads_legacy (the pre-bundle path Moritono used before it was redone).
    s = Settlement(1200, 900, seed=3)
    s.meta(name="L", scale="hamlet")
    fld = (300, 300, 620, 560)
    s.paddy_field(fld, "", "f", amp=20)
    s.ring(fld, 12, 24, ["plain"])  # 8-16 px seated houses inside the paddy set-back once the field edge became chords pushed out by 3 px (feature 140)
    n = s.farmsteads()
    assert n > 0


@pytest.mark.parametrize("sides", (2, 3, 4))
def test_the_legacy_path_plants_every_rolled_side_on_every_grove_farm(sides: int) -> None:
    """Feature 291, plan D8: a house-first farm with a grove is seated only where the whole rolled grove fits, and then
    plants a band on every face - none dropped for want of room (`meta.grove_faces_unplanted` stays unset)."""
    s = Settlement(1200, 900, seed=3)
    s.meta(name="L", scale="hamlet", grove_sides=sides, grove_flank=-1)
    fld = (300, 300, 620, 560)
    s.paddy_field(fld, "", "f", amp=20)
    s.ring(fld, 12, 24, ["plain"])
    assert s.farmsteads() > 0
    faces: dict = {}
    for g in s.M["groves"]:
        faces.setdefault(tuple(g["of"]), set()).add((tuple(g["face"]), g["depth"]))
    assert faces, "the ring's farms carry groves - the rule was not vacuous"
    assert all(len({f for f, _d in fs}) == sides for fs in faces.values()), faces
    assert "grove_faces_unplanted" not in s.M["meta"]


def test_a_legacy_grove_farm_with_no_room_for_its_whole_grove_is_not_seated() -> None:
    """Feature 291, plan D8: the old fallback to a yard-and-garden-only spot is gone for a farm that has a grove."""
    s = Settlement(1200, 900, seed=3)
    s.meta(name="L", scale="hamlet", grove_sides=4, grove_flank=-1)
    s._grove_reserve = lambda *a: None  # type: ignore[method-assign]  # no seat anywhere holds the whole grove
    rec = {"x": 600.0, "y": 450.0, "w": 23.0, "h": 14.0, "rot": 0.0, "kind": "plain", "shed": False, "wealth": 1.0}
    s.placed.append((600.0, 450.0, 23.0, 14.0))
    assert s._solve_homestead(rec) is None
    s._wants_grove = lambda *a: False  # type: ignore[method-assign]  # a farm with no grove keeps its yard-and-garden seat
    assert s._solve_homestead(dict(rec)) is not None


def test_a_farm_inside_a_city_wall_wants_no_grove() -> None:
    s = Settlement(800, 800, seed=1)
    s.meta(name="C", scale="city")
    s.M["wall"] = [(100, 100), (700, 100), (700, 700), (100, 700), (100, 100)]
    assert not s._wants_grove(400, 400)
    s.M["meta"]["inwall_groves"] = True
    assert s._wants_grove(400, 400)


def test_relax_gardens_south_skips_a_bundle_without_gardens():
    # defensive: a homestead bundle whose geom carries no garden beds is simply skipped (no shift, no error)
    s = Settlement(800, 800, seed=1)
    s.meta(name="V", scale="village", ftpx=2)
    rec = {"x": 100, "y": 100, "w": 23, "h": 14, "geom": {"house": (100, 100, 23, 14), "yard": (100, 120, 20, 16)}}  # no "gardens" key
    s._relax_gardens_south([rec])
    assert "gardens" not in rec["geom"]


def test_relax_gardens_south_nudges_an_east_shaded_garden_south():
    # a garden on the E lee side with a neighbor grove hard against its east, open ground south -> it shifts S
    s = Settlement(800, 800, seed=1)
    s.meta(name="V", scale="village", ftpx=2)
    s.grove_rects = [(340, 300, 16, 40)]  # a neighbor grove arm just east of the garden
    beds = [(320, 300, 12, 12)]  # garden east edge x=326; tree west edge=332 (in band)
    rec = {"x": 300, "y": 300, "w": 23, "h": 14, "geom": {"house": (300, 300, 23, 14), "yard": (300, 322, 20, 12), "gardens": list(beds)}}
    s._relax_gardens_south([rec])
    assert rec["geom"]["gardens"][0][1] > 300  # the bed moved SOUTH to clear the east tree
    # ...and a bundle that carries its parts' drawn boxes (269 B18) moves the bed's box with the bed
    rec = {"x": 300, "y": 300, "w": 23, "h": 14, "geom": {"house": (300, 300, 23, 14), "yard": (300, 322, 20, 12), "gardens": list(beds)}}
    rec["geom"]["boxes"] = {"house": (300, 300, 23, 14), "yard": (300, 322, 20, 12), "shed": None, "gardens": [(320, 300, 13, 13)]}
    s._relax_gardens_south([rec])
    moved = rec["geom"]["gardens"][0][1] - 300
    assert moved > 0 and rec["geom"]["boxes"]["gardens"][0][1] == 300 + moved, "the drawn box moved as far as the bed"


# ---- _rect_blocked: the hill/pond ELLIPSE branch -------------------------------------------
def test_rect_blocked_by_a_hill_or_pond_ellipse():
    s = _village()
    s.ellipses.append((300, 300, 80, 60))  # a hill/pond footprint
    assert s._rect_blocked((300, 300, 40, 26), fields=False) is True  # bed center inside the ellipse


# ---- _bundle_side_fits: the OUT-OF-BOUNDS bbox branch --------------------------------------
def test_bundle_side_fits_rejects_a_bbox_running_off_the_canvas():
    s = _village()
    geom = {"bbox": (5, 300, 40, 26), "gardens": []}  # cx - W/2 = -15 < 6 -> spills off the west edge
    assert s._bundle_side_fits(geom) is False


# ---- _garden_beds_clear: a bed landing on a paddy ------------------------------------------
def test_garden_beds_clear_rejects_a_bed_on_a_paddy():
    s = _nuc_village()  # field_polys carries a paddy over the east half (x >= 640)
    assert s._garden_beds_clear([(880, 400, 30, 20)], []) is False  # bed sits in the paddy


# ---- ring: a BIG house whose placement FAILS is un-counted ---------------------------------
def test_ring_decrements_the_big_count_when_a_placement_fails():
    # every candidate lands on paddy (whole map is a field), so try_place fails; each 'big' that was
    # counted up must be counted back down, leaving the tally at zero.
    s = _nuc_village()
    s.field_polys.append([(0, 0), (1200, 0), (1200, 900), (0, 900)])  # the entire canvas is flooded paddy
    s._nbig = 0
    s.ring((100, 100, 500, 500), 8, 30, ["big"], max_big=10)
    assert s._nbig == 0  # each big incremented then decremented on its failed placement
    assert not s.M["houses"]  # nothing could be placed


def test_waterfront_seeds_line_both_banks_of_a_canal():
    import random as _r

    s = Settlement(1600, 1600, seed=1)
    s.meta(name="Wt", scale="village")
    canal = [(200, 200), (200, 700), (500, 1200)]  # a BENT canal (2 segments) so later seeds fall past the first
    seeds = s.waterfront_seeds(canal, 20, 60.0, _r.Random(3))
    assert len(seeds) == 20 and s.M["meta"]["settlement_form"] == "water_town"
    # seeds sit on BOTH banks (both sides of x=200), offset ~60px
    xs = [p[0] for p in seeds]
    assert any(x > 250 for x in xs) and any(x < 150 for x in xs)
    # record=False leaves meta untouched
    s2 = Settlement(1600, 1600, seed=1)
    s2.meta(name="Wt2", scale="village")
    s2.waterfront_seeds(canal, 6, 60.0, _r.Random(1), record=False)
    assert "settlement_form" not in s2.M["meta"]


def test_line_seeds_strings_along_the_line_and_records_form():
    import random as _r

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="Ln", scale="village")
    pts = s.line_seeds((400, 400), (400, 1000), 80, 40, _r.Random(3))
    assert len(pts) == 80
    assert s.M["meta"]["settlement_form"] == "linear"  # recorded (a twin-detector axis)
    assert all(abs(p[0] - 400) <= 40 + 1e-9 for p in pts)  # a vertical line: x stays within the band
    assert max(p[1] for p in pts) - min(p[1] for p in pts) > 400  # strung along the length
    # record=False leaves meta untouched
    s2 = Settlement(1000, 1000, seed=1)
    s2.meta(name="L2", scale="village")
    s2.line_seeds((0, 0), (100, 0), 5, 10, _r.Random(1), record=False)
    assert "settlement_form" not in s2.M["meta"]


def test_scatter_seeds_spreads_over_area_and_records_dispersed():
    import random as _r

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="Sc", scale="village")
    pts = s.scatter_seeds(600, 600, 200, 300, 150, _r.Random(5))
    assert len(pts) == 150
    assert s.M["meta"]["settlement_form"] == "dispersed"  # recorded (a twin-detector axis)
    assert all(((p[0] - 600) / 200) ** 2 + ((p[1] - 600) / 300) ** 2 <= 1.0 + 1e-6 for p in pts)  # within the ellipse
    # an even (area-uniform) scatter fills the ellipse, not clumped at the center
    assert sum(1 for p in pts if math.hypot(p[0] - 600, p[1] - 600) > 150) > 30
    # record=False leaves meta untouched
    s2 = Settlement(1000, 1000, seed=1)
    s2.meta(name="S2", scale="village")
    s2.scatter_seeds(500, 500, 100, 100, 5, _r.Random(1), record=False)
    assert "settlement_form" not in s2.M["meta"]


def test_ring_drops_candidates_severed_from_their_field_by_a_road():
    # a road along the fan's south flank: ring candidates ACROSS it can never reach the field
    # (hoshizora's south-of-road farmhouse), so they are dropped rather than seated
    s = _town()
    s.road([(-50, 620), (1050, 620)])
    s.paddy_field((200, 200, 600, 600), "", "f", amp=20)
    s.ring(("poly", s.field_polys[0]), 40, 60, ["plain"])
    s.farmsteads()
    assert s.M["houses"]  # the near side seats normally
    assert all(h["y"] < 620 for h in s.M["houses"])


# ---- feature 118: the composed RollingMixin surface ----------------------------------------------
# The one thing a package split can break SILENTLY. A member dropped by the transformer yields a
# package that imports cleanly, type-checks cleanly under mypy --strict, and draws nothing - it
# surfaces only when whichever generator calls that member happens to run. A member defined TWICE
# yields a working import, a clean typecheck, and one silently dead implementation, because the MRO
# just picks the first base. Contract: specs/118-rolling-package/contracts/mixin-surface.md.

_ROLLING_SURFACE = frozenset(
    {
        # public - called from pool gens, wip/, other engine modules and tests
        "farmsteads",
        "headman",
        "line_seeds",
        "ring",
        "roll_village",
        "scatter_seeds",
        "sun_corridor",
        "waterfront_seeds",
        "west_sun_lane",
        # private - reached through self., including from OUTSIDE the package
        "_bbox_of",
        "_bundle_common_fits",
        "_bundle_fits",
        "_bundle_geom",
        "_bundle_side_fits",
        "_closest_on_seg",
        "_east_trees",
        "_farmsteads_bundle",
        "_farmsteads_legacy",
        "_field_adjacent",
        "_garden_beds",
        "_garden_beds_clear",
        "_garden_shaded",
        "_gardens_sun_ok",
        "_kura_side",
        "_nearest_field_point",
        "_nearest_placed_point",
        "_perim_bbox",
        "_perim_poly",
        "_place_bundle",
        "_place_bundle_nucleated",
        "_poly_bboxes",
        "_rect_blocked",
        "_rect_corners",
        "_rect_hits",
        "_rect_on_water",
        "_relax_gardens_south",
        "_slide",
        "_solve_homestead",
        "_sun_corridor_ok",
        "_water_obstacles",
        "_yard_sun_conflict",
        # class-level DATA, not a callable - a callable-only census would not notice it going
        # missing, which is the extra test feature 112 had to write after the fact
        "_NUC_SIDES",
    }
)


def _own_members(cls: type) -> set[str]:
    """Every non-dunder name this class body defines - data attributes included, not just callables."""
    return {k for k in vars(cls) if not k.startswith("__")}


def _rolling_sub_mixins() -> list[type]:
    from l7r.diagram.settlement.rolling import RollingMixin

    return [c for c in RollingMixin.__mro__ if c is not RollingMixin and c is not object]


def test_no_member_of_the_pre_split_rolling_surface_is_lost():
    # SUPERSET, not equality, deliberately: a later decomposition legitimately adds named private
    # helpers, and equality would turn every such change into a contract edit - training a reader to
    # bump the frozenset without thinking, which is the reflex that lets a real subtraction through.
    # This feature is itself that case: the roll_village stage split adds seven _roll_* members.
    from l7r.diagram.settlement.rolling import RollingMixin

    composed = set().union(*(_own_members(c) for c in RollingMixin.__mro__))
    assert composed >= _ROLLING_SURFACE, f"missing={sorted(_ROLLING_SURFACE - composed)}"


def test_no_rolling_member_is_defined_in_two_sub_mixins():
    # C1 cannot see this: a name defined in two bases still appears in the union, so a duplicate
    # passes C1, passes the import, passes mypy --strict, and runs whichever definition the MRO
    # reaches first - leaving the other as dead code a future reader will edit believing it is live.
    # The transformer refuses such a partition, but the transformer is a one-shot script; this test
    # outlives it and covers the member somebody adds by hand later.
    seen: dict[str, str] = {}
    dupes: list[str] = []
    for cls in _rolling_sub_mixins():
        for name in _own_members(cls):
            if name in seen:
                dupes.append(f"{name} in both {seen[name]} and {cls.__name__}")
            seen[name] = cls.__name__
    assert not dupes, f"defined twice: {sorted(dupes)}"


def test_bundle_common_fits_refuses_a_grove_on_a_tread_and_a_shaded_bundle() -> None:
    """Feature 146: two of the bundle's refusal reasons - a yashikirin planted across a lane's drawn tread
    (feature 126's finding: `_rect_blocked` tests keep-out polygons and says nothing about a tread), and a
    bundle whose sun corridor is closed."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(1200, 1200, seed=1)
    s.meta(name="B", scale="hamlet", ftpx=1, down_deg=90, windward="N")
    geom = {
        "house": (600.0, 600.0, 56.0, 30.0),
        "yard": (600.0, 640.0, 34.0, 22.0),
        "groves": [(600.0, 520.0, 90.0, 26.0), (540.0, 600.0, 26.0, 90.0)],
    }
    s.lane([(300.0, 520.0), (900.0, 520.0)], width=6, worn=True)  # drawn, so it has a tread
    assert s._bundle_common_fits(geom) is False, "the north grove sits on the lane's tread"


def test_a_bundle_is_refused_when_its_house_or_its_grove_stands_on_a_drawn_tread():
    """`_rect_blocked`'s corridor test reads a CENTER; these two read the drawn tread by footprint.
    The grove arm arrived with the settlement-form knob (until it was rolled, only dispersed maps grew
    per-house groves and the scripted tier never rolled one), and every linear and dispersed hamlet
    then planted yashikirin across the connector."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    clean = {"house": (500.0, 500.0, 40.0, 26.0), "yard": (500.0, 560.0, 36.0, 26.0)}
    assert s._bundle_common_fits(clean), "nothing drawn yet"

    on_house = Settlement(1000, 1000, seed=1)
    on_house.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    on_house.treads.append(([(400.0, 500.0), (600.0, 500.0)], 3.0, [(400.0, 500.0), (600.0, 500.0)]))
    assert not on_house._bundle_common_fits(clean), "the house has a corner on the lane"

    on_grove = Settlement(1000, 1000, seed=1)
    on_grove.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    on_grove.treads.append(([(400.0, 300.0), (600.0, 300.0)], 3.0, [(400.0, 300.0), (600.0, 300.0)]))
    with_grove = {**clean, "groves": [(500.0, 300.0, 30.0, 20.0), (450.0, 500.0, 20.0, 30.0)]}
    assert not on_grove._bundle_common_fits(with_grove), "the windward grove is planted across the lane"


def test_the_sun_corridor_clears_a_bundle_that_has_no_yard_of_its_own() -> None:
    """A no-yard bundle (feature 150) has nothing of its own to keep sunny, so once it has been
    checked against the yards ALREADY standing there is nothing left to ask and it clears.

    Both directions are tested on purpose - this house may not shade a yard already placed, and this
    yard may not be shaded by a house already standing - and it is the second direction that has
    nothing to say here. The rule is opt-in, so the corridor is turned on explicitly; with it off
    every seat clears for a different reason and the branch is never reached."""
    s = Settlement(1000, 1000, seed=3)
    s.meta(name="V", scale="hamlet")
    s.sun_corridor(39)
    assert s._sun_corridor_ok({"house": (400.0, 400.0, 46.0, 28.0)}) is True, "no yard, no standing houses"

    # ...and it still answers about the OTHER direction: a standing house with a yard, shaded by this one
    # y grows southward, so a house shades a yard that lies just NORTH of it (smaller y)
    s.M["houses"] = [{"x": 400.0, "y": 340.0, "w": 46.0, "h": 28.0, "geom": {"house": (400.0, 340.0, 46.0, 28.0), "yard": (400.0, 360.0, 40.0, 20.0)}}]
    assert s._sun_corridor_ok({"house": (400.0, 400.0, 46.0, 28.0)}) is False, "it shades the standing yard"

    # with the corridor OFF nothing is refused, whatever stands where
    off = Settlement(1000, 1000, seed=3)
    off.meta(name="V", scale="hamlet")
    off.M["houses"] = list(s.M["houses"])
    assert off._sun_corridor_ok({"house": (400.0, 400.0, 46.0, 28.0)}) is True


def test_a_nucleated_bundle_whose_envelope_fits_but_no_side_passes_the_parts_rules_is_refused() -> None:
    """`_place_bundle_nucleated` (feature 227): the envelope stands clear, so the parts are laid out - and if no
    garden side passes the rules that read the parts (the wall rule, the eave gap, the sun), there is no bundle
    to return. Asked with the two collaborators patched on the instance."""
    from tests.settlement._builders import _nuc_village

    s = _nuc_village()
    s._envelope_blocked = lambda env: None  # type: ignore[method-assign]
    s._parts_fit = lambda geom: False  # type: ignore[method-assign]
    assert s._place_bundle_nucleated(300.0, 300.0, 23.0, 14.0) is None


def test_the_envelope_is_the_box_around_every_garden_side() -> None:
    """Feature 227 FR-001/D2: the envelope encloses the house, the yard, the kura and the garden on EITHER side -
    the largest configuration the roll can take - so a part laid inside it never needs ground it did not clear."""
    from tests.settlement._builders import _nuc_village

    s = _nuc_village()
    env = s._bundle_envelope(500.0, 500.0, 46.0, 28.0, shed=True)
    for side in s._NUC_SIDES:
        g = s._bundle_geom(500.0, 500.0, 46.0, 28.0, side, shed=True)
        for rect in (g["house"], g["yard"], g["shed"], *g["gardens"]):
            assert rect[0] - rect[2] / 2 >= env[0] - env[2] / 2 - 1e-6 and rect[0] + rect[2] / 2 <= env[0] + env[2] / 2 + 1e-6
            assert rect[1] - rect[3] / 2 >= env[1] - env[3] / 2 - 1e-6 and rect[1] + rect[3] / 2 <= env[1] + env[3] / 2 + 1e-6
    assert env[2] > 46.0 + 2 * 0.48 * 46.0 - 1e-6, "wider than the house plus a garden on both walls"


def test_envelope_blocked_answers_clear_ground_one_neighbor_or_refused() -> None:
    """Feature 227: None on clear ground, the ONE placed box that overlaps it on clear ground (so the placer can make its
    single computed move), True when the ground refuses it or two boxes overlap it."""
    from tests.settlement._builders import _nuc_village

    s = _nuc_village()
    s.placed = type(s.placed)([]) if hasattr(s.placed, "__iter__") else []
    assert s._envelope_blocked((500.0, 500.0, 120.0, 90.0)) is None
    s.placed.append((560.0, 500.0, 60.0, 40.0))
    assert s._envelope_blocked((500.0, 500.0, 120.0, 90.0)) == (560.0, 500.0, 60.0, 40.0)
    s.placed.append((440.0, 500.0, 60.0, 40.0))
    assert s._envelope_blocked((500.0, 500.0, 120.0, 90.0)) is True, "two neighbors: no single move clears both"
    assert s._envelope_blocked((30.0, 500.0, 120.0, 90.0)) is True, "off the canvas margin"


def test_the_one_computed_move_clears_a_single_neighbor_by_the_measured_overlap() -> None:
    """Feature 227 FR-002 (the GM: "measuring the distance to the neighbor and then moving however much the correct
    amount is"): a seat whose envelope overlaps one placed box is shifted once by the overlap plus the 2 px margin,
    along the axis that needs the smaller push, away from that neighbor - and seated there, clear of it."""
    from tests.settlement._builders import _nuc_village

    s = _nuc_village()
    s._parts_fit = lambda geom: True  # type: ignore[method-assign]
    s.placed.append((500.0 - 23.0 - 15.0, 500.0, 40.0, 20.0))  # a box on the house's own west wall: it overlaps every configuration's box
    got = s._place_bundle_nucleated(500.0, 500.0, 46.0, 28.0)
    assert got is not None
    cx, cy, geom = got
    assert cx > 500.0 and cy == 500.0, "moved east, along the axis of the smaller overlap, away from the neighbor"
    assert s._envelope_blocked(geom["bbox"]) is None, "...by exactly enough to clear it"
    assert s._seat_search["placer_calls"] == 1 and s._seat_search["positions"] <= 9, "the union, then at most one rectangle and one move per configuration"


def test_parts_fit_refuses_a_house_whose_wall_stands_on_the_bund() -> None:
    """Feature 227: the parts' rules run once at the seat - the first of them the wall rule against the paddy,
    which the envelope test (nine points at the chord's own keep-out) cannot stand in for."""
    from tests.settlement._builders import _nuc_village

    s = _nuc_village()  # the paddy east of x = 640
    on_the_bund = s._bundle_geom(630.0, 300.0, 46.0, 28.0, "W")  # the house's east wall 13 px into the paddy
    assert s._parts_fit(on_the_bund) is False
    clear = s._bundle_geom(500.0, 300.0, 46.0, 28.0, "W")
    assert s._parts_fit(clear) is True


def test_bundle_side_fits_refuses_a_bundle_outside_the_bounding_ring() -> None:
    """The dispersed path's side test (the town's and the village's placer): a bundle whose box reaches outside the
    settlement's bounding ring - a walled town - is refused before any ground test."""
    from tests.settlement._builders import _nuc_village

    s = _nuc_village()
    s.bound = [(0.0, 0.0), (300.0, 0.0), (300.0, 300.0), (0.0, 300.0)]
    assert s._bundle_side_fits(s._bundle_geom(500.0, 500.0, 46.0, 28.0, "E")) is False
    assert s._bundle_side_fits(s._bundle_geom(150.0, 120.0, 46.0, 28.0, "E")) is True
    s.bound = None
    assert s._bundle_side_fits(s._bundle_geom(20.0, 500.0, 46.0, 28.0, "E")) is False, "...and one whose box reaches past the canvas margin"
    assert s._bundle_side_fits(s._bundle_geom(600.0, 500.0, 46.0, 28.0, "E")) is False, "...and one whose east garden bed lies on the paddy at x = 640"
    assert s._bundle_side_fits(s._bundle_geom(600.0, 500.0, 46.0, 28.0, "W")) is True, "the same house with its garden on the west wall"


def test_bundle_side_fits_refuses_a_layout_whose_lot_fixture_found_no_seat() -> None:
    """Feature 280 M21/M22 carried into 287: a layout marked `unlaid` (its bath room or wood shed found no seat) is refused
    even where every ground test would pass - the envelope admits a household only with room for every part it keeps."""
    from tests.settlement._builders import _nuc_village

    s = _nuc_village()
    geom = s._bundle_geom(600.0, 500.0, 46.0, 28.0, "W")
    geom.pop("unlaid", None)
    assert s._bundle_side_fits(geom) is True, "the case: this layout fits on its ground"
    geom["unlaid"] = "FixtureUnlaid: bath"
    assert s._bundle_side_fits(geom) is False, "...and is refused once a fixture of its lot is unlaid"


def _village_with_houses(seed: int = 1, pin: str | None = None) -> Settlement:
    s = Settlement(1600, 1600, seed=seed)
    s.meta(name="V", scale="village", ftpx=2)
    s.M["houses"] = [{"x": x, "y": y, "w": 23.0, "h": 14.0} for x, y in ((760, 760), (800, 760), (760, 800), (800, 800))]
    if pin:
        s.knob_pins["cremation_seat"] = pin
    return s


def test_a_village_cremation_ground_stands_apart_and_on_its_own_draws_no_jizo() -> None:
    """Research 530 and the GM's ruling of 2026-09-27 (feature 273): a village draws its own cremation ground, 120 ft
    clear of the houses, near their middle, down the fall line where clear. Feature 280 M71 (research 700): the six jizo
    stand at a burial ground's entrance, and a cremation ground on its own draws none."""
    from l7r.diagram.settlement.civic_grounds.edge_seat import rect_gap

    s = _village_with_houses(pin="apart")
    s._roll_cremation(90.0, [(780.0, 700.0), (780.0, 660.0)])  # the shrine's approach runs north of the houses
    (g,) = s.M["cremation_grounds"]
    assert s.M["meta"]["cremation_seat"] == "apart" and "cremation_seat_note" not in s.M["meta"]
    assert g["y"] > 800, "below the houses, down the fall line"
    assert min(rect_gap((g["x"], g["y"], g["w"], g["h"]), (h["x"], h["y"], h["w"], h["h"])) for h in s.M["houses"]) >= s.px(120)
    assert math.dist((g["x"], g["y"]), (780, 780)) <= s.px(650)
    assert "jizo" not in g


def test_beside_the_burial_ground_says_so_while_the_village_draws_none() -> None:
    s = _village_with_houses(pin="beside_burial")
    s._roll_cremation(90.0, [(780.0, 700.0)])
    assert s.M["meta"]["cremation_seat_note"].startswith("beside the burial ground")
    assert s.M["cremation_grounds"]


def test_the_cremation_seat_knob_rolls_both_and_refuses_nonsense() -> None:
    seen = {(_s := _village_with_houses(seed=k), _s._roll_cremation(90.0, [(780.0, 700.0)]), _s.M["meta"]["cremation_seat"])[2] for k in range(1, 30)}
    assert seen == {"apart", "beside_burial"}
    with pytest.raises(ValueError, match="cremation_seat"):
        _village_with_houses(pin="in_the_well")._roll_cremation(90.0, [(780.0, 700.0)])


def test_no_seat_draws_no_cremation_ground() -> None:
    s = _village_with_houses(pin="apart")
    s.M["fields"] = [{"outline": [(0, 0), (1600, 0), (1600, 1600), (0, 1600)]}]
    s.M["dry_plots"] = [{"poly": [(0, 0), (1600, 0), (1600, 1600), (0, 1600)]}]  # every seat on a dry plot
    s._roll_cremation(90.0, [(780.0, 700.0)])
    assert s.M["meta"]["cremation_ground"] == "no seat" and not s.M["cremation_grounds"]


def test_a_hamlet_draws_no_cremation_ground_shrine_or_headman() -> None:
    """FR-003 (feature 273): within its district the village alone keeps the shrine, the headman's house and the
    cremation ground. The roller's civic stage draws nothing for a hamlet, and no shipped hamlet carries any of them."""
    import glob
    import json

    s = Settlement(1600, 1600, seed=1)
    s.meta(name="H", scale="hamlet", ftpx=1)
    s._roll_civic({"gateway": (800.0, 800.0)}, "hamlet", True, 0.0, 1.0)
    assert not s.M["cremation_grounds"] and not s.M["shrines"] and not s.M["torii"]
    for path in glob.glob("pool/hamlets/*/*.json"):
        with open(path, encoding="utf-8") as fh:
            m = json.load(fh)
        assert not m.get("cremation_grounds") and not m.get("shrines") and not m.get("religious"), path
        assert not any(h.get("role") == "headman" for h in m.get("houses", [])), path


# ---- feature 276 FR-003: the placed-house index answers every fit rule exactly as the linear scans did -------------


class _AllOf:
    """A stand-in for a PointGrid that returns every entry: the linear scan the index replaced."""

    def __init__(self, entries):  # type: ignore[no-untyped-def]
        self.entries = list(entries)

    def near(self, *_a, **_k):  # type: ignore[no-untyped-def]
        return self.entries


@pytest.mark.parametrize("nucleated", [True, False])
def test_the_house_and_placed_indexes_answer_every_fit_rule_as_the_scans_did(nucleated: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    import random

    from l7r.diagram.settlement.rolling import fit

    s = Settlement(1800, 1800, seed=11)
    s.meta(name="I", scale="hamlet", ftpx=1, toscale=True, households=15, down_deg=90, water_flow=90, nucleated=nucleated)
    s._nucleated = nucleated
    s.sun_corridor(39)
    r = random.Random(276)
    for i in range(160):  # a dense grid, so every rule has neighbors to read
        s.try_place(200 + (i % 13) * 105 + r.uniform(-25, 25), 200 + (i // 13) * 105 + r.uniform(-25, 25), "plain")
    houses = s.M["houses"]
    assert len(houses) >= 40 and isinstance(houses, fit.Indexed), "non-vacuity: many houses standing, in the versioned list"

    def rules(geom):  # type: ignore[no-untyped-def]
        return (
            s._house_too_near_a_neighbor(geom["house"]),
            s._sun_corridor_ok(geom),
            s._gardens_sun_ok(geom),
            s._yard_sun_conflict(geom) if geom.get("yard") is not None else None,
            s._bundle_side_fits(geom),
            s._envelope_blocked(geom["bbox"]),
        )

    cands = []
    for _ in range(400):
        x, y = r.uniform(150, 1650), r.uniform(150, 1650)
        side = r.choice(s._NUC_SIDES) if nucleated else "E"
        cands.append(s._bundle_geom(x, y, 30.0, 20.0, side, False))
    indexed = [rules(g) for g in cands]
    monkeypatch.setattr(fit, "houses_meeting", lambda hs, _box: list(hs))
    real_reach = s._reach_index
    monkeypatch.setattr(s, "_reach_index", lambda reg, key: _AllOf(real_reach(reg, key).near(900.0, 900.0, 5000.0)) if key == "placed_reach" else real_reach(reg, key))
    linear = [rules(g) for g in cands]
    assert indexed == linear
    assert sum(1 for v in indexed if v[0]) and sum(1 for v in indexed if not v[4]), "non-vacuity: the eave gap and the overlap both fire"


def test_a_house_moved_in_place_is_not_answered_from_its_old_box() -> None:
    """`_solve_homestead` moves a record; the house index must see the move (the list's version is bumped there)."""
    from l7r.diagram.settlement.rolling import fit

    houses = fit.Indexed([{"x": 100.0, "y": 100.0, "w": 30.0, "h": 20.0}])
    assert fit.houses_meeting(houses, (90, 90, 110, 110))
    houses[0]["x"] = 900.0
    houses._bump()
    assert not fit.houses_meeting(houses, (90, 90, 110, 110)) and fit.houses_meeting(houses, (890, 90, 910, 110))


def test_the_eave_gap_ignores_an_abandoned_neighbor_and_flags_a_standing_one():
    # feature 276: the indexed eave-gap scan still skips a derelict (no roof left to shed) and still flags a house
    s = _village()
    s.M["houses"].append({"x": 330.0, "y": 300.0, "w": 40.0, "h": 26.0, "kind": "abandoned"})
    assert s._house_too_near_a_neighbor((300.0, 300.0, 40.0, 26.0)) is False
    s.M["houses"].append({"x": 330.0, "y": 300.0, "w": 40.0, "h": 26.0, "kind": "plain"})
    assert s._house_too_near_a_neighbor((300.0, 300.0, 40.0, 26.0)) is True


def test_a_quarter_turned_neighbor_is_measured_on_its_drawn_quad(monkeypatch: pytest.MonkeyPatch) -> None:
    """The drip-line rule is ONE predicate (feature 287, FR-003): `eave_gap` measures wall to wall on the drawn, rotated
    quads, and the placer and the gate both read it. The violating case: a neighbor recorded 20 x 60 and turned a quarter
    stands 60 wide along x, so an UNROTATED box (the gate's old measure) sees a wide gap where the walls stand closer than
    the eave gap - the placer refuses the seat, and the one measure says why."""
    from l7r.diagram.settlement import FARMHOUSE_EAVE_GAP_FT
    from l7r.diagram.settlement._geom import eave_gap

    s = _village()
    monkeypatch.setattr(s, "_house_rot", lambda _x, _y: 0.0)
    near = s.px(FARMHOUSE_EAVE_GAP_FT) - 1.0  # a wall gap under the rule
    cand = {"x": 300.0, "y": 300.0, "w": 40.0, "h": 26.0, "rot": 0.0}
    turned = {"x": 300.0 + 20.0 + 30.0 + near, "y": 300.0, "w": 20.0, "h": 60.0, "rot": 90.0, "kind": "plain"}
    unrotated = abs(turned["x"] - cand["x"]) - (cand["w"] + turned["w"]) / 2  # the retired measure
    assert unrotated >= s.px(FARMHOUSE_EAVE_GAP_FT), "the unrotated box would have admitted this pair"
    assert eave_gap(cand, turned) == pytest.approx(near), "the drawn walls stand `near` apart"
    s.M["houses"].append(turned)
    assert s._house_too_near_a_neighbor((300.0, 300.0, 40.0, 26.0)) is True, "the placer refuses the seat on the drawn quad"
    turned["x"] += s.px(3.0) + 1.0  # past the rule and the placer's hair of margin
    assert s._house_too_near_a_neighbor((300.0, 300.0, 40.0, 26.0)) is False
    assert eave_gap(cand, turned) >= s.px(FARMHOUSE_EAVE_GAP_FT)


def test_the_sun_rules_pass_over_a_neighbor_record_with_no_bundle():
    # feature 276: a drawn house with no `geom` (no yard, no garden, no grove) inside the indexed reach box has nothing
    # the corridor or the yard-sun rule can read, so both pass it over
    s = _village()
    s.meta(name="V", scale="village", ftpx=2, toscale=True)
    s.sun_corridor(39)  # the rule is opt-in; the scripted path asks for it
    geom = s._bundle_geom(300, 300, 40, 26)
    s.M["houses"].append({"x": 300.0, "y": 260.0, "w": 30.0, "h": 20.0, "kind": "plain"})  # north: in the corridor's box
    assert s._sun_corridor_ok(geom) is True
    yard = geom["yard"]
    s.M["houses"].append({"x": yard[0], "y": yard[1] + yard[3] / 2 + 11, "w": 10.0, "h": 10.0, "kind": "plain"})  # the yard's strip
    assert s._yard_sun_conflict(geom) is False


def test_the_bundle_prescreen_refuses_off_the_bound_on_a_placed_box_and_on_a_sun_rule(monkeypatch):
    # feature 276 (D9a): three of `_bundle_refused`'s conjuncts - a bbox corner outside the bounding ring, a placed box
    # inside the 2 px margin, a sun rule - and nothing refused on open ground
    s = _village()
    geom = s._bundle_geom(300, 300, 40, 26)
    assert s._bundle_refused(geom) is False
    s.bound = [(290, 290), (600, 290), (600, 600), (290, 600)]
    assert s._bundle_refused(geom) is True
    s.bound = None
    s.placed.append((300.0, 300.0, 20.0, 20.0))
    assert s._bundle_refused(geom) is True
    s.placed.clear()
    monkeypatch.setattr(Settlement, "_gardens_sun_ok", lambda self, g: False)
    assert s._bundle_refused(geom) is True


def test_slide_stops_where_the_free_ground_refuses_the_next_step():
    # feature 276 (D9): the step the pre-screen refuses (a placed box in the way) ends the slide where it stands
    s = _village()
    s.placed.append((240.0, 200.0, 40.0, 26.0))  # the first 2 px step comes within the 2 px margin of it
    assert s._slide(200, 200, 40, 26, lambda x, y: (400.0, 200.0), True) == (200, 200)


def test_the_stream_index_is_rebuilt_when_the_courses_change_and_kept_while_they_do_not():
    """Feature 281 (FR-005): `_rect_on_stream`'s cached index is reused while the same streams stand and rebuilt when the
    list, a record, a course or a width is replaced - a different list of the SAME length included, which a length key
    served stale."""
    s = _crop_settlement()
    s.M["streams"] = [{"poly": [(430, 300), (430, 500)], "w": 9}]
    rect = (450, 400, 20, 16)
    assert s._rect_on_stream(rect) is False
    kept = s._stream_idx_cache
    assert s._rect_on_stream((600, 400, 20, 16)) is False and s._stream_idx_cache is kept  # nothing changed: reused
    s.M["streams"][0]["poly"] = [(450, 300), (450, 500)]  # the course replaced in the same record
    assert s._rect_on_stream(rect) is True
    s.M["streams"][0]["w"] = 9  # the same width: the key holds
    kept = s._stream_idx_cache
    assert s._rect_on_stream(rect) is True and s._stream_idx_cache is kept
    s.M["streams"].append({"poly": [(0, 0), (10, 10)], "w": 4})  # a course added
    assert s._rect_on_stream(rect) is True and s._stream_idx_cache is not kept
    s.M["streams"] = [{"poly": [(900, 300), (900, 500)], "w": 9}, {"poly": [(0, 0), (1, 1)], "w": 4}]  # a new list, same length
    assert s._rect_on_stream(rect) is False


def test_a_bundles_parts_are_turned_and_boxed_as_the_turn_helpers_turn_and_box_them() -> None:
    """`_bundle_geom` takes its turn's cosine and sine once for every part: each part's center is where `turn_about` carries
    it and each box is `turned_box`'s, at several turns - and the yard, rolled once per seat, is the same for every side."""
    from l7r.diagram.settlement._geom import turn_about
    from l7r.diagram.settlement.rolling.bearing import turned_box

    s = _nuc_village()
    for rot in (0.0, 7.5, -23.0, 90.0):
        for side in s._NUC_SIDES:
            flat = s._bundle_geom(500.0, 500.0, 46.0, 28.0, side, True, rot=0.0)
            geom = s._bundle_geom(500.0, 500.0, 46.0, 28.0, side, True, rot=rot)
            for k in ("yard", "shed"):
                ((x, y),) = turn_about([(flat[k][0], flat[k][1])], 500.0, 500.0, rot)
                assert geom[k] == (x, y, flat[k][2], flat[k][3])
                assert geom["boxes"][k] == turned_box(geom[k], rot)
            assert [turned_box(g, rot) for g in geom["gardens"]] == geom["boxes"]["gardens"]
            assert geom["yard"][2:] == s._bundle_geom(500.0, 500.0, 46.0, 28.0, "SE", True, rot=rot)["yard"][2:]
