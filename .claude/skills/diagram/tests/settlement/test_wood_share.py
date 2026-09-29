"""Feature 287, woods W25 made absolute (plan D9): each household reserves its share of the wood floor at its seat - each
guarantee on constructed inputs that include the violating case, read through the placer's own predicate."""

from __future__ import annotations

import math

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom import CanopyArea, seg_dist
from l7r.diagram.settlement.homestead_parts.groves import HOMESTEAD_WOOD_FT2
from l7r.diagram.settlement.homestead_parts.wood_share import (
    BAR_MARGIN_PX,
    ReservedSeats,
    bundle_parts,
    copse_keepouts,
    in_keepouts,
    install_wood_shares,
    well_keepout,
    within_reach,
)
from l7r.diagram.settlement.rolling.access import corridor_clear, start_tree
from l7r.diagram.settlement.rolling.lot import record_parts

FLOOR, REACH = HOMESTEAD_WOOD_FT2[0], 90.0


def _open(W: float = 1400.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    s._house_rot = lambda x, y: 0.0  # type: ignore[method-assign]
    return s


def _area(seats: list[tuple[float, float]], r: float, cell: float = 2.0) -> float:
    canopy = CanopyArea(cell)
    for x, y in seats:
        canopy.add(x, y, r)
    return canopy.area


def test_the_keepouts_are_the_copses_own_figures_a_hair_stricter() -> None:
    """The occupancy disc of a solid part, a wellhead's wider disc, the sunny strip south of a yard and a bed and the
    morning lane east of a bed - each `village_grove`'s figure plus `BAR_MARGIN_PX`."""
    parts = {"house": (100.0, 100.0, 40.0, 30.0), "yard": (100.0, 140.0, 40.0, 20.0), "gardens": [(140.0, 100.0, 20.0, 20.0)], "well": (60.0, 150.0, 10.0, 10.0), "shed": None}
    circles, rects = copse_keepouts(parts, 22.0, 39.0, 12.0)
    assert circles[0] == (100.0, 100.0, 25.0 + 11.0 + 2.0 + BAR_MARGIN_PX), "the house: half its diagonal, the clump's radius, 2 px"
    assert (60.0, 150.0, 12.0 + 22.0 * 1.05 + 1.0 + BAR_MARGIN_PX) in circles, "the wellhead: its drawn half-size and 1.05 clumps"
    yard_sun = (100.0 - 33.0 - BAR_MARGIN_PX, 150.0 - 13.0 - BAR_MARGIN_PX, 100.0 + 33.0 + BAR_MARGIN_PX, 150.0 + 39.0 + 13.0 + BAR_MARGIN_PX)
    assert rects[0] == yard_sun, "the yard's sunny strip, 39 ft deep"
    assert rects[-1] == (150.0 - 13.0 - BAR_MARGIN_PX, 100.0 - 23.0 - BAR_MARGIN_PX, 150.0 + 24.0 + 11.0 + BAR_MARGIN_PX, 100.0 + 23.0 + BAR_MARGIN_PX), "the bed's morning lane"
    assert in_keepouts(100.0, 140.0, circles, rects) and in_keepouts(160.0, 100.0, circles, rects)
    assert not in_keepouts(100.0, 30.0, circles, rects), "behind the house, clear of every keep-out"
    assert not in_keepouts(100.0, 100.0 - 38.5, [(100.0, 100.0, 38.5)], []), "a disc's edge is not inside it (the planting's strict test)"


def test_a_household_on_open_ground_reserves_its_floor_behind_its_house() -> None:
    s = _open()
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    assert s._wood is wood
    geom = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    seats = wood.share(geom, 0.0, [])
    assert seats is not None
    assert _area(seats, wood.cr) >= FLOOR, "the crowns cover the floor"
    assert all(math.dist(p, (700.0, 700.0)) <= REACH for p in seats), "every seat within the dooryard copse's reach"
    assert all(not wood.seat_barred(x, y, (700.0, 700.0), wood.keepouts(geom), []) for x, y in seats), "and every one a legal seat"
    assert sum(1 for _x, y in seats if y < 700.0) > len(seats) / 2, "most of it behind the house"
    assert seats[0][1] < 700.0 - 14.0, "the first seat at the back"


def test_ground_that_cannot_hold_the_floor_refuses_the_seat() -> None:
    """The violating case: a paddy round the house but for its own bundle - no seat within reach, the homestead refused."""
    s = _open()
    install_wood_shares(s, FLOOR, REACH, 7.0)
    ring = [(600.0, 600.0), (800.0, 600.0), (800.0, 800.0), (600.0, 800.0)]
    hole_free = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    assert s._parts_fit(hole_free), "open ground: admitted"
    assert "wood" in hole_free and hole_free["wood"]
    s2 = _open()
    s2.field_polys.append(ring)
    wood = install_wood_shares(s2, FLOOR, REACH, 7.0)
    geom = s2._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    assert wood.share(geom, 0.0, []) is None
    assert not s2._parts_fit(s2._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0))


