"""Feature 317, plan D2-D5: a household reached across a neighbor's yard (`settlement/rolling/passage.py`)."""

from __future__ import annotations

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
