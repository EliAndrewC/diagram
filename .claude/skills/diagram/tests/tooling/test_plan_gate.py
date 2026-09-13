"""`scripts/_plan_gate.py` and the tick refusal, proven to fire (feature 243).

A plan's decisions are reviewed before its tasks are ticked. Each case is a rule a later session could
break without noticing: a missing plan passing, a stale review counting, a BLOCKED review ticking, a
typed verdict overriding its own rulings, a record written without the reviewer's declaration, a push
reading the working tree instead of what lands, and a bare escape token honored.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("_plan_gate", REPO / "scripts" / "_plan_gate.py")
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
sys.modules["_plan_gate"] = gate
_spec.loader.exec_module(gate)
_tt = importlib.util.spec_from_file_location("tick_task_for_gate", REPO / "scripts" / "tick-task.py")
assert _tt and _tt.loader
tt = importlib.util.module_from_spec(_tt)
_tt.loader.exec_module(tt)

PLAN = b"# plan\n\n**P1 - a decision.**\n"
TASKS = "# Tasks\n\n- [ ] T01 plan review\n      verify:\n- [ ] T02 build it\n      verify:\n"
NARROW_BAD = {"id": "P1", "summary": "a cutoff", "class": "narrowing", "ruling": "NOT LEGITIMATE", "why": "w"}
NARROW_OK = {"id": "P1", "summary": "a cutoff", "class": "narrowing", "ruling": "LEGITIMATE", "why": "w"}
WITHIN = {"id": "P2", "summary": "a module", "class": "within", "why": "w"}


@pytest.fixture(autouse=True)
def _isolated_census(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A recording guard's fixtures must never land in the live guard census (feature 169)."""
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "guard-log"))


def feature(root: pathlib.Path, plan: bytes | None = PLAN, review: dict | None = None, name: str = "243-x") -> pathlib.Path:
    d = root / "specs" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "tasks.md").write_text(TASKS, encoding="utf-8")
    if plan is not None:
        (d / "plan.md").write_bytes(plan)
    if review is not None:
        (d / "plan-review.json").write_text(json.dumps(review), encoding="utf-8")
    return d


def current(decisions: list[dict], verdict: str = "CLEAR", plan: bytes = PLAN) -> dict:
    return {"plan_sha256": hashlib.sha256(plan).hexdigest(), "decisions": decisions, "verdict": verdict}


def test_each_reason_a_feature_owes_a_review(tmp_path: pathlib.Path) -> None:
    assert gate.owed(feature(tmp_path / "a", plan=None))[0] == "plan-missing"
    assert gate.owed(feature(tmp_path / "b"))[0] == "plan-review-missing"
    d = feature(tmp_path / "c")
    (d / "plan-review.json").write_text("{not json", encoding="utf-8")
    assert gate.owed(d)[0] == "plan-review-missing"
    assert gate.owed(feature(tmp_path / "d", review=current([], plan=b"an older plan")))[0] == "plan-review-stale"
    blocked = gate.owed(feature(tmp_path / "e", review=current([NARROW_BAD], "BLOCKED")))
    assert blocked[0] == "plan-review-blocked" and "P1" in blocked[1]
    assert gate.owed(feature(tmp_path / "f", review=current([WITHIN, NARROW_OK]))) is None


def test_a_ticked_task_is_a_column_zero_line_in_either_case() -> None:
    text = "- [x] T01 a\n- [X] T02 b\n- [ ] T03 c\n  - [x] research pass - [x] source-reader confirmed\n"
    assert gate.ticked(text) == 2


@pytest.mark.parametrize(
    "decision, why",
    [
        ({"id": "P1", "summary": "s", "class": "maybe"}, "class must be"),
        ({"id": "P1", "summary": "s", "class": "narrowing"}, "needs a ruling"),
        ({"id": "P1", "summary": "s", "class": "within", "ruling": "LEGITIMATE"}, "carries no ruling"),
        ({"summary": "s", "class": "within"}, "id and a summary"),
    ],
)
def test_a_malformed_decision_is_refused(decision: dict, why: str) -> None:
    with pytest.raises(ValueError, match=why):
        gate.derive_verdict([decision])


def test_the_verdict_is_derived_from_the_rulings() -> None:
    assert gate.derive_verdict([]) == "CLEAR"
    assert gate.derive_verdict([WITHIN, NARROW_OK]) == "CLEAR"
    assert gate.derive_verdict([WITHIN, NARROW_BAD]) == "BLOCKED"


def test_recording_declines_without_the_reviewer_and_refuses_what_it_cannot_trust(tmp_path: pathlib.Path) -> None:
    d = feature(tmp_path)
    with pytest.raises(PermissionError, match="only the `spec-fidelity` subagent"):
        gate.record(d, current([]), "main")
    with pytest.raises(ValueError, match="plan changed while it was being reviewed"):
        gate.record(d, current([], plan=b"another plan"), "spec-fidelity")
    with pytest.raises(ValueError, match="says CLEAR but its rulings make it BLOCKED"):
        gate.record(d, current([NARROW_BAD], "CLEAR"), "spec-fidelity")
    with pytest.raises(ValueError, match="decisions must be a list"):
        gate.record(d, {"plan_sha256": hashlib.sha256(PLAN).hexdigest()}, "spec-fidelity")
    with pytest.raises(ValueError, match="no plan.md"):
        gate.record(feature(tmp_path / "np", plan=None), current([]), "spec-fidelity")
    assert not (d / "plan-review.json").exists(), "a refusal writes nothing"
    out = gate.record(d, {"plan_sha256": hashlib.sha256(PLAN).hexdigest(), "decisions": [NARROW_BAD]},
                      "spec-fidelity", today="2026-09-13")
    assert out["verdict"] == "BLOCKED" and out["reviewed"] == "2026-09-13" and out["declared"] == "spec-fidelity"
    assert gate.owed(d)[0] == "plan-review-blocked"
    gate.record(d, current([WITHIN]), "spec-fidelity")
    assert gate.owed(d) is None


