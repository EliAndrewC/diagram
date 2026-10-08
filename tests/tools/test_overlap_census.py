"""The overlap census (feature 306, FR-006): comparisons per call of every check a roll runs, the ones past the flag named.

The GM's rule, 2026-10-02: an overlap check against more than a certain number of other things means a box or a line to stay
on the right side of was not drawn. These tests hold the instrument to what it claims: a scan over many items is flagged and an
indexed ask is not; a measure inside a measure is one comparison; a comprehension is its function's; shapely's predicates
count; the census disarms when it ends. The rolls are stand-in stages (no map), as the perf tools' are."""

from __future__ import annotations

import pathlib
from typing import Any

import pytest
from shapely.geometry import Point

from l7r.diagram.settlement._geom.primitives import edge_dist, seg_dist
from l7r.diagram.tools import overlap_census as oc

SEGS = [((float(i), 0.0), (float(i) + 1.0, 0.0)) for i in range(6000)]


def scan_every_item(p: tuple[float, float]) -> float:
    """A check with no box: every segment on the map measured."""
    return min(seg_dist(p[0], p[1], a, b) for a, b in SEGS)


def ask_the_near_ones(p: tuple[float, float]) -> float:
    """The same check with its box: three segments near the point."""
    i = int(p[0])
    return min(seg_dist(p[0], p[1], a, b) for a, b in SEGS[max(0, i - 1) : i + 2])


def a_ring_measured() -> float:
    """One `edge_dist`, which measures every edge itself: one comparison, not four."""
    return edge_dist(0.0, 0.0, [(1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)])


def shapely_asked() -> bool:
    return Point(0.0, 0.0).intersects(Point(0.0, 0.0))


def _row(rows: list[tuple[float, str, str, int, int]], fn: str) -> tuple[float, str, str, int, int]:
    return next(r for r in rows if r[2].endswith(f":{fn}"))


def test_a_scan_over_every_item_is_flagged_and_an_indexed_ask_is_not() -> None:
    with oc.Census() as c:
        c.stage = "web"
        scan_every_item((10.0, 1.0))
        for _ in range(4):
            ask_the_near_ones((10.0, 1.0))
    rows = c.rows()
    scan, near = _row(rows, "scan_every_item"), _row(rows, "ask_the_near_ones")
    assert scan[0] == 6000 and scan[3] == 1 and scan[1] == "web"
    assert near[0] == 3 and near[3] == 4 and near[4] == 12
    text = oc.report(rows, oc.CENSUS_FLAG, 0)
    assert "1 check(s) over 5,000" in text and "scan_every_item" in text.split("FLAGGED")[0]
    assert "ask_the_near_ones" not in text, "a row under the flag is shown only within `top`"


def test_a_measure_inside_a_measure_is_one_comparison_and_shapely_counts() -> None:
    with oc.Census() as c:
        a_ring_measured()
        shapely_asked()
    rows = c.rows()
    assert _row(rows, "a_ring_measured")[4] == 1
    assert _row(rows, "shapely_asked")[4] == 1


def test_the_census_disarms_when_it_ends() -> None:
    with oc.Census() as c:
        ask_the_near_ones((5.0, 0.0))
    ask_the_near_ones((5.0, 0.0))
    assert _row(c.rows(), "ask_the_near_ones")[3] == 1


def test_a_frame_with_no_caller_and_one_wholly_inside_the_measures_are_not_charged() -> None:
    c = oc.Census()

    class Frame:
        def __init__(self, filename: str, back: Any) -> None:
            self.f_code = type("Code", (), {"co_filename": filename, "co_name": "f"})()
            self.f_back = back

    import os

    shapely_file = os.sep + os.path.join("a", "shapely", "b.py")
    c.charge(Frame("x.py", None))  # no caller
    c.charge(Frame("x.py", Frame(shapely_file, None)))  # a measure called it: part of that one
    # a caller that is only a comprehension, with nothing named above it: nowhere to charge
    lone = Frame("q.py", None)
    lone.f_code = type("Code", (), {"co_filename": "q.py", "co_name": "<genexpr>"})()
    c.charge(Frame("x.py", lone))
    assert not c.comparisons


def test_the_names_and_the_measures() -> None:
    assert oc.inside(str(pathlib.Path("x") / "settlement" / "_geom" / "p.py").replace("x", "/x")) and not oc.inside("/x/hamletgen/plan.py")
    assert oc.name_of(scan_every_item.__code__).endswith("test_overlap_census.py:scan_every_item")
    names = {f.__name__ for f in oc.primitives()}
    assert {"seg_dist", "point_in_poly", "intersects", "distance"} <= names


