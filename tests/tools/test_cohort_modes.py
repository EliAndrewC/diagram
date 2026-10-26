"""The cohort's iteration modes (feature 426, D4): the seeds that failed last time first or alone, the stop at the first failing
seed, the failures a partial run carries forward unrolled, and the rolled/served count."""

from __future__ import annotations

import concurrent.futures
import json
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.tools import cohort_audit as ca

pytestmark = pytest.mark.tooling


@pytest.fixture(autouse=True)
def _record_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "cohort-log"
    monkeypatch.setattr(ca, "LOG_DIR", str(d))
    return d


def _roll(monkeypatch: pytest.MonkeyPatch, failing: set[int], seen: list[int], how: str = "rolled") -> None:
    def fake(spec: Any) -> Any:
        seen.append(spec[0])
        header = f"--- seed {spec[0]} row={('street/one/own', 'edge/both/shared')[spec[0] % 2]} water={('channel', 'well')[spec[0] % 2]}"
        return (header, ["c[1]"] if spec[0] in failing else [], ["c detail"] if spec[0] in failing else []), how

    monkeypatch.setattr(ca, "roll_how", fake)


def _records(d: Path) -> list[dict[str, Any]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))]


def test_failed_first_rolls_last_run_s_failures_first_and_last_failed_only_them(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], _record_dir: Path) -> None:
    seen: list[int] = []
    _roll(monkeypatch, {2, 3}, seen)
    ca.audit(4, 1, jobs=1, households=10)
    seen.clear()
    ca.audit(4, 1, jobs=1, households=10, failed_first=True)
    assert seen == [2, 3, 1, 4], "the failures first, then the rest, each in seed order"
    assert "those first: 2, 3" in capsys.readouterr().out
    seen.clear()
    ca.audit(4, 1, jobs=1, households=10, last_failed=True)
    assert seen == [2, 3]
    assert _records(_record_dir)[-1]["partial"] is True, "a run of some seeds is partial: never a landing record"


def test_with_no_last_run_on_the_block_every_seed_rolls_and_it_says_why(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    seen: list[int] = []
    _roll(monkeypatch, set(), seen)
    ca.audit(3, 1, jobs=1, households=10, last_failed=True)
    assert seen == [1, 2, 3] and "no failing seed recorded for this seed block (no last run)" in capsys.readouterr().out


def test_exitfirst_stops_at_the_first_failing_seed_says_how_many_it_left_and_is_red(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], _record_dir: Path) -> None:
    seen: list[int] = []
    _roll(monkeypatch, {2}, seen)
    assert ca.audit(5, 1, jobs=1, households=10, exitfirst=True) == 1
    assert seen == [1, 2]
    out = capsys.readouterr().out
    assert "3 seed(s) not rolled" in out and "cohort: rolled 2, served 0" in out
    assert _records(_record_dir)[-1]["partial"] is True


def test_a_partial_run_carries_forward_the_earlier_failures_it_did_not_roll(monkeypatch: pytest.MonkeyPatch, _record_dir: Path) -> None:
    """The GM's "pytest thing": a full run fails 3, 7 and 9; LAST_FAILED with EXITFIRST rolls 3, fails, stops; the next
    LAST_FAILED still rolls 7 and 9, never only 3."""
    seen: list[int] = []
    _roll(monkeypatch, {3, 7, 9}, seen)
    ca.audit(10, 1, jobs=1, households=10)
    seen.clear()
    ca.audit(10, 1, jobs=1, households=10, last_failed=True, exitfirst=True)
    assert seen == [3]
    assert _records(_record_dir)[-1]["carried"] == [7, 9]
    seen.clear()
    _roll(monkeypatch, set(), seen)
    ca.audit(10, 1, jobs=1, households=10, last_failed=True)
    assert seen == [3, 7, 9]


