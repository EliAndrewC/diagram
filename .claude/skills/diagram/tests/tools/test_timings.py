"""The iteration-loop benchmark harness (`tools/timings.py`).

Feature 174, under the GM's 2026-09-02 ruling that every engine module owes 100% coverage the day it
lands; this one had never been measured. It writes the `timings.md` ledger the project reasons about
its own speed from, so what these tests pin is the ARITHMETIC and the HONESTY of the rows - a
benchmark that quietly reports a wrong number is worse than no benchmark.

Every subprocess goes through `sh()`, so `sh()` is the seam: stub it and each `bench_*` becomes a
pure function from canned timings to a `Result`.

`tooling`, because two tests run a real subprocess and one writes a ledger file.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.tools import timings

pytestmark = pytest.mark.tooling


def _sh(script: dict[str, tuple[float, bool, str]], default: tuple[float, bool, str] = (1.0, True, "")) -> Any:
    """A stub `sh` that answers by the first matching substring of the command it is given."""
    calls: list[list[str]] = []

    def fake(cmd: list[str], env: dict[str, str] | None = None) -> tuple[float, bool, str]:
        calls.append(list(cmd))
        joined = " ".join(cmd)
        for needle, answer in script.items():
            if needle in joined:
                return answer
        return default

    fake.calls = calls  # type: ignore[attr-defined]
    return fake


# ---- the two leaf helpers -------------------------------------------------------------------
def test_sh_wall_clocks_a_real_command_and_reports_its_success_and_output() -> None:
    secs, ok, out = timings.sh(["python3", "-c", "print('hi')"])
    assert ok and "hi" in out and secs >= 0.0
    _s, bad, err = timings.sh(["python3", "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"])
    assert bad is False and "boom" in err, "stdout and stderr are combined, and rc drives ok"


@pytest.mark.parametrize(
    ("seconds", "want"),
    [(0.0, "0.0 s"), (12.34, "12.3 s"), (89.9, "89.9 s"), (90.0, "1 min 30.0 s"), (3661.0, "61 min 01.0 s")],
)
def test_fmt_switches_to_minutes_at_ninety_seconds(seconds: float, want: str) -> None:
    """A ledger a reader scans wants "4 min 12.0 s", not "252.0 s" - but only once the number is big
    enough that minutes help. 90 is the boundary and it is asserted from both sides."""
    assert timings.fmt(seconds) == want


# ---- the benchmarks, each a pure function of what `sh` returned -------------------------------
def test_bench_hamlet_derives_generate_and_render_BY_DIFFERENCE_and_never_reports_negative_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """The generator gates its own output and has no flag to stop it, so RENDER is (with PNG minus
    without) and GENERATE is (without PNG minus gate). Both are floored at zero: on a fast box the
    two runs can invert, and a benchmark reporting "-0.3 s of rendering" is not a finding, it is
    noise wearing a finding's clothes."""
    monkeypatch.setattr(timings, "sh", _sh({"--out": (10.0, True, ""), "check_village": (2.0, True, "")}))
    # `sh` is asked for the with-PNG run first, then the without-PNG run; both match "--out"
    monkeypatch.setattr(timings, "sh", _sh({"check_village": (2.0, True, "")}, default=(10.0, True, "")))
    r = timings.bench_hamlet("/tmp/x")
    assert r.key == "hamlet_gen_gate" and r.total == 10.0
    parts = dict(r.parts)
    assert parts["gate (check_village, 189 checks)"] == 2.0
    assert parts["generate (compose + draw)"] == 8.0, "without-PNG minus the gate"
    assert parts["render PNG (resvg)"] == 0.0, "floored, not negative, when the two runs tie"


def test_bench_hamlet_is_NOT_ok_when_any_of_its_three_runs_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(timings, "sh", _sh({"check_village": (2.0, False, "")}, default=(10.0, True, "")))
    assert timings.bench_hamlet("/tmp/x").ok is False


