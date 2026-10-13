"""The persimmon a household could not keep, given to one that has room (feature 315, `homesteads/persimmon_reseat.py`)."""

from __future__ import annotations

from typing import Any

from l7r.diagram.hamletgen.homesteads.persimmon_reseat import _turned, give_way, in_bands, persimmon_for, reseat_persimmons
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


def test_a_household_whose_dooryard_has_no_seat_takes_none_and_the_next_is_offered(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from l7r.diagram.hamletgen.homesteads import persimmon_reseat

    s = _hamlet()
    a, b = _house(1000.0, 1000.0), _house(1400.0, 1400.0)
    s.M["houses"] = [a, b]
    monkeypatch.setattr(persimmon_reseat, "_persimmon", lambda *args: None)
    assert persimmon_for(s, a, FixtureForms()) is None, "no seat in its dooryard"
    assert reseat_persimmons(s, s.M["houses"], 1, FixtureForms()) == 0 and not a["fixtures"] and not b["fixtures"]


def test_the_seat_search_looks_past_a_seat_in_a_neighbor_s_sun(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 317: a neighbor's sun is asked of each seat the search tries, so a seat that shades one is passed over for the
    next - asked only of the chosen seat, the household gave the tree up (Inashiro: 11 drawn of 12 rolled)."""
    s = _hamlet()
    h = _house(1000.0, 1000.0)
    s.M["houses"] = [h]
    asked: list[int] = []

    def shades(self, g, tree, r, reach):  # type: ignore[no-untyped-def]
        asked.append(1)
        return len(asked) == 1  # the first seat tried is in a neighbor's sun, the rest are not

    monkeypatch.setattr(Settlement, "_persimmon_shades_a_neighbor", shades)
    rec = persimmon_for(s, h, FixtureForms(persimmon_front=0.05))
    assert rec is not None and len(asked) >= 2, "the next seat taken"


def test_a_household_without_a_seat_on_its_rolled_side_tries_the_other(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from l7r.diagram.hamletgen.homesteads import persimmon_reseat

    s = _hamlet()
    h = _house(1000.0, 1000.0)
    s.M["houses"] = [h]
    sides: list[bool] = []
    monkeypatch.setattr(persimmon_reseat, "_persimmon", lambda hw, hh, taken, roofs, front, px, clear: sides.append(front) or (None if front else (0.0, -40.0, 23.0, 23.0)))
    rec = persimmon_for(s, h, FixtureForms(persimmon_front=0.95))
    assert sides == [True, False] and rec is not None, "front rolled, no seat there: behind the house"


def test_its_own_grove_is_open_to_the_tree_and_its_conifers_no_bar() -> None:
    """Feature 374 wave 152 (0046): a farm's persimmon may stand in its own grove, whose trees give way round it - its own bands
    are not taken ground and its own conifers do not refuse the seat; another stand's conifer still does."""
    s = _hamlet()
    h = _house(1000.0, 1000.0)
    s.M["houses"] = [h]
    seat = persimmon_for(s, h, FixtureForms(persimmon_front=0.05))
    assert seat is not None
    h["geom"]["groves"] = [(seat["x"], seat["y"], 80.0, 40.0)]
    s._conifer_crowns = [(seat["x"], seat["y"], 10.0)]
    own = persimmon_for(s, h, FixtureForms(persimmon_front=0.05))
    assert own is not None and (own["x"], own["y"]) == (seat["x"], seat["y"]), "its own grove gives way"
    h["geom"]["groves"] = []
    other = persimmon_for(s, h, FixtureForms(persimmon_front=0.05))
    assert other is None or (other["x"], other["y"]) != (seat["x"], seat["y"]), "another stand's conifer refuses it"


def test_the_grove_gives_way_out_of_the_drawing_and_the_record() -> None:
    s = _hamlet()
    s.M["tree_crowns"] = [100.0, 100.0, 8.0, 160.0, 100.0, 8.0, 100.0, 300.0, 8.0]
    s._conifer_crowns = [(100.0, 100.0, 8.0), (100.0, 300.0, 8.0)]
    s.out[:] = ['<g transform="translate(90.0,90.0)"><circle cx="10.0" cy="10.0" r="8.0" fill="#2A4"/><circle cx="70.0" cy="10.0" r="8.0" fill="#2A4"/></g>', "<path/>"]
    bands = [(130.0, 100.0, 100.0, 40.0)]
    assert in_bands(100.0, 100.0, bands) and not in_bands(100.0, 300.0, bands)
    assert give_way(s, 100.0, 100.0, 11.5, bands) == 1, "only the crown under the tree, of its own grove"
    assert s.M["tree_crowns"] == [160.0, 100.0, 8.0, 100.0, 300.0, 8.0] and s._conifer_crowns == [(100.0, 300.0, 8.0)]
    assert 'cx="10.0"' not in s.out[0] and 'cx="70.0"' in s.out[0] and s.out[1] == "<path/>"
    assert give_way(s, 500.0, 500.0, 11.5, bands) == 0, "nothing under it, nothing taken"


def test_a_reseated_tree_in_its_own_grove_counts_the_crowns_given_way(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    import l7r.diagram.hamletgen.homesteads.persimmon_reseat as pr

    s = _hamlet()
    a = _house(1000.0, 1000.0, groves=[(1000.0, 960.0, 80.0, 40.0)])
    s.M["houses"] = [a]
    s.M["tree_crowns"] = [1000.0, 960.0, 8.0]
    monkeypatch.setattr(pr, "persimmon_for", lambda s_, h, f: {"kind": "persimmon", "x": 1000.0, "y": 960.0, "w": 23.0, "h": 23.0})
    assert reseat_persimmons(s, s.M["houses"], 1, FixtureForms()) == 1
    assert s.M["meta"]["persimmon_grove_gave_way"] == 1 and s.M["tree_crowns"] == []