def test_a_seat_across_a_stream_is_refused() -> None:
    s = _open()
    s.M["streams"].append({"poly": [[600.0, 660.0], [800.0, 660.0]], "w": 6.0})
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    own = wood.keepouts(s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0))
    assert wood.seat_barred(700.0, 620.0, (700.0, 700.0), own, []), "across the brook from its house"
    assert not wood.seat_barred(760.0, 700.0 - 45.0 + 60.0 + 30.0, (700.0, 700.0), ([], []), []), "on its own bank"
    assert wood.seat_barred(700.0, 620.0, (700.0, 700.0), ([], []), [], banks=[]) is False, "no reach asked: nothing crossed"


def test_the_one_predicate_refuses_each_kind_of_ground() -> None:
    s = _open(400.0)
    s.field_polys.append([(300.0, 0.0), (400.0, 0.0), (400.0, 400.0), (300.0, 400.0)])
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    none: tuple[list[tuple[float, float, float]], list[tuple[float, float, float, float]]] = ([], [])
    assert wood.seat_barred(3.0, 200.0, (60.0, 200.0), none, []), "off the canvas margin"
    assert wood.seat_barred(200.0, 200.0, (60.0, 200.0), none, []), "past the reach"
    assert wood.seat_barred(290.0, 200.0, (250.0, 200.0), none, []), "on the crop's pad"
    assert wood.seat_barred(150.0, 200.0, (100.0, 200.0), none, [((150.0, 150.0), (150.0, 250.0))]), "on a corridor"
    assert not wood.seat_barred(150.0, 200.0, (100.0, 200.0), none, [((190.0, 150.0), (190.0, 250.0))]), "a corridor 40 px off"
    wood.file([(150.0, 250.0, 20.0)], [(100.0, 100.0, 120.0, 120.0)])
    assert wood.seat_barred(150.0, 240.0, (100.0, 200.0), none, []), "in a filed disc"
    assert wood.seat_barred(110.0, 110.0, (100.0, 160.0), none, []), "in a filed rectangle"
    assert not wood.seat_barred(150.0, 200.0, (100.0, 200.0), none, [])


def test_a_later_homestead_may_not_stand_over_a_reserved_seat_nor_share_its_ground() -> None:
    """The violating case in both directions: a neighbor whose house's keep-out covers a reserved seat is refused, and a
    second household's reservation counts only ground the first did not reserve."""
    s = _open()
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    first = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    seats = wood.share(first, 0.0, [])
    assert seats is not None
    covered = wood.commit(first, seats)
    assert covered >= FLOOR and wood.cells
    sx, sy = seats[0]
    over = s._bundle_geom(sx, sy, 46.0, 28.0, "SE", rot=0.0)
    assert wood.covers_a_seat(over), "a house standing on the seat"
    assert not s._parts_fit(s._bundle_geom(sx, sy, 46.0, 28.0, "SE", rot=0.0))
    far = s._bundle_geom(1100.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    assert not wood.covers_a_seat(far)
    second = s._bundle_geom(760.0, 560.0, 46.0, 28.0, "SE", rot=0.0)
    mine = wood.share(second, 0.0, [])
    assert mine is not None
    fresh = CanopyArea(2.0)
    for x, y in mine:
        fresh.add(x, y, wood.cr)
    assert len(fresh.cells - wood.cells) * 4.0 >= FLOOR, "its floor stands on ground the first did not reserve"


def test_a_corridor_through_reserved_seats_is_refused() -> None:
    s = _open()
    start_tree(s, (300.0, 300.0), (1.0, 0.0), 50.0)
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    geom = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    seats = wood.share(geom, 0.0, [])
    assert seats is not None
    wood.commit(geom, seats)
    sx, sy = seats[0]
    other = s._bundle_geom(1000.0, 1000.0, 46.0, 28.0, "SE", rot=0.0)
    assert wood.corridor_bars((sx - 100.0, sy), (sx + 100.0, sy))
    assert not corridor_clear(s, (sx - 100.0, sy), (sx + 100.0, sy), other)
    assert not wood.corridor_bars((sx - 100.0, sy + 400.0), (sx + 100.0, sy + 400.0))


def test_the_placer_seats_with_the_reservation_and_the_record_carries_it() -> None:
    """Through the placer: an admitted homestead's record carries its share (`wood_share`), the share is committed, and a
    household the reservation cannot hold is refused - the nucleated placer returns no seat."""
    s = _open()
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    assert s.try_place(700.0, 700.0, "plain")
    rec = s.M["houses"][-1]
    share = rec["wood_share"]
    assert share["r"] == wood.cr and share["ft2"] >= FLOOR and share["seats"] and wood.seats.n == len(share["seats"]), "committed"
    assert "wood" not in rec["geom"], "the seats ride on the record, once"
    assert ReservedSeats([rec]).disc_covers(share["seats"][0][0], share["seats"][0][1], 1.0)
    geom = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    geom["wood"] = [(1.0, 1.0)]
    s._wood = None
    bare = {"x": 0.0, "y": 0.0, "rot": 0.0}
    record_parts(s, bare, geom, None)
    assert "wood_share" not in bare, "no reservation installed: nothing recorded"


def test_the_shared_sheds_pockets_bar_the_seats_round_them() -> None:
    s = _open()
    s._byre_pockets = [(500.0, 500.0)]
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    assert wood.seat_barred(500.0, 520.0, (500.0, 560.0), ([], []), [])
    assert not wood.seat_barred(500.0, 600.0, (500.0, 560.0), ([], []), [])


def test_a_well_keeps_its_keepout_off_the_reserved_seats() -> None:
    s = _open()
    r = well_keepout(s)
    assert r == s._well_vr() + 22.0 * 1.05 + 1.0 + BAR_MARGIN_PX
    seats = ReservedSeats([{"wood_share": {"seats": [[100.0, 100.0]]}}, {"x": 0.0}])
    assert seats.disc_covers(100.0 + r - 1.0, 100.0, r) and not seats.disc_covers(100.0 + r + 1.0, 100.0, r)


def test_the_bundle_parts_and_the_reach_prefilter() -> None:
    s = _open()
    geom = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    parts = bundle_parts(geom)
    assert parts["house"] == geom["house"] and parts["gardens"] == list(geom["gardens"]) and parts["retirement"] is None
    geom["fixtures"] = {"retirement": (700.0, 650.0, 18.0, 15.0)}
    assert bundle_parts(geom)["retirement"] == (700.0, 650.0, 18.0, 15.0)
    segs = [((0.0, 0.0), (10.0, 0.0)), ((500.0, 500.0), (510.0, 500.0))]
    assert within_reach(segs, (5.0, 50.0), 60.0) == [segs[0]]


def test_ground_every_other_household_reserved_holds_no_share_and_a_moat_is_water() -> None:
    """A lattice whose every crown lies on ground already reserved adds nothing and the seat is refused; a moat is open
    water to the seats as a stream is."""
    s = _open()
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    wood.cells = {(i, j) for i in range(250, 450) for j in range(250, 450)}  # 400 x 400 px round the house, reserved
    assert wood.share(s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0), 0.0, []) is None
    s.M["moat"] = [[600.0, 640.0], [800.0, 640.0]]
    moated = install_wood_shares(s, FLOOR, REACH, 7.0)
    assert moated.ground.hard(700.0, 640.0 + 15.0) and not moated.ground.hard(700.0, 640.0 + 30.0), "22 ft wide: 11 + 11 + the margin"


