"""Feature 297, FR-002 (plan C): a seat's own questions asked once, before any garden-side layout is built."""

from __future__ import annotations

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import access
from l7r.diagram.settlement.rolling.access import AccessTree, seat_reaches_tree


def _open(W: float = 1400.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    return s


def test_the_core_is_the_house_and_yard_every_garden_side_lays() -> None:
    s = _open()
    for x, y in ((400.0, 500.0), (700.0, 650.0), (911.3, 333.7)):
        core = s._core_geom(x, y, 46.0, 28.0, False)
        for side in s._NUC_SIDES:
            g = s._bundle_geom(x, y, 46.0, 28.0, side, False)
            assert core["boxes"]["house"] == g["boxes"]["house"] and core["boxes"]["yard"] == g["boxes"]["yard"], (x, y, side)
            assert core["turn"] == g["turn"]


def test_a_seat_reaches_the_tree_only_where_a_door_has_a_corridor_and_the_search_continues_from_its_peek(monkeypatch) -> None:
    s = _open()
    assert seat_reaches_tree(s, s._core_geom(500.0, 500.0, 46.0, 28.0)), "no tree installed: nothing is held"
    s._access = AccessTree(7.0)
    s._access.add((0.0, 600.0), (1400.0, 600.0))
    calls: list[int] = []
    real = access._house_candidates

    def counted(*a, **k):
        calls.append(1)
        return real(*a, **k)

    monkeypatch.setattr(access, "_house_candidates", counted)
    core = s._core_geom(500.0, 500.0, 46.0, 28.0)
    assert seat_reaches_tree(s, core) and seat_reaches_tree(s, core), "a door below the house sees the line"
    assert len(calls) == 1, "the memo entry is made once and peeked again"
    monkeypatch.setattr(access, "_house_candidates", lambda *a, **k: iter(()))
    assert not seat_reaches_tree(s, s._core_geom(300.0, 200.0, 46.0, 28.0)), "no candidate at all: the seat is refused"


def test_a_seat_failing_its_own_questions_builds_no_layout(monkeypatch) -> None:
    from l7r.diagram.settlement.rolling import place

    s = _open()
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    built: list[str] = []
    monkeypatch.setattr(type(s), "_bundle_geom", lambda self, *a, **k: built.append("x") or {})
    monkeypatch.setattr(place, "seat_reaches_tree", lambda s_, core: False)
    assert s._place_bundle_nucleated(500.0, 500.0, 46.0, 28.0) is None and not built, "no corridor: no layout"
    monkeypatch.setattr(place, "seat_reaches_tree", lambda s_, core: True)
    monkeypatch.setattr(place, "within_field_reach", lambda s_, x, y: False)
    assert s._place_bundle_nucleated(500.0, 500.0, 46.0, 28.0) is None and not built, "beyond the field's reach: no layout"
    monkeypatch.setattr(place, "within_field_reach", lambda s_, x, y: True)
    s._household_watered, s._household_well = True, False
    monkeypatch.setattr(place, "watered", lambda s_, x, y, well: False)
    assert s._place_bundle_nucleated(500.0, 500.0, 46.0, 28.0) is None and not built, "no water: no layout"
