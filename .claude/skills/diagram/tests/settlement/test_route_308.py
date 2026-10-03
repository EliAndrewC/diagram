"""Feature 308, plan D3 (FR-005): a house's path routed round what stands where no straight corridor clears."""

from __future__ import annotations

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import access, route
from l7r.diagram.settlement.rolling.access import access_corridor, start_tree
from l7r.diagram.settlement.rolling.route import search, taut


def _open(W: float = 1400.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    return s


def test_the_search_finds_the_goal_round_a_wall_and_none_where_it_is_shut_in() -> None:
    wall = {(2, j) for j in range(-3, 4)}  # a wall across x = 2, open past y = +-4

    def goal(c: tuple[int, int]) -> tuple[float, float] | None:
        return (float(c[0]), float(c[1])) if c[0] >= 4 else None

    got = search(lambda c: c not in wall, goal, [(4.0, 0.0)], 10, 1.5)
    assert got is not None
    cells, q = got
    assert cells[0] == (0, 0) and q[0] >= 4 and not set(cells) & wall, "from the start, round the wall, to the goal"
    assert max(abs(cells[1][0]), abs(cells[1][1])) <= 2, "the first step off the start spans up to two cells (feature 314)"
    assert all(max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1 for a, b in zip(cells[1:], cells[2:], strict=False)), "...then eight-neighbor steps"
    assert search(lambda c: False, goal, [], 10, 1.5) is None, "shut in: no route"
    assert search(lambda c: True, goal, [(4.0, 0.0)], 2, 1.5) is None, "the goal beyond the search's reach: none"


def test_a_route_is_pulled_taut_through_the_leg_test_and_refused_when_it_cannot_be() -> None:
    pts = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)]
    never = lambda a, b, c: False  # noqa: E731
    assert taut(pts, lambda a, b: True, never, 5) == ((0.0, 0.0), (3.0, 0.0)), "a clear run: one leg"
    bent = [(0.0, 0.0), (1.0, 1.0), (2.0, 0.0)]
    assert taut(bent, lambda a, b: abs(a[0] - b[0]) <= 1.0, never, 5) == tuple(bent), "a leg the test refuses: two"
    assert taut(bent, lambda a, b: abs(a[0] - b[0]) <= 1.0, never, 1) is None, "...more legs than allowed: refused"
    assert taut(bent, lambda a, b: abs(a[0] - b[0]) <= 1.0, lambda a, b, c: True, 5) is None, "a turn back: refused"
    assert taut(bent, lambda a, b: False, never, 5) is None, "no leg admitted: refused"


def _hemmed(s: Settlement) -> dict:
    """A homestead whose every straight and round-the-gable run to the exit strip crosses one wide neighbor."""
    start_tree(s, (700.0, 450.0), (1.0, 0.0), 300.0)
    s.placed.append((700.0, 560.0, 500.0, 40.0))
    return s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)


def test_a_house_no_straight_corridor_reaches_is_routed_round_what_stands_only_where_the_tree_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)  # the corridor's own beds are test_access's
    s = _open()
    geom = _hemmed(s)
    assert access_corridor(s, geom) is None, "no straight run and no tree that routes: refused, as before"
    s = _open()
    geom = _hemmed(s)
    s._access.routed = True
    got = access_corridor(s, geom)
    assert got is not None and len(got) >= 3, "a path of two legs or more"
    assert abs(got[-1][1] - 450.0) < 1e-6 and 700.0 <= got[-1][0] <= 1000.0, "...ending on the exit strip"
    for a, b in zip(got, got[1:], strict=False):
        assert not access.seg_box_within(a, b, (700.0, 560.0, 500.0, 40.0), s._access.half), "...every leg clear of the neighbor"
    assert len(route.routed_corridors.__doc__ or "") > 0


def test_a_door_shut_in_has_no_route_and_its_search_is_remembered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)
    s = _open()
    geom = _hemmed(s)
    s.placed.extend([(400.0, 700.0, 60.0, 500.0), (1000.0, 700.0, 60.0, 500.0), (700.0, 950.0, 700.0, 60.0)])  # walled in all round
    s._access.routed = True
    calls: list[int] = []
    real = route._route_from
    monkeypatch.setattr(route, "_route_from", lambda *a: calls.append(1) or real(*a))
    assert access_corridor(s, geom) is None
    n = len(calls)
    assert n == 2, "the two dooryard doors each searched"
    assert access_corridor(s, geom) is None and len(calls) == n, "...once, while nothing standing changes"


