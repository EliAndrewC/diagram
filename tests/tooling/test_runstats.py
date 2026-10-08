"""The gate's run stats (GM 2026-10-03): first and last failure times and the host's figures, read from
fake /proc and /sys trees so every field and every absence is pinned without depending on this machine.

No `tooling` marker: it calls functions over temporary files, it runs no make, git or subprocess.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import types

import pytest

from tests import _gate_failures

REPO = pathlib.Path(__file__).resolve().parents[2]
SKILL = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("_runstats", REPO / "scripts" / "_runstats.py")
assert _spec and _spec.loader
runstats = importlib.util.module_from_spec(_spec)
sys.modules["_runstats"] = runstats
_spec.loader.exec_module(runstats)


def _host(
    root: pathlib.Path, *, load: str = "1.50", avail_kb: int = 4096 * 1024, io_total: int = 2_000_000, temp: int = 61000, core_ms: tuple[int, int] = (10, 20), package_ms: int = 7
) -> tuple[str, str]:
    """A fake /proc and /sys holding every figure the snapshot reads."""
    proc, sysr = root / "proc", root / "sys"
    (proc / "pressure").mkdir(parents=True, exist_ok=True)
    (proc / "loadavg").write_text(f"{load} 1.00 0.50 1/100 42\n")
    (proc / "meminfo").write_text(f"MemTotal: 16000000 kB\nMemAvailable: {avail_kb} kB\n")
    (proc / "pressure" / "cpu").write_text("some avg10=0.00 avg60=0.00 avg300=0.00 total=1000000\n")
    (proc / "pressure" / "io").write_text(f"some avg10=0.50 avg60=0.10 avg300=0.02 total={io_total}\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=500000\n")
    (proc / "pressure" / "memory").write_text("some avg10=0.00 avg60=0.00 avg300=0.00 total=0\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n")
    for i, name in enumerate(("nvme", "coretemp")):
        hw = sysr / "class" / "hwmon" / f"hwmon{i}"
        hw.mkdir(parents=True, exist_ok=True)
        (hw / "name").write_text(name + "\n")
        (hw / "temp1_input").write_text(f"{temp if name == 'coretemp' else 99000}\n")
        if name == "coretemp":
            (hw / "temp1_label").write_text("Package id 0\n")
            (hw / "temp2_input").write_text("90000\n")
            (hw / "temp2_label").write_text("Core 0\n")
    for cpu, ms in enumerate(core_ms):
        tt = sysr / "devices" / "system" / "cpu" / f"cpu{cpu}" / "thermal_throttle"
        tt.mkdir(parents=True, exist_ok=True)
        (tt / "core_throttle_total_time_ms").write_text(f"{ms}\n")
        (tt / "package_throttle_total_time_ms").write_text(f"{package_ms}\n")
    return str(proc), str(sysr)


def test_the_snapshot_reads_every_figure(tmp_path: pathlib.Path) -> None:
    proc, sysr = _host(tmp_path)
    snap = runstats.snapshot(proc, sysr)
    assert snap["load"] == 1.5
    assert snap["mem_avail_mb"] == 4096
    assert snap["stall_us"] == {"cpu": 1000000, "io": 2000000, "io_full": 500000, "memory": 0}
    # The package sensor, not the hotter core one and not the nvme drive.
    assert snap["cpu_temp_c"] == 61.0
    # Core time summed over CPUs; package time from one CPU, since each CPU of a package repeats it.
    assert snap["throttle_ms"] == {"core": 30, "package": 7}


def test_a_host_without_the_figures_gives_none_and_nothing(tmp_path: pathlib.Path) -> None:
    snap = runstats.snapshot(str(tmp_path / "noproc"), str(tmp_path / "nosys"))
    assert (snap["load"], snap["mem_avail_mb"], snap["cpu_temp_c"]) == (None, None, None)
    assert snap["stall_us"] == {} and snap["throttle_ms"] == {}


def test_coretemp_without_a_package_label_reports_its_hottest_sensor(tmp_path: pathlib.Path) -> None:
    hw = tmp_path / "class" / "hwmon" / "hwmon0"
    hw.mkdir(parents=True)
    (hw / "name").write_text("coretemp\n")
    (hw / "temp1_input").write_text("50000\n")
    (hw / "temp2_input").write_text("72000\n")
    (hw / "temp3_input").write_text("garbage\n")
    assert runstats._cpu_temp_c(str(tmp_path)) == 72.0


def test_coretemp_with_no_readable_sensor_reports_none(tmp_path: pathlib.Path) -> None:
    hw = tmp_path / "class" / "hwmon" / "hwmon0"
    hw.mkdir(parents=True)
    (hw / "name").write_text("coretemp\n")
    assert runstats._cpu_temp_c(str(tmp_path)) is None


def test_end_without_a_start_is_empty(tmp_path: pathlib.Path) -> None:
    assert runstats.end(str(tmp_path)) == {}


def test_end_reports_both_ends_and_the_deltas_over_the_run(tmp_path: pathlib.Path) -> None:
    gitdir = tmp_path / "git"
    gitdir.mkdir()
    proc, sysr = _host(tmp_path / "a")
    runstats.start(str(gitdir), proc, sysr)
    proc2, sysr2 = _host(tmp_path / "b", load="9.25", avail_kb=1024 * 1024, io_total=14_500_000, temp=88000, core_ms=(510, 20), package_ms=1007)
    out = runstats.end(str(gitdir), proc2, sysr2)
    assert "first_failure_s" not in out and "failed_tests" not in out
    host = out["host"]
    assert host["load"] == [1.5, 9.25]
    assert host["mem_avail_mb"] == [4096, 1024]
    assert host["cpu_temp_c"] == [61.0, 88.0]
    assert host["stall_s"] == {"cpu": 0.0, "io": 12.5, "io_full": 0.0, "memory": 0.0}
    assert host["throttle_ms"] == {"core": 500, "package": 1000}


def test_end_leaves_out_a_figure_missing_at_either_end(tmp_path: pathlib.Path) -> None:
    gitdir = tmp_path / "git"
    gitdir.mkdir()
    runstats.start(str(gitdir), str(tmp_path / "noproc"), str(tmp_path / "nosys"))
    proc, sysr = _host(tmp_path / "b")
    assert runstats.end(str(gitdir), proc, sysr) == {}


def _marks(gitdir: pathlib.Path, start_t: float, lines: list[str]) -> None:
    (gitdir / runstats.START).write_text(json.dumps({"t": start_t, "load": None, "mem_avail_mb": None, "stall_us": {}, "cpu_temp_c": None, "throttle_ms": {}}))
    (gitdir / runstats.FAILURES).write_text("".join(line + "\n" for line in lines))


def test_test_marks_give_first_and_last_and_the_test_phase_end_is_dropped(tmp_path: pathlib.Path) -> None:
    """The phase's end would otherwise be the last failure every time a test failed."""
    _marks(tmp_path, 1000.0, ["1004.0 phase:static", "1050.25 test", "1080.0 test", "not-a-time test", "1150.0 phase:test-full"])
    out = runstats.end(str(tmp_path), str(tmp_path / "noproc"), str(tmp_path / "nosys"))
    assert out == {"first_failure_s": 4.0, "last_failure_s": 80.0, "failed_tests": 2}


