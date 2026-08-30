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
    assert pr.main(["check", "--feature", "", "--log-dir", str(log)]) == 0, "a docs-only push names no feature and owes nothing (the first direct push after 129 was refused here)"
    assert "nothing to review" in capsys.readouterr().out
    assert pr.main(["explain", "--why", "x", "--feature", "", "--log-dir", str(log)]) == 2
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


# ---------------------------------------------------------------------------------------------------
# THE TWO SKIP BRANCHES THE DELETED COVERAGE CARRIERS USED TO REACH (feature 166)
# ---------------------------------------------------------------------------------------------------
#
# `tests/full/test_coverage_carriers.py` replayed frozen subjects through the whole gate so deep
# branches executed, and it went with the check battery. Two branches in `perf_review` lost their only
# reader with it. They are RE-DERIVED here as real tests rather than exempted, because a coverage floor
# lowered to match a deletion stops being a floor - and both branches are behavior somebody depends on,
# not filler: a malformed file in an append-only log directory must not take the review down.


def test_a_corrupt_review_record_is_skipped_not_fatal(log: Path) -> None:
    """`_records`' ValueError arm. `dev/perf-log/` is append-only history written by several sessions at
    once, and a half-written or truncated file is a real thing to find there - a run killed mid-write
    leaves one. The reader must step over it and return the records it CAN parse, because the
    alternative is that one bad byte anywhere in the history blocks every future push.

    The same reasoning the guard-log rule states one directory over: a log that cannot be WRITTEN must
    not take the guard down. Here it is a log that cannot be READ.

    (Written against `_records` after a first draft asserted it of `_snapshots` - a different function
    with a different glob and no `_file` key. The two sit ten lines apart and both read this directory.)"""
    band(log, 0.0)
    good = {"kind": "explanation", "verdict": "pending", "feature": "129", "environment": "local"}
    (log / "20260825T040000Z-129-review-local-a.json").write_text(json.dumps(good), encoding="utf-8")
    (log / "20260825T020000Z-129-review-local-c.json").write_text("{not json at all", encoding="utf-8")
    (log / "20260825T030000Z-129-review-local-d.json").write_text("", encoding="utf-8")
    got = pr._records(log)
    assert [d["_file"] for d in got] == ["20260825T040000Z-129-review-local-a.json"], (
        f"the two corrupt records were not stepped over cleanly: {[d.get('_file') for d in got]}"
    )


def test_a_snapshot_for_another_feature_is_not_paired_with_this_one(log: Path) -> None:
    """`pairs` line 89. The log holds every feature's bookends together, so the label filter is what keeps
    feature 129's verdict from being computed against feature 166's numbers. A pair built across features
    would compare two different engines and report the difference as a regression in whichever one was
    being reviewed."""
    band(log, 0.0)
    snap(log, "166-start", {1: 999.0, 2: 999.0}, "20260830T000000Z")
    snap(log, "166-end", {1: 1.0, 2: 1.0}, "20260830T010000Z")
    got = pr.pairs(log, F)
    assert "local" in got, "the feature's own pair went missing"
    for env, verdict in got.items():
        assert verdict is not None, f"{env}: no verdict from this feature's own bookends"
    # the smoking gun: 999 -> 1 across features would be an enormous 'improvement' if the filter leaked
    assert pr.pairs(log, "166-x").keys() == {"local"}, "feature 166's own pair should still resolve on its own"