def test_a_route_that_crosses_back_over_its_own_yard_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)
    monkeypatch.setattr(access, "leaves_its_yard", lambda *a, **k: False)
    s = _open()
    geom = _hemmed(s)
    s._access.routed = True
    assert access_corridor(s, geom) is None, "the yard rule every corridor keeps"


def test_a_grid_point_on_taken_ground_or_by_a_reserved_seat_is_shut() -> None:
    """The open ground the route searches: off the site's raster and the reserved wood seats, as well as the placed boxes."""

    class Ground:
        def point_taken(self, x: float, y: float) -> bool:
            return 800.0 < x < 1100.0

    class Wood:
        seats = type("Seats", (), {"n": 0})()  # what the standing memo's state reads

        def corridor_bars(self, a: tuple[float, float], b: tuple[float, float]) -> bool:
            return a[0] < 600.0

    s = _open()
    geom = _hemmed(s)
    s._access.routed = True
    s._free_ground = Ground()  # type: ignore[assignment]
    s._wood = Wood()  # type: ignore[assignment]
    mine = route.own_parts(s, geom, geom["boxes"]["house"], access.house_gap(s), s._access.half)
    run = route._route_from(
        s,
        s._access,
        access.doors_of(geom, s._access.half)[0],
        mine,
        None,
        s._access.half,
        access.house_gap(s),
        s._free_ground,
        s._wood,
        s._reach_index(s.placed, "placed_reach"),
        route.ROUTE_STEP_PX,
        lambda a, b: True,
        geom,
    )
    assert run is None, "east of the neighbor taken, west of it a reserved wood: no way round"


def test_a_search_starts_where_it_is_told_and_its_first_steps_are_judged() -> None:
    """Feature 314: the search starts at any cell of the map's grid; its first step may span two cells, and `first_ok` judges
    each - none admitted, none found."""

    def goal(c: tuple[int, int]) -> tuple[float, float] | None:
        return (float(c[0]), float(c[1])) if c[0] >= 14 else None

    got = search(lambda c: True, goal, [(14.0, 5.0)], 10, 1.5, (5, 5))
    assert got is not None and got[0][0] == (5, 5) and max(abs(got[0][1][0] - 5), abs(got[0][1][1] - 5)) <= 2, "a first step of two cells"
    assert search(lambda c: True, goal, [(14.0, 5.0)], 10, 1.5, (5, 5), lambda c: False) is None, "every first step refused"
    assert search(lambda c: True, goal, [], 10, 1.5, (5, 5)) is not None, "no aim: the start's own"