def test_a_test_phase_with_no_test_marks_stands_on_its_end(tmp_path: pathlib.Path) -> None:
    """A coverage floor or the roll census fails test-full with no test failing: its end is the only moment."""
    _marks(tmp_path, 1000.0, ["1150.0 phase:test-full"])
    out = runstats.end(str(tmp_path), str(tmp_path / "noproc"), str(tmp_path / "nosys"))
    assert out == {"first_failure_s": 150.0, "last_failure_s": 150.0}


def test_start_clears_the_last_runs_marks_and_fail_appends(tmp_path: pathlib.Path) -> None:
    (tmp_path / runstats.FAILURES).write_text("1.0 test\n")
    runstats.start(str(tmp_path))
    assert not (tmp_path / runstats.FAILURES).exists()
    runstats.start(str(tmp_path))  # nothing to clear is fine
    runstats.fail(str(tmp_path), "reference")
    assert (tmp_path / runstats.FAILURES).read_text().endswith(" phase:reference\n")


def test_main_runs_each_command_and_refuses_a_bad_one(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert runstats.main(["start", str(tmp_path)]) == 0
    assert runstats.main(["fail", str(tmp_path), "static"]) == 0
    assert runstats.main(["end", str(tmp_path)]) == 0
    assert "first_failure_s" in json.loads(capsys.readouterr().out)
    assert runstats.main(["fail", str(tmp_path)]) == 2
    assert "_runstats.py start" in capsys.readouterr().err


def test_a_failed_report_is_marked_and_a_pass_is_not(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    path = str(tmp_path / "gate-failures")
    assert _gate_failures.mark(types.SimpleNamespace(failed=True), path)
    assert not _gate_failures.mark(types.SimpleNamespace(failed=False), path)
    assert not _gate_failures.mark(types.SimpleNamespace(failed=True), None)
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw0")
    assert not _gate_failures.mark(types.SimpleNamespace(failed=True), path)
    assert pathlib.Path(path).read_text().count(" test\n") == 1


def test_the_hooks_mark_into_the_file_the_gate_named(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    monkeypatch.setattr(_gate_failures, "_PATH", str(tmp_path / "gate-failures"))
    _gate_failures.pytest_runtest_logreport(types.SimpleNamespace(failed=True))
    _gate_failures.pytest_collectreport(types.SimpleNamespace(failed=True))
    assert (tmp_path / "gate-failures").read_text().count(" test\n") == 2


def test_the_gate_variable_is_not_left_for_child_processes() -> None:
    """A fixture repository's own pytest, failing on purpose, must not mark into this gate."""
    import os

    assert "L7R_GATE_FAILURES" not in os.environ


def test_the_gate_wires_the_stats_into_every_entry_it_writes() -> None:
    """The start snapshot, the export pytest reads, a mark per failed phase, and the stats on each entry."""
    recipe = (SKILL / "Makefile").read_text().split("\ndone:", 1)[1].split("\ntest-full:", 1)[0]
    makefile = (SKILL / "Makefile").read_text()
    assert "**json.loads(os.environ.get('RUN_STATS') or '{}')" in makefile.split("LOGRUN = ", 1)[1].split("\n\n", 1)[0]
    assert '$(RUNSTATS) start "$$G"' in recipe and 'export L7R_GATE_FAILURES="$$G/gate-failures"' in recipe
    # Two phase loops and the reference step mark their failures.
    assert recipe.count('$(RUNSTATS) fail "$$G"') == 3
    # Each LOGRUN that follows a run (two failure paths, the reference failure, green) carries the stats.
    assert recipe.count('RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" ') == 4
