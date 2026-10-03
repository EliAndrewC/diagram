"""Feature 317, plan D2-D5: a household reached across a neighbor's yard (`settlement/rolling/passage.py`)."""

from __future__ import annotations

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import passage
from l7r.diagram.settlement.rolling.access import start_tree


def test_the_share_is_rolled_from_the_seed_within_its_band_and_the_budget_floors_it() -> None:
    lo, hi = passage.PASSAGE_SHARE_BAND
    shares = [passage.passage_share(seed) for seed in range(1, 40)]
    assert all(lo <= v <= hi for v in shares) and len(set(shares)) > 10, "rolled within the band, and varied"
    assert passage.passage_share(7) == passage.passage_share(7), "the seed and the knob's name, nothing else"
    assert passage.passage_budget(0.217, 15) == 3 and passage.passage_budget(0.05, 15) == 0


def test_a_household_s_depth_is_its_corridor_s_or_its_passage_s_or_none() -> None:
    assert passage.depth_of({"geom": {"access": ((0.0, 0.0), (1.0, 0.0))}}) == 0, "a corridor of its own"
    assert passage.depth_of({"passage_depth": 2, "geom": {}}) == 2, "reached across a yard, at its depth"
    assert passage.depth_of({"geom": {}}) is None, "neither: no household the tree reaches"


def test_the_box_measures_the_custom_s_condition_reads() -> None:
    """`box_foot`, `grown`, `apart` (the growth's own parting measure), `adjoins` and `on_their_land`."""
    box = (10.0, 10.0, 20.0, 10.0)
    assert passage.box_foot((50.0, 12.0), box) == (20.0, 12.0) and passage.box_foot((10.0, 10.0), box) == (10.0, 10.0)
    assert passage.grown(box, 2.0) == (10.0, 10.0, 24.0, 14.0)
    right = (32.0, 10.0, 20.0, 10.0)  # its west edge at 22: 2 px east of the box's east edge
    assert passage.apart(box, right) == pytest.approx(2.0) and passage.adjoins(box, right, 3.0) and not passage.adjoins(box, right, 1.9)
    lands = [passage.grown(box, 1.0), passage.grown(right, 1.0)]
    assert passage.on_their_land((5.0, 10.0), (40.0, 10.0), lands, 4.0), "across the parting, on the two lands"
    assert not passage.on_their_land((5.0, 10.0), (40.0, 40.0), lands, 4.0), "...off them"


