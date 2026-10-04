"""Feature 317, plan D2-D5: a household reached across a neighbor's yard (`settlement/rolling/passage.py`)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import passage
from tests.settlement._builders import seed_tree


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
    seed_tree(s, (600.0, 450.0), (1.0, 0.0), 400.0)
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
    from l7r.diagram.settlement.rolling import fit, place

    s = _open()
    nb, _geom, tight = _pair(s)
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    s._tight_of = tight
    s._passage_left = 1
    walk = ((1000.0, 1000.0), (1040.0, 1000.0))
    monkeypatch.setattr(place, "landlocked", lambda s, lays: False)
    assert not s.try_place(1000.0, 1100.0, "plain"), "not land the custom covers (a way of its own, or no walk): refused"
    monkeypatch.setattr(place, "landlocked", lambda s, lays: True)
    monkeypatch.setattr(fit, "passage_of", lambda s, g: None)
    assert not s.try_place(1000.0, 1100.0, "plain"), "this layout's walk: none - refused"
    monkeypatch.setattr(fit, "passage_of", lambda s, g: {"walk": walk, "of": (600.0, 700.0), "depth": 1})
    monkeypatch.setattr(fit, "opens", lambda s, g: True)
    assert not s.try_place(1000.0, 1100.0, "plain"), "a way of its own from this layout: refused"
    monkeypatch.setattr(fit, "opens", lambda s, g: False)
    s._tight_of = {**tight, "own_way": False}  # a fresh seat's word, as the growth gives each seat
    assert s.try_place(1000.0, 1100.0, "plain"), "a passage and no corridor: seated"
    rec = s.M["houses"][-1]
    assert rec["reached_across"] == [600.0, 700.0] and rec["passage_depth"] == 1 and rec["passage"] == [[1000.0, 1000.0], [1040.0, 1000.0]]
    assert s._passage_left == 0 and "access" not in rec["geom"]
    assert s._access.covers_box((1020.0, 1000.0, 4.0, 4.0)), "the walk kept clear of later homesteads, as a corridor is"
    assert not s._access.covers_box((1020.0, 1300.0, 4.0, 4.0))


def test_a_way_of_its_own_is_the_seat_regions_word_where_one_stands(monkeypatch: pytest.MonkeyPatch) -> None:
    """`passage.opens` (feature 318, FR-013): the seat region's one predicate where a region stands; a roll with none keeps the
    straight or round-the-gable corridor test. And `depth_of` counts a household seated with its yard open (`opens`) as reached."""
    s = _open()
    s._seat_region = SimpleNamespace(opens=lambda g: g["id"] == "a")
    assert passage.opens(s, {"id": "a"}) and not passage.opens(s, {"id": "b"})
    s._seat_region = None
    monkeypatch.setattr(passage, "access_corridor", lambda s_, g, routed=True: None if routed else ((0.0, 0.0), (1.0, 0.0)))
    assert passage.opens(s, {"id": "b"}), "no region: an unrouted corridor"
    assert passage.depth_of({"geom": {"opens": True}}) == 0 and passage.depth_of({"geom": {}}) is None


def _seated_passage(s: Settlement) -> tuple[dict, dict, dict, tuple]:
    """The pair, the household reached across the yard seated (its box placed, its walk barred) and another layout at its seat."""
    nb, geom, _tight = _pair(s)
    rec = {"x": float(geom["house"][0]), "y": float(geom["house"][1]), "rot": 0.0, "geom": geom, "reached_across": [600.0, 700.0], "passage_depth": 1, "passage": [[0.0, 0.0]]}
    s.M["houses"] = [nb, rec]
    s.placed.append(geom["bbox"])
    walk = ((rec["x"], 690.0), (rec["x"] + 40.0, 690.0), (590.0, 690.0))
    for a, b in zip(walk, walk[1:], strict=False):
        s._access.bar(a, b)
    lay = s._bundle_geom(float(geom["house"][0]), 700.0, 46.0, 28.0, "SE", rot=0.0)
    return nb, rec, lay, walk


def test_a_passage_crosses_only_to_a_reached_household_with_a_yard() -> None:
    assert passage.crossable({"geom": {"access": ((0.0, 0.0), (1.0, 0.0)), "boxes": {"yard": (0.0, 0.0, 1.0, 1.0)}}})
    assert passage.crossable({"passage_depth": 1, "geom": {"boxes": {"yard": (0.0, 0.0, 1.0, 1.0)}}}), "within the chain"
    assert not passage.crossable({"passage_depth": passage.PASSAGE_CHAIN, "geom": {"boxes": {"yard": (0.0, 0.0, 1.0, 1.0)}}}), "at its end"
    assert not passage.crossable({"geom": {"boxes": {"yard": (0.0, 0.0, 1.0, 1.0)}}}), "nothing reaches it"
    assert not passage.crossable({"geom": {"access": ((0.0, 0.0), (1.0, 0.0)), "boxes": {}}}), "no yard"


def test_a_seat_where_one_layout_has_a_way_of_its_own_is_refused_for_every_layout(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_parts_fit` (feature 317, `own_way`): once a garden layout at a tight seat finds a corridor, the household there is not on
    land the custom covers - its other layouts are refused unasked."""
    from l7r.diagram.settlement.rolling import fit

    s = _open()
    _nb, geom, tight = _pair(s)
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    s._tight_of = tight
    s._passage_left = 1
    asked: list[int] = []
    monkeypatch.setattr(fit, "passage_of", lambda s, g: asked.append(1) or {"walk": ((0.0, 0.0), (1.0, 0.0)), "of": (600.0, 700.0), "depth": 1})
    monkeypatch.setattr(fit, "opens", lambda s, g: True)
    assert not s._parts_fit(geom) and tight["own_way"] and asked == [1], "a way of its own from this layout"
    assert not s._parts_fit(geom) and asked == [1], "...so the next is refused without its walk asked"


