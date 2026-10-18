"""Feature 387 T04 (plan D4): the plots' sun boxes are built once per state of the registries they are read from - keyed on
`M["threshing_yards"]`'s, `M["gardens"]`'s and `M["houses"]`'s own versions - and asked through a grid; every answer is the old
form's (each ask rebuilding the plot list and filtering every box), in the same order. A writer that changes a plot in place
without bumping a version is caught under `L7R_CHECK_CACHES=1`, never served stale. The old form is kept here as the oracle."""

from __future__ import annotations

import random
from typing import Any

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom.indexes import Indexed
from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT, plot_box, sun_box


def _old(s: Settlement, bbox: tuple[float, float, float, float], reach_ft: float = CANOPY_SHADE_FT) -> list[Any]:
    """`_sun_keepouts` before feature 387."""
    if not getattr(s, "_sun_corridor_ft", 0.0):
        return []
    reach = s.px(reach_ft)
    plots = [b for k in ("threshing_yards", "gardens") for o in s.M.get(k) or () if (b := plot_box(o)) is not None]
    for rec in s.M.get("houses") or ():
        g = rec.get("geom") or {}
        boxes = g.get("boxes") or {}
        yard = boxes.get("yard", g.get("yard"))
        plots += [p for p in ([yard] if yard is not None else []) + list(boxes.get("gardens", g.get("gardens")) or ())]
    sun = [sun_box(p, reach) for p in plots]
    bx0, by0, bx1, by1 = bbox
    return [b for b in sun if b[0] + b[2] >= bx0 and b[0] - b[2] <= bx1 and b[1] + b[3] >= by0 and b[1] - b[3] <= by1]


def _sunny(seed: int) -> Settlement:
    rng = random.Random(seed)
    s = Settlement(3000, 3000, seed=1)
    s.meta(name="S", scale="hamlet", ftpx=1)
    s.sun_corridor(39)
    for _ in range(30):
        s.M["threshing_yards"].append({"x": rng.uniform(0, 3000), "y": rng.uniform(0, 3000), "w": 40.0, "h": 20.0})
        s.M["gardens"].append({"x": rng.uniform(0, 3000), "y": rng.uniform(0, 3000), "w": 14.0, "h": 20.0})
    for _ in range(30):
        x, y = rng.uniform(0, 3000), rng.uniform(0, 3000)
        s.M["houses"].append({"x": x, "y": y, "w": 40.0, "h": 30.0, "geom": {"boxes": {"yard": (x, y + 40, 30.0, 20.0), "gardens": [(x + 50, y, 14.0, 20.0)]}}})
    return s


def _asks(rng: random.Random) -> list[tuple[float, float, float, float]]:
    out = []
    for _ in range(200):
        x, y, w, h = rng.uniform(-100, 3000), rng.uniform(-100, 3000), rng.uniform(5, 400), rng.uniform(5, 400)
        out.append((x, y, x + w, y + h))
    return [*out, (-1e9, -1e9, 1e9, 1e9)]


def test_the_registries_are_versioned() -> None:
    s = Settlement(100, 100, seed=1)
    assert isinstance(s.M["threshing_yards"], Indexed) and isinstance(s.M["gardens"], Indexed) and isinstance(s.M["houses"], Indexed)


def test_every_answer_is_the_old_forms_through_appends_and_an_in_place_shift() -> None:
    s = _sunny(1)
    rng = random.Random(2)
    for bbox in _asks(rng):
        assert s._sun_keepouts(bbox) == _old(s, bbox)
        assert s._sun_keepouts(bbox, 120.0) == _old(s, bbox, 120.0)
    s.M["gardens"].append({"x": 1500.0, "y": 1500.0, "w": 14.0, "h": 20.0})
    rec = s.M["houses"][3]
    rec["geom"]["boxes"]["gardens"] = [(rec["x"] + 50, rec["y"] + 8, 14.0, 20.0)]  # the bed shift `_relax_gardens_south` makes...
    s.M["houses"].touch()  # ...and the bump it carries
    for bbox in _asks(rng):
        assert s._sun_keepouts(bbox) == _old(s, bbox)


def test_a_plain_list_rebound_into_the_manifest_is_never_served_from_the_memo() -> None:
    s = _sunny(3)
    s.M["threshing_yards"] = [{"x": 100.0, "y": 100.0, "w": 40.0, "h": 20.0}]  # a caller (a test) rebinding a plain list
    bbox = (0.0, 0.0, 3000.0, 3000.0)
    assert s._sun_keepouts(bbox) == _old(s, bbox)
    s.M["threshing_yards"].append({"x": 200.0, "y": 200.0, "w": 40.0, "h": 20.0})
    assert s._sun_keepouts(bbox) == _old(s, bbox)


def test_an_unbumped_in_place_write_is_caught_under_the_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("L7R_CHECK_CACHES", "1")
    s = _sunny(4)
    bbox = (0.0, 0.0, 3000.0, 3000.0)
    s._sun_keepouts(bbox)
    s.M["houses"][0]["geom"]["boxes"]["yard"] = (10.0, 10.0, 30.0, 20.0)  # a writer that forgot `touch()`
    with pytest.raises(AssertionError, match="stale"):
        s._sun_keepouts(bbox)


def test_an_ask_on_a_standing_state_reuses_the_built_plots(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_CHECK_CACHES", raising=False)
    s = _sunny(5)
    s._sun_keepouts((0.0, 0.0, 10.0, 10.0))
    built = s.__dict__["_sun_memo"]
    for bbox in _asks(random.Random(6)):
        s._sun_keepouts(bbox)
    assert s.__dict__["_sun_memo"] is built, "the plots are read once per state, not once per ask"
    s.M["gardens"].append({"x": 1.0, "y": 1.0, "w": 14.0, "h": 20.0})
    s._sun_keepouts((0.0, 0.0, 10.0, 10.0))
    assert s.__dict__["_sun_memo"] is not built, "a new plot is a new state"
