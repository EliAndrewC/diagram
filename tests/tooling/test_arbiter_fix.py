"""An arbiter's tooling fix is made, not lost (feature 379, the GM 2026-10-10).

On 2026-10-10 the round arbiter ruled on the research clone's two overlapping red gates and wrote, in its `what`, "the gate
should refuse to start while another make done is running in the same clone. File that as a tooling row". Nothing filed it.
Each case is a step that let it be lost: the fix only in prose, nothing holding the session to it, nothing showing the GM.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess

import pytest

from tests._scripts import script
from tests.tooling.test_modal_checks import _load

ha = _load("hm_arbiter")
cc = _load("close_check")

#: 378's ruling, replayed with its fix as the field (SC-001): the fix itself landed as scripts/gates/gate_lock.py
RULING_378 = {
    "ruling": "continue",
    "why": "The second trigger is the same event, since two gates ran at once in one clone.",
    "what": "Run exactly one make done, alone, in the foreground.",
    "tooling_fix": "the gate refuses to start while another make done is running in the same clone",
}
TRIGGER = "red-gate@2026-10-10T22:25:57Z"


@pytest.fixture
def root(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """A clone whose feature 900 has one task ticked and one open, a CLEAR plan review and its report."""
    monkeypatch.setattr(cc, "GRANDFATHERED", tmp_path / "none.txt")
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "guard-log"))
    r = tmp_path / "clone"
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    d = r / "specs" / "900-z"
    d.mkdir(parents=True)
    (d / "spec.md").write_text("# Feature 900\n")
    (d / "tasks.md").write_text("- [x] T01 a\n- [ ] T02 b\n      verify:\n- [ ] T03 c\n      verify:\n")
    plan = "# plan\n"
    (d / "plan.md").write_text(plan)
    (d / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan.encode()).hexdigest(), "plan_text": plan, "decisions": [], "verdict": "CLEAR"}))
    (d / "report.md").write_text("# report\n")
    (r / ".specify").mkdir()
    (r / ".specify" / "feature.json").write_text('{"feature_directory": "specs/900-z"}')
    (r / "tests" / "tooling").mkdir(parents=True)
    (r / "tests" / "tooling" / "test_gate_lock.py").write_text("def test_x():\n    pass\n")
    return r


def _tick(root: pathlib.Path, task: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", str(script("tick-task.py")), "900", task, "done it"], cwd=root, capture_output=True, text=True)


def test_the_fix_is_a_field_recorded_open_and_shown_to_the_gm(root: pathlib.Path) -> None:
    d = root / "specs" / "900-z"
    row = ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter", "2026-10-10T22:34:00Z")
    assert row["fix"] == "open" and row["tooling_fix"] == RULING_378["tooling_fix"]
    assert ha.open_fixes(d) == [(TRIGGER, RULING_378["tooling_fix"])]
    gm = json.loads((d / "gm-review.jsonl").read_text())
    assert gm["tooling_fix"] == RULING_378["tooling_fix"], "the GM sees the recommendation itself"
    assert list(ha.rulings(root)) == [TRIGGER]


def test_a_process_fault_names_its_fault_as_the_fix_and_files_nothing(root: pathlib.Path) -> None:
    d = root / "specs" / "900-z"
    with pytest.raises(ValueError, match="tooling_fix"):
        ha.record_ruling(root, "reversal:/a.md", {"ruling": "process-fault", "why": "an oscillation"}, "round-arbiter")
    ha.record_ruling(root, "reversal:/a.md", {"ruling": "process-fault", "why": "an oscillation", "tooling_fix": "the bundle keeps each round's reply"}, "round-arbiter")
    assert ha.open_fixes(d) == [("reversal:/a.md", "the bundle keeps each round's reply")]
    assert not (d / "found.jsonl").exists(), "the open item replaces the found row nothing enforced"


def test_an_open_fix_holds_every_tick_and_the_close(root: pathlib.Path) -> None:
    """SC-001, SC-002: on the old code this tick went through with the fix still open, as 378's T04 did at 18:49."""
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    r = _tick(root, "T02")
    assert r.returncode == 2 and "tooling fix is open" in r.stderr and TRIGGER in r.stderr
    assert "make arbiter-fix-done" in r.stderr and "make arbiter-fix-declined" in r.stderr
    assert "- [ ] T02" in (d / "tasks.md").read_text(), "a refused tick writes nothing"
    assert any("tooling fix is open" in why for why in cc.reasons(d, root / "specs")), "no route closes around it"