def _open() -> Settlement:
    s = Settlement(1400.0, 1400.0, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    return s


def _pair(s: Settlement, gap: float = 2.0) -> tuple[dict, dict, dict]:
    """A neighbor seated at (600, 700) with a corridor of its own and its bed to the east of its yard, and a household laid
    against its land to the WEST, `gap` px off it, its own bed on its far side - so the two yards face each other across the
    parting - with the tight seat's word on the two (`_tight_of`)."""
    start_tree(s, (600.0, 450.0), (1.0, 0.0), 400.0)
    nb_geom = s._bundle_geom(600.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    nb_geom["access"] = ((600.0, 680.0), (600.0, 450.0))
    nb = {"x": 600.0, "y": 700.0, "geom": nb_geom}
    s.placed.append(nb_geom["bbox"])
    land = tuple(float(v) for v in nb_geom["bbox"][:4])
    probe = s._bundle_geom(1000.0, 700.0, 46.0, 28.0, "SW", rot=0.0)
    off = float(probe["bbox"][0]) - 1000.0
    x = land[0] - land[2] / 2.0 - gap - float(probe["bbox"][2]) / 2.0 - off
    geom = s._bundle_geom(x, 700.0, 46.0, 28.0, "SW", rot=0.0)
    hx, hy = float(geom["boxes"]["house"][0]), float(geom["boxes"]["house"][1])
    bx, by, bw, bh = (float(v) for v in geom["bbox"][:4])
    own = (hx - (bx - bw / 2), (bx + bw / 2) - hx, hy - (by - bh / 2), (by + bh / 2) - hy)
    tight = {"rec": nb, "land": land, "own": own, "gap": 2.0}
    return nb, geom, tight


def test_a_household_against_its_neighbor_s_land_is_reached_across_its_yard() -> None:
    s = _open()
    nb, geom, tight = _pair(s)
    s._tight_of = tight
    s._passage_left = 1
    got = passage.passage_of(s, geom)
    assert got is not None, "a walk from its dooryard to the neighbor's yard, on the two lands"
    assert got["of"] == (600.0, 700.0) and got["depth"] == 1
    walk = got["walk"]
    yard = nb["geom"]["boxes"]["yard"]
    assert passage.box_foot(walk[-1], yard) == pytest.approx(walk[-1]), "...ending on the neighbor's yard"
    hx, hy = (float(v) for v in geom["boxes"]["house"][:2])
    w, e, n, so = tight["own"]
    own = (hx + (e - w) / 2.0, hy + (so - n) / 2.0, w + e, n + so)
    lands = [passage.grown(tight["land"], 3.0), passage.grown(own, 3.0)]
    assert all(passage.on_their_land(a, b, lands, 4.0) for a, b in zip(walk, walk[1:], strict=False)), "...on the two lands"


@pytest.mark.parametrize(
    ("why", "setup"),
    [
        ("off a tight seat", lambda s, nb, g, t: setattr(s, "_tight_of", None)),
        ("the share spent", lambda s, nb, g, t: setattr(s, "_passage_left", 0)),
        ("the chain at its limit", lambda s, nb, g, t: nb.update(passage_depth=passage.PASSAGE_CHAIN)),
        ("a neighbor nothing reaches", lambda s, nb, g, t: nb["geom"].pop("access")),
        ("a neighbor with no yard", lambda s, nb, g, t: nb["geom"]["boxes"].pop("yard")),
    ],
)
def test_no_passage_where_the_custom_or_the_plan_does_not_give_one(why, setup) -> None:  # noqa: ANN001
    s = _open()
    nb, geom, tight = _pair(s)
    s._tight_of = tight
    s._passage_left = 1
    setup(s, nb, geom, tight)
    assert passage.passage_of(s, geom) is None, why


def test_land_that_does_not_adjoin_the_neighbor_s_is_not_reached_across_it() -> None:
    """The custom's condition is land against land, never a walk across open ground (plan D2)."""
    s = _open()
    nb, geom, tight = _pair(s, gap=40.0)
    s._tight_of = tight
    s._passage_left = 1
    assert passage.passage_of(s, geom) is None


def test_a_walk_shut_in_finds_no_passage(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _open()
    nb, geom, tight = _pair(s)
    s._tight_of = tight
    s._passage_left = 1
    monkeypatch.setattr(passage, "walk_clear", lambda *a: False)  # no leg the walk may take
    assert passage.passage_of(s, geom) is None


def test_the_walk_is_refused_by_each_thing_it_may_not_cross(monkeypatch: pytest.MonkeyPatch) -> None:
    """`walk_clear`: the household's own house, the neighbor's house, another homestead whole, the site's static ground and the
    reserved wood seats - and passed where none stands across it."""
    from types import SimpleNamespace

    from l7r.diagram.settlement.rolling import access

    s = _open()
    nb, geom, _t = _pair(s)
    hgap, half = access.house_gap(s), float(s._access.half)
    yard = nb["geom"]["boxes"]["yard"]
    door = (float(geom["boxes"]["yard"][0]), float(geom["boxes"]["yard"][1]))
    foot = passage.box_foot(door, yard)
    assert passage.walk_clear(s, door, foot, geom, nb, hgap, half, None), "yard to yard across the parting: clear"
    own_house, nb_house = geom["boxes"]["house"], nb["geom"]["boxes"]["house"]
    assert not passage.walk_clear(s, (own_house[0] - 30.0, own_house[1]), (own_house[0] + 30.0, own_house[1]), geom, nb, hgap, half, None), "its own house"
    assert passage.walk_clear(s, (nb_house[0] - 10.0, nb_house[1] - 60.0), (nb_house[0] + 30.0, nb_house[1] - 60.0), geom, nb, hgap, half, None)
    assert not passage.walk_clear(s, (nb_house[0] - 10.0, nb_house[1]), (nb_house[0] + 30.0, nb_house[1]), geom, nb, hgap, half, None), "the neighbor's"
    s.placed.append(((door[0] + foot[0]) / 2.0, door[1], 6.0, 6.0))
    assert not passage.walk_clear(s, door, foot, geom, nb, hgap, half, None), "a third homestead between"
    s.placed.pop()
    monkeypatch.setattr(passage, "site_edge_samples", lambda *a: None)
    assert not passage.walk_clear(s, door, foot, geom, nb, hgap, half, None), "on the site's taken ground"
    monkeypatch.setattr(passage, "site_edge_samples", lambda *a: [])
    assert not passage.walk_clear(s, door, foot, geom, nb, hgap, half, SimpleNamespace(corridor_bars=lambda a, b: True)), "a wood seat"


def test_a_walk_with_no_open_ground_to_the_yard_is_none() -> None:
    """`walk_of`'s search: every cell on the site's taken ground - no walk."""
    from types import SimpleNamespace

    from l7r.diagram.settlement.rolling import access

    s = _open()
    nb, geom, tight = _pair(s)
    s._free_ground = SimpleNamespace(point_taken=lambda x, y: True)
    hgap, half = access.house_gap(s), float(s._access.half)
    lands = [passage.grown(tight["land"], 3.0), passage.grown(geom["bbox"], 3.0)]
    door = access.doors_of(geom, half)[0]
    assert passage.walk_of(s, geom, nb, door, nb["geom"]["boxes"]["yard"], lands, hgap, half, None) is None


def test_a_third_homestead_across_the_walk_is_routed_round_or_refuses_it() -> None:
    """`walk_of`: a placed homestead standing across the direct line is kept off by the search, as a corridor's route keeps off
    one - the walk found goes round it, or there is none."""
    from l7r.diagram.settlement.rolling import access

    s = _open()
    nb, geom, tight = _pair(s)
    hgap, half = access.house_gap(s), float(s._access.half)
    door = access.doors_of(geom, half)[0]
    yard = nb["geom"]["boxes"]["yard"]
    foot = passage.box_foot(door, yard)
    block = ((door[0] + foot[0]) / 2.0, door[1], 8.0, 30.0)
    s.placed.append(block)
    lands = [passage.grown(tight["land"], 3.0), passage.grown(geom["bbox"], 3.0)]
    walk = passage.walk_of(s, geom, nb, door, yard, lands, hgap, half, None)
    assert walk is None or all(not access.seg_box_within(a, b, block, half) for a, b in zip(walk, walk[1:], strict=False))


def test_the_placer_seats_a_tight_household_only_by_passage_and_records_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_parts_fit` at a tight seat (plan D2): no passage, or a corridor of its own, refuses it; a passage and no corridor
    seats it, and the seat records the walk, the neighbor and the chain's depth, bars the walk (`AccessTree.bar`) and spends
    the share."""
    from l7r.diagram.settlement.rolling import fit

    s = _open()
    nb, _geom, tight = _pair(s)
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    s._tight_of = tight
    s._passage_left = 1
    walk = ((1000.0, 1000.0), (1040.0, 1000.0))
    monkeypatch.setattr(fit, "passage_of", lambda s, g: None)
    assert not s.try_place(1000.0, 1100.0, "plain"), "no passage: refused"
    monkeypatch.setattr(fit, "passage_of", lambda s, g: {"walk": walk, "of": (600.0, 700.0), "depth": 1})
    monkeypatch.setattr(fit, "access_corridor", lambda s, g: ((1000.0, 1080.0), (1000.0, 450.0)))
    assert not s.try_place(1000.0, 1100.0, "plain"), "a corridor of its own: not land the custom covers"
    monkeypatch.setattr(fit, "access_corridor", lambda s, g: None)
    assert s.try_place(1000.0, 1100.0, "plain"), "a passage and no corridor: seated"
    rec = s.M["houses"][-1]
    assert rec["reached_across"] == [600.0, 700.0] and rec["passage_depth"] == 1 and rec["passage"] == [[1000.0, 1000.0], [1040.0, 1000.0]]
    assert s._passage_left == 0 and "access" not in rec["geom"]
    assert s._access.covers_box((1020.0, 1000.0, 4.0, 4.0)), "the walk kept clear of later homesteads, as a corridor is"
    assert not s._access.covers_box((1020.0, 1300.0, 4.0, 4.0))
