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
    assert not fs.exists and "no specs/999-nope/" in fs.why


def test_open_tasks_and_no_verdict_are_both_named(tmp_path: Path) -> None:
    _feature(tmp_path, "900-a", "- [x] T001 done\n- [ ] T002 not yet\n- [ ] T003 nor this\n- [ ] T004 four\n- [ ] T005 five\n", spec="no verdict here\n")
    fs = feature_status(tmp_path, "900-a")
    assert not fs.complete
    assert len(fs.open_tasks) == 4 and fs.open_tasks[0].startswith("T002")
    assert "4 open task(s)" in fs.why and "+1 more" in fs.why and "no FAITHFUL verdict" in fs.why


def test_complete_feature(tmp_path: Path) -> None:
    _feature(tmp_path, "900-b", "- [x] T001 done\n- [x] T002 also\n")
    fs = feature_status(tmp_path, "900-b")
    assert fs.complete and "is complete" in fs.why


def test_no_spec_file_means_no_verdict(tmp_path: Path) -> None:
    _feature(tmp_path, "900-c", "- [x] T001 done\n", spec=None)
    assert not feature_status(tmp_path, "900-c").faithful


def test_status_dataclass_defaults() -> None:
    assert FeatureStatus(name=None).open_tasks == ()
