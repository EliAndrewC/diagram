"""The perf report's two bands - the DIAGNOSE trigger and the CAP - proven to fire and to stay quiet.

Constitution XVIII: a guard ships with a test companion, and the companion proves it FIRES. This one
is worth pinning harder than most, because the guard's whole history is of noticing without acting -
it printed "diagnose before shipping" and returned 0 for its first three weeks, so feature 127 shipped
its own push before the report had been read. A test that only checked the printed text would have
passed throughout that.
"""

from __future__ import annotations

import json
import json as _json
import os
import platform as _platform
import subprocess as _subprocess
from pathlib import Path as _Path
from typing import Any
from typing import Any as _Any

import pytest

from l7r.diagram.tools import perf_snapshot as ps


def _snap(tmp: Any, label: str, seconds: dict[int, float], utc: str) -> None:
    rows = [{"seed": s, "seconds": v} for s, v in seconds.items()]
    total = sum(seconds.values())
    body = {
        "utc": utc,
        "label": label,
        "commit": "abc1234",
        "rows": rows,
        "total_seconds": total,
        "median_seconds": sorted(seconds.values())[len(seconds) // 2],
        "worst_seconds": max(seconds.values()),
    }
    (tmp / f"{utc}-{label}.json").write_text(json.dumps(body), encoding="utf-8")


@pytest.fixture
def logdir(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    os.makedirs(tmp_path, exist_ok=True)
    return tmp_path


def test_a_20_percent_total_is_band_3_and_the_report_says_who_it_needs(logdir: Any, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 129 superseded the 10% CAP: the report exits 0 and PRINTS the band (FR-009b); the push enforces it."""
    _snap(logdir, "900-start", {1: 100.0, 2: 100.0}, "20260824T000000Z")
    _snap(logdir, "900-end", {1: 120.0, 2: 120.0}, "20260824T010000Z")
    assert ps.report("900-start") == 0
    out = capsys.readouterr().out
    assert "REGRESSION" not in out and "+20.0%" in out
    assert "band 3" in out and "total +20.0% > 10%" in out and "FLAG: this looks slower" in out, "a flag since feature 375 amendment 5"


def test_the_cap_STAYS_QUIET_when_the_aggregate_improves_even_with_a_slower_seed(logdir: Any, capsys: pytest.CaptureFixture[str]) -> None:
    """The motivating case: feature 128 reordered the stages, so the maps are genuinely different.

    One seed 31% slower, another 64% faster, total down 30%. The old rule blocked on the seed alone;
    the seed still has to be DIAGNOSED, but it no longer stops the merge."""
    _snap(logdir, "901-start", {4: 23.7, 25: 222.7, 39: 67.8, 47: 68.3}, "20260824T000000Z")
    _snap(logdir, "901-end", {4: 26.8, 25: 80.6, 39: 71.5, 47: 89.3}, "20260824T010000Z")
    assert ps.report("901-start") == 0
    out = capsys.readouterr().out
    assert "FLAG" in out and "seed 47 +30.7%" in out, "a seed over the line is still called out"
    assert "REGRESSION" not in out
    assert "-29.9%" in out
    assert "band 3" in out and "seed 47 +30.7% > 20%" in out, "SC-002b: faster overall, but seed 47 is flagged"


def test_a_seed_inside_the_noise_band_is_not_even_mentioned(logdir: Any, capsys: pytest.CaptureFixture[str]) -> None:
    """Under 5% nothing is owed - that band is the noise of a loaded machine."""
    _snap(logdir, "902-start", {1: 100.0}, "20260824T000000Z")
    _snap(logdir, "902-end", {1: 103.0}, "20260824T010000Z")
    assert ps.report("902-start") == 0
    out = capsys.readouterr().out
    assert "FLAG" not in out and "band 0" in out
    assert "REGRESSION" not in out


def test_the_cap_is_the_number_the_GM_set() -> None:
    """Pinned so a later session cannot drift it without the test saying so out loud - since feature 129 it is band 3's TOTAL line."""
    assert ps.TOTAL_SLOWDOWN_CAP_PCT == 10.0


def test_a_review_record_in_the_log_dir_does_not_break_the_trend(logdir: Any, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 129 keeps its review records beside the snapshots; the report must read past them (found by the perf-audit subagent)."""
    _snap(logdir, "903-start", {1: 100.0}, "20260825T000000Z")
    _snap(logdir, "903-end", {1: 106.0}, "20260825T010000Z")
    (logdir / "20260825T020000Z-review-903-explanation-local-c.json").write_text(json.dumps({"kind": "explanation", "feature": "903-x", "explanation": "noise"}), encoding="utf-8")
    assert ps.report("903-start") == 0
    assert "band 2" in capsys.readouterr().out, "one seed of one, +6%: the total is over band 2's 5% too"


# ---- feature 174: the recorder and the CLI ------------------------------------------------------


def test_a_worktree_reports_its_OWN_directory_rather_than_claiming_to_be_main(monkeypatch) -> None:
    """The first snapshot ever recorded was taken in a detached baseline worktree and this said
    "main" - in a project where main is never a workspace, that is a claim that would mislead anyone
    reading the trend later. A clone reports its clone name; a worktree reports its own directory."""
    monkeypatch.setattr(ps, "SKILL", "/diagram/.clones/diagram-tooling")
    assert ps._where() == "diagram-tooling"

    monkeypatch.setattr(ps, "SKILL", "/tmp/base125")
    monkeypatch.setattr(ps, "_git", lambda *a: "/tmp/base125")
    assert ps._where() == "base125", "the worktree's own name, not 'main'"

    monkeypatch.setattr(ps, "_git", lambda *a: "")
    assert ps._where() == "unknown", "and it never guesses"


def test_git_that_is_unavailable_degrades_to_an_empty_string(monkeypatch) -> None:
    """A snapshot is worth recording even where git is not answering; the commit field goes empty
    rather than the measurement being lost."""

    def boom(*_a: _Any, **_kw: _Any) -> _Any:
        raise OSError("no git")

    monkeypatch.setattr(_subprocess, "run", boom)
    assert ps._git("rev-parse", "HEAD") == ""


def test_the_machine_identity_pairs_on_a_CLASS_not_a_hostname(monkeypatch) -> None:
    """The laptop's container gets a fresh random hostname on every rebuild, so pairing on it would
    refuse every laptop-vs-laptop comparison across a rebuild. A build is keyed by compute type and
    image, so a change of either is a different machine and refuses to pair - which is the point:
    laptop and build numbers were never comparable, and pretending otherwise is how feature 126
    shipped a +51% slowdown unnoticed."""
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    local = ps.machine_identity()
    assert local["environment"] == "local" and local["host"] == "laptop"
    assert local["hostname"] == _platform.node(), "the hostname is recorded BESIDE the class, as information"

    monkeypatch.setenv("CODEBUILD_BUILD_ID", "build:123")
    monkeypatch.setenv("COMPUTE_TYPE", "BUILD_GENERAL1_XLARGE")
    monkeypatch.setenv("CODEBUILD_BUILD_IMAGE", "acct.dkr.ecr/diagram:latest")
    build = ps.machine_identity()
    assert build["environment"] == "codebuild" and build["host"] == "codebuild:BUILD_GENERAL1_XLARGE"
    assert build["image"].endswith(":latest")
    assert ps.identity_of(build) != ps.identity_of(local), "the two never pair"


def test_a_snapshot_older_than_the_identity_fields_is_read_as_a_LOCAL_laptop_run() -> None:
    """Every snapshot predating features 129/130 was taken locally; defaulting them anywhere else
    would silently re-key the whole historical trend."""
    assert ps.identity_of({"label": "126-start"}) == ("local", "laptop", "laptop")


def test_record_writes_a_snapshot_keyed_by_stamp_label_and_TREE(tmp_path, monkeypatch, capsys) -> None:
    """The filename carries where it was taken, because a bookend pair is only meaningful within one
    tree - and the totals are derived from the rows rather than restated, so the file cannot disagree
    with itself."""
    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    monkeypatch.setattr(ps, "_where", lambda: "diagram-tooling")
    monkeypatch.setattr(ps, "_git", lambda *a: "abc1234")
    monkeypatch.setattr(
        ps,
        "measure",
        lambda seeds, households=None, warm=False: [
            {"seed": s, "seconds": float(s), "cpu_seconds": float(s), "form": "nucleated", "shape": "crescent", "houses": 15, "asked": 15, "stages": {"web": float(s)}} for s in seeds
        ],
    )
    monkeypatch.setattr(ps, "machine_state", lambda path=ps.SKILL: {"load": [1.0, 1.0, 1.0], "ram_available_mb": 4096})
    monkeypatch.setattr(ps, "count_calls", lambda seeds, households=None: {s: {"web": 1000 * s} for s in seeds})

    path = ps.record("174-end", (2, 4, 6))
    assert path.endswith("-174-end-diagram-tooling.json")
    snap = _json.loads(_Path(path).read_text())
    assert snap["total_seconds"] == 12.0 and snap["median_seconds"] == 4.0 and snap["worst_seconds"] == 6.0
    assert snap["seeds"] == [2, 4, 6] and snap["commit"] == "abc1234"
    assert snap["environment"] in ("local", "codebuild")
    assert snap["total_cpu_seconds"] == 12.0 and snap["machine_before"] == snap["machine_after"] == {"load": [1.0, 1.0, 1.0], "ram_available_mb": 4096}
    assert snap["scaling"] == [], "the scaling leg only when asked for (feature 375 amendment 5)"
    assert "total 12.0s" in capsys.readouterr().out
    assert [r["calls"] for r in snap["rows"]] == [{"web": 2000}, {"web": 4000}, {"web": 6000}] and snap["total_calls"] == 12000, "feature 427 T02"
    assert set(snap["versions"]) == {"python", "numpy", "shapely"} and isinstance(snap["count_seconds"], float)
    monkeypatch.setenv("L7R_PERF_NO_COUNTS", "1")  # ...and `make perf-ab`'s later runs skip the counting pass (feature 435)
    skipped = _json.loads(_Path(ps.record("ab-B2", (2, 4))).read_text())
    assert "calls" not in skipped["rows"][0] and skipped["total_calls"] == 0


def test_the_counting_pass_counts_each_stage_s_python_calls_the_same_on_every_roll(monkeypatch) -> None:
    """Feature 427 T02 (D2): a stage's count is its Python function calls, exact and deterministic per seed - the same code and
    seed count the same on any machine under any load, which is why counts and not timings are what is watched. STAND-IN
    stages, as `measure`'s test uses: each calls a helper a known number of times; a refusal keeps the stages before it."""
    from l7r.diagram.hamletgen import driver

    def helper() -> int:
        return 1

    def stage_water_frame(s, plan):  # noqa: ANN001, ARG001
        for _ in range(500):
            helper()

    def stage_field(s, plan):  # noqa: ANN001, ARG001
        for _ in range(2000):
            helper()

    def stage_sink(s, plan):  # noqa: ANN001, ARG001
        raise ValueError("SinkRefused: a stand-in refusal")

    monkeypatch.setattr(driver, "STAGES", (stage_water_frame, stage_field, stage_sink))
    first = ps.count_calls((6, 7))
    assert first == ps.count_calls((6, 7)), "the same code and seed: the same count"
    assert set(first) == {6, 7} and list(first[6]) == ["water_frame", "field", "sink"]
    assert 500 <= first[6]["water_frame"] < 600 and 2000 <= first[6]["field"] < 2100, "the helper's calls, and little else"
    assert first[6]["field"] - first[6]["water_frame"] == 1500, "exactly the 1,500 more calls the second stage makes"
    import sys as _sys  # noqa: PLC0415

    held = [t for t in ps.COUNT_TOOLS if _sys.monitoring.get_tool(t) is None]
    assert ps.free_tool() == held[0], "the counter's tool id is given back, the first free one taken next"
    taken = [t for t in ps.COUNT_TOOLS if _sys.monitoring.get_tool(t) is None]
    for t in taken:
        _sys.monitoring.use_tool_id(t, "a test holding every id")
    try:
        with pytest.raises(RuntimeError, match="every sys.monitoring tool id"):
            ps.free_tool()
    finally:
        for t in taken:
            _sys.monitoring.free_tool_id(t)


def test_the_trend_reads_SNAPSHOTS_only_and_steps_over_the_review_records(tmp_path, monkeypatch) -> None:
    """`dev/perf-log/` also holds the review records since feature 129 - no rows, no label. The
    report died with KeyError('utc') on one, found by the perf-audit subagent on this feature's own
    first confirmation."""
    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    (tmp_path / "a.json").write_text(_json.dumps({"label": "x", "rows": [], "utc": "20260101T000000Z"}))
    (tmp_path / "b.json").write_text(_json.dumps({"kind": "explanation", "why": "a written explanation"}))
    (tmp_path / "c.txt").write_text("not json at all")
    loaded = ps._load()
    assert [s["label"] for s in loaded] == ["x"], "the review record and the text file are stepped over"


def test_load_answers_empty_when_there_is_no_log_directory_at_all(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path / "never-created"))
    assert ps._load() == []


def test_report_says_how_to_get_a_snapshot_when_there_are_none(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    assert ps.report(None) == 0
    assert "run: make perf" in capsys.readouterr().out


def test_main_records_then_reports_and_takes_its_seeds_from_the_flag(tmp_path, monkeypatch) -> None:

    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    seen: dict[str, _Any] = {}
    monkeypatch.setattr(ps, "record", lambda label, seeds, scaling=False: seen.update(label=label, seeds=seeds, scaling=scaling) or "")
    monkeypatch.setattr(ps, "report", lambda against: seen.update(against=against) or 0)

    assert ps.main(["--record", "--label", "174-end", "--seeds", "2,4"]) == 0
    assert seen["seeds"] == (2, 4) and seen["label"] == "174-end" and seen["scaling"] is False
    assert "against" not in seen, "--record alone does not also report"
    assert ps.main(["--record", "--label", "x", "--scaling"]) == 0 and seen["scaling"] is True

    assert ps.main(["--record", "--report", "--against", "174-start"]) == 0
    assert seen["against"] == "174-start"


def _snap174(label: str, utc: str, rows: list[dict[str, _Any]], **kw: _Any) -> dict[str, _Any]:
    totals = [float(r["seconds"]) for r in rows]
    return {
        "label": label,
        "utc": utc,
        "commit": "abc1234",
        "rows": rows,
        "total_seconds": round(sum(totals), 1),
        "median_seconds": round(sorted(totals)[len(totals) // 2], 1),
        "worst_seconds": round(max(totals), 1),
        **kw,
    }


def _log(tmp_path, monkeypatch, *snaps: dict[str, _Any]) -> None:
    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    for i, s in enumerate(snaps):
        (tmp_path / f"{i:02d}-{s['label']}.json").write_text(_json.dumps(s))


def test_report_refuses_a_baseline_label_that_does_not_exist(tmp_path, monkeypatch, capsys) -> None:
    _log(tmp_path, monkeypatch, _snap174("174-end", "20260101T000000Z", [{"seed": 1, "seconds": 10.0}]))
    assert ps.report("174-start") == 1
    assert "no snapshot labelled '174-start'" in capsys.readouterr().out


def test_a_single_snapshot_prints_the_trend_and_no_comparison(tmp_path, monkeypatch, capsys) -> None:
    _log(tmp_path, monkeypatch, _snap174("174-end", "20260101T000000Z", [{"seed": 1, "seconds": 10.0}]))
    assert ps.report(None) == 0
    out = capsys.readouterr().out
    assert "174-end" in out and "vs" not in out


def test_a_RETROACTIVE_baseline_is_compared_against_the_newest_that_is_NOT_itself(tmp_path, monkeypatch, capsys) -> None:
    """It used to be `snaps[-1]` flat, which silently compares a baseline against ITSELF whenever the
    baseline is the newest file - and that is what a retroactive `-start` looks like. Feature 127
    took its end bookend first and its start afterwards in a detached worktree, so the start sorted
    last, and the report printed the trend table and then simply no comparison at all. No error, no
    zero rows, nothing."""
    end = _snap174("127-end", "20260101T000000Z", [{"seed": 1, "seconds": 12.0}])
    start = _snap174("127-start", "20260102T000000Z", [{"seed": 1, "seconds": 10.0}])
    _log(tmp_path, monkeypatch, end, start)
    ps.report("127-start")
    out = capsys.readouterr().out
    assert "127-end vs 127-start" in out, "the older end IS compared, against the newer start"
    assert "+20.0%" in out and "FLAG" in out, "12.0 against 10.0 is +20%"


def test_a_baseline_taken_again_is_the_NEWEST_with_its_label(tmp_path, monkeypatch, capsys) -> None:
    """Feature 317 took its bookends again once main moved: the report compared the newest end against the OLDEST start, on
    another main, where the push's `perf_review` pairs the newest - two answers for one pair."""
    old = _snap174("317-start", "20260101T000000Z", [{"seed": 1, "seconds": 20.0}])
    new = _snap174("317-start", "20260103T000000Z", [{"seed": 1, "seconds": 10.0}])
    end = _snap174("317-end", "20260104T000000Z", [{"seed": 1, "seconds": 12.0}])
    _log(tmp_path, monkeypatch, old, new, end)
    ps.report("317-start")
    out = capsys.readouterr().out
    assert "seed   1   +20.0%" in out and "FLAG" in out, "against the newer start: +20%, not -40%"


def test_only_ONE_snapshot_with_that_label_says_there_is_nothing_to_compare(tmp_path, monkeypatch, capsys) -> None:
    _log(tmp_path, monkeypatch, _snap174("174-start", "20260101T000000Z", [{"seed": 1, "seconds": 10.0}]))
    assert ps.report("174-start") == 0
    assert "nothing to compare it against" in capsys.readouterr().out


def test_a_CROSS_ENVIRONMENT_pair_is_REFUSED_because_the_number_would_look_like_an_answer(tmp_path, monkeypatch, capsys) -> None:
    """ "the bands are evaluated PER ENVIRONMENT, and a cross-environment percentage is
    indistinguishable from a regression". A laptop start against a build end is a meaningless number,
    and a meaningless number that prints looks like an answer."""
    base = _snap174("174-start", "20260101T000000Z", [{"seed": 1, "seconds": 10.0}], environment="local", host="laptop", image="laptop")
    cur = _snap174("174-end", "20260102T000000Z", [{"seed": 1, "seconds": 10.0}], environment="codebuild", host="codebuild:XL", image="ecr:latest")
    _log(tmp_path, monkeypatch, base, cur)
    assert ps.report("174-start") == 1
    out = capsys.readouterr().out
    assert "REFUSED" in out and "PER ENVIRONMENT" in out
    assert "a local pair needs a local -start" in out, "and it says how to get a valid pair"


def test_a_seed_the_baseline_never_measured_is_skipped_rather_than_compared_against_nothing(tmp_path, monkeypatch, capsys) -> None:
    base = _snap174("174-start", "20260101T000000Z", [{"seed": 1, "seconds": 10.0}])
    cur = _snap174("174-end", "20260102T000000Z", [{"seed": 1, "seconds": 10.0}, {"seed": 99, "seconds": 3.0}])
    _log(tmp_path, monkeypatch, base, cur)
    ps.report("174-start")
    out = capsys.readouterr().out
    assert "seed 99" not in out.split("vs")[-1] or "99" not in out.split("174-end vs")[-1].split("\n")[1]


def test_measure_times_every_STAGE_of_the_reference_hamlet(monkeypatch) -> None:
    """The per-stage breakdown is what makes a snapshot actionable: "the free per-stage delta every
    snapshot carries says WHICH stage grew". STAND-IN STAGES under a deterministic clock (feature 214, GM
    2026-09-08): the tool's behavior - one row per seed, a time per stage that sums to the row's seconds,
    what was asked beside what landed - holds on stages that do nothing, and the real seeds belong to
    `make perf-gate`. What this no longer proves, stated (spec FR-007): the reference hamlet's own times."""
    from l7r.diagram.hamletgen import driver

    def stage_water_frame(s, plan):  # noqa: ANN001, ARG001
        return None

    def stage_field(s, plan):  # noqa: ANN001, ARG001
        return None

    def stage_sink(s, plan):  # noqa: ANN001, ARG001
        return None

    monkeypatch.setattr(driver, "STAGES", (stage_water_frame, stage_field, stage_sink))
    # a COUNTER clock, not a list: roll_scope and the census read the clock too, so a fixed list of ticks lands on
    # the wrong calls (measured: every stage came out 0.0); every call advancing 0.05 s makes each stage 0.05 s
    # whatever else reads it
    clock = iter(i * 0.05 for i in range(1000))
    monkeypatch.setattr(ps.time, "time", lambda: next(clock))
    rows = ps.measure((6,))
    assert len(rows) == 1
    row = rows[0]
    assert row["seed"] == 6 and row["seconds"] == pytest.approx(0.15, abs=0.06)
    assert row["stages"] == {"water_frame": 0.05, "field": 0.05, "sink": 0.05}
    assert sum(row["stages"].values()) == pytest.approx(row["seconds"], abs=0.5)
    assert row["houses"] == 0 and row["asked"] == ps.REFERENCE["households"], "and it records what was ASKED beside what landed"


def test_the_skill_root_is_put_on_sys_path_when_it_is_not_already_there(monkeypatch) -> None:
    import importlib
    import sys as _sys

    monkeypatch.setattr(_sys, "path", [p for p in _sys.path if _Path(p).resolve() != _Path(ps.SKILL).resolve()])
    reloaded = importlib.reload(ps)
    assert _Path(reloaded.SKILL).resolve() in [_Path(p).resolve() for p in _sys.path]


def test_with_no_baseline_named_the_comparison_is_against_the_PREVIOUS_snapshot(tmp_path, monkeypatch, capsys) -> None:
    """The default a session actually uses: `make perf-report` with no `--against` compares the two
    most recent snapshots, so a bookend pair taken in order needs no arguments at all."""
    older = _snap174("174-start", "20260101T000000Z", [{"seed": 1, "seconds": 10.0}])
    newer = _snap174("174-end", "20260102T000000Z", [{"seed": 1, "seconds": 11.0}])
    _log(tmp_path, monkeypatch, older, newer)
    assert ps.report(None) == 0
    assert "174-end vs 174-start" in capsys.readouterr().out


# ---- feature 375 amendment 5: the machine's state at both ends, and the trend that says when ----------------------------------


def test_machine_state_reads_ram_load_and_disk_and_leaves_out_what_it_cannot(monkeypatch, tmp_path) -> None:
    state = ps.machine_state(str(tmp_path))
    assert set(state) >= {"load", "disk_free_gb", "disk_total_gb"} and len(state["load"]) == 3
    if _platform.system() == "Linux":
        assert state["ram_available_mb"] > 0 and state["ram_total_mb"] >= state["ram_available_mb"]

    def no(*_a: _Any, **_k: _Any) -> _Any:
        raise OSError("not here")

    monkeypatch.setattr("builtins.open", no)
    monkeypatch.setattr(ps.os, "getloadavg", no)
    monkeypatch.setattr(ps.shutil, "disk_usage", no)
    assert ps.machine_state(str(tmp_path)) == {}, "a field the machine cannot report is left out, never guessed"


def test_the_trend_prints_each_snapshots_load_and_free_ram_and_dashes_for_older_ones(tmp_path, monkeypatch, capsys) -> None:
    old = _snap174("500-start", "20260101T000000Z", [{"seed": 1, "seconds": 10.0}])
    new = _snap174("500-end", "20260102T000000Z", [{"seed": 1, "seconds": 10.0, "cpu_seconds": 9.0}])
    new.update(total_cpu_seconds=9.0, machine_before={"load": [3.25, 2.0, 1.0], "ram_available_mb": 6144}, machine_after={"load": [7.5, 3.0, 2.0]})
    _log(tmp_path, monkeypatch, old, new)
    ps.report(None)
    out = capsys.readouterr().out
    line_old = next(ln for ln in out.splitlines() if "500-start" in ln and "vs" not in ln)
    line_new = next(ln for ln in out.splitlines() if "500-end" in ln and "vs" not in ln)
    assert "     -  " in line_old and line_old.count(" - ") >= 2, "a snapshot from before amendment 5 prints dashes"
    assert "9.0s" in line_new and "3.2>7.5" in line_new and "6.0>-" in line_new


def test_measure_warms_an_untimed_roll_first_and_times_cpu_beside_wall(monkeypatch) -> None:
    """The first roll in a process counted another thread's start-up as its own CPU time (R4): a warm-up roll comes first."""
    import l7r.diagram.hamletgen as hg
    import l7r.diagram.hamletgen.driver as drv

    rolled: list[int] = []

    class Plan:
        def __init__(self, seed: int) -> None:
            self.W = self.H = 10
            self.spec = type("S", (), {"seed": seed, "households": 15})()
            self.cluster_shape = "crescent"

    def stage_web(s: _Any, plan: _Any) -> None:
        rolled.append(plan.spec.seed)

    monkeypatch.setattr(hg, "plan_site", lambda spec: Plan(spec.seed))
    monkeypatch.setattr(hg, "HamletSpec", lambda seed, **kw: type("H", (), {"seed": seed})())
    monkeypatch.setattr(drv, "STAGES", (stage_web,))
    rows = ps.measure((7, 8), warm=True)
    assert rolled == [7, 7, 8], "the warm-up rolls the first seed once, untimed"
    assert [r["seed"] for r in rows] == [7, 8] and all("cpu_seconds" in r and set(r["cpu_stages"]) == {"web"} for r in rows)
