"""The review records and the push-time check (feature 129, T010/T012): FIRES on every missing,
stale, negative or self-granted record; STAYS QUIET when the ladder is complete."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.tools import perf_review as pr

F = "129-perf-audit-subagent"


def snap(log: Path, label: str, seconds: dict[int, float], utc: str, commit: str = "abc1234", environment: str = "local") -> None:
    body: dict[str, Any] = {
        "label": label,
        "utc": utc,
        "commit": commit,
        "environment": environment,
        "rows": [{"seed": s, "seconds": v, "stages": {"web": v * 0.8, "field": v * 0.2}} for s, v in seconds.items()],
    }
    (log / f"{utc}-{label}-{environment}-c.json").write_text(json.dumps(body), encoding="utf-8")


@pytest.fixture
def log(tmp_path: Path) -> Path:
    d = tmp_path / ".clones" / "myclone" / "dev" / "perf-log"
    d.mkdir(parents=True)
    return d


def band(log: Path, seed_pct: float, env: str = "local") -> None:
    snap(log, "129-start", {1: 100.0, 2: 100.0}, "20260825T000000Z", environment=env)
    snap(log, "129-end", {1: 100.0 * (1 + seed_pct / 100), 2: 100.0}, "20260825T010000Z", environment=env)


def run(log: Path, *args: str, env: str = "local") -> int:
    return pr.main([*args, "--feature", F, "--log-dir", str(log), "--environment", env])


def test_no_pair_means_nothing_to_review(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(log, "check") == 0 and "nothing to review" in capsys.readouterr().out
    assert run(log, "explain", "--why", "x") == 2, "no pair: the bookends come first"


def test_no_increase_owes_nothing(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    band(log, -2.0)
    assert run(log, "check") == 0 and "nothing owed" in capsys.readouterr().out


def test_band_1_FIRES_without_explanation_then_without_confirmation(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    band(log, 0.5)
    assert run(log, "check") == 1
    out = capsys.readouterr()
    assert "MISSING: a written explanation" in out.out and "perf-audit confirmation" in out.out and "REFUSED" in out.err
    assert run(log, "explain", "--why", "") == 2, "an empty explanation is noticed, not explained"
    assert run(log, "explain", "--why", "seed 1 +0.5% is inside the 1.7% per-seed floor") == 0
    assert run(log, "check") == 1 and "MISSING: a perf-audit confirmation" in capsys.readouterr().out
    # the main session cannot confirm: the prompt, and DECLINED
    assert run(log, "confirm", "--verdict", "consistent") == 1
    assert "WHO IS ASKING" in capsys.readouterr().err
    assert run(log, "confirm", "--verdict", "consistent", "--as", "perf-audit") == 0
    assert run(log, "check") == 0 and "every owed record present" in capsys.readouterr().out


def test_an_inconsistent_confirmation_does_not_pass(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    band(log, 0.5)
    run(log, "explain", "--why", "cause")
    assert run(log, "confirm", "--verdict", "inconsistent", "--as", "perf-audit") == 0
    assert run(log, "check") == 1 and "negative or inconclusive records do not count: confirmation=inconsistent" in capsys.readouterr().out
    assert run(log, "confirm", "--verdict", "maybe", "--as", "perf-audit") == 2


def test_band_2_needs_the_audit_with_every_criterion(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    band(log, 12.0)
    run(log, "explain", "--why", "a new placement rule in web")
    run(log, "confirm", "--verdict", "consistent", "--as", "perf-audit")
    assert run(log, "check") == 1 and "escalated audit" in capsys.readouterr().out
    assert run(log, "audit", "--verdict", "justified", "--necessary", "yes", "--as", "perf-audit") == 2, "commensurate and no_way_around missing"
    assert "missing: commensurate, no_way_around" in capsys.readouterr().err
    assert run(log, "audit", "--verdict", "justified", "--necessary", "yes", "--commensurate", "yes", "--no-way-around", "no", "--as", "perf-audit") == 0
    assert run(log, "check") == 0
    assert run(log, "audit", "--verdict", "sure", "--necessary", "a", "--commensurate", "b", "--no-way-around", "c", "--as", "perf-audit") == 2
    assert run(log, "audit", "--verdict", "justified", "--necessary", "a", "--commensurate", "b", "--no-way-around", "c") == 1, "the main session is prompted and declined"


@pytest.mark.parametrize("verdict", ["not-justified", "cannot-determine"])
def test_a_negative_or_inconclusive_audit_does_not_pass(log: Path, verdict: str, capsys: pytest.CaptureFixture[str]) -> None:
    band(log, 12.0)
    run(log, "explain", "--why", "cause")
    run(log, "confirm", "--verdict", "consistent", "--as", "perf-audit")
    assert run(log, "audit", "--verdict", verdict, "--necessary", "a", "--commensurate", "b", "--no-way-around", "c", "--as", "perf-audit") == 0
    assert run(log, "check") == 1 and f"audit={verdict}" in capsys.readouterr().out


def test_band_3_needs_the_GMs_signoff_at_a_terminal(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    band(log, 25.0)
    run(log, "explain", "--why", "cause")
    run(log, "confirm", "--verdict", "consistent", "--as", "perf-audit")
    run(log, "audit", "--verdict", "justified", "--necessary", "a", "--commensurate", "b", "--no-way-around", "c", "--as", "perf-audit")
    assert run(log, "check") == 1 and "GM's sign-off" in capsys.readouterr().out
    assert run(log, "signoff", "--why", "ok", "--tty", "no") == 1, "no terminal: refused"
    assert "in person" in capsys.readouterr().err
    assert run(log, "signoff", "--why", "", "--tty", "yes") == 2
    assert run(log, "signoff", "--why", "the map gains a whole tier; accepted", "--tty", "yes") == 0
    assert run(log, "check") == 0
    rec = json.loads(next(log.glob("*-review-129-signoff-*.json")).read_text(encoding="utf-8"))
    assert rec["granted_by"]["declared"] == "GM" and rec["band"] == 3 and rec["verdict"] == "signed" and rec["binding"]


def test_a_record_is_bound_to_the_numbers_and_the_commit(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    band(log, 0.5)
    run(log, "explain", "--why", "cause")
    run(log, "confirm", "--verdict", "consistent", "--as", "perf-audit")
    assert run(log, "check") == 0
    # a NEWER -end with different numbers: every earlier record is stale, by name
    snap(log, "129-end", {1: 103.0, 2: 100.0}, "20260825T020000Z", commit="def5678")
    assert run(log, "check") == 1
    out = capsys.readouterr().out
    assert "stale records" in out and "review-129-confirmation" in out
    # a fresh explanation for the new numbers does NOT revive the old confirmation: it is bound to the old ones
    assert run(log, "explain", "--why", "the new numbers") == 0
    assert run(log, "check") == 1 and "MISSING: a perf-audit confirmation" in capsys.readouterr().out


def test_environments_are_checked_independently(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    band(log, -1.0, "local")
    band(log, 0.8, "codebuild")
    assert run(log, "check") == 1
    out = capsys.readouterr().out
    assert "[codebuild]" in out and "MISSING" in out and "[local]" in out and "nothing owed" in out
    assert run(log, "explain", "--why", "x", env="codebuild") == 0
    assert run(log, "confirm", "--verdict", "consistent", "--as", "perf-audit", env="codebuild") == 0
    assert run(log, "check") == 0
    assert run(log, "show", env="codebuild") == 0 and "perf bands [codebuild]" in capsys.readouterr().out


def test_no_feature_and_no_pair_for_environment(log: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert pr.main(["check", "--feature", "", "--log-dir", str(log)]) == 2
    band(log, 1.0)
    assert run(log, "show", env="codebuild") == 2 and "no 129-start/-end pair for environment 'codebuild'" in capsys.readouterr().err


def test_unreadable_files_are_skipped_and_the_clone_is_named(log: Path) -> None:
    (log / "broken.json").write_text("{", encoding="utf-8")
    (log / "20260825T000000Z-review-129-audit-x.json").write_text("{", encoding="utf-8")
    band(log, 0.5)
    run(log, "explain", "--why", "cause")
    name = next(log.glob("*-review-129-explanation-*")).name
    assert name.endswith("-local-myclone.json")
    assert pr.feature_number("adhoc") == ""