def test_a_routes_last_leg_onto_the_tree_is_judged_where_it_is_searched(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 314: a goal whose last leg onto the tree the standing ground refuses is no goal - the search goes on, and where
    every last leg is refused, no route. (The search kept off the household's own parts too until research R12 withdrew it.)"""
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)
    s = _open()
    geom = _hemmed(s)
    s._access.routed = True
    assert access_corridor(s, geom) is not None, "routed while the last legs stand clear"
    s = _open()
    geom = _hemmed(s)
    s._access.routed = True
    real = access.standing_ground
    monkeypatch.setattr(access, "standing_ground", lambda s_, a, b, memo: abs(b[1] - 450.0) > 1e-6 and real(s_, a, b, memo))
    assert access_corridor(s, geom) is None, "every last leg onto the tree refused: no goal"


def test_the_route_keeps_off_the_household_s_own_parts_each_by_its_leg_test_s_gap() -> None:
    """Feature 317 T06: the house by the house gap, the shed, byre, well and beds by the parts' gap, the fixtures by a corridor's
    half-width - but not the persimmon, held by the door since feature 315: the taut pull keeps the legs off its trunk."""
    s = _open()
    geom = {
        "house": (0.0, 0.0, 40.0, 20.0),
        "boxes": {"shed": (50.0, 0.0, 10.0, 10.0), "gardens": [(0.0, 60.0, 30.0, 20.0)], "fixtures": {"privy": (80.0, 0.0, 6.0, 6.0), "persimmon": (90.0, 40.0, 30.0, 30.0)}},
    }
    got = route.own_parts(s, geom, geom["house"], 12.0, 7.0)
    pgap = s.px(access.TREAD_HALF_FT + access.PART_MARGIN_FT)
    assert got[0] == ((0.0, 0.0, 40.0, 20.0), 12.0), "the house first, by the house gap"
    assert ((50.0, 0.0, 10.0, 10.0), pgap) in got and ((0.0, 60.0, 30.0, 20.0), pgap) in got, "the shed and the bed by the parts' gap"
    assert ((80.0, 0.0, 6.0, 6.0), 7.0) in got, "fixtures by the half-width"
    assert all(b[:2] != (90.0, 40.0) for b, _g in got), "...the persimmon left to the taut pull"
    assert len(got) == 4, "no byre or well, and the persimmon: none listed"


def test_each_layout_of_one_seat_is_routed_round_its_own_beds_and_asked_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 317 T06: the route is remembered per LAYOUT - two garden sides of one house and yard search their own routes (feature
    314's version searched one for the house and yard, so every layout took the route laid round the first one's beds)."""
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)
    s = _open()
    geom = _hemmed(s)
    s._access.routed = True
    other = {**geom, "boxes": {**geom["boxes"], "gardens": [(760.0, 760.0, 20.0, 20.0)]}}
    calls: list[int] = []
    real = route._route_from
    monkeypatch.setattr(route, "_route_from", lambda *a: calls.append(1) or real(*a))
    list(route.routed_corridors(s, s._access, geom))
    list(route.routed_corridors(s, s._access, other))
    assert len(calls) == 4, "two doors for each of the two layouts"
    list(route.routed_corridors(s, s._access, geom))
    assert len(calls) == 4, "...and a layout asked again is remembered"


def test_a_routed_path_the_tree_will_not_take_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 317 T06: a routed path is admitted as every candidate is (`admitted`) - here the lane law over the tree refuses it."""
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)
    monkeypatch.setattr(access, "tree_admits", lambda *a: False)
    s = _open()
    geom = _hemmed(s)
    s._access.routed = True
    assert next(route.routed_corridors(s, s._access, geom), None) is not None, "a route is found"
    assert access_corridor(s, geom) is None, "...and refused by the tree"


def test_a_door_shut_in_round_its_house_alone_is_not_searched_again_for_another_layout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 317 (`house_reaches`): once a layout's search finds nothing and the search round the house alone reaches no goal,
    the seat's other layouts - which search a part of that ground - skip the door; where the house alone reaches, they search."""
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)
    s = _open()
    geom = _hemmed(s)
    s.placed.extend([(400.0, 700.0, 60.0, 500.0), (1000.0, 700.0, 60.0, 500.0), (700.0, 950.0, 700.0, 60.0)])  # walled in all round
    s._access.routed = True
    other = {**geom, "boxes": {**geom["boxes"], "gardens": [(760.0, 760.0, 20.0, 20.0)]}}
    calls: list[int] = []
    real = route._route_from
    monkeypatch.setattr(route, "_route_from", lambda *a: calls.append(1) or real(*a))
    assert list(route.routed_corridors(s, s._access, geom)) == [] and len(calls) == 2
    assert list(route.routed_corridors(s, s._access, other)) == [] and len(calls) == 2, "the other layout: no search"
    assert route.house_reaches(s, s._access, access.doors_of(geom, s._access.half)[0], geom["boxes"]["house"], s._access.half, access.house_gap(s), None, None, s._reach_index(s.placed, "placed_reach"), route.ROUTE_STEP_PX) is False
    open_ = _open()
    g2 = _hemmed(open_)
    open_._access.routed = True
    assert route.house_reaches(open_, open_._access, access.doors_of(g2, open_._access.half)[0], g2["boxes"]["house"], open_._access.half, access.house_gap(open_), None, None, open_._reach_index(open_.placed, "placed_reach"), route.ROUTE_STEP_PX)
