"""Feature 318, plan D12-D13: every household's way laid once, in the gaps, after the last house stands
(`settlement/rolling/gap_ways.py`)."""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.homesteads import household_ways as hw
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import gap_ways as gw
from tests.settlement._builders import seed_tree


def _site(xs: tuple[float, ...] = (600.0, 900.0)) -> tuple[Settlement, list[dict]]:
    """A strip along y = 450 and a household seated at each x on y = 700, their homesteads parted by far more than the gap."""
    s = Settlement(1400.0, 1400.0, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=len(xs), down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    seed_tree(s, (300.0, 450.0), (1.0, 0.0), 900.0)
    houses = []
    for x in xs:
        geom = s._bundle_geom(x, 700.0, 46.0, 28.0, "SE", rot=0.0)
        s.placed.append(geom["bbox"])
        houses.append({"x": x, "y": 700.0, "w": 46.0, "h": 28.0, "rot": 0.0, "geom": geom})  # as a seated record carries them
    s.M["houses"] = houses
    return s, houses


def test_nothing_is_laid_with_no_tree_or_no_house() -> None:
    s, _houses = _site()
    s._access = None
    assert hw.lay_the_ways(s) == (0, 0)
    s2, _ = _site(())
    assert hw.lay_the_ways(s2) == (0, 0)


def test_every_household_is_given_a_way_through_the_gaps_recorded_as_its_corridor() -> None:
    """D12: each household's way leaves its dooryard and joins the way out or a way laid before it; recorded and reserved as
    the seating's corridor was (`access_corridors`, the first leg naming the house)."""
    s, houses = _site()
    assert hw.lay_the_ways(s) == (0, 0)
    assert all(h["geom"].get("access") for h in houses), "every household reached"
    named = [c["of"] for c in s.M["access_corridors"] if c.get("of")]
    assert sorted(named) == [[600.0, 700.0], [900.0, 700.0]]
    for h in houses:
        run = h["geom"]["access"]
        assert all(math.isfinite(v) for p in run for v in p) and len(run) >= 2


def test_a_passage_the_laid_ways_make_unnecessary_is_ended_where_it_stands() -> None:
    """FR-001: a household reached across a yard that the gap pass gives a way keeps its house, and its passage ends."""
    s, houses = _site()
    houses[1].update(reached_across=[600.0, 700.0], passage_depth=1, passage=[[0.0, 0.0]])
    assert hw.lay_the_ways(s) == (1, 0)
    assert "reached_across" not in houses[1] and "passage" not in houses[1] and houses[1]["geom"]["access"]


def test_the_pinch_needs_a_household_with_a_way() -> None:
    rec = {"x": 0.0, "y": 0.0}
    assert not gw.pinch(rec, []) and "reached_across" not in rec
    nb = {"x": 10.0, "y": 0.0, "geom": {}}
    assert gw.pinch(rec, [nb]) and rec["passage"] == [[0.0, 0.0], [10.0, 0.0]], "no yard: to its house"


# ---- feature 328 wave 4: a way's foot gathered onto the junction beside it ---------------------------------------------


def test_the_knot_reach_is_the_web_gathers() -> None:
    from l7r.diagram.hamletgen.ways.smooth import _KNOT_FT

    assert gw.KNOT_FT == _KNOT_FT == 25.0
