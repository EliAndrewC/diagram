"""`tools/perf_ab.py` (features 435, 436): two engines timed against each other - three forms decided by the count compared,
quick first (a wider run refused without a quick one of the same engines, or a stated reason), alternated A B / B A, wall
and CPU time each with best and spread, calls, the A/A floor beside a quick result; it exits 0 whatever the times."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.tools import perf_ab as pa


class _Fake:
    """A worker that answers from a table: `times[(households, seed)]` is a list consumed one roll at a time."""

    def __init__(self, tree: str, times: dict[Any, list[Any]], seen: list[str]) -> None:
        self.tree, self.times, self.seen = tree, times, seen

    def roll(self, k: Any) -> Any:
        self.seen.append(self.tree)
        return self.times[(self.tree, k)].pop(0)

    def send(self, q: Any) -> None:
        self.seen.append(f"{self.tree}:{q['op']}")
        self.last = q

    def answer(self) -> dict[str, Any]:
        return {"calls": 100 if self.tree.endswith("A") else 90} if self.last["op"] == "count" else {}

    def close(self) -> None:
        self.seen.append("closed")


def test_the_form_is_the_count_compared_and_the_order_alternates() -> None:
    assert pa.form([25], [40], False) == "quick" and pa.form([25, 39], [40], False) == "subset"
    assert pa.form([25], [20, 40], False) == "subset" and pa.form([25], [40], True) == "full"
    assert [pa.order(i) for i in range(3)] == [("A", "B"), ("B", "A"), ("A", "B")]
    assert pa.keys_of([25, 39], [40]) == [(40, 25), (40, 39)] and pa.pair("b", "a") == pa.pair("a", "b") == "a-b"


def test_a_worker_answers_its_marked_lines_and_says_when_it_ended(tmp_path: Path) -> None:
    script = 'import json, sys\nfor line in sys.stdin:\n    q = json.loads(line)\n    print("progress")\n    print("@@" + json.dumps({"wall": 1.5, "cpu": 1.25, "calls": 7}), flush=True)\n'
    w = pa.Worker(str(tmp_path), script)
    assert w.roll((40, 25)) == (1.5, 1.25) and w.ask({"op": "count"})["calls"] == 7
    w.close()
    dead = pa.Worker(str(tmp_path), "import sys; sys.stdin.readline()")
    with pytest.raises(RuntimeError, match="ended before it answered"):
        dead.ask({"op": "roll"})
    dead.close()


def test_rolled_warms_and_counts_both_at_once_and_alternates_by_run_and_by_key() -> None:
    seen: list[str] = []
    times = {("tA", (40, 25)): [(2.0, 1.9), (2.2, 2.0)], ("tB", (40, 25)): [(1.5, 1.4), (1.7, 1.6)], ("tA", (40, 39)): [(3.0, 3.0)] * 2, ("tB", (40, 39)): [(2.9, 2.9)] * 2}
    runs, calls = pa.rolled({"A": "tA", "B": "tB"}, [(40, 25), (40, 39)], 2, make=lambda tree: _Fake(tree, times, seen))
    assert seen[:2] == ["tA:warm", "tB:warm"], "both warmed before any timed roll"
    assert seen[2:10] == ["tA", "tB", "tB", "tA", "tB", "tA", "tA", "tB"], "the first version alternates key by key and run by run"
    assert seen[10:] == ["tA:count", "tB:count", "tA:count", "tB:count", "closed", "closed"]
    assert runs["A"] == [{(40, 25): (2.0, 1.9), (40, 39): (3.0, 3.0)}, {(40, 25): (2.2, 2.0), (40, 39): (3.0, 3.0)}]
    assert calls == {"A": {(40, 25): 100, (40, 39): 100}, "B": {(40, 25): 90, (40, 39): 90}}


def test_a_full_snapshot_runs_make_perf_in_its_tree_and_its_legs_read_from_the_stages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    snap = {
        "rows": [{"asked": 40, "seed": 25, "seconds": 6.4, "stages": {"web": 3.21, "wells": 3.17}, "cpu_stages": {"web": 3.0}, "calls": {"web": 5}}],
        "scaling": [{"asked": 40, "seed": 4, "seconds": None}, {"asked": 10, "seed": 4, "seconds": 1.2, "cpu_seconds": 1.1}],
    }
    run_, counted = pa.legs(snap)
    assert run_ == {(40, 25): (6.38, 3.0), (40, 4): (None, None), (10, 4): (1.2, 1.1)} and counted[(40, 25)] == 5


def test_swept_alternates_and_keeps_the_first_snapshots_calls() -> None:
    seen: list[tuple[str, str, bool]] = []

    def take(tree: str, label: str, counted: bool) -> dict[str, Any]:
        seen.append((tree, label, counted))
        return {"rows": [{"asked": 15, "seed": 4, "seconds": 2.0, "calls": {"web": 10 if counted else 0}}]}

    runs, calls = pa.swept({"A": "ta", "B": "tb"}, 2, take)
    assert [s[1] for s in seen] == ["ab-A1", "ab-B1", "ab-B2", "ab-A2"] and calls["A"][(15, 4)] == 10 and len(runs["B"]) == 2


def test_the_table_reads_wall_and_cpu_best_spread_and_change_and_names_a_refused_leg() -> None:
    runs = {
        "A": [{(40, 25): (3.0, 2.8), (40, 4): (None, None), (10, 4): (0.0, None)}, {(40, 25): (2.5, 2.4)}],
        "B": [{(40, 25): (2.0, 2.0), (40, 4): (6.0, 5.0), (10, 4): (1.0, None)}, {(40, 25): (2.4, 2.1)}],
    }
    lines = pa.compare(runs, {"A": {(40, 25): 100}, "B": {(40, 25): 50}})
    row = next(ln for ln in lines if ln.strip().startswith("(40, 25)")).split()
    assert row[2:7] == ["2.50", "0.50", "2.00", "0.40", "-20%"] and row[7:12] == ["2.40", "0.40", "2.00", "0.10", "-17%"] and row[-3:] == ["100", "50", "-50%"]
    assert any(ln.strip().startswith("(40, 4)") and "refused" in ln for ln in lines)
    assert "never as a pass" in lines[-1] and "B A" in lines[-1]
    no_cpu = next(ln for ln in lines if ln.strip().startswith("(10, 4)"))
    assert "%" not in no_cpu, "a zero best, no CPU time or no calls gives no change"
    assert pa.floor_of(runs, (40, 25)) == {"wall": "-20%", "cpu": "-17%"} and pa.floor_of(runs, (40, 99)) == {"wall": "n/a", "cpu": "n/a"}


def test_the_refusal_and_the_floor_line_name_the_command_that_answers_them() -> None:
    text = pa.refusal("abc", "HEAD", "subset", 25, 40)
    assert "make perf-ab A=abc B=HEAD SEEDS=25 HOUSEHOLDS=40" in text and "never a timing" in text and pa.ESCAPE in text
    assert "make perf-ab AA=1 SEEDS=25 HOUSEHOLDS=40 N=6" in pa.floor_line(None, 25, 40, 6)
    assert "wall -3%" in pa.floor_line({"utc": "t", "wall": "-3%", "cpu": "+1%"}, 25, 40, 6)


def test_the_state_the_key_and_the_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert pa.state_dir().endswith("perf-ab")
    monkeypatch.setattr(pa.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="/abs/.git\n"))
    assert pa.state_dir() == "/abs/.git/perf-ab"
    monkeypatch.undo()
    assert len(pa.engine_key(str(Path(__file__).resolve().parents[2]))) == 16
    assert pa.read(str(tmp_path / "none.json")) is None
    pa.write(str(tmp_path / "x" / "r.json"), {"a": 1})
    assert pa.read(str(tmp_path / "x" / "r.json")) == {"a": 1}
    assert hasattr(pa.escape_log(), "escape")


@pytest.fixture
def rig(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    made: list[str] = []
    removed: list[list[str]] = []
    monkeypatch.setattr(pa, "state_dir", lambda: str(tmp_path / "state"))
    monkeypatch.setattr(pa, "worktree", lambda commit, where, name: made.append(commit) or f"{where}/{name}")
    monkeypatch.setattr(pa, "engine_key", lambda tree: "k" + tree[-1])
    monkeypatch.setattr(pa.subprocess, "run", lambda cmd, **_k: removed.append(cmd) or subprocess.CompletedProcess(cmd, 0))
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "guard-log"))
    seen: list[str] = []

    def make(tree: str) -> _Fake:
        return _Fake(tree, {(tree, (40, 25)): [(2.0, 1.9)] * 9, (tree, (20, 25)): [(1.0, 0.9)] * 9, (tree, (20, 39)): [(1.1, 1.0)] * 9, (tree, (40, 39)): [(2.5, 2.4)] * 9}, seen)

    return {"made": made, "removed": removed, "make": make, "state": tmp_path / "state", "seen": seen}


def test_main_quick_records_the_pair_and_prints_the_floor_line(rig: dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
    assert pa.main(["abc"], make=rig["make"], env={}) == 0
    out = capsys.readouterr().out
    assert "(40, 25)" in out and "make perf-ab AA=1 SEEDS=25 HOUSEHOLDS=40 N=1" in out
    assert (rig["state"] / "quick" / "kA-kB.json").is_file() and len(rig["removed"]) == 2


def test_main_refuses_a_wider_run_with_no_quick_record_and_lets_it_through_with_one(rig: dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
    assert pa.main(["abc", "--seeds", "25,39"], make=rig["make"], env={}) == 2
    assert "make perf-ab A=abc B=HEAD SEEDS=25 HOUSEHOLDS=40" in capsys.readouterr().err and not rig["seen"], "refused before any roll"
    assert pa.main(["abc", "--seeds", "25,39"], make=rig["make"], env={pa.ESCAPE: "x"}) == 2
    assert "REASON" in capsys.readouterr().err
    assert pa.main(["abc", "--households", "20,40"], make=rig["make"], env={pa.ESCAPE: "the quick run was taken on the other host"}) == 0
    assert pa.main(["abc"], make=rig["make"], env={}) == 0
    assert pa.main(["abc", "--seeds", "25,39", "--households", "20,40"], make=rig["make"], env={}) == 0
    out = capsys.readouterr().out
    assert all(f"({h}, {s})" in out for h in (20, 40) for s in (25, 39)), "a row for every seed at every size (SC-006)"


def test_main_full_sweeps_and_aa_records_the_floor(rig: dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
    pa.write(str(rig["state"] / "quick" / "kA-kB.json"), {"a": "abc"})
    snap = {"rows": [{"asked": 15, "seed": 4, "seconds": 2.0, "stages": {"web": 2.0}, "calls": {}}]}
    assert pa.main(["abc", "--full", "--n", "1"], make=rig["make"], take=lambda tree, label, counted: snap, env={}) == 0
    assert "(15, 4)" in capsys.readouterr().out
    assert pa.main(["abc", "--aa", "--seeds", "25,39"], make=rig["make"], env={}) == 2
    assert pa.main(["HEAD", "--aa"], make=rig["make"], env={}) == 0
    assert "floor recorded" in capsys.readouterr().out and rig["made"][-1] == "HEAD"
    floor = pa.read(str(rig["state"] / "floor" / "25-40-1.json"))
    assert floor is not None and floor["wall"] == "+0%"
    assert pa.main(["abc"], make=rig["make"], env={}) == 0
    assert "floor (one engine against itself" in capsys.readouterr().out


def test_the_worker_script_rolls_with_the_versions_own_measure(tmp_path: Path) -> None:
    """The worker's protocol against a stand-in `perf_snapshot` laid out as a version's tree."""
    pkg = tmp_path / "l7r" / "diagram" / "tools"
    pkg.mkdir(parents=True)
    for d in (tmp_path / "l7r", tmp_path / "l7r" / "diagram", pkg):
        (d / "__init__.py").write_text("")
    (pkg / "perf_snapshot.py").write_text(
        "def measure(seeds, households=None, warm=False):\n"
        "    print('rolling')\n"
        "    return [{'refused': 'x'}] if seeds[0] == 4 else [{'stages': {'a': 1.004, 'b': 2.0}, 'cpu_stages': {'a': 0.5}}]\n"
        "def count_calls(seeds, households=None):\n    return {seeds[0]: {'a': 3, 'b': 4}}\n"
    )
    w = pa.Worker(str(tmp_path))
    try:
        assert w.ask({"op": "warm", "households": 40, "seed": 25}) == {}
        assert w.roll((40, 25)) == (3.0, 0.5) and w.roll((40, 4)) == (None, None)
        assert w.ask({"op": "count", "households": 40, "seed": 25}) == {"calls": 7}
    finally:
        w.close()
    assert sys.executable


def test_a_worktree_is_a_detached_checkout_under_the_temporary_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[list[str]] = []
    monkeypatch.setattr(pa.subprocess, "run", lambda cmd, **_k: seen.append(cmd) or subprocess.CompletedProcess(cmd, 0))
    assert pa.worktree("abc", "/tmp/x", "A") == "/tmp/x/A" and seen[0][3:] == ["worktree", "add", "--detach", "/tmp/x/A", "abc"]
