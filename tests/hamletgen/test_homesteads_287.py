"""Feature 287's homes guarantees at the homestead stage: the wells (H12; no clustered pocket since feature 374 wave 155), the
household bamboo on its house's bank (H01), the eaves stack against its steading (H35) and the woodpile form (H33).

Split from test_homesteads.py when feature 287 took it past the 1,000-line bar; the helpers stay there.
"""

import math

import pytest

import l7r.diagram.settlement.rolling.access as access_mod
from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from .test_homesteads import _WELL_HOUSES, _only_seat, _toy_hamlet


def test_a_well_past_the_crop_is_refused_now_the_pockets_water_every_house() -> None:
    """Feature 287, homes H12: a lattice seat whose wellhead would reach past the crop's box is not drawn."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.homesteads.wells import crop_extent_added

    boxed = SimpleNamespace(_crop_boxes=lambda city: [(900.0, 1100.0, 900.0, 1100.0)])
    assert crop_extent_added(boxed, (1000.0, 1000.0), [0.0], [0.0]) == 0.0
    assert crop_extent_added(boxed, (1100.0, 1000.0), [0.0], [0.0]) == pytest.approx(12.376)  # the glyph's roof half-size (feature 328)
    east = (1110.0, 1000.0)
    plan = SimpleNamespace(spec=SimpleNamespace(households=6), ftpx=1.0, well_siting="cluster")
    fake = _only_seat(*east)
    fake._crop_boxes = lambda city: [(950.0, 1100.0, 950.0, 1450.0)]  # type: ignore[attr-defined]
    assert hg.place_wells(fake, plan, _WELL_HOUSES) == 0, "the one legal seat reaches 22 px past the box"  # type: ignore[arg-type]


def test_no_clustered_household_carries_a_well_pocket_and_every_well_is_shared() -> None:
    """Feature 374 wave 155 (row 787, 0028: "the well, shared off the farmstead"): a clustered hamlet's seating lays no
    well inside any household's homestead, and every well `place_wells` draws is a shared well of the rolled siting."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    s, plan = _toy_hamlet(10, seed=4)
    stage_homesteads(s, plan)
    assert not any(h.get("well_pocket") for h in s.M["houses"]), "no household's homestead holds a well"
    hg.place_wells(s, plan, s.M["houses"])
    assert s.M["wells"] and {w.get("form") for w in s.M["wells"]} <= {"cluster", "lane"}