def test_a_pool_gen_hands_over_its_spec_without_rolling(tmp_path: pathlib.Path) -> None:
    gen = tmp_path / "x.gen.py"
    gen.write_text("from l7r.diagram.hamletgen import HamletSpec, generate\ngenerate(HamletSpec(name='X', seed=5, households=12), out_base='nowhere')\n", encoding="utf-8")
    spec = oc.spec_of(str(gen))
    assert (spec.name, spec.seed, spec.households) == ("X", 5, 12)
    idle = tmp_path / "idle.gen.py"
    idle.write_text("x = 1\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="handed generate no spec"):
        oc.spec_of(str(idle))


def test_the_specs_are_the_gens_and_the_reference_at_its_size(tmp_path: pathlib.Path) -> None:
    gen = tmp_path / "x.gen.py"
    gen.write_text("from l7r.diagram.hamletgen import HamletSpec, generate\ngenerate(HamletSpec(name='X', seed=5, households=12))\n", encoding="utf-8")
    got = oc.specs([str(gen)], 40)
    assert [s.households for s in got] == [12, 40]
    assert oc.specs([], 0) == []


def test_a_roll_labels_each_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stand-in stages (feature 214's form): the census is told each stage's name as it runs."""
    from l7r.diagram.hamletgen import HamletSpec, driver

    seen: list[str] = []

    def stage_field(s: Any, plan: Any) -> None:  # noqa: ARG001
        seen.append(census.stage)

    def stage_web(s: Any, plan: Any) -> None:  # noqa: ARG001
        seen.append(census.stage)

    monkeypatch.setattr(driver, "STAGES", (stage_field, stage_web))
    census = oc.Census()
    oc.roll(HamletSpec(name="X", seed=6, households=10), census)
    assert seen == ["field", "web"]


def test_main_rolls_the_pool_and_prints_the_report(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    rolled: list[Any] = []
    monkeypatch.setattr(oc, "specs", lambda gens, h: [("spec", tuple(gens), h)])
    monkeypatch.setattr(oc, "roll", lambda spec, census: rolled.append(spec) or scan_every_item((1.0, 1.0)))
    assert oc.main(["--gens", "a.gen.py", "--households", "0", "--top", "2"]) == 0
    assert rolled == [("spec", ("a.gen.py",), 0)]
    assert "FLAGGED" in capsys.readouterr().out
    monkeypatch.setattr(oc, "specs", lambda gens, h: [("all", len(gens) >= 5, h)])
    rolled.clear()
    oc.main([])
    assert rolled == [("all", True, oc.REFERENCE_HOUSEHOLDS)], "by default every pool hamlet and the reference at 40"


def test_charging_called_directly_counts_the_check_and_arms_it_once() -> None:
    """`charge` and `_start` run inside `sys.monitoring`'s callbacks, where coverage cannot see them; asked directly here with
    the real frames of this test (the frame passed is the 'measure's', so the charge goes to its caller - this test)."""
    import sys

    with oc.Census() as c:
        c.stage = "seat"
        c.charge(sys._getframe(0))  # the measure's frame is this one: charged to this test's caller
        caller = sys._getframe(1).f_code
        assert c.comparisons[("seat", caller)] == 1 and c.calls[("seat", caller)] == 1 and caller in c._armed
        c.charge(sys._getframe(0))  # armed already: a second comparison, no second count of the call under way
        assert c.comparisons[("seat", caller)] == 2 and c.calls[("seat", caller)] == 1
        c._start(caller, 0)  # an armed check starting: a call
        assert c.calls[("seat", caller)] == 2
        c._start(scan_every_item.__code__, 0)  # not armed: `_start` hands `charge` this test's frame, charged to its caller
        assert c.comparisons[("seat", caller)] == 3


def test_the_skill_root_is_put_on_sys_path_when_it_is_not_already_there(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib
    import sys

    monkeypatch.setattr(sys, "path", [p for p in sys.path if pathlib.Path(p).resolve() != pathlib.Path(oc.SKILL).resolve()])
    reloaded = importlib.reload(oc)
    assert pathlib.Path(reloaded.SKILL).resolve() in [pathlib.Path(p).resolve() for p in sys.path]


def test_a_refused_roll_is_said_and_the_census_goes_on(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from l7r.diagram.hamletgen.ways.last_resort import WebRefused

    def roll(spec: Any, census: Any) -> None:
        if spec == "bad":
            raise WebRefused("lanes 8 (access)")
        scan_every_item((1.0, 1.0))

    monkeypatch.setattr(oc, "specs", lambda gens, h: ["bad", "good"])
    monkeypatch.setattr(oc, "roll", roll)
    assert oc.main(["--gens"]) == 0
    out = capsys.readouterr().out
    assert "refused (its checks counted up to the refusal): bad: WebRefused: lanes 8 (access)" in out and "FLAGGED" in out
