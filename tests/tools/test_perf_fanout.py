"""`tools/perf_fanout.py` (feature 427 T01, D1): the call-volume survey - its chain walk on synthetic `pstats` data, the report,
and the survey and command line with the profiling seam stubbed, as `perf_profile`'s own tests stub it.

Not marked `tooling`: it runs in milliseconds, and a `tooling`-marked test outside the tooling tree can go uncounted by the gate's
coverage floor (feature 430's research R1, the sixth red, 9a157cc4b)."""

from __future__ import annotations

import cProfile
import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.tools import perf_fanout as pf
from l7r.diagram.tools import perf_profile

E = "/r/l7r/diagram/hamletgen/ways/law.py"
ANCHOR = (E, 10, "stage_lanes")
LOOP = (E, 20, "seat_all")
LAMBDA = (E, 25, "<lambda>")
LEAF = (E, 40, "dist")
MIN = ("~", 0, "<built-in method builtins.min>")


def _row(n: int, callers: dict[Any, int]) -> tuple[Any, ...]:
    return (n, n, 0.0, 0.0, {c: (k, k, 0.0, 0.0) for c, k in callers.items()})


def _stats(scale: int = 1) -> dict[Any, tuple[Any, ...]]:
    """stage_lanes (called once) -> seat_all (300 x scale) -> min(key=lambda) -> lambda -> dist, the lambda reached only through
    the builtin, as `min(..., key=lambda c: dist(c))` is."""
    return {
        ANCHOR: _row(1, {}),
        LOOP: _row(300 * scale, {ANCHOR: 300 * scale}),
        MIN: _row(300 * scale, {LOOP: 300 * scale}),
        LAMBDA: _row(60_000 * scale, {MIN: 60_000 * scale}),
        LEAF: _row(120_000 * scale, {LAMBDA: 120_000 * scale}),
    }


def test_short_names_engine_files_from_the_package_and_builtins_by_name() -> None:
    assert pf.short(LEAF) == "hamletgen/ways/law.py:40:dist"
    assert pf.short(("/usr/lib/python3/heapq.py", 5, "heappush")) == "heapq.py:5:heappush"
    assert pf.short(MIN) == "builtins.min"


def test_a_lambda_reached_only_through_a_builtin_steps_to_its_enclosing_def() -> None:
    st = _stats()
    assert pf.next_up(st, LEAF) == LAMBDA
    assert pf.next_up(st, LAMBDA) == LOOP, "the def it is written in, not the builtin that called it"
    assert pf.enclosing(st, LAMBDA) == LOOP
    assert pf.next_up(st, ANCHOR) is None


def test_the_chain_climbs_the_heaviest_edge_to_an_anchor_and_groups_by_it() -> None:
    st = _stats()
    ch = pf.chain(st, LEAF)
    assert [k for k, _n in ch] == [LEAF, LAMBDA, LOOP], "stops at seat_all: 300 calls is the anchor bound"
    by = pf.anchors(st)
    assert set(by) == {LOOP} and len(by[LOOP]) == 2, "dist and the lambda both hang from the loop"
    assert pf.anchors(st, hot=200_000) == {}


def test_totals_growth_and_growers() -> None:
    small, large = _stats(1), _stats(4)
    assert pf.total(small) == 1 + 300 + 300 + 60_000 + 120_000
    assert pf.exponent(1000, 4000, 2.0) == pytest.approx(2.0), "four times the calls for twice the size: quadratic"
    assert math.isnan(pf.exponent(0, 10, 2.0)) and math.isnan(pf.exponent(5, 10, 1.0))
    rows = pf.growers(small, large)
    assert rows[0][1] in (LEAF, LAMBDA) and rows[0][0] == pytest.approx(4.0)
    assert all(r[3] >= pf.GROWER for r in rows)