def test_bench_cohort_reports_the_PER_MAP_average_and_says_it_is_not_a_component(monkeypatch: pytest.MonkeyPatch) -> None:
    """The per-map figure is the one to watch, but it is an average, not a share of the total - so
    the row carries `shares=False` and a note saying so. Without that the table would print "25%"
    beside it, which would be arithmetic nonsense."""
    monkeypatch.setattr(timings, "sh", _sh({}, default=(40.0, True, "")))
    r = timings.bench_cohort(4, quick=True)
    assert r.key == "cohort_4" and r.parts == [("per map", 10.0)]
    assert r.shares is False and "not a component" in r.note
    assert "does a fix generalize?" in r.what
    assert "the bar for an archetype" in timings.bench_cohort(24, quick=False).what


def test_bench_cache_forces_a_COLD_run_first_and_says_so_when_the_warm_run_still_missed(monkeypatch: pytest.MonkeyPatch) -> None:
    """ "A cold regen is FORCED first or this measures whatever the cache happened to hold." The
    no-cache flag on the first call is the whole method, and a warm run that did NOT hit is itself
    the finding - the note has to say that rather than quietly reporting a fast second run."""
    fake = _sh({"--no-cache": (30.0, True, "")}, default=(2.0, True, "CACHED sawada"))
    monkeypatch.setattr(timings, "sh", fake)
    r = timings.bench_cache("/tmp/x")
    assert "--no-cache" in " ".join(fake.calls[0]), "the cold run is forced FIRST"
    assert "--no-cache" not in " ".join(fake.calls[1]), "and the warm run is not"
    assert r.total == 30.0 and dict(r.parts)["warm (cache hit)"] == 2.0
    assert "did NOT hit" not in r.note

    monkeypatch.setattr(timings, "sh", _sh({"--no-cache": (30.0, True, "")}, default=(29.0, True, "REGENERATED")))
    miss = timings.bench_cache("/tmp/x")
    assert "warm (STILL A MISS)" in dict(miss.parts)
    assert "did NOT hit, which is itself the finding" in miss.note


def test_bench_pool_sweep_takes_the_EIGHT_SLOWEST_tests_from_pytest_s_own_durations(monkeypatch: pytest.MonkeyPatch) -> None:
    """The sweep is dominated by a handful of heavy maps, so the breakdown is the slowest tests
    rather than an even split. The parts overlap in wall clock (parallel workers), which is why the
    row disowns shares."""
    durations = "\n".join(f"{20 - i}.50s call     tests/test_villages.py::test_map_{i}" for i in range(12))
    monkeypatch.setattr(timings, "sh", _sh({}, default=(60.0, True, durations + "\n=== 12 passed ===")))
    r = timings.bench_pool_sweep()
    assert len(r.parts) == 8, "capped at eight"
    assert r.parts[0] == ("test_map_0", 20.5), "the slowest first, named by test"
    assert r.shares is False and "overlap in wall clock" in r.note


def test_bench_gate_times_the_FOUR_PHASES_and_keys_cold_and_warm_differently(monkeypatch: pytest.MonkeyPatch) -> None:
    """The gate is timed phase by phase rather than by running `make done` - the target is a loop
    over these four, so the sum IS the gate and this costs one gate instead of two."""
    fake = _sh({"typecheck": (0.5, True, "")}, default=(3.0, True, ""))
    monkeypatch.setattr(timings, "sh", fake)
    cold = timings.bench_gate()
    assert [c[1] for c in fake.calls] == ["lint", "format", "typecheck", "test"]
    assert cold.key == "full_gate" and cold.total == 3.0 + 3.0 + 0.5 + 3.0
    assert "GATE_NO_CACHE=1" in cold.what

    monkeypatch.setattr(timings, "sh", _sh({}, default=(1.0, False, "")))
    warm = timings.bench_gate(bypass=False)
    assert warm.key == "warm_gate" and warm.ok is False, "a failed phase makes the whole row untrustworthy"


# ---- the record it writes ---------------------------------------------------------------------
def test_context_records_what_the_numbers_DEPEND_on_and_answers_question_marks_rather_than_raising() -> None:
    """ "A container rebuild moves these, and the timings with them." A ledger row whose context is
    missing is a number nobody can compare, so every probe degrades to "?" instead of taking the
    benchmark down - the run is worth recording even if `resvg --version` is not installed."""
    ctx = timings.context()
    assert set(ctx) == {"cpus", "python", "resvg", "commit", "tests", "maps"}
    assert ctx["python"][0].isdigit() and int(ctx["cpus"]) >= 1
    assert ctx["maps"].isdigit() and int(ctx["maps"]) > 0, "both trees are censused"


