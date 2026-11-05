"""Feature 308, plan D3 (FR-005): a house's path routed round what stands where no straight corridor clears."""

from __future__ import annotations

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import access, route
from l7r.diagram.settlement.rolling.route import search
from tests.settlement._builders import seed_tree


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


def _hemmed(s: Settlement) -> dict:
    """A homestead whose every straight and round-the-gable run to the exit strip crosses one wide neighbor."""
    seed_tree(s, (700.0, 450.0), (1.0, 0.0), 300.0)
    s.placed.append((700.0, 560.0, 500.0, 40.0))
    return s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)


def test_a_search_starts_where_it_is_told_and_its_first_steps_are_judged() -> None:
    """Feature 314: the search starts at any cell of the map's grid; its first step may span two cells, and `first_ok` judges
    each - none admitted, none found."""

    def goal(c: tuple[int, int]) -> tuple[float, float] | None:
        return (float(c[0]), float(c[1])) if c[0] >= 14 else None

    got = search(lambda c: True, goal, [(14.0, 5.0)], 10, 1.5, (5, 5))
    assert got is not None and got[0][0] == (5, 5) and max(abs(got[0][1][0] - 5), abs(got[0][1][1] - 5)) <= 2, "a first step of two cells"
    assert search(lambda c: True, goal, [(14.0, 5.0)], 10, 1.5, (5, 5), lambda c: False) is None, "every first step refused"
    assert search(lambda c: True, goal, [], 10, 1.5, (5, 5)) is not None, "no aim: the start's own"


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
