"""A cohort's seed newly failing owes the active task's part B (feature 385 D9), kept with `cohort_known.py` until T068 (`ask:449-T066-scope`)."""

from __future__ import annotations

import json
import pathlib
import subprocess

from tests.tooling.test_modal_checks import _load

ck = _load("cohort_known")


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True, capture_output=True, text=True).stdout


def feature(root: pathlib.Path) -> pathlib.Path:
    d = root / "specs" / "999-x"
    d.mkdir(parents=True)
    _git(root, "init", "-q")
    (root / "docs").mkdir()
    (root / "docs" / "approach-checklist.md").write_text("## A. x\n\n1. a\n\n## B. y\n\n1. b\n")
    (d / "plan.md").write_text("## T01 x\n")
    (d / "tasks.md").write_text("- [ ] T01 x\n")
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/999-x"}))
    return d


def _rec(utc: str, commit: str, verdicts: dict[int, str], households: int | None = None) -> dict:
    return {"utc": utc, "commit": commit, "households": households, "seeds": [{"seed": s, "verdict": v} for s, v in verdicts.items()]}


def test_a_seed_is_newly_failing_only_against_a_baseline_on_main() -> None:
    main = {"m1", "m2"}.__contains__
    now = _rec("20261017T2000Z", "c9", {1: "pass", 2: "fail", 3: "fail", 4: "fail", 5: "fail"})
    earlier = [
        _rec("20261017T1000Z", "m1", {2: "pass", 3: "pass", 4: "fail"}),
        _rec("20261017T1100Z", "m2", {3: "fail"}),
        _rec("20261017T1200Z", "c8", {5: "pass"}),
        _rec("20261017T1300Z", "m2", {2: "pass"}, households=40),
        _rec("20261017T2100Z", "m2", {4: "pass"}),
    ]
    assert ck.newly_failing(now, earlier, main) == [2]
    dirty = {**_rec("20261017T1500Z", "m2", {3: "fail"}), "engine_diff": "abc"}
    assert ck.newly_failing(now, [*earlier, dirty], main) == [2]
    assert ck.newly_failing(now, [_rec("20261017T1000Z", "m1", {3: "pass"}), {**_rec("20261017T1500Z", "m1", {3: "fail"}), "engine_diff": "abc"}], main) == [3]


def test_a_cohort_with_a_newly_failing_seed_owes_part_b_and_a_fit_failure_the_room_table(tmp_path: pathlib.Path) -> None:
    root = tmp_path
    feature(root)
    (root / "f").write_text("x")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    _git(root, "branch", "-M", "main")
    head = _git(root, "rev-parse", "HEAD").strip()
    logs = root / "dev" / "cohort-log"
    logs.mkdir(parents=True)
    assert ck.approach_owed(root) == "", "no record, nothing owed"
    (logs / "20261017T1000Z-a.json").write_text(json.dumps(_rec("20261017T1000Z", head, {7: "pass", 8: "pass"})))
    now = _rec("20261017T2000Z", "feedface", {7: "fail", 8: "pass"})
    now["seeds"][0]["failures"] = ["row_rules"]
    (logs / "20261017T2000Z-a.json").write_text(json.dumps(now))
    msg = ck.approach_owed(root)
    assert "seed(s) 7 newly failing" in msg and "part B" in msg and "room table" not in msg
    now = _rec("20261017T2100Z", "feedface", {7: "pass", 8: "refused"})
    now["seeds"][1]["failures"] = ["refused:WebRefused"]
    (logs / "20261017T2100Z-a.json").write_text(json.dumps(now))
    msg = ck.approach_owed(root)
    assert "seed(s) 8 newly failing" in msg and "## The room table" in msg and "`grow_gap`" in msg
    (logs / "20261017T2200Z-a.json").write_text(json.dumps(_rec("20261017T2200Z", "feedface", {9: "fail"})))
    assert ck.approach_owed(root) == "", "a seed with no baseline fires nothing"
