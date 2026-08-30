"""The scope lock in the Python entry points (feature 132, FR-013): every module that can roll more
than one map refuses FIRST, before any map rolls - and stays quiet when unlocked. These modules are
by-hand drivers outside the coverage rule, so each case here exists to PROVE the guard fires."""

from __future__ import annotations

from typing import Any

import pytest

from l7r.diagram import switches
from l7r.diagram.pipeline import regen
from l7r.diagram.tools import cache_audit, cohort_audit, make_regressions, mapcheck, perf_snapshot

LOCKED = switches.Switches(switches.Axis("on"), switches.Axis("reference", "test lock", "t", "2026-08-25T00:00:00Z"))


@pytest.fixture
def locked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(switches, "read", lambda skill: LOCKED)


def rolled_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Any path that would generate a map explodes - the refusal must come before it."""

    def boom(*a: Any, **k: Any) -> Any:
        raise AssertionError("a map was rolled under the scope lock")

    monkeypatch.setattr(regen, "regen_captured", boom)
    monkeypatch.setattr(cohort_audit, "_reference_ok", boom)
    monkeypatch.setattr(cohort_audit, "audit", boom)
    monkeypatch.setattr(cache_audit, "gens", boom)
    monkeypatch.setattr(perf_snapshot, "record", boom)
    monkeypatch.setattr(mapcheck, "_run", boom)


def test_cohort_refuses_first(locked: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    rolled_nothing(monkeypatch)
    assert cohort_audit.main(["--count", "48", "--anyway"]) == 2  # --anyway is not a way past the lock
    assert "make scope-unlock" in capsys.readouterr().err


def test_regen_refuses_a_list_but_not_one_map(locked: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    rolled_nothing(monkeypatch)
    assert regen.main(["pool/hamlets/a/a.gen.py", "pool/hamlets/b/b.gen.py", "--frozen-ok"]) == 2
    assert "regen of 2 maps" in capsys.readouterr().err
    monkeypatch.setattr(regen, "regen_captured", lambda gen, use_cache: ("REGENERATED", 1.0, ""))
    assert regen.main(["pool/hamlets/a/a.gen.py", "--frozen-ok"]) == 0  # ONE map per invocation is the carve-out (FR-012)


def test_cache_audit_and_regressions_and_perf_refuse(locked: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    rolled_nothing(monkeypatch)
    assert cache_audit.main(["--all"]) == 2 and "cache-audit --all" in capsys.readouterr().err
    assert make_regressions.main() == 2 and "regressions" in capsys.readouterr().err
    assert perf_snapshot.main(["--record", "--label", "x"]) == 2 and "perf --record" in capsys.readouterr().err
    monkeypatch.setattr(perf_snapshot, "report", lambda against: 0)
    assert perf_snapshot.main(["--report"]) == 0  # reading the log is not a roll


def test_mapcheck_locked_runs_the_reference_map_only_and_never_widens(locked: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    ran: list[list[str]] = []
    monkeypatch.setattr(mapcheck, "_run", lambda gens, stop_early: (ran.append(gens), (True, []))[1])
    monkeypatch.setattr(mapcheck, "_tripwire", lambda: (_ for _ in ()).throw(AssertionError("tripwire rolled under the lock")))
    monkeypatch.setattr(mapcheck, "_load", lambda: {"ok": True})  # a PASSED last run would normally widen
    monkeypatch.setattr(mapcheck, "_save", lambda ok, scope, failed: None)
    monkeypatch.setattr(mapcheck, "_live_gens", lambda tier: ["pool/hamlets/inashiro/inashiro.gen.py", "pool/hamlets/other/other.gen.py"])
    assert mapcheck.main([]) == 0
    assert ran == [["pool/hamlets/inashiro/inashiro.gen.py"]]
    assert "LOCKED" in capsys.readouterr().out
    assert mapcheck.main(["--scope", "all"]) == 1 and "make scope-unlock" in capsys.readouterr().err


def test_unlocked_stays_quiet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(switches, "read", lambda skill: switches.DEFAULTS)
    assert not switches.locked_out("anything")
