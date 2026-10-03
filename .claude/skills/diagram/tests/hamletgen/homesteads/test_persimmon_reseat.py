"""The persimmon a household could not keep, given to one that has room (feature 315, `homesteads/persimmon_reseat.py`)."""

from __future__ import annotations

from typing import Any

from l7r.diagram.hamletgen.homesteads.persimmon_reseat import _turned, persimmon_for, reseat_persimmons
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.homestead_parts.fixture_seats import FixtureForms


def _hamlet() -> Settlement:
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="P", scale="hamlet", ftpx=1)
    s.sun_corridor(39)
    return s


def _house(x: float, y: float, **extra: Any) -> dict[str, Any]:
    geom = {"house": (x, y, 46.0, 28.0), "yard": (x, y + 30.0, 30.0, 20.0), "gardens": [], "fixtures": {}, "turn": 0.0, **extra}
    return {"x": x, "y": y, "w": 46.0, "h": 28.0, "geom": geom, "fixtures": []}


def test_a_part_is_carried_about_the_house_by_its_rake() -> None:
    x, y, w, h = _turned((10.0, 0.0, 4.0, 2.0), 0.0, 0.0, 90.0)
    assert abs(x) < 1e-9 and abs(y - 10.0) < 1e-9 and (w, h) == (4.0, 2.0)


def test_a_household_without_a_tree_takes_one_in_its_dooryard_behind_the_house() -> None:
    """Front first or not, its own yard's sun sends the tree behind the house; a household with no laid house takes none."""
    s = _hamlet()
    h = _house(1000.0, 1000.0)
    s.M["houses"] = [h]
    rec = persimmon_for(s, h, FixtureForms(persimmon_front=0.95))
    assert rec is not None and rec["kind"] == "persimmon" and rec["y"] < 1000.0 - 14.0, "behind the house"
    assert persimmon_for(s, {"geom": {}}, FixtureForms()) is None


def test_no_tree_where_it_would_shade_a_neighbor_stand_in_a_neighbors_grove_or_over_a_conifer() -> None:
    s = _hamlet()
    h = _house(1000.0, 1000.0)
    s.M["houses"] = [h]
    seat = persimmon_for(s, h, FixtureForms(persimmon_front=0.05))
    assert seat is not None
    # a neighbor's yard just behind this house: the tree there would shade it
    shaded = _house(1000.0, 900.0)
    shaded["geom"]["yard"] = (seat["x"], seat["y"] - 30.0, 30.0, 20.0)
    s.M["houses"] = [h, shaded]
    assert persimmon_for(s, h, FixtureForms(persimmon_front=0.05)) is None, "in a neighbor's sun"
    grove = _house(1600.0, 1600.0, groves=[(seat["x"], seat["y"], 60.0, 60.0)])
    s.M["houses"] = [h, grove]
    assert persimmon_for(s, h, FixtureForms(persimmon_front=0.05)) is None, "in a neighbor's grove"
    s.M["houses"] = [h]
    s._conifer_crowns = [(seat["x"], seat["y"], 10.0)]
    other = persimmon_for(s, h, FixtureForms(persimmon_front=0.05))
    assert other is None or (other["x"], other["y"]) != (seat["x"], seat["y"]), "never painted over a conifer"


def test_the_count_short_of_the_roll_is_laid_at_households_without_a_tree() -> None:
    """`reseat_persimmons` lays only what the roll is short of, skips a household that keeps one, and does nothing off the sun
    corridor."""
    s = _hamlet()
    kept = _house(400.0, 400.0)
    kept["fixtures"] = [{"kind": "persimmon"}]
    a, b = _house(1000.0, 1000.0), _house(1400.0, 1400.0)
    s.M["houses"] = [kept, a, b]
    assert reseat_persimmons(s, s.M["houses"], 2, FixtureForms()) == 1
    assert any(f["kind"] == "persimmon" for f in a["fixtures"]) and not b["fixtures"], "one short, one laid"
    assert "persimmon" in a["geom"]["fixtures"]
    off = Settlement(2000, 2000, seed=1)
    off.meta(name="P", scale="hamlet", ftpx=1)
    assert reseat_persimmons(off, [_house(1000.0, 1000.0)], 1, FixtureForms()) == 0
