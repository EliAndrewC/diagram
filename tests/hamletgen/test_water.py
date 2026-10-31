"""Unit tests for the water frame and the field it shapes (`hamletgen/water/`), plus the waterfields frame math it stands on.

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from ._builders import a_plan

# ---- the derivations that read the map ----------------------------------------------------------


def test_declared_knob_pins_reach_the_engine() -> None:
    """A `pins` entry is forwarded to the engine's own knob catalog, so a spec can steer a knob this
    module does not model (a land-use overlay, a field archetype)."""
    from l7r.diagram.settlement import Settlement

    plan = hg.plan_site(hg.HamletSpec(name="Pinned", seed=2, households=12, pins={"land_use_overlay": "lotus"}))
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    hg.stage_water_frame(s, plan)
    assert s.knob_pins["land_use_overlay"] == "lotus"


def test_dike_face_reads_the_rings_own_side_and_carries_a_gap() -> None:
    """`dike_face` (feature 150 T54) is what makes the waterward strip end exactly at the embankment:
    it takes the OUTERMOST point per bin on the flank's own half of the ring, so the strip can only
    stop at or outside the face - and a bin the ring does not reach (a crossing GAP cuts the outline,
    and the strip runs past the dike's ends) keeps its neighbor's face rather than jumping to the far
    side, which is how Kuwabata's west strip once came out 2,422 px wide and drowned the map."""
    ring = [(200.0, y) for y in range(200, 401, 10)]  # west face, y 200-400
    ring += [(210.0, y) for y in range(600, 801, 10)]  # west face again below a gap, 10 px further in
    ring += [(900.0, y) for y in range(200, 801, 10)]  # the east face
    face = hg.water.dike_face(ring, "W", 100.0, 900.0, bins=16)
    assert 3 <= len(face) <= 16  # thinned as it goes: a straight run of bins emits two points, not sixteen
    assert all(x <= 210.0 for x, _y in face), f"the east face leaked into the west flank: {face}"
    at = lambda y: min(face, key=lambda p: abs(p[1] - y))[0]  # noqa: E731 - the bin whose center is nearest y
    assert at(250.0) == 200.0 and at(750.0) == 210.0  # each stretch reports its own face
    assert at(500.0) == 200.0  # the gap between them keeps the neighbor's, not a jump across the ring
    east = hg.water.dike_face(ring, "E", 100.0, 900.0, bins=16)
    assert all(x >= 900.0 for x, _y in east)
    # a NOTCH the dike RECORDS steps the face inward, so the wet ground reaches into the cut; the same
    # empty bins with nothing recorded there stay at the neighbor's face (a sparse ring is not a notch)
    notched = hg.water.dike_face(ring, "W", 100.0, 900.0, bins=16, cut=40.0, cuts=[(205.0, 500.0)])
    at_n = min(notched, key=lambda p: abs(p[1] - 500.0))[0]
    assert at_n == 240.0, notched
    assert min(notched, key=lambda p: abs(p[1] - 250.0))[0] == 200.0  # the face itself is untouched
    # ...and the step reads the RECORD, not an empty bin: a notch whose own bin is FULL (the ring's cut
    # ends fill it, which is what Kuwabata's does - the first cut of this rule never fired anywhere)
    full = [(200.0, y) for y in range(200, 801, 10)]  # an unbroken west face, no gap at all
    full += [(900.0, y) for y in range(200, 801, 10)]
    stepped = hg.water.dike_face(full, "W", 100.0, 900.0, bins=16, cut=40.0, cuts=[(205.0, 500.0)])
    assert min(stepped, key=lambda p: abs(p[1] - 500.0))[0] == 240.0, stepped
    assert min(stepped, key=lambda p: abs(p[1] - 250.0))[0] == 200.0


def test_the_waterward_strip_stops_at_the_dikes_face() -> None:
    """T54: no strip vertex may stand inside the drawn band, and the strip must still cover the
    ground 28 px outside the dike's extreme, which is where `polder_waterward_flanks_wet` samples."""
    plan = a_plan()
    plan.field_archetype = "polder_grid"
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    band = [(500.0 + 40.0 * (i % 2), 400.0 + i * 10.0) for i in range(40)]  # a wandering west face
    band += [(1400.0, 400.0 + i * 10.0) for i in range(40)]
    s.M["dikes"] = [{"outline": [list(p) for p in band], "w_min": 14.0, "w_max": 38.0}]
    hg.water.stage_waterward(s, plan)
    strips = [m for m in s.M["marshes"] if m["role"] == "waterside"]
    assert strips, "no waterward strip was drawn"
    west = [m for m in strips if m["x"] < 900][0]
    assert max(p[0] for p in west["poly"]) <= 540.0  # never past the outermost face of the band
    assert hg.point_in_poly(500.0 - 28.0, 600.0, [(float(a), float(b)) for a, b in west["poly"]])  # the check's own sample is inside


# ---- feature 219: Polder 12's three lines, as unit tests of the functions that own them ----------------


# ---- the intake, and the brook that runs on past it (feature 230) --------------------------------


def test_the_finished_course_rounds_the_bends_and_holds_the_tap() -> None:
    """`finished_course` (feature 287, M2): a course in, the drawn course out - every free corner rounded at
    `BROOK_BEND_WIDTHS` of the width, the vertex at the tap kept, the ends kept; a tap more than a foot off every vertex,
    or at an end, holds nothing; a two-point course has no corner."""
    from l7r.diagram.hamletgen.consts import BROOK_BEND_WIDTHS
    from l7r.diagram.hamletgen.water.brook import finished_course
    from l7r.diagram.settlement._geom import fillet_polyline

    course = [(0.0, 0.0), (300.0, 0.0), (300.0, 300.0), (600.0, 300.0)]
    held = finished_course(course, 8.0, [(300.4, 300.3)])
    assert held[0] == (0.0, 0.0) and held[-1] == (600.0, 300.0) and (300.0, 300.0) in held, "the ends and the tap stay"
    assert (300.0, 0.0) not in held and len(held) > 4, "the free corner is rounded"
    assert held == [*fillet_polyline(course[:3], BROOK_BEND_WIDTHS * 8.0), *fillet_polyline(course[2:], BROOK_BEND_WIDTHS * 8.0)[1:]]
    free = finished_course(course, 8.0, [(300.0, 302.0), (0.0, 0.0)])
    assert free == fillet_polyline(course, BROOK_BEND_WIDTHS * 8.0) and (300.0, 300.0) not in free, "no tap within a foot: both corners round"
    assert finished_course([(0, 0), (5, 5)], 8.0) == [(0.0, 0.0), (5.0, 5.0)]


def test_round_the_brooks_draws_each_brook_at_its_finished_course() -> None:
    """`round_the_brooks` + `Settlement.round_stream` (feature 287, M2): the drawn brook IS `finished_course` of the course
    as first drawn, its width and the head race's tap; the first course is kept as `stations`, the no-build corridor
    follows the drawn course, a second pass draws the same course, and a two-point stream is left alone."""
    from l7r.diagram.hamletgen.water.brook import finished_course, round_the_brooks

    s = Settlement(800, 800, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    first = [(100.0, 100.0), (400.0, 100.0), (400.0, 400.0), (700.0, 400.0)]
    s.stream(first, width=9)
    s.stream([(10.0, 10.0), (20.0, 700.0)], width=7)
    s.M["channels"].append({"poly": [[400.0, 400.0], [460.0, 520.0]], "frm": {"kind": "stream"}, "to": {"kind": "field"}, "w": 6})
    s.M["channels"].append({"poly": [], "frm": {"kind": "stream"}})
    rec, short = s.M["streams"][-2], s.M["streams"][-1]
    round_the_brooks(s)  # type: ignore[arg-type]
    want = finished_course(first, 9.0, [(400.0, 400.0)])
    assert [tuple(p) for p in rec["poly"]] == want, "round_stream applies finished_course"
    assert (400.0, 400.0) in want and (400.0, 100.0) not in want
    assert rec["stations"] == [list(p) for p in first], "the course as first drawn is kept"
    assert any(list(c[0]) == want for c in s.corridors) and not any(list(c[0]) == first for c in s.corridors), "the corridor follows"
    round_the_brooks(s)  # type: ignore[arg-type]
    assert [tuple(p) for p in rec["poly"]] == want, "a second pass rounds the first course again, not the rounded one"
    assert "stations" not in short and short["poly"] == [[10.0, 10.0], [20.0, 700.0]]


def test_the_sink_stage_finishes_the_water_after_the_sink(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, M2: the brook is rounded as `stage_sink`'s last step - after the drain is laid, before the seat."""
    calls: list[str] = []
    monkeypatch.setattr(hg.sink, "lay_sink", lambda s_, plan_: calls.append("sink"))
    monkeypatch.setattr(hg.sink, "round_the_brooks", lambda s_: calls.append("round"))
    from types import SimpleNamespace

    s = SimpleNamespace(M={"meta": {}})
    hg.sink.stage_sink(s, SimpleNamespace(water_sink="offmap"))  # type: ignore[arg-type]
    assert calls == ["sink", "round"]
    assert s.M["meta"]["water_sink"] == "offmap", "the sink as drawn is recorded for the title card (feature 319 plan D10)"
    names = [st.__name__ for st in hg.driver.STAGES]
    assert names.index("stage_sink") + 1 == names.index("stage_seat"), "nothing reads the water between the sink and the seat"


def test_the_ways_route_against_the_course_as_first_drawn() -> None:
    """`stream_segs` (feature 287, M2): the router's brook is the `stations` - the course before rounding - so rounding
    the brook early does not move the ways; a stream never rounded is read from its poly."""
    from l7r.diagram.hamletgen.ways.checks import stream_segs

    class _S:
        M = {"streams": [{"poly": [[0, 0], [5, 3], [10, 0]], "stations": [[0, 0], [10, 0]]}, {"poly": [[0, 50], [0, 90]]}, {"poly": []}]}

    assert stream_segs(_S()) == [((0.0, 0.0), (10.0, 0.0)), ((0.0, 50.0), (0.0, 90.0))]  # type: ignore[arg-type]


def test_a_hamlet_keeps_its_yards_wherever_grain_is_grown() -> None:
    """Feature 328 (0037: every rice and dry-field farm keeps a yard): the yards go only where no grain grows - a dike-pond
    hamlet whose leftover parcels are ponds - and a dike-pond hamlet with rice left, or a dry-field one, keeps them."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.water.skeleton import grows_grain

    assert not grows_grain(SimpleNamespace(field_archetype="mulberry_dike_fishpond", leftover="pond"))  # type: ignore[arg-type]
    assert grows_grain(SimpleNamespace(field_archetype="mulberry_dike_fishpond", leftover="rice"))  # type: ignore[arg-type]
    assert grows_grain(SimpleNamespace(field_archetype="dry_terrace", leftover="rice"))  # type: ignore[arg-type]
