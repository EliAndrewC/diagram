"""`hamletgen/pondstock.py` - the pig sties on a dike-pond hamlet's ponds (feature 150 A3; feature 287, water W50/W51)."""

from __future__ import annotations

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.pondstock import _bank_seats, _centroid, stage_pond_stock, sty_on_near_half
from l7r.diagram.settlement import Settlement


def _pond(x: float, y: float) -> dict:
    parcel = [(x - 60.0, y - 40.0), (x + 60.0, y - 40.0), (x + 60.0, y + 40.0), (x - 60.0, y + 40.0)]
    return {"parcel": parcel, "water": parcel, "kind": "growout"}


def _hamlet(houses: int) -> tuple[Settlement, object]:
    plan = hg.plan_site(hg.HamletSpec(name="X", seed=3, households=16, field_archetype="mulberry_dike_fishpond"))
    s = Settlement(W=900, H=900, seed=1)
    s.meta(name="X", scale="hamlet")
    s.M["houses"] = [{"x": 450.0 + 3 * k, "y": 150.0, "w": 46.0, "h": 28.0} for k in range(houses)]
    return s, plan


def test_a_sty_never_stands_on_the_far_half_of_its_pond() -> None:
    """W51: the far bank of a pond is refused by the one predicate the placer and the test read, and every sty the stage
    seats keeps to the near half."""
    par = _pond(450.0, 400.0)["parcel"]
    hc = (450.0, 150.0)
    seats = _bank_seats(par, hc)
    near = [q for q, _r in seats if sty_on_near_half(q, par, hc)]
    far = [q for q, _r in seats if not sty_on_near_half(q, par, hc)]
    assert near and far, "a pond's bank has seats on both halves"
    assert all(q[1] < _centroid(par)[1] for q in near) and all(q[1] >= _centroid(par)[1] for q in far)
    s, plan = _hamlet(8)
    s.M["dikeponds"] = [_pond(450.0, 400.0), _pond(450.0, 650.0)]
    stage_pond_stock(s, plan)  # type: ignore[arg-type]
    sties = s.M["pig_sties"]
    assert sties
    for st in sties:
        assert sty_on_near_half((st["x"], st["y"]), s.M["dikeponds"][st["pond"]]["parcel"], (450.0 + 3 * 3.5, 150.0))


def test_one_sty_is_seated_even_when_every_bank_midpoint_is_taken() -> None:
    """W50: a dike-pond hamlet keeps at least one sty - the share of ONE household rounds to none, and the stage still
    seats one; and with every edge midpoint of the only pond taken (a well on each), the rest of the bank is tried."""
    s, plan = _hamlet(1)
    s.M["dikeponds"] = [_pond(450.0, 400.0)]
    for q, _rot in _bank_seats(s.M["dikeponds"][0]["parcel"], (450.0, 150.0))[:4]:  # the four midpoints
        s.M.setdefault("wells", []).append({"x": q[0], "y": q[1], "w": 8.0, "h": 8.0})
    stage_pond_stock(s, plan)  # type: ignore[arg-type]
    assert s.M["meta"]["pond_stock"]["sties"] == 1
    assert len(s.M.get("pig_sties") or []) == 1, "the sty takes a seat further along the near bank"
    st = s.M["pig_sties"][0]
    assert sty_on_near_half((st["x"], st["y"]), s.M["dikeponds"][0]["parcel"], (450.0, 150.0))
