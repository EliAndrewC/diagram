"""The waterward reed strip runs off the frame (feature 287, water:W43): decided in `stage_frame`, where the view is final."""

from typing import Any

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement, point_in_poly

fr = hg.frame

DIKE = [(800.0, 800.0), (1200.0, 800.0), (1200.0, 1200.0), (800.0, 1200.0)]


def _polder(view: list[float]) -> Settlement:
    s = Settlement(2400, 2400, seed=4)
    s.meta(name="P", scale="hamlet", ftpx=1, waterward=["W", "S"])
    s.M["dikes"] = [{"outline": [list(p) for p in DIKE], "crest": [[790.0, 790.0], [790.0, 1210.0]], "w_min": 10.0, "w_max": 10.0}]
    s.M["meta"]["view"] = view
    return s


def test_the_strip_face_and_its_reach_are_read_from_the_record() -> None:
    box = (800.0, 800.0, 1200.0, 1200.0)
    west = [(520.0, 770.0), (790.0, 770.0), (790.0, 1220.0), (520.0, 1220.0)]
    south = [(770.0, 1210.0), (1220.0, 1210.0), (1220.0, 1490.0), (770.0, 1490.0)]
    assert fr.strip_face(west, box) == "W" and fr.strip_face(south, box) == "S"
    assert fr.strip_face([(1210.0, 800.0), (1480.0, 800.0), (1480.0, 1200.0), (1210.0, 1200.0)], box) == "E"
    assert fr.strip_face([(800.0, 520.0), (1200.0, 520.0), (1200.0, 790.0), (800.0, 790.0)], box) == "N"
    assert not fr.strip_reaches_view(west, (100.0, 100.0, 2000.0, 2000.0), ["W"])
    assert fr.strip_reaches_view(west, (600.0, 100.0, 2000.0, 2000.0), ["W"])
    assert fr.strip_reaches_view(south, (100.0, 100.0, 1300.0, 1300.0), ["S", "Q"])
    assert fr.band_to_edge(west, "W", (100.0, 100.0, 2000.0, 2000.0)) == [(80.0, 770.0), (522.0, 770.0), (522.0, 1220.0), (80.0, 1220.0)]
    assert fr.band_to_edge(west, "E", (100.0, 100.0, 1000.0, 2000.0))[1][0] == 1120.0
    assert fr.band_to_edge(south, "S", (100.0, 100.0, 2000.0, 2000.0))[2][1] == 2120.0
    assert fr.band_to_edge(south, "N", (100.0, 100.0, 2000.0, 2000.0))[0][1] == 80.0


def test_a_strip_that_stops_inside_the_view_is_carried_to_its_edge() -> None:
    """The violating case: the view reaches 400 ft west of the dike and the strip stops at `WATERWARD_DEPTH`. After the
    frame's pass the strip's record runs to the view's edge, still one record; a strip already reaching the edge and a
    strip on a landward flank are left as they are."""
    s = _polder([100.0, 100.0, 2000.0, 2000.0])
    s.marsh([(520.0, 770.0), (790.0, 770.0), (790.0, 1220.0), (520.0, 1220.0)], role="waterside")
    s.marsh([(770.0, 1210.0), (1220.0, 1210.0), (1220.0, 2200.0), (770.0, 2200.0)], role="waterside")  # already off the frame
    s.marsh([(1210.0, 800.0), (1480.0, 800.0), (1480.0, 1200.0), (1210.0, 1200.0)], role="waterside")  # east: landward here
    before = [list(m["poly"]) for m in s.M["marshes"]]
    faces, view = s.M["meta"]["waterward"], s.M["meta"]["view"]
    assert not fr.strip_reaches_view(before[0], view, faces), "the constructed short strip"
    fr.waterward_to_the_frame(s)
    strips = [m for m in s.M["marshes"] if m["role"] == "waterside"]
    assert len(strips) == 3
    assert fr.strip_reaches_view(strips[0]["poly"], view, faces)
    assert strips[1]["poly"] == before[1] and strips[2]["poly"] == before[2]


def test_a_band_with_no_open_ground_adds_nothing_and_a_separate_ground_keeps_its_own_record() -> None:
    s = _polder([100.0, 100.0, 2000.0, 2000.0])
    s.marsh([(520.0, 770.0), (790.0, 770.0), (790.0, 1220.0), (520.0, 1220.0)], role="waterside")
    s.block_polys.append([(0.0, 0.0), (523.0, 0.0), (523.0, 2400.0), (0.0, 2400.0)])  # the whole band is built ground
    fr.waterward_to_the_frame(s)
    assert len(s.M["marshes"]) == 1
    t = _polder([100.0, 100.0, 2000.0, 2000.0])
    t.marsh([(520.0, 770.0), (790.0, 770.0), (790.0, 1220.0), (520.0, 1220.0)], role="waterside")
    t.block_polys.append([(505.0, 0.0), (530.0, 0.0), (530.0, 2400.0), (505.0, 2400.0)])  # a lane between strip and band
    fr.waterward_to_the_frame(t)
    (strip,) = t.M["marshes"]
    assert fr.strip_reaches_view(strip["poly"], t.M["meta"]["view"], ["W"]), "two grounds that do not join are one record, bridged"
    assert point_in_poly(515.0, 1000.0, strip["poly"]) is False, "the lane between them stays outside the record"
    assert point_in_poly(600.0, 1000.0, strip["poly"]) and point_in_poly(300.0, 1000.0, strip["poly"])


def test_one_ring_keeps_a_hole_out_and_bridges_a_second_piece_either_way_round() -> None:
    from shapely.geometry import MultiPolygon, Polygon

    sq = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    far = [(30.0, 0.0), (40.0, 0.0), (40.0, 10.0), (30.0, 10.0)]
    holed = Polygon(sq, [[(4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0)]])
    for other in (far, far[::-1]):
        ring = fr.one_ring(MultiPolygon([holed, Polygon(other)]))
        inside = {(x, y): point_in_poly(x, y, ring) for x, y in ((2.0, 2.0), (5.0, 5.0), (20.0, 5.0), (35.0, 5.0))}
        assert inside == {(2.0, 2.0): True, (5.0, 5.0): False, (20.0, 5.0): False, (35.0, 5.0): True}
        assert Polygon(ring).buffer(0).area == pytest.approx(100.0 - 4.0 + 100.0)


def test_no_waterward_declaration_changes_nothing() -> None:
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1)
    fr.waterward_to_the_frame(s)
    assert s.M["marshes"] == []


def test_the_frame_carries_the_strips_after_the_title(monkeypatch: pytest.MonkeyPatch) -> None:
    """The view is final only once the title has grown its band, so the strips are carried to the edge after it."""
    calls: list[str] = []
    s: Any = type("_S", (), {})()
    s.M = {"meta": {}}
    s.crop_to_view = lambda view: calls.append("crop")
    s.title = lambda name, prefer=None: calls.append("title")
    plan: Any = type("_P", (), {"view": (0, 0, 10, 10), "spec": type("_Sp", (), {"name": "X"})()})()
    monkeypatch.setattr(fr, "title_pocket", lambda s_, plan_: (0.0, 0.0, 1.0, 1.0))
    monkeypatch.setattr(fr, "frame_for", lambda s_, plan_: (0, 0, 10, 10))
    monkeypatch.setattr(fr, "waterward_to_the_frame", lambda s_: calls.append("waterward"))
    fr.stage_frame(s, plan)
    assert calls == ["crop", "title", "waterward"]
