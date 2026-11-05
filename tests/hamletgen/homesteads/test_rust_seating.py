"""The homesteads stage's door to the Rust seating (`homesteads/rust_seating.py`, feature 444 T30): what it records of a household
reached across a neighbor's yard, and of a row village's sheltered farms, holdings and streets. The Rust call and the record's
helpers are stubbed: the seating itself is tested in Rust (`rust/phases/src/homesteads/*_tests.rs`)."""

from __future__ import annotations

import types
from typing import Any

import pytest

from l7r.diagram.hamletgen import phases_ext
from l7r.diagram.hamletgen.homesteads import rust_seating as rs


def _seated(x: float, passage: Any = None, kura: bool = False) -> dict[str, Any]:
    return {"x": x, "passage": passage, "kura": kura}


def _stub_records(monkeypatch: pytest.MonkeyPatch) -> None:
    """A household's geometry and its reservations stubbed to what `record_seated` reads of them."""
    monkeypatch.setattr(rs, "homestead_geom", lambda h: {"house": (h["x"], 10.0, 30.0, 20.0), "turn": 0.0, "shed": None, "byre": None, "bbox": (h["x"], 10.0, 60.0, 60.0), "opens": True})
    monkeypatch.setattr(rs, "reserve_way", lambda *a: None)
    monkeypatch.setattr(rs, "record_parts", lambda *a: None)


def _settlement() -> Any:
    return types.SimpleNamespace(placed=[], M={"houses": [], "meta": {}}, _pending_farmsteads=[], _seat_search={}, _byre_form=None, block_polys=[], hard_polys=[])


def test_a_household_reached_across_a_yard_records_its_walk_and_whom(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_records(monkeypatch)
    s = _settlement()
    got = {"seated": [_seated(100.0), _seated(200.0, passage=([[200.0, 10.0], [150.0, 10.0]], 0, 1), kura=True)], "search": (2, 3, 4, 5), "counts": {"seg_test@x": 7}}
    assert rs.record_seated(s, got) == 2
    first, second = s.M["houses"]
    assert "passage" not in first["geom"] and first["shed"] is False
    assert second["geom"]["passage"] == {"walk": [(200.0, 10.0), (150.0, 10.0)], "of": (100.0, 10.0), "depth": 1}
    assert "opens" not in second["geom"] and second["shed"] is True, "a passage farm's yard opens onto no lane ground; its lot's kura recorded"
    assert s._seat_search["grow_took"] == 2 and s._seat_search["rust_counts"] == 7


def test_a_row_village_records_its_sheltered_farms_holdings_and_streets(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_records(monkeypatch)
    monkeypatch.setattr(rs, "grove_inputs", lambda *a: {})
    got = {
        "seated": [_seated(100.0), _seated(400.0)],
        "search": (2, 0, 0, 0),
        "counts": {},
        "sheltered": [False, True],
        "holdings": [([[350.0, 0.0], [450.0, 0.0], [450.0, -100.0], [350.0, -100.0]], (1.0, 0.0), (0.0, -1.0), 100.0, 1)],
        "streets": [([[0.0, 50.0], [500.0, 50.0]], [[100.0, 10.0], [400.0, 10.0]])],
    }
    seen: dict[str, Any] = {}
    monkeypatch.setattr(phases_ext, "phases", lambda: types.SimpleNamespace(seat_rows=lambda inputs: seen.update(inputs) or got))
    s = _settlement()
    s.W = s.H = 1000.0
    s.toe_band = lambda: None
    s._site_corridors = None
    plan = types.SimpleNamespace(
        envelope=[(0.0, 60.0), (500.0, 60.0), (500.0, 300.0), (0.0, 300.0)],
        row_sides="both",
        row_line="street",
        row_shelter="sheltered",
        windward="NW",
        grove_sides=2,
        grove_flank="W",
        seat={"cx": 250.0, "cy": 40.0},
    )
    assert rs.rust_rows(s, plan, (60.0, 30.0), 400.0, (300.0, 100.0), {}) == 2
    both, form, shelter, *_rest, polys, strips = seen["rows"]
    assert (both, form, shelter) == (True, "street", True) and polys == [plan.envelope] and strips == []
    assert [h.get("sheltered", False) for h in s.M["houses"]] == [False, True] and s.M["meta"]["sheltered_farms"] == 1
    assert s.M["row_holdings"][0]["of"] == [400.0, 10.0] and s.block_polys == s.hard_polys == [s._row_holdings[0][0]]
    assert s._row_streets == [[(0.0, 50.0), (500.0, 50.0)]] and s._row_street_farms == [[(100.0, 10.0), (400.0, 10.0)]]
    assert s.M["meta"]["row_streets"] == 1 and s.M["row_street_plans"][0][0] == [0.0, 50.0]