def test_the_record_cli_resolves_a_feature_and_reports(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    d = feature(tmp_path)
    src = tmp_path / "review.json"
    src.write_text(json.dumps(current([WITHIN])), encoding="utf-8")
    assert gate.main(["record", str(d), str(src), "--as", "main"]) == 2
    assert "declined" in capsys.readouterr().err
    assert gate.main(["record", str(tmp_path / "specs" / "nope"), str(src), "--as", "spec-fidelity"]) == 2
    assert gate.main(["record", str(d), str(tmp_path / "missing.json"), "--as", "spec-fidelity"]) == 1
    assert gate.main(["record", str(d), str(src), "--as", "spec-fidelity"]) == 0
    assert "CLEAR recorded" in capsys.readouterr().out
    assert gate.resolve("243", tmp_path) == d and gate.resolve("999", tmp_path) is None
    assert gate.main(["owed", str(d)]) == 0
    assert gate.main(["owed", str(feature(tmp_path / "o"))]) == 1
    assert gate.main(["what"]) == 2


def _log_rules(tmp_path: pathlib.Path) -> list[str]:
    return [json.loads(p.read_text()).get("rule") for p in sorted((tmp_path / "guard-log").glob("*.json"))]


def test_a_tick_is_refused_then_escaped_only_with_a_reason_and_recorded(tmp_path: pathlib.Path) -> None:
    d = feature(tmp_path)
    (tmp_path / ".claude" / "skills" / "diagram" / "dev").mkdir(parents=True)
    ok, message = gate.tick_permitted(d, tmp_path, None)
    assert not ok and "no current CLEAR review" in message and "make plan-verdict" in message
    ok, message = gate.tick_permitted(d, tmp_path, "x")
    assert not ok and "needs a REASON" in message
    ok, message = gate.tick_permitted(d, tmp_path, "a superseded plan nobody implements")
    assert ok and "BYPASSED" in message
    entries = list((tmp_path / ".claude" / "skills" / "diagram" / "dev" / "bypass-log").glob("*.json"))
    assert len(entries) == 1 and "a superseded plan" in entries[0].read_text()
    assert sorted(_log_rules(tmp_path)) == sorted(["plan-review-missing", "PLAN_REVIEW_OK-no-reason", "plan-review-ok"])
    gate.record(d, current([]), "spec-fidelity")
    assert gate.tick_permitted(d, tmp_path, None) == (True, "")


def test_make_tick_refuses_and_writes_nothing_until_the_plan_is_reviewed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    d = feature(tmp_path)
    monkeypatch.setattr(tt, "repo_root", lambda start=None: tmp_path)
    monkeypatch.delenv("PLAN_REVIEW_OK", raising=False)
    assert tt.main(["243", "T01", "reviewed"]) == 2
    assert "plan-verdict" in capsys.readouterr().err
    assert (d / "tasks.md").read_text(encoding="utf-8") == TASKS
    gate.record(d, current([]), "spec-fidelity")
    assert tt.main(["243", "T01", "reviewed"]) == 0
    assert "- [x] T01" in (d / "tasks.md").read_text(encoding="utf-8")
    (d / "plan.md").write_bytes(PLAN + b"\n**P2 - a new narrowing.**\n")
    assert tt.main(["243", "T02", "built"]) == 2, "a plan edited after its review owes a new one (FR-004)"
    monkeypatch.setenv("PLAN_REVIEW_OK", "a probe escape with a reason")
    monkeypatch.setattr(gate, "bypass_record", lambda *a: None)
    assert tt.main(["243", "T02", "built"]) == 0
    assert "BYPASSED" in capsys.readouterr().out


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def test_the_push_judges_every_touched_feature_with_a_tick_at_HEAD(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "README").write_text("x")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    base = _git(root, "rev-parse", "HEAD")
    ticked_no_review = feature(root, name="001-a")
    (ticked_no_review / "tasks.md").write_text(TASKS.replace("- [ ] T01", "- [x] T01"), encoding="utf-8")
    feature(root, name="002-b")  # no tick: a plan still being drafted passes
    cleared = feature(root, name="003-c", review=current([WITHIN]))
    (cleared / "tasks.md").write_text(TASKS.replace("- [ ] T01", "- [x] T01"), encoding="utf-8")
    no_plan = feature(root, plan=None, name="004-d")
    (no_plan / "tasks.md").write_text(TASKS.replace("- [ ] T02", "- [X] T02"), encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "work")
    assert gate.touched_features(root, f"{base}..HEAD") == ["specs/001-a", "specs/002-b", "specs/003-c", "specs/004-d"]
    found = {f: rule for f, rule, _ in gate.push_owed(root, f"{base}..HEAD")}
    assert found == {"specs/001-a": "plan-review-missing", "specs/004-d": "plan-missing"}
    # what lands is HEAD: a review written in the working tree and not committed does not count
    (ticked_no_review / "plan-review.json").write_text(json.dumps(current([])), encoding="utf-8")
    assert "specs/001-a" in {f for f, _, _ in gate.push_owed(root, f"{base}..HEAD")}