def test_the_stop_cancels_what_has_not_started_in_the_pool(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    class _Future:
        def __init__(self, value: Any) -> None:
            self.value, self.stopped = value, False

        def cancel(self) -> bool:
            self.stopped = True
            return True

        def cancelled(self) -> bool:
            return self.stopped

        def result(self) -> Any:
            return self.value

    class _Pool:
        def __init__(self, max_workers: int) -> None:
            pass

        def __enter__(self) -> _Pool:
            return self

        def __exit__(self, *_a: Any) -> None:
            return None

        def submit(self, fn: Any, spec: Any) -> _Future:
            return _Future(fn(spec))

    monkeypatch.setattr(concurrent.futures, "ProcessPoolExecutor", _Pool)
    monkeypatch.setattr(concurrent.futures, "as_completed", lambda futs: list(futs))
    seen: list[int] = []
    _roll(monkeypatch, {2}, seen)
    assert ca.audit(4, 1, jobs=2, households=10, exitfirst=True) == 1
    assert "2 seed(s) not rolled" in capsys.readouterr().out, "seeds 3 and 4 cancelled after 2 failed"
    seen.clear()
    _roll(monkeypatch, set(), seen)
    assert ca.audit(2, 1, jobs=2, households=10, exitfirst=True) == 0, "no failure: every seed rolled"


def test_the_cli_passes_the_three_modes_through(monkeypatch: pytest.MonkeyPatch) -> None:
    got: list[tuple] = []
    monkeypatch.setattr(ca, "audit", lambda *a: got.append(a) or 0)
    assert ca.main(["--anyway", "--failed-first", "--last-failed", "--exitfirst"]) == 0
    assert got[0][-3:] == (True, True, True)


def test_a_corrupt_record_is_skipped_and_a_clean_exitfirst_run_rolls_every_seed(monkeypatch: pytest.MonkeyPatch, _record_dir: Path) -> None:
    seen: list[int] = []
    _roll(monkeypatch, {2}, seen)
    ca.audit(3, 1, jobs=1, households=10)
    (_record_dir / "99999999T999999Z-corrupt.json").write_text("{not json", encoding="utf-8")
    assert ca.previous_failures(1, 3, 10, None)[0] == [2], "the newest readable record of the block"
    assert ca.previous_failures(1, 4, 10, None)[0] == [], "a block of another size is another block"
    seen.clear()
    _roll(monkeypatch, set(), seen)
    assert ca.audit(3, 1, jobs=1, households=10, exitfirst=True) == 0 and seen == [1, 2, 3]


def test_a_partial_run_skips_the_cohort_wide_checks_it_cannot_answer(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """A LAST_FAILED run of one seed cannot say every knob value was rolled: "-1/1 passed" on the first real run (feature 426)."""
    seen: list[int] = []
    _roll(monkeypatch, {2}, seen)
    ca.audit(3, 1, jobs=1, households=10)
    capsys.readouterr()
    ca.audit(3, 1, jobs=1, households=10, last_failed=True)
    assert "0/1 passed the whole gate" in capsys.readouterr().out


def test_the_landing_asks_the_cohort_a_developer_runs_so_it_serves_every_seed_rolled_before() -> None:
    """FR-012 (User Story 3b, the GM: "run the seeds locally and then do a make landing"): `make cohort-landing` rolls exactly
    `make cohort N=48 FRESH=0` - the same seeds, sizes and pinned rows - so each seed's stored roll (keyed on what it runs,
    T03) is served; measured 2026-10-26: a full run then the landing, rolled 0 of 54 (research R6)."""
    recipe = (Path(__file__).resolve().parents[2] / "Makefile").read_text(encoding="utf-8").split("\ncohort-landing:", 1)[1].split("\n\n", 1)[0]
    assert "$(MAKE) --no-print-directory cohort N=48 FRESH=0" in recipe
    assert not any(mode in recipe for mode in ("FAILED_FIRST", "LAST_FAILED", "EXITFIRST")), "the landing judges every seed (FR-008)"
