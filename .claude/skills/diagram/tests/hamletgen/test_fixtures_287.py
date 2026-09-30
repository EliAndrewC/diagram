"""Feature 287, homes H32 (plan M5 and D9): every rolled farmstead fixture is drawn. The lots keep each kind as a quota
by seat order, the bundle lays it (`settlement/homestead_parts/fixture_seats.py`), and `farmstead_fixtures` draws it
where it was laid - so no fixture is recorded short, and `meta.farm_fixtures_unseated` is never written."""

import math
from collections import Counter

import pytest

import l7r.diagram.settlement.rolling.access as access_mod
from l7r.diagram.hamletgen.homesteads import fixtures as fx
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling.lot import HouseholdLots

from ._builders import a_plan
from .test_homesteads import _toy_hamlet


@pytest.mark.parametrize("n", [10, 13, 17, 20])
def test_each_kinds_quota_is_its_share_of_the_households_and_a_floor_raises_it(n: int) -> None:
    shares = fx.fixture_shares(7)
    quota = fx.fixture_quota(7, n, {"shrine": 2})
    lots = HouseholdLots(7, n, 0.0, quota)
    kept = Counter(k for i in range(n) for k in lots.fixtures_of(i))
    for kind, share in shares.items():
        want = max(math.floor(share * n + 0.5), 2 if kind == "shrine" else 0)
        assert kept[kind] == want, (kind, kept[kind], want)
    assert lots.fixtures_of(n) == () and lots.fixtures_of(-1) == ()


def test_a_seated_hamlet_draws_every_fixture_its_lots_keep_and_records_none_short(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    # the toy's bundles lay a bed or the well pocket where a flank door stands, and a corridor over its own parts is refused
    # since feature 287 M8 (`access.parts_clear`); the seating's count, not the parts, is under test here
    monkeypatch.setattr(access_mod, "parts_clear", lambda *a: True)

    s, plan = _toy_hamlet(12)
    stage_homesteads(s, plan)
    houses = s.M["houses"]
    laid = Counter(f["kind"] for h in houses for f in h.get("fixtures") or ())
    assert laid and all(h.get("fixtures") for h in houses), "every household keeps some"
    drawn = fx.farmstead_fixtures(s, plan, houses, early=True)
    pending = len(s._fixtures_pending)
    assert drawn + pending == sum(v for k, v in laid.items() if k != "retirement")
    target = s.M["meta"]["farm_fixtures_target"]
    assert {k: v for k, v in target.items() if v} == {k: v for k, v in laid.items() if k != "retirement"}, "the declared counts are the laid ones"
    assert fx.farmstead_fixtures(s, plan, houses) == pending, "the later call draws the held-back forms and nothing twice"
    got = Counter(r["kind"] for r in s.M["farm_fixtures"])
    got["persimmon"] = len(s.M.get("persimmons") or [])
    assert {k: v for k, v in got.items() if v} == {k: v for k, v in target.items() if v}
    assert "farm_fixtures_unseated" not in s.M["meta"] and "bath_seats_drawn" in s.M["meta"]


def _house(fixtures: list[dict[str, object]]) -> dict[str, object]:
    return {"x": 400.0, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain", "fixtures": fixtures}


def _laid(kind: str, x: float, y: float, w: float, h: float) -> dict[str, object]:
    return {"kind": kind, "x": x, "y": y, "w": w, "h": h, "box": [x, y, w, h]}


def _sheet() -> Settlement:
    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    return s


def test_a_field_pit_stands_at_the_paddy_edge_else_the_laid_pit(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B11: a household in the pit hamlet's field share keeps its night-soil pit at its nearest paddy edge, recorded
    `seat: field_edge`; with no field in reach, the pit the seating laid beside the privy."""
    monkeypatch.setattr(fx, "PIT_FIELD_SHARE_BAND", (1.0, 1.0))
    plan = a_plan()
    plan.manure_form = "pit"
    pit = _laid("manure", 400.0 + 10.0, 350.0 - 20.0, 3.5, 3.5)
    s = _sheet()
    s.field_polys.append([(520.0, 250.0), (700.0, 250.0), (700.0, 450.0), (520.0, 450.0)])
    fx.farmstead_fixtures(s, plan, [_house([pit])])
    (got,) = s.M["farm_fixtures"]
    assert s.M["meta"]["pit_field_share"] == 1.0 and got["seat"] == "field_edge" and got["form"] == "pit" and 500.0 < got["x"] < 520.0
    s = _sheet()
    fx.farmstead_fixtures(s, plan, [_house([pit])])
    (laid,) = s.M["farm_fixtures"]
    assert (laid["x"], laid["y"]) == (pit["x"], pit["y"]) and "seat" not in laid


def test_a_bath_room_is_drawn_at_its_laid_size_with_its_wall_and_a_flank_seat_along_its_flank() -> None:
    """Feature 280 M22 carried into 287's drawing: the bath room is drawn at the size the household rolled (`ft`, on the
    laid record) and records the wall it took (`seat`, counted in `bath_seats_drawn`); the wood shed laid along a flank is
    turned to it."""
    plan = a_plan()
    s = _sheet()
    bath = {**_laid("bath", 400.0 + 23.0 + 3.0, 350.0, 6.0, 10.0), "ft": [10.0, 6.0], "seat": "floored_rooms"}  # along the east end wall
    coop = _laid("coop", 400.0 - 23.0 - 3.5 - 2.5, 350.0, 5.0, 5.0)
    shed = _laid("woodpile", 400.0 - 23.0 - 3.5 - 6.0 - 6.0, 330.0, 12.0, 24.0)  # along the west flank
    fx.farmstead_fixtures(s, plan, [_house([bath, coop, shed])])
    got = {r["kind"]: r for r in s.M["farm_fixtures"]}
    assert got["bath"]["seat"] == "floored_rooms" and s.M["meta"]["bath_seats_drawn"] == {"floored_rooms": 1}
    assert (got["bath"]["w"], got["bath"]["h"]) == (10.0, 6.0) and got["bath"]["rot"] == 90.0, "its rolled size, turned along its wall"
    assert got["woodpile"]["rot"] == 90.0 and got["coop"]["rot"] == 0.0 and "form" not in got["woodpile"], "the shed laid along a flank is turned to it"


def test_no_house_no_fixture() -> None:
    assert fx.farmstead_fixtures(_sheet(), a_plan(), []) == 0


def test_a_spec_floor_is_declared_and_a_field_pit_across_the_brook_is_not_taken(monkeypatch: pytest.MonkeyPatch) -> None:
    """The floor is declared beside the counts (`farm_fixtures_min`); a field-edge seat with the brook between it and the
    house is not the household's (`across_the_brook`), so the pit stays where the seating laid it."""
    monkeypatch.setattr(fx, "PIT_FIELD_SHARE_BAND", (1.0, 1.0))
    plan = a_plan(fixtures_min={"shrine": 1})
    plan.manure_form = "pit"
    pit = _laid("manure", 410.0, 330.0, 3.5, 3.5)
    s = _sheet()
    s.field_polys.append([(520.0, 250.0), (700.0, 250.0), (700.0, 450.0), (520.0, 450.0)])
    s.M["streams"] = [{"poly": [[480.0, 100.0], [480.0, 600.0]], "w": 4.0}]
    fx.farmstead_fixtures(s, plan, [_house([pit])])
    (laid,) = s.M["farm_fixtures"]
    assert s.M["meta"]["farm_fixtures_min"] == {"shrine": 1} and "seat" not in laid and laid["x"] == pytest.approx(410.0)