def test_the_stage_report_lists_every_chain_of_a_hot_function_with_both_sizes() -> None:
    """SC-001: every chain of HOT calls or more, with no floor on the stage's total."""
    out = pf.stage_report("lanes", {20: _stats(1), 40: _stats(2)})
    assert out[0].startswith("lanes: 180,601 calls @20, 361,201 calls @40, growth exponent")
    assert "  anchor hamletgen/ways/law.py:10:stage_lanes [1]" in out, "at 40 the loop runs 600 times, past the anchor bound: up to the stage"
    assert any("hamletgen/ways/law.py:40:dist [240,000|120,000]" in ln for ln in out)
    assert any("fastest growers @20 -> @40" in ln for ln in out)
    one = pf.stage_report("lanes", {40: _stats(1)})
    assert "growth" not in one[0] and not any("growers" in ln for ln in one) and any("dist [120,000]" in ln for ln in one)
    quiet = pf.stage_report("lanes", {40: _stats(1)}, hot=10**9)
    assert quiet == [quiet[0]], "no hot function: totals only"


def _prof(tmp: Path, name: str, n: int) -> str:
    def leaf(x: int) -> int:
        return x + 1

    prof = cProfile.Profile()
    prof.enable()
    for i in range(n):
        leaf(i)
    prof.disable()
    path = tmp / f"{name}.prof"
    prof.dump_stats(str(path))
    return str(path)


def test_the_survey_profiles_each_size_and_stage_once_and_reports_the_totals(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[tuple[int, str, int | None]] = []

    def profile_stage(seed: int, stage: str, top: int, households: int | None = None) -> tuple[str, str]:
        seen.append((seed, stage, households))
        return "", _prof(tmp_path, f"{stage}-{households}", 100 * (households or 1))

    monkeypatch.setattr(perf_profile, "profile_stage", profile_stage)
    report = pf.survey(39, [20, 40], ["water", "lanes"], jobs=2, hot=1000, pool_cls=ThreadPoolExecutor)
    assert sorted(seen) == [(39, "lanes", 20), (39, "lanes", 40), (39, "water", 20), (39, "water", 40)]
    assert report.startswith("perf-fanout seed 39, sizes 20, 40, HOT 1,000, ANCHOR 300")
    assert "water: " in report and "lanes: " in report and report.rstrip().splitlines()[-1].startswith("all stages: ")


def test_the_command_line_writes_the_report_and_refuses_an_unknown_stage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(pf, "stage_names", lambda: ["water", "lanes"])
    got: dict[str, Any] = {}

    def survey(seed: int, sizes: list[int], stages: list[str], jobs: int, hot: int) -> str:
        got.update(seed=seed, sizes=sizes, stages=stages, jobs=jobs, hot=hot)
        return "THE REPORT\n"

    monkeypatch.setattr(pf, "survey", survey)
    monkeypatch.setattr(perf_profile, "LOG_DIR", str(tmp_path / "perf-log"))
    monkeypatch.setattr(perf_profile, "SKILL", str(tmp_path))
    assert pf.main(["--households", "40,20", "--label", "t01"]) == 0
    assert got == {"seed": 39, "sizes": [20, 40], "stages": ["water", "lanes"], "jobs": pf.JOBS, "hot": pf.HOT}
    written = list((tmp_path / "perf-log").glob("*-fanout-t01.txt"))
    assert len(written) == 1 and written[0].read_text() == "THE REPORT\n" and "wrote perf-log/" in capsys.readouterr().out
    assert pf.main(["--stages", "lanes", "--jobs", "1"]) == 0 and got["stages"] == ["lanes"] and got["jobs"] == 1
    with pytest.raises(SystemExit, match="no stage nosuch"):
        pf.main(["--stages", "nosuch"])


def test_the_stage_names_are_the_drivers() -> None:
    from l7r.diagram.hamletgen.driver import STAGES

    assert pf.stage_names() == [st.__name__.replace("stage_", "") for st in STAGES] and "web" in pf.stage_names()
