"""FR-011: the gated merge needs a named feature with no open task and a FAITHFUL spec."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from l7r.diagram.ci.features import FeatureStatus, active_feature, feature_status


def _feature(root: Path, name: str, tasks: str, spec: str | None = "## Review history\nFAITHFUL\n") -> None:
    d = root / "specs" / name
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(tasks, encoding="utf-8")
    if spec is not None:
        (d / "spec.md").write_text(spec, encoding="utf-8")


def test_no_feature_named(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPECIFY_FEATURE", raising=False)
    assert active_feature(tmp_path) is None
    fs = feature_status(tmp_path, None)
    assert not fs.complete and "no spec-kit feature is named" in fs.why


def test_env_then_feature_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPECIFY_FEATURE", "130-x")
    assert active_feature(tmp_path) == "130-x"
    monkeypatch.delenv("SPECIFY_FEATURE")
    (tmp_path / ".specify").mkdir()
    (tmp_path / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/131-y/"}), encoding="utf-8")
    assert active_feature(tmp_path) == "131-y"
    (tmp_path / ".specify" / "feature.json").write_text("not json", encoding="utf-8")
    assert active_feature(tmp_path) is None
    (tmp_path / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": ""}), encoding="utf-8")
    assert active_feature(tmp_path) is None


def test_missing_directory(tmp_path: Path) -> None:
    fs = feature_status(tmp_path, "999-nope")
    assert not fs.exists and "no specs/999-nope/" in fs.why and "SPECIFY_FEATURE=<NNN-slug> scripts/sync-with-main.sh done" in fs.why


def test_open_tasks_and_no_verdict_are_both_named(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The boxes the push's rule says hold the merge are named, at most three and a count (feature 405 T32: the rule is the
    active task's - stubbed here with four held boxes to reach the count)."""
    import l7r.diagram.ci.features as features

    _feature(tmp_path, "900-a", "- [x] T001 done\n- [ ] T002 not yet\n- [ ] T003 nor this\n- [ ] T004 four\n- [ ] T005 five\n", spec="no verdict here\n")
    monkeypatch.setattr(features, "holding", lambda d: ["T002 not yet", "T003 nor this", "T004 four", "T005 five"])
    fs = feature_status(tmp_path, "900-a")
    assert not fs.complete
    assert len(fs.open_tasks) == 4 and fs.open_tasks[0].startswith("T002")
    assert "4 open task(s)" in fs.why and "+1 more" in fs.why and "no FAITHFUL verdict" in fs.why


def test_complete_feature(tmp_path: Path) -> None:
    _feature(tmp_path, "900-b", "- [x] T001 done\n- [x] T002 also\n")
    fs = feature_status(tmp_path, "900-b")
    assert fs.complete and "no task holds this landing" in fs.why, "the words say what was checked: an unstarted open task holds none (2026-10-26)"


def test_no_spec_file_means_no_verdict(tmp_path: Path) -> None:
    _feature(tmp_path, "900-c", "- [x] T001 done\n", spec=None)
    assert not feature_status(tmp_path, "900-c").faithful


def test_status_dataclass_defaults() -> None:
    assert FeatureStatus(name=None).open_tasks == ()


def test_only_the_active_task_holds_the_merge(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 405 T32 (D4): the gated merge asks the push's own rule - a feature in progress is held only by the clone's
    active task while it is open; a task nobody started holds nothing (the GM 2026-10-20: no Lands open line)."""
    import subprocess

    monkeypatch.delenv("L7R_LAND_TICKS", raising=False)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    _feature(tmp_path, "405-x", "- [x] T12 done\n- [ ] T01 later\n- [ ] T02 the one being worked\n")
    assert feature_status(tmp_path, "405-x").complete
    (tmp_path / ".git" / "active-task").write_text(json.dumps({"feature": "405-x", "task": "T02"}), encoding="utf-8")
    fs = feature_status(tmp_path, "405-x")
    assert not fs.complete and fs.open_tasks == ("T02 the one being worked",)


def test_a_spec_the_round_arbiter_accepted_at_its_cap_is_faithful(tmp_path: Path) -> None:
    """Feature 387: the spec review went past its round cap and the arbiter ruled `accept`; the review gate took the ruling as the
    verdict and this check, reading only for FAITHFUL, refused the merge. A plan's cap, another feature's or a `continue` is no verdict."""
    import json

    _feature(tmp_path, "387-x", "- [x] T01 done\n", spec="## Review history\n- round 5: CHANGES REQUIRED\n")
    d = tmp_path / "specs" / "387-x"
    assert not feature_status(tmp_path, "387-x").faithful
    rows = [
        {"trigger": "round:spec-fidelity|plan:387-x#T01@3", "ruling": "accept"},
        {"trigger": "round:spec-fidelity|388-y#1@6", "ruling": "accept"},
        {"trigger": "round:spec-fidelity|387-x#1@6", "ruling": "continue"},
    ]
    (d / "arbiter.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n")
    assert not feature_status(tmp_path, "387-x").faithful
    with (d / "arbiter.jsonl").open("a") as fh:
        fh.write(json.dumps({"trigger": "round:spec-fidelity|387-x#1@6", "ruling": "accept"}) + "\n")
    assert feature_status(tmp_path, "387-x").complete