def test_a_household_is_landlocked_only_where_some_layout_walks_and_none_has_a_way(monkeypatch: pytest.MonkeyPatch) -> None:
    """`landlocked` (feature 317, research R8): the household's land, not one layout - a walk from some layout, a corridor from
    none; the corridors asked first, straight or round the gable only (the GM's ruling of 2026-10-03: no routed search)."""
    asked: list[str] = []
    walks = {"a": None, "b": {"walk": ()}}
    ways = {"a": None, "b": None}
    monkeypatch.setattr(passage, "passage_of", lambda s, g: asked.append("walk") or walks[g["id"]])
    monkeypatch.setattr(passage, "access_corridor", lambda s, g, routed=True: asked.append("way" if not routed else "routed") or ways[g["id"]])
    lays = [{"id": "a"}, {"id": "b"}, None, {"id": "a", "unlaid": True}]
    assert passage.landlocked(None, lays), "b walks, neither has a way"
    assert asked == ["way", "way", "walk", "walk"], "both layouts' unrouted corridors, then the walks until one is found"
    ways["a"] = ((0.0, 0.0), (1.0, 0.0))
    asked.clear()
    assert not passage.landlocked(None, lays) and asked == ["way"], "a has a way of its own: no walk asked"
    ways["a"], walks["b"] = None, None
    assert not passage.landlocked(None, lays), "no walk from any layout: not landlocked"


def test_the_passage_asks_no_routed_corridor(monkeypatch: pytest.MonkeyPatch) -> None:
    """`access_corridor`, `routed` False (the GM's ruling of 2026-10-03): the candidates after the routed marker (`ROUTE_LATER`)
    are not asked - a household that only a path bending round the homesteads would reach has no way of its own."""
    from l7r.diagram.settlement.rolling import access

    s = _open()
    _pair(s)
    route = ((0.0, 0.0), (5.0, 5.0), (5.0, 9.0))
    monkeypatch.setattr(access, "_house_candidates", lambda s, tree, g: iter([access.ROUTE_LATER, route]))
    monkeypatch.setattr(access, "admitted", lambda s, c, g, memo: c)
    geom = s._bundle_geom(900.0, 900.0, 46.0, 28.0, "SE", rot=0.0)
    assert access.access_corridor(s, geom, routed=False) is None, "the routed corridor is not sought"
    assert access.access_corridor(s, geom) == route, "the seating's own question still routes"


def test_a_layout_s_walk_is_searched_once_a_seat(monkeypatch: pytest.MonkeyPatch) -> None:
    """`passage_of` remembers each layout's walk on the seat's word (`walks`): `landlocked` asks it, the parts' test again."""
    s = _open()
    _nb, geom, tight = _pair(s)
    s._tight_of = tight
    s._passage_left = 1
    calls: list[int] = []
    real = passage.walk_of
    monkeypatch.setattr(passage, "walk_of", lambda *a: calls.append(1) or real(*a))
    first = passage.passage_of(s, geom)
    n = len(calls)
    assert first is not None and n >= 1 and passage.passage_of(s, geom) is first and len(calls) == n