def test_a_household_bamboo_strip_stands_on_its_house_bank_and_names_its_house() -> None:
    """Feature 287, homes H01: a strip whose seat lies across the brook from its house is refused and the next tried; a
    seated strip records its owner (`plan.bamboo_of`, by its index among the stands)."""
    from l7r.diagram.hamletgen.homesteads.bamboo import household_bamboo
    from l7r.diagram.settlement._geom.water_index import crosses_a_stream

    got = 0
    for seed in range(40):
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        houses = [{"x": 200.0 + 120.0 * k, "y": 200.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for k in range(8)]
        s.M["streams"] = [{"poly": [[100.0, 180.0], [1300.0, 180.0]], "w": 2.0}]  # across every house's back
        rings = household_bamboo(s, plan, houses)
        for i, ring in enumerate(rings):
            cx, cy = sum(p[0] for p in ring) / 4, sum(p[1] for p in ring) / 4
            owner = plan.bamboo_of[i]
            assert not crosses_a_stream(owner, (cx, cy), s.M["streams"])
        got += len(rings)
    assert got, "some strips seated over the seeds"


def test_a_household_bamboo_strip_with_every_seat_across_the_brook_is_not_seated(monkeypatch: pytest.MonkeyPatch) -> None:
    """...and where EVERY seat the strip could take lies across the brook, none is seated: the refusal itself, asked
    directly (the pool's rolls reached it only by the accident of a layout, and feature 306's regenerated maps moved off it)."""
    from l7r.diagram.hamletgen.homesteads import bamboo

    asked: list[object] = []

    def across(house: object, strip: object, streams: object) -> bool:
        asked.append(strip)
        return True

    monkeypatch.setattr(bamboo, "crosses_a_stream", across)
    for seed in range(10):
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        houses = [{"x": 200.0 + 120.0 * k, "y": 200.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for k in range(8)]
        assert bamboo.household_bamboo(s, plan, houses) == []
    assert asked, "non-vacuity: seats reached the brook's question"


def test_a_household_bamboo_strip_gives_way_to_every_reserved_copse_seat() -> None:
    """Feature 280 keeps the copse two crowns off the bamboo, feature 287 woods W25 plants every reserved seat: a strip is
    refused where a household's reserved seat falls in its keep-out (`stand_spares_seats`), and the next side tried."""
    from l7r.diagram.hamletgen.homesteads.bamboo import household_bamboo
    from l7r.diagram.settlement.homestead_parts.bamboo_keepout import stand_spares_seats

    for seed in range(40):
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        house = {"x": 600.0, "y": 400.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"}
        first = household_bamboo(s, plan, [house])
        if not first:
            continue
        ring = first[0]
        seat = (sum(p[0] for p in ring) / 4, sum(p[1] for p in ring) / 4)
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        s.M["houses"] = [{**house, "wood_share": {"seats": [list(seat)]}}]
        for r in household_bamboo(s, plan, [house]):
            xs, ys = [p[0] for p in r], [p[1] for p in r]
            assert stand_spares_seats((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys), [seat], s.bscale)
        return
    raise AssertionError("no seed seated a strip")


# ---- homes H06: the shared sheds' pockets, reserved before any house ----------------------------------------------


def test_a_commons_hamlet_reserves_every_shared_shed_before_its_houses_and_draws_each(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes H06: on `detached_commons` the sheds' pockets are laid in the band first, the houses pack round
    them, and `draft_byres` draws a shed in every pocket - the count asked (`commons_byre_target`) is the count drawn."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.settlement.shrines_wells.byres import COMMONS_BYRE_GAP, commons_byre_target

    # the toy's bundles lay a bed or the well pocket where a flank door stands, and a corridor over its own parts is refused
    # since feature 287 M8 (`access.parts_clear`); the seating's count, not the parts, is under test here
    monkeypatch.setattr(access_mod, "parts_clear", lambda *a: True)
    s, plan = _toy_hamlet(12)
    s.pin_knob("byre_form", "detached_commons")
    stage_homesteads(s, plan)
    pockets = list(s._byre_pockets)
    assert len(pockets) == commons_byre_target(12) == 3
    assert all(math.dist(a, b) > COMMONS_BYRE_GAP for i, a in enumerate(pockets) for b in pockets[i + 1 :])
    for x, y in pockets:  # no house laps a pocket's ground
        assert all(abs(x - h["x"]) >= (h["w"] + 16.0) / 2 or abs(y - h["y"]) >= (h["h"] + 11.0) / 2 for h in s.M["houses"])
    drawn = s.draft_byres()
    assert drawn == pockets and s.M["meta"]["byre_target"] == 3 and len(s.M["byres"]) == 3


def test_a_band_with_no_ground_for_the_shared_sheds_refuses_the_site(monkeypatch: pytest.MonkeyPatch) -> None:
    """The reservation's refusal: a band holding fewer pockets than asked is refused, naming it, before any house."""
    from l7r.diagram.hamletgen.homesteads import stages
    from l7r.diagram.hamletgen.homesteads.capacity import SiteRefused

    s, plan = _toy_hamlet(12)
    s.pin_knob("byre_form", "detached_commons")
    monkeypatch.setattr(Settlement, "reserve_commons_byres", lambda self, seat, n: [])
    with pytest.raises(SiteRefused, match="no ground for 3 shared byres"):
        stages._seat_households(s, plan)
    assert not s.M["houses"]


def test_the_commons_pockets_widen_past_a_full_core_and_keep_off_the_paddy() -> None:
    """The band's core walled by placed ground: the pockets are found in the widened rounds, none on the paddy, none within
    the gap of another - and a band with no free ground at all yields fewer than asked (the caller refuses it)."""
    from l7r.diagram.settlement.shrines_wells.byres import COMMONS_BYRE_GAP

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="B", scale="hamlet", ftpx=1, toscale=True)
    seat = {"cx": 700.0, "cy": 500.0, "along": (1.0, 0.0), "out": (0.0, -1.0), "lat": 400.0, "dep": 150.0}
    s.placed.append((700.0, 500.0, 330.0, 250.0))  # the core (0.8 of the band) is built on
    s.field_polys.append([(0.0, 600.0), (1400.0, 600.0), (1400.0, 1400.0), (0.0, 1400.0)])
    pockets = s.reserve_commons_byres(seat, 20)
    assert len(pockets) == 4 and all(y < 600.0 - 10.0 for _x, y in pockets)
    assert all(math.dist(a, b) > COMMONS_BYRE_GAP for i, a in enumerate(pockets) for b in pockets[i + 1 :])
    full = Settlement(1400, 1400, seed=3)
    full.meta(name="F", scale="hamlet", ftpx=1, toscale=True)
    full.placed.append((700.0, 500.0, 1400.0, 1000.0))
    assert full.reserve_commons_byres(seat, 20) == []


def _brook_site() -> Settlement:
    """A brook between the cluster (west) and its field (east), a ford on it, and the tree's exit strip running west."""
    from tests.settlement._builders import seed_tree

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="F", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    field = [(800.0, 400.0), (1200.0, 400.0), (1200.0, 1000.0), (800.0, 1000.0)]
    s.M["fields"] = [{"outline": [list(p) for p in field]}]
    s.field_polys.append(field)
    s.M["streams"] = [{"poly": [[700.0, 0.0], [700.0, 1400.0]], "w": 6.0}]
    s.M["meta"]["brook_fords"] = [[700.0, 650.0]]
    seed_tree(s, (500.0, 700.0), (-1.0, 0.0), 300.0)
    return s


def test_a_household_bamboo_strip_whose_every_seat_is_in_a_plots_sun_is_not_seated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 315: a strip whose seat stands in a yard's or bed's sun ground at bamboo's reach is refused, and where every seat
    does, none is seated; the test itself, asked directly, is a rect against the sun boxes."""
    from l7r.diagram.hamletgen.homesteads import bamboo

    assert bamboo.in_the_sun(0.0, 0.0, 16.0, 22.0, [(20.0, 0.0, 15.0, 5.0)]), "overlapping a sun box"
    assert not bamboo.in_the_sun(0.0, 0.0, 16.0, 22.0, [(23.0, 0.0, 15.0, 5.0)]), "touching it"
    asked: list[object] = []

    def sunny(*args: object) -> bool:
        asked.append(args)
        return True

    monkeypatch.setattr(bamboo, "in_the_sun", sunny)
    for seed in range(10):
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        houses = [{"x": 200.0 + 120.0 * k, "y": 200.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for k in range(8)]
        assert bamboo.household_bamboo(s, plan, houses) == []
    assert asked, "non-vacuity: seats reached the sun's question"


def test_a_strip_keeps_its_gap_off_every_seated_part() -> None:
    """Feature 374 wave 149: the strip is seated before any farmstead is drawn, so it keeps `PART_GAP_FT` off each homestead's
    seated box - its own house's included."""
    from l7r.diagram.hamletgen.homesteads.bamboo import parts_hit

    shed = [(100.0, 100.0), (120.0, 100.0), (120.0, 110.0), (100.0, 110.0)]
    assert parts_hit(105.0, 105.0, 16.0, 22.0, [shed], 2.0), "on the shed"
    assert parts_hit(91.0, 105.0, 16.0, 22.0, [shed], 2.0), "1 ft off its west face, inside the gap"
    assert not parts_hit(85.0, 105.0, 16.0, 22.0, [shed], 2.0), "7 ft clear"
    assert not parts_hit(105.0, 105.0, 16.0, 22.0, [], 2.0), "nothing seated"


def test_seat_strips_seats_off_the_seated_parts_and_holds_them_as_fabric() -> None:
    """Feature 374 wave 149 (0075): `seat_strips` seats each farm's strip clear of every homestead as seated - each house's
    yard and every other farm's grove band stand where a strip would go - adds it to the plan's stands and holds it for the
    ways' fabric. The even houses keep groves (their bamboo is in the grove), the odd ones strips."""
    from l7r.diagram.hamletgen.homesteads import bamboo

    got = 0
    for seed in range(20):
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        s.M["houses"] = [
            {
                "x": 200.0 + 120.0 * k,
                "y": 300.0,
                "w": 46.0,
                "h": 28.0,
                "rot": 0.0,
                "shed_side": "N",
                "geom": {"boxes": {"yard": (200.0 + 120.0 * k, 260.0, 40.0, 30.0)}, **({"groves": [(200.0 + 120.0 * k, 345.0, 60.0, 20.0)]} if k % 2 == 0 else {})},
            }
            for k in range(8)
        ]
        n = bamboo.seat_strips(s, plan)
        held = s._household_strips  # type: ignore[attr-defined]
        assert n == len(plan.bamboo_polys) and len(held) == 2 * n, "each strip, and the ground between it and its house"
        assert s.M["meta"]["household_bamboo_wanted"] - s.M["meta"]["household_bamboo_no_room"] == n
        parts = [bamboo.box_poly((200.0 + 120.0 * k, 260.0, 40.0, 30.0)) for k in range(8)]
        parts += [bamboo.box_poly((200.0 + 120.0 * k, 345.0, 60.0, 20.0)) for k in range(0, 8, 2)]
        for ring, owner, kind in held[:n]:
            cx, cy = sum(p[0] for p in ring) / 4, sum(p[1] for p in ring) / 4
            assert owner is None and kind == "bamboo_stands" and not bamboo.parts_hit(cx, cy, 22.0 * s.bscale, 16.0 * s.bscale, parts, 0.0)
        got += n
    assert got, "some strips seated over the seeds"


def test_the_ground_between_a_house_and_its_strip_is_their_hull() -> None:
    """Feature 374 wave 149: no lane runs between a house and its bamboo (`across_a_lane`, feature 302) - with the strip seated
    first, the ways keep off the hull of the house's center and the strip's corners."""
    from shapely.geometry import Point, Polygon

    from l7r.diagram.hamletgen.homesteads.bamboo import between

    hull = Polygon(between((0.0, 0.0), [(30.0, -8.0), (46.0, -8.0), (46.0, 8.0), (30.0, 8.0)]))
    assert hull.contains(Point(20.0, 0.0)), "the gap between the house and its strip"
    assert not hull.contains(Point(20.0, 15.0)) and hull.area == 16.0 * 16.0 + 0.5 * 30.0 * 16.0


def test_a_stepped_strip_is_never_nearer_a_neighbors_house_than_its_own(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 374 wave 149 (the round-3 decide): stepped out up to 54 ft, a strip could stand at a neighbor's door - a seat
    nearer another house's center than its own is passed over for the next."""
    from l7r.diagram.hamletgen.homesteads import bamboo

    s, plan = _toy_hamlet(10, seed=1)
    plan.bamboo = "homestead"
    monkeypatch.setattr(bamboo, "HOUSEHOLD_BAMBOO_PREVALENCE", 1.1)
    monkeypatch.setattr(bamboo, "strip_refused", lambda *a, **k: False)
    own, behind = (400.0, 400.0), (400.0, 360.0)  # its neighbor 40 ft behind it
    # the first seat offered stands at the neighbor's door, the second beside its own house
    monkeypatch.setattr(bamboo, "strip_candidates", lambda *a, **k: iter([(400.0, 365.0, 22.0, 16.0), (440.0, 400.0, 16.0, 22.0)]))
    houses = [{"x": own[0], "y": own[1], "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "W"}, {"x": behind[0], "y": behind[1], "w": 46.0, "h": 28.0, "rot": 0.0}]
    rings = bamboo.household_bamboo(s, plan, houses[:1] + [{**houses[1], "geom": {"groves": [(0, 0, 1, 1)]}}])
    cx, cy = sum(p[0] for p in rings[0]) / 4, sum(p[1] for p in rings[0]) / 4
    assert (cx, cy) == (440.0, 400.0), "the seat at its neighbor's door passed over for its own"