def test_the_reservation_is_offered_behind_its_house_before_its_flanks() -> None:
    from l7r.diagram.settlement.homestead_parts.wood_share import FOCUS_DEPTH, seat_rank

    back, side = (0.0, -1.0), (1.0, 0.0)
    d = FOCUS_DEPTH * 90.0
    assert seat_rank(0.0, -d, back, side, d) == 0.0, "the focus, straight behind"
    assert seat_rank(0.0, -d - 20.0, back, side, d) < seat_rank(20.0, -d, back, side, d), "deeper before wider"
    turned = (1.0, 0.0), (0.0, 1.0)  # a house turned a quarter: its back is +x
    assert seat_rank(d, 0.0, *turned, d) == 0.0


def test_a_corridor_admitted_over_the_households_own_seats_sends_its_share_to_be_sought_again(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The share is asked before the dearer corridor; where the corridor then runs over one of the seats, the share is
    sought again with it standing - kept clear of every leg, or the homestead refused where it no longer fits."""
    from l7r.diagram.settlement.homestead_parts import wood_share as ws
    from l7r.diagram.settlement.rolling.access import legs

    s = _open()
    wood = install_wood_shares(s, FLOOR, REACH, 7.0)
    start_tree(s, (720.0, 300.0), (0.0, -1.0), 100.0)
    asked: list[int] = []
    real = ws.WoodShares.share

    def share(self, geom, rot, corridors):  # type: ignore[no-untyped-def]
        asked.append(len(corridors))
        return real(self, geom, rot, corridors)

    monkeypatch.setattr(ws.WoodShares, "share", share)
    geom = s._bundle_geom(720.0, 520.0, 46.0, 28.0, "SE", rot=0.0)
    assert s._parts_fit(geom)
    assert len(asked) == 2, "sought again once the corridor stood"
    assert all(seg_dist(x, y, a, b) >= wood.lane_gap for x, y in geom["wood"] for a, b in legs(geom["access"]))
    monkeypatch.setattr(ws.WoodShares, "share", lambda self, geom, rot, corridors: None if len(corridors) > 1 else real(self, geom, rot, corridors))
    assert not s._parts_fit(s._bundle_geom(720.0, 520.0, 46.0, 28.0, "SE", rot=0.0)), "no room left beside the corridor: refused"
    monkeypatch.setattr(ws.WoodShares, "share", lambda self, geom, rot, corridors: None)
    assert not s._parts_fit(s._bundle_geom(720.0, 520.0, 46.0, 28.0, "SE", rot=0.0)), "no share at all: refused before the corridor is sought"
