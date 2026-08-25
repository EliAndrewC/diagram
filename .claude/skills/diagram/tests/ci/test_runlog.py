"""The remote run-log entry and the month-to-date sum over LOCAL records (FR-020)."""

from __future__ import annotations

import json
from pathlib import Path

from l7r.diagram.ci import config, runlog
from tests.ci.conftest import git


def test_entry_shape_and_month_to_date(repo: Path) -> None:
    skill = repo / ".claude" / "skills" / "diagram"
    p = runlog.write_remote(skill, "ci-check", "reference", 300, "SUCCEEDED", "gm-assistant-check:abc", 4.0, "done")
    e = json.loads(p.read_text(encoding="utf-8"))
    assert e["where"] == "codebuild" and e["build_id"] == "gm-assistant-check:abc" and e["minutes"] == 4.0
    assert e["cost_usd"] == round(4.0 * config.RATE_PER_MIN, 4) and e["target"] == "ci-check" and e["seconds"] == 300
    assert e["commit"] == git(repo, "rev-parse", "--short", "HEAD")
    runlog.write_remote(skill, "ci-merge", "full", 500, "FAILED", "gm-assistant-merge:def", 10.0)
    # a local (non-remote) entry and a malformed file are ignored by the remote sum
    (skill / "dev" / "run-log" / "local.json").write_text(json.dumps({"utc": e["utc"], "scope": "reference", "seconds": 1, "result": "green", "commit": "x"}), encoding="utf-8")
    (skill / "dev" / "run-log" / "broken.json").write_text("{not json", encoding="utf-8")
    assert runlog.month_to_date(skill, now=e["utc"]) == round(14.0 * config.RATE_PER_MIN, 4)
    assert runlog.month_to_date(skill, now="1999-01-01T00:00:00Z") == 0.0
    rep = runlog.remote_spend_report(skill)
    assert "Remote spend" in rep and "gm-assistant-merge:def" in rep and "month-to-date: $1.12" in rep and "2 run(s)" in rep


def test_report_with_no_remote_runs(repo: Path) -> None:
    skill = repo / ".claude" / "skills" / "diagram"
    rep = runlog.remote_spend_report(skill)
    assert "(no remote runs yet)" in rep and "month-to-date: $0.00" in rep


# ---- the would-have-dispatched trail (feature 133 FR-004) -----------------------------------------


def test_would_have_entries_are_recorded_reported_and_never_spend(repo: Path) -> None:
    from l7r.diagram.ci import runlog

    skill = repo / ".claude" / "skills" / "diagram"
    before = runlog.month_to_date(skill)
    p = runlog.write_would_have(skill, "ci-check", "reference", 5.0, "remote off: attempted")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["where"] == "would-have-dispatched" and d["result"] == "would-have-dispatched" and d["minutes"] == 5.0 and d["cost_usd"] == round(5.0 * 0.08, 4)
    assert runlog.month_to_date(skill) == before, "an estimate is never spend"
    assert runlog.remote_entries(skill) == [] or all(r["where"] == "codebuild" for r in runlog.remote_entries(skill))
    rows = runlog.would_have_entries(skill)
    assert len(rows) == 1 and rows[0]["reason"] == "remote off: attempted"
    rep = runlog.remote_spend_report(skill)
    assert "Would have dispatched" in rep and "ci-check" in rep and "1 attempt(s)" in rep and "not spent" in rep
    assert "(none)" in runlog.would_have_report(repo / "nowhere")
