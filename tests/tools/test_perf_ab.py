"""`tools/perf_ab.py` (feature 435): two engines timed against each other - alternated, best of N, each arm's spread and calls,
a refused leg named; it decides nothing and exits 0 whatever the times."""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.tools import perf_ab as pa


def _snap(seconds: dict[tuple[int, int], float | None], calls: int = 0) -> dict[str, Any]:
    legs = [{"asked": n, "seed": s, "seconds": t, "calls": {"web": calls} if calls else {}} for (n, s), t in seconds.items()]
    return {"rows": legs[:1], "scaling": legs[1:]}


def test_the_table_reads_each_arms_best_spread_and_calls_and_names_a_refused_leg() -> None:
    runs = {
        "A": [_snap({(15, 4): 3.0, (40, 4): None, (40, 39): 8.0}, calls=100), _snap({(15, 4): 2.5, (40, 4): None, (40, 39): 8.6})],
        "B": [_snap({(15, 4): 2.0, (40, 4): 6.0, (40, 39): 7.0}, calls=50), _snap({(15, 4): 2.4, (40, 4): 6.2, (40, 39): 7.4})],
    }
    lines = pa.compare(runs)
    row = next(ln for ln in lines if ln.strip().startswith("(15, 4)"))
    assert row.split()[2:9] == ["2.50", "0.50", "2.00", "0.40", "-20%", "100", "50"]
    assert any(ln.strip().startswith("(40, 4)") and "refused" in ln for ln in lines)
    assert "never as a pass" in lines[-1]
    assert "%" not in pa.compare({"A": [_snap({(15, 4): 0.0})], "B": [_snap({(15, 4): 1.0})]})[1], "a zero best or no calls gives no share"


def test_the_arms_alternate_and_count_on_their_first_run_only() -> None:
    seen: list[tuple[str, str, bool]] = []
    out = pa.ab({"A": "ta", "B": "tb"}, 2, run=lambda tree, label, counted: seen.append((tree, label, counted)) or {"label": label})
    assert seen == [("ta", "ab-A1", True), ("tb", "ab-B1", True), ("ta", "ab-A2", False), ("tb", "ab-B2", False)]
    assert [s["label"] for s in out["A"]] == ["ab-A1", "ab-A2"]


def test_a_snapshot_runs_make_perf_in_its_tree_and_reads_its_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], dict[str, str]]] = []

    def run(cmd: list[str], env: dict[str, str], **_k: Any) -> None:
        calls.append((cmd, env))
        (tmp_path / "dev" / "perf-log").mkdir(parents=True, exist_ok=True)
        (tmp_path / "dev" / "perf-log" / "20261027T000000Z-ab-A1-x.json").write_text(json.dumps({"rows": []}))

    monkeypatch.setattr(pa.subprocess, "run", run)
    assert pa.snapshot(str(tmp_path), "ab-A1", True) == {"rows": []}
    assert calls[0][0][-2:] == ["LABEL=ab-A1", "SCALING=1"] and "L7R_PERF_NO_COUNTS" not in calls[0][1]
    pa.snapshot(str(tmp_path), "ab-A1", False)
    assert calls[1][1]["L7R_PERF_NO_COUNTS"] == "1"


def test_main_builds_two_worktrees_compares_and_always_removes_them(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    git: list[list[str]] = []
    monkeypatch.setattr(pa.subprocess, "run", lambda cmd, **_k: git.append(cmd) or subprocess.CompletedProcess(cmd, 0))
    fake = lambda tree, label, counted: _snap({(15, 4): 2.0}, calls=10)  # noqa: E731
    assert pa.main(["abc123", "--n", "1"], run=fake) == 0
    assert [c[3:5] for c in git if "worktree" in c][:2] == [["worktree", "add"], ["worktree", "add"]]
    assert sum(1 for c in git if "remove" in c) == 2 and "(15, 4)" in capsys.readouterr().out


def test_a_leg_is_timed_from_its_stages_to_the_hundredth() -> None:
    """Feature 435 T06: the leg's `seconds` is rounded to the tenth, so the stages are summed instead; a refused leg stays refused."""
    snap = {"rows": [{"asked": 40, "seed": 25, "seconds": 6.4, "stages": {"web": 3.21, "wells": 3.17}, "calls": {}}, {"asked": 40, "seed": 4, "seconds": None, "stages": {"web": 1.0}}]}
    got = pa.legs(snap)
    assert got[(40, 25)][0] == 6.38 and got[(40, 4)][0] is None