def test_made_with_its_test_it_settles_and_reaches_the_gm(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    with pytest.raises(ValueError, match="under tests/"):
        ha.settle_fix(root, TRIGGER, "done", "gate_lock.py refuses a second gate", "scripts/x.py")
    with pytest.raises(ValueError, match="under tests/"):
        ha.settle_fix(root, TRIGGER, "done", "gate_lock.py refuses a second gate")
    with pytest.raises(ValueError, match="two words"):
        ha.settle_fix(root, TRIGGER, "done", "done", "tests/tooling/test_gate_lock.py")
    with pytest.raises(ValueError, match="no open tooling fix"):
        ha.settle_fix(root, "red-gate@else", "done", "gate_lock.py refuses a second gate", "tests/tooling/test_gate_lock.py")
    with pytest.raises(ValueError, match="done or declined"):
        ha.settle_fix(root, TRIGGER, "maybe", "gate_lock.py refuses a second gate")
    # SC-004 (amendment 1, FR-006): made but not landed is not done
    with pytest.raises(ValueError, match="make land-tooling"):
        ha.settle_fix(root, TRIGGER, "done", "gate_lock.py refuses a second gate", "tests/tooling/test_gate_lock.py")
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "tests"], check=True)
    subprocess.run([*git, "commit", "-qm", "the fix's test"], check=True)
    with pytest.raises(ValueError, match="not on main"):
        ha.settle_fix(root, TRIGGER, "done", "gate_lock.py refuses a second gate", "tests/tooling/test_gate_lock.py")
    subprocess.run([*git, "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
    monkeypatch.chdir(root)
    assert ha.main(["fix", "done", TRIGGER, "gate_lock.py refuses a second gate", "tests/tooling/test_gate_lock.py"]) == 0
    assert ha.open_fixes(d) == [] and _tick(root, "T02").returncode == 0
    rows = [json.loads(ln) for ln in (d / "gm-review.jsonl").read_text().splitlines()]
    assert rows[-1]["kind"] == "arbiter-fix-done" and rows[-1]["test"] == "tests/tooling/test_gate_lock.py"
    assert rows[-1]["tooling_fix"] == RULING_378["tooling_fix"] and "gate_lock.py" in rows[-1]["note"]
    assert ha.main(["fix", "done", TRIGGER, "again and again", "tests/tooling/test_gate_lock.py"]) == 1, "settled once"


def test_an_overhaul_is_declined_to_the_gm_never_filed(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    monkeypatch.chdir(root)
    assert ha.main(["fix", "declined", TRIGGER, "it rebuilds how every gate is scheduled"]) == 0
    row = json.loads((d / "gm-review.jsonl").read_text().splitlines()[-1])
    assert row["kind"] == "arbiter-fix-declined" and "rebuilds" in row["note"] and "test" not in row
    assert ha.open_fixes(d) == [] and not (d / "found.jsonl").exists()
    assert sorted(p.name for p in (root / "specs").iterdir()) == ["900-z"], "no feature filed"
    assert ha.fix_hold(d) == ""


def test_the_record_reads_through_noise_and_needs_a_feature(root: pathlib.Path) -> None:
    d = root / "specs" / "900-z"
    ha.record_ruling(root, TRIGGER, RULING_378, "round-arbiter")
    (d / "arbiter.jsonl").write_text((d / "arbiter.jsonl").read_text() + "not json\n")
    assert ha.open_fixes(d) == [(TRIGGER, RULING_378["tooling_fix"])]
    assert ha.open_fixes(root / "specs" / "nowhere") == []
    (root / ".specify" / "feature.json").write_text("not json")
    with pytest.raises(ValueError, match="no active feature"):
        ha.settle_fix(root, TRIGGER, "declined", "it rebuilds every gate")


ab = _load("arbiter_bundle")


def test_a_process_question_goes_to_the_arbiter_first(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Amendment 2, SC-006 (the GM 2026-10-10: "things should go to the arbiter at the point where they were previously coming
    to me"): a regression the session cannot fix, put to the arbiter, is ruled once and lands on the GM's review."""
    d = root / "specs" / "900-z"
    (d / "request.md").write_text("the GM's words")
    monkeypatch.chdir(root)
    assert ha.main(["ask", "bad id!", "a real question here"]) == 2
    assert ha.main(["ask", "polder-regression", "fails"]) == 2, "the question needs two words"
    q = "the polder test fails on main too and cannot be fixed in this feature - waive it?"
    assert ha.main(["ask", "polder-regression", q]) == 0
    assert ha.owed(root)["ask:polder-regression"]["kind"] == "ask" and ha.blocking(root, "anything") == [], "it holds nothing"
    manifest = ab.bundle(root, "ask:polder-regression", tmp_path / "out").read_text()
    assert "## The question" in manifest and q in manifest
    ha.record_ruling(root, "ask:polder-regression", {"ruling": "accept", "why": "pre-existing and out of scope"}, "round-arbiter")
    assert json.loads((d / "gm-review.jsonl").read_text().splitlines()[-1])["trigger"] == "ask:polder-regression"
    assert ha.main(["ask", "polder-regression", q]) == 1, "one ruling per question"


def test_a_spec_review_trigger_points_the_arbiter_at_the_review_history(root: pathlib.Path, tmp_path: pathlib.Path) -> None:
    ha.trip(root, "round:spec-fidelity|900-z@6", "round", "spec-fidelity|900-z", "round 6 of specs/900-z's spec review")
    manifest = ab.bundle(root, "round:spec-fidelity|900-z@6", tmp_path / "out").read_text()
    assert "## Rounds - the spec review of 900-z" in manifest and "Review history" in manifest