def test_context_degrades_to_question_marks_when_every_probe_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """The failure half of the same rule, driven directly: with nothing runnable the harness still
    returns a complete context rather than raising out of the middle of a benchmark run."""

    def boom(*_a: Any, **_kw: Any) -> Any:
        raise OSError("no such tool")

    monkeypatch.setattr(subprocess, "run", boom)
    ctx = timings.context()
    assert ctx["resvg"] == "?" and ctx["commit"] == "?" and ctx["tests"] == "?"
    assert int(ctx["cpus"]) >= 1, "what can still be answered, is"


def test_render_block_prints_shares_only_where_they_MEAN_something_and_flags_a_failed_row() -> None:
    """Percentage shares only mean something when the parts are sequential components of the total.
    For an average or a parallel sweep the row disowns them and the table prints "-" - printing a
    percentage there would be inviting the reader to trust arithmetic nobody did."""
    ctx = {"cpus": "8", "python": "3.14.0", "resvg": "resvg 0.45", "commit": "abc1234", "tests": "2700", "maps": "10"}
    good = timings.Result("k", "a real loop", 100.0, [("part", 25.0)], True)
    avg = timings.Result("a", "an average", 40.0, [("per map", 10.0)], True, note="not a component", shares=False)
    bad = timings.Result("b", "a broken loop", 5.0, [], False)
    block = timings.render_block([good, avg, bad], ctx, "after feature 174")

    assert "| &nbsp;&nbsp;↳ part | | 25.0 s | 25% |" in block, "a component gets its share"
    assert "| &nbsp;&nbsp;↳ per map | | 10.0 s | - |" in block, "an average does not"
    assert "*not a component*" in block, "and says why, in the table"
    assert "**(FAILED - number is not trustworthy)**" in block, "a failed row is not quietly recorded as a time"
    assert "8 cpus, python 3.14.0" in block and "`abc1234`" in block and "after feature 174" in block


def test_render_block_survives_a_zero_total_without_dividing_by_it() -> None:
    ctx = dict.fromkeys(("cpus", "python", "resvg", "commit", "tests", "maps"), "?")
    block = timings.render_block([timings.Result("z", "instant", 0.0, [("part", 0.0)], True)], ctx, "")
    assert "| - |" in block


def test_main_dry_run_lists_the_plan_and_quick_is_the_INNER_LOOPS_only(capsys: pytest.CaptureFixture[str]) -> None:
    """`--quick` is "~1 min" against a full run's many minutes, so which benchmarks it drops is the
    knob's whole meaning and is asserted rather than described."""
    assert timings.main(["--dry-run", "--quick"]) == 0
    quick = capsys.readouterr().out.split()
    assert quick == ["hamlet_gen_gate", "cohort_4"]

    assert timings.main(["--dry-run"]) == 0
    full = capsys.readouterr().out.split()
    assert full[:2] == quick and "pool_sweep" in full and "warm_gate" in full


def test_main_runs_the_plan_and_APPENDS_to_the_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The end-to-end shape, with the ledger redirected so the test cannot append to the project's
    own `timings.md`. Appending (not rewriting) is the contract: the ledger is a trend, and a run
    that overwrote it would destroy the comparison the whole tool exists to make."""
    ledger = tmp_path / "timings.md"
    ledger.write_text("# earlier blocks\n")
    monkeypatch.setattr(timings, "LEDGER", ledger)
    monkeypatch.setattr(timings, "sh", _sh({}, default=(2.0, True, "")))
    monkeypatch.setattr(timings, "context", lambda: dict.fromkeys(("cpus", "python", "resvg", "commit", "tests", "maps"), "x"))

    assert timings.main(["--quick", "--note", "a one-clause note"]) == 0
    text = ledger.read_text()
    assert text.startswith("# earlier blocks\n"), "the earlier blocks survive"
    assert "hamlet_gen_gate" in text and "cohort_4" in text and "a one-clause note" in text
    out = capsys.readouterr().out
    assert "running hamlet_gen_gate" in out, "progress is printed as it goes, not only at the end"
    assert "QUICK set only - not a full row" in out, "and the ledger entry is labelled as partial"
