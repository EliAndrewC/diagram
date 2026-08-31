"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/urban.py`."""

import math

from l7r.diagram.settlement import Settlement, point_in_poly, rot_rect
from tests.settlement._builders import _city, _crop_settlement, _scatter_base_points, _town, _ward_city_with_samurai


def test_face_street_rot_without_streets_and_with_a_road():
    s = _town()
    r, d = s._face_street_rot(500, 500)  # no streets at all
    assert r is None and d > 1e17
    s.M["road"] = [[100, 500], [900, 500]]  # the road branch
    r, d = s._face_street_rot(500, 480)
    assert r is not None and d < 100


def test_merchant_storehouses_attaches_behind_shops_and_skips_corridors():
    # a kura is tucked behind a merchant's shopfront (its back, opposite the awning) unless that
    # back would land on a street - then it is skipped. rot=0 -> awning faces +y, back faces -y.
    s = _town()
    s.street([(100, 470), (900, 470)], width=24)  # sits just behind shop A's back -> A skipped
    s.building(500, 500, 40, 28, "merchant", rot=0)  # back (-y) runs into the street corridor
    s.building(300, 800, 40, 28, "merchant", rot=0)  # back faces open ground -> kura attached
    n = s.merchant_storehouses(count=6)
    assert n == 1 and len(s.M["storehouses"]) == 1


def test_commons_clears_the_urban_halo_around_buildings():
    s = _crop_settlement()
    s.building(300, 300, 40, 28, "merchant")  # axis-aligned
    s.building(430, 300, 40, 28, "laborer", rot=30)  # rotated - covered by its half-diagonal square
    s.building(1900, 1400, 40, 28, "shop")  # far outside the cover poly - the bbox prefilter drops it
    before = len(s.out)
    s.commons([(150, 150), (600, 150), (600, 500), (150, 500)], role="pasture")
    pts = _scatter_base_points(s.out[before:])
    assert pts  # the open ground beyond the halos still got its scatter
    halo = 30 * s.bscale - 0.06  # the SVG rounds coords to 0.1, so a base just OUTSIDE the halo can print ON its edge
    hd = math.hypot(20, 14) + halo
    for px, py in pts:
        assert not (280 - halo <= px <= 320 + halo and 286 - halo <= py <= 314 + halo)
        assert not (430 - hd <= px <= 430 + hd and 300 - hd <= py <= 300 + hd)


def test_marsh_clears_the_urban_halo_and_wellheads():
    s = _crop_settlement()
    s.building(300, 300, 40, 28, "merchant")
    s.well(460, 300)
    before = len(s.out)
    s.marsh([(150, 150), (600, 150), (600, 450), (150, 450)])
    lim = s.M["wells"][0]["vr"] + 20 * s.bscale - 0.06  # 0.1-rounding slack, as in the halo test
    halo = 30 * s.bscale - 0.06
    pts = _scatter_base_points(s.out[before:])
    assert pts
    for px, py in pts:
        assert not (280 - halo <= px <= 320 + halo and 286 - halo <= py <= 314 + halo)
        assert (px - 460) ** 2 + (py - 300) ** 2 > lim * lim


def test_merchant_residences_places_behind_band_and_skips_bad_spots():
    s = Settlement(1000, 1000, seed=1)
    s.road([(50, 500), (950, 500)])  # horizontal road
    s.building(850, 640, 40, 28, "shop", rot=180)  # a DEEP, far shop: raises the band depth so the others'
    #                                                       homes land well behind their own shop (clearance)
    s.building(300, 560, 40, 28, "shop", rot=180)  # its home lands ~(300,684), clear -> PLACES
    s.building(395, 560, 40, 28, "shop", rot=180)  # home ~95px away: clears overlap but within `spread` -> skipped
    s.building(600, 560, 40, 28, "shop", rot=180)  # its home ~(600,684) lands in the paddy below -> skipped
    s.paddy_field((540, 650, 660, 760), "", "p", amp=6)  # a paddy under the 600-shop's home (blocked ground)
    n = s.merchant_residences(count=6)
    homes = [b for b in s.M["buildings"] if b["kind"] == "merchant_large"]
    assert n >= 1 and homes and all(h["y"] > 600 for h in homes)  # placed BEHIND the band (further from the road)


def test_merchant_residences_respects_the_bound():
    s = Settlement(1000, 1000, seed=1)
    s.road([(50, 500), (950, 500)])
    s.building(850, 640, 40, 28, "shop", rot=180)  # deep+far: raises band depth so the 300-home clears its shop
    s.building(300, 560, 40, 28, "shop", rot=180)  # its home lands ~(300,684), clear of shops
    s.bound = [(0, 0), (1000, 0), (1000, 600), (0, 600)]  # bound excludes y > 600 -> the 300-home is outside -> skipped
    assert s.merchant_residences() == 0


def test_rowpack_blocked_zone_terminates_and_places_nothing():
    # a zone fully covered by an earlier structure yields no houses: every row scans past the
    # obstacle, the row pitch still advances, and the loop ends at the zone's south edge
    s = _city()
    s.building(400, 250, 420, 130, "civic")  # a compound covering the whole zone
    assert s.rowpack((200, 200, 600, 300), ["laborer"] * 30) == 0


