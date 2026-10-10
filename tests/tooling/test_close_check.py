"""`scripts/gates/close_check.py` - no route closes a feature without its report and its carried keys (feature 375, FR-009,
FR-014; plan D13).

Before this feature a feature's last `make tick` closed it with nothing to show for where its time went, and a success
criterion carried to a later feature rested on that feature remembering it. Each case is a route that closed a feature then.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from tests._scripts import script
from tests.tooling.test_modal_checks import _load

cc = _load("close_check")


@pytest.fixture
def specs(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    monkeypatch.setattr(cc, "GRANDFATHERED", tmp_path / "closed-before-375.txt")
    s = tmp_path / "specs"
    (s / "375-x").mkdir(parents=True)
    (s / "375-x" / "spec.md").write_text("- **SC-003** `Carried: SC-003 -> 374 sc003-first-three`\n")
    (s / "374-y").mkdir()
    (s / "374-y" / "spec.md").write_text("# Feature 374\n")
    return s


def test_a_feature_closes_with_its_report_and_its_carried_keys(specs: pathlib.Path) -> None:
    d = specs / "374-y"
    why = cc.reasons(d, specs)
    assert len(why) == 2 and "no report.md" in why[0] and "375-x's SC-003 is carried here and `sc003-first-three`" in why[1]
    (d / "report.md").write_text("# report\n")
    (d / "measurements.json").write_text(json.dumps({"sc003-first-three": {"value": 1}}))
    assert cc.reasons(d, specs) == []
    assert cc.carries(specs) == [("375-x", "SC-003", "374", "sc003-first-three")]
    (d / "measurements.json").write_text("not json")
    assert len(cc.reasons(d, specs)) == 1, "an unreadable file holds no key"
    cc.GRANDFATHERED.write_text("374-y\n")
    assert cc.reasons(d, specs) == [], "closed before the check landed: not asked"


def test_the_last_tick_refuses_without_the_report(tmp_path: pathlib.Path) -> None:
    """The old behavior: `make tick` on the last open task closed the feature with no report."""
    root = tmp_path / "clone"
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    d = root / "specs" / "900-z"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text("- [x] T01 a\n- [ ] T02 b\n      verify:\n")
    plan = "# plan\n"
    (d / "plan.md").write_text(plan)
    import hashlib

    (d / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan.encode()).hexdigest(), "plan_text": plan, "decisions": [], "verdict": "CLEAR"}))
    (d / "spec.md").write_text("# Feature 900\n")
    tick = script("tick-task.py")
    r = subprocess.run(["python3", str(tick), "900", "T02", "done it"], cwd=root, capture_output=True, text=True)
    assert r.returncode == 2 and "this tick would close the feature" in r.stderr and "no report.md" in r.stderr
    (d / "report.md").write_text("# report\n")
    r = subprocess.run(["python3", str(tick), "900", "T02", "done it"], cwd=root, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_the_push_asks_every_touched_feature_that_reads_closed(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "clone"
    env = {"GIT_AUTHOR_NAME": "a", "GIT_AUTHOR_EMAIL": "a@b", "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@b", "PATH": "/usr/bin:/bin"}
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "--allow-empty", "-m", "base"], check=True, env=env)
    for name, tasks, spec in (
        ("901-done", "- [x] T01\n", "**Status**: In progress\n"),
        ("902-open", "- [ ] T01\n", "x\n"),
        ("903-withdrawn", "- [ ] T01\n", "**Status**: Withdrawn - superseded by nothing\n"),
    ):
        d = root / "specs" / name
        d.mkdir(parents=True)
        (d / "tasks.md").write_text(tasks)
        (d / "spec.md").write_text(spec)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "work"], check=True, env=env)
    monkeypatch.setattr(cc, "GRANDFATHERED", tmp_path / "none.txt")
    found = cc.push_reasons(root, "HEAD~1..HEAD")
    assert any("901-done has no report.md" in f for f in found) and any("903-withdrawn" in f for f in found)
    assert not any("902-open" in f for f in found), "an open feature is not closing"
    monkeypatch.chdir(root)
    assert cc.main(["--push", "HEAD~1..HEAD"]) == 1
    assert cc.main([str(root / "specs" / "902-open")]) == 1 and cc.main(["--carries"]) == 0 and cc.main([]) == 2
    monkeypatch.setattr(cc, "GRANDFATHERED", tmp_path / "written.txt")
    assert cc.main(["--write-grandfathered"]) == 0 and "901-done" in (tmp_path / "written.txt").read_text()