def test_merchant_storehouse_is_never_drawn_across_a_neighbor():
    """A kura's overlap is legitimate only because it is an annex of ITS OWN shop. One tucked behind
    a narrow shopfront that happens to back onto the next lot's larger house is a defect - the case
    the old blanket storehouse exemption could not express, and which the matrix found twice."""
    s = _town()
    s.building(500, 500, 54, 36, "merchant", rot=0)
    s.building(500, 455, 86, 60, "merchant_large", rot=0)  # squarely BEHIND it (rot=0 puts the kura north)
    assert s.merchant_storehouses(count=4) == 0
    s2 = _town()
    s2.building(500, 500, 54, 36, "merchant", rot=0)
    assert s2.merchant_storehouses(count=4) == 1  # nothing behind it - the annex is fine


def test_building_refuses_commoners_inside_a_declared_samurai_ward():
    # GM 2026-08-02 (Minami): whole-interior top-up sweeps seated laborers and a merchant row
    # inside the ward fence. Once s.ward has run, the engine refuses those seats at s.building
    # itself - the one chokepoint every pack, frontage and gen-side top-up funnels through.
    s = Settlement(1000, 1000, seed=1)
    s.M["wall"] = [[200, 200], [800, 200], [800, 800], [200, 800]]
    s.ward("samurai", [(400, 795), (400, 400), (795, 400)], gates=[])
    assert s.building(600, 600, 16, 11, "laborer") is False
    assert all(b["kind"] != "laborer" for b in s.M["buildings"])
    assert s.building(600, 600, 16, 11, "samurai") is True  # a resident seats normally
    assert s.building(250, 250, 16, 11, "laborer") is True  # outside the fence - unaffected


def test_building_refuses_a_freestanding_servant_inside_the_ward():
    # barring the commoner kinds alone just handed their ground to the servant packs
    s = _ward_city_with_samurai((600, 600, "samurai", 0.0))
    assert s.building(700, 700, 10, 7, "servant") is False
    assert s.building(150, 150, 10, 7, "servant") is True  # outside the fence, unaffected


def test_servant_ranges_skips_a_house_too_narrow_to_carry_a_range():
    # below ~2.3x the range depth it stops reading as a range and starts reading as a cottage,
    # so the household simply gets none - its servants sleep under the master's roof
    s = _ward_city_with_samurai()
    s.building(600, 600, 8, 6, "samurai", 0.0)
    assert s.servant_ranges() == 0


def test_servant_ranges_with_no_samurai_ward_attaches_NOTHING() -> None:
    """The first guard: servants are a samurai-ward institution, so a map with no such interior has
    nowhere to put them - the answer is zero, not an error and not a range in a commoner quarter."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="W", scale="city", ftpx=3)
    s.building(500.0, 500.0, 30.0, 20.0, "samurai", 0.0)
    assert s.servant_ranges() == 0


def test_a_TILTED_board_caption_walks_its_whole_fallback_ladder() -> None:
    """Feature 174. The caption ladder in `boards.py` is four rungs deep and every one of them was
    added because a previous version shipped a defect:

      - the SATISFICE rung, because an unbounded `max(..., key=box_clearance)` has no lateral term;
      - the HUG CAP, for the same reason one rung down;
      - the FLOOR rung ("give up the MARGIN, never the 2 ft the rule asks");
      - and only then the old thirty-seat search, "so a board with genuinely nowhere to put its
        caption behaves as it always has".

    Measured across 48 cohort seeds, six boards took the unbounded fallback and every one landed at
    the coarse ladder's own +/-38.9 px lateral against bounds of 10.7-11.3 - "the GM's Kuwabata
    defect, reproduced by the fallback on maps nobody had looked at".

    A board TILTED beside a lane with its ground built up on both sides drives the ladder past its
    early rungs, which a board on open ground never does.
    """
    s = Settlement(1200, 1200, seed=21)
    s.meta(name="T", scale="town")
    s.lane([(200.0, 600.0), (1000.0, 600.0)], width=16)
    for i in range(10):  # frontage on both sides, so the easy seats are taken
        s.building(360.0 + i * 36, 636.0, 32.0, 22.0, "kura", 0.0)
        s.building(360.0 + i * 36, 566.0, 32.0, 22.0, "kura", 0.0)
    s.kosatsuba(600.0, 612.0, rot=-32.0)
    s.place_labels()

    captions = [lb for lb in s.M["labels"] if len(lb) > 5 and "notice board" in str(lb[5])]
    assert captions, "the board is captioned even where every easy seat is taken"


def test_a_range_never_walls_a_NEIGHBORS_DOORWAY() -> None:
    """A range is service accommodation on its household's own ground, never a wall across the next
    house's entrance - the ground behind a house is often the roji the row behind it faces. The
    neighbor here stands just north of the range's seat with its door face opening onto it (the door
    geometry is sampled the way `city_house_doors_unblocked` samples it, so the two agree)."""
    s = _ward_city_with_samurai((600.0, 600.0, "samurai", 0.0))
    s.building(619.0, 597.0, 10.0, 5.0, "shrine")  # its door face opens south, into the range's seat
    s.servant_ranges()
    door = next(o for o in s.M["buildings"] if o["kind"] == "shrine")
    for r in [b for b in s.M["buildings"] if b["kind"] == "servant"]:
        quad = rot_rect(r["x"], r["y"], r["w"], r["h"], r.get("rot", 0.0))
        assert not point_in_poly(door["x"], door["y"] + door["h"] / 2 + 0.8, quad), f"the doorway stays open: {r}"
