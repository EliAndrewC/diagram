"""The door between the Python that still needs the plan gate and the gate in Rust (feature 449 T066, `ask:449-T066-scope`): what crosses it. The
gate's own cases are in `rust/gate/src/plan/`."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

from tests._scripts import script
from tests.tooling.test_modal_checks import _load

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / "scripts"), str(REPO / "scripts" / "gates")]
import plan_door  # noqa: E402
import task_start  # noqa: E402
import wording  # noqa: E402

_tt = importlib.util.spec_from_file_location("tick_task_for_door", script("tick-task.py"))
assert _tt and _tt.loader
tt = importlib.util.module_from_spec(_tt)
_tt.loader.exec_module(tt)

PLAN = b"# plan\n\n**P1 - a decision.**\n"
PLAN_TASKS = b"# plan\n\n**D1 - a decision.** Each tub by a door.\n\n## T05 the bath (amendment 1)\n\n- the bath 10 x 8 ft (GUESS)\n\n## T06 the wells\n\n- a well by the kitchen\n"
TASKS = "# Tasks\n\n- [ ] T01 plan review\n      verify:\n- [ ] T02 build it\n      verify:\n"
TRIG = "round:spec-fidelity|plan:385-x#T17@3"


@pytest.fixture(autouse=True)
def _isolated_census(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "guard-log"))


def feature(root: pathlib.Path, plan: bytes = PLAN, name: str = "243-x") -> pathlib.Path:
    d = root / "specs" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "tasks.md").write_text(TASKS, encoding="utf-8")
    (d / "request.md").write_text("> the GM's words\n", encoding="utf-8")
    (d / "plan.md").write_bytes(plan)
    return d


def clear(d: pathlib.Path, plan: bytes = PLAN) -> None:
    (d / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan).hexdigest(), "decisions": [], "verdict": "CLEAR"}), encoding="utf-8")


def test_the_door_forwards_each_answer_as_the_caller_expects_it(tmp_path: pathlib.Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    d = feature(tmp_path, PLAN_TASKS, "375-x")
    assert set(plan_door.task_sections(PLAN_TASKS.decode())) == {"T05", "T06"}
    assert [k for k, _b, _a in plan_door.blocks("# t\n\n## A\n")] == ["preamble", "## A"]
    assert plan_door.resolve("375", tmp_path) == d and plan_door.resolve("999", tmp_path) is None
    assert plan_door.active_task(tmp_path) == (None, "")
    (tmp_path / ".specify").mkdir()
    (tmp_path / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/375-x"}))
    assert plan_door.active_task(tmp_path) == (d, "T01")
    assert plan_door.touched_features(tmp_path, "HEAD") == []
    assert plan_door.approach_refusal(d, tmp_path, "T05") is None
    assert plan_door.approach_ruled(tmp_path, "ask:x") is None
    assert plan_door.owe_in_flight(tmp_path, "hour:1", "B") == ""
    assert plan_door.wording_only("### T05 Decisions\n\n**Wording only.** x\n") and not plan_door.wording_only("x")
    assert plan_door.archive(d) == []
    with pytest.raises(ValueError, match="is not a plan review"):
        plan_door.arbiter_accept(d, "ask:385-route")
    with pytest.raises(PermissionError, match="holds no accept"):
        plan_door.arbiter_accept(d, TRIG)


def test_a_tick_is_asked_through_the_door_escape_and_all(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    d = feature(tmp_path)
    (tmp_path / "dev").mkdir()
    monkeypatch.delenv("PLAN_REVIEW_OK", raising=False)
    ok, message = plan_door.tick_permitted(d, tmp_path, None)
    assert not ok and "no current CLEAR review" in message
    ok, message = plan_door.tick_permitted(d, tmp_path, "a superseded plan nobody implements")
    assert ok and "BYPASSED" in message and len(list((tmp_path / "dev" / "bypass-log").rglob("*.json"))) == 1


def test_make_tick_refuses_and_writes_nothing_until_the_plan_is_reviewed(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    d = feature(tmp_path)
    monkeypatch.setattr(tt, "repo_root", lambda start=None: tmp_path)
    monkeypatch.delenv("PLAN_REVIEW_OK", raising=False)
    assert tt.main(["243", "T01", "reviewed"]) == 2
    assert "plan-verdict" in capsys.readouterr().err
    assert (d / "tasks.md").read_text(encoding="utf-8") == TASKS
    clear(d)
    assert tt.main(["243", "T01", "reviewed"]) == 0
    assert "- [x] T01" in (d / "tasks.md").read_text(encoding="utf-8")
    (d / "plan.md").write_bytes(PLAN + b"\n**P2 - a new narrowing.**\n")
    assert tt.main(["243", "T02", "built"]) == 2, "a plan edited after its review owes a new one (FR-004)"


def test_make_tick_asks_the_approach_gate(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    plan = b"## T02 x\n\n### T02 Approach (checklist part A)\n\n1. **a.** b\n"
    d = feature(tmp_path, plan)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "approach-checklist.md").write_text("## A. x\n\n1. **a.** b\n2. **c.** d\n")
    clear(d, plan)
    monkeypatch.setattr(tt, "repo_root", lambda start=None: tmp_path)
    assert tt.main(["243", "T02", "x"]) == 2
    assert "item(s) 2 unanswered" in capsys.readouterr().err


def test_task_start_marks_the_task_and_names_its_feature(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "clone"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    d = feature(root, PLAN_TASKS, "375-x")
    (d / "tasks.md").write_text("- [ ] T05 the bath\n- [ ] T06 the wells\n")
    monkeypatch.chdir(root)
    assert task_start.main(["375", "T06"]) == 0 and json.loads((root / ".git" / "active-task").read_text())["task"] == "T06"
    assert json.loads((root / ".git" / "task-starts.jsonl").read_text().splitlines()[-1])["task"] == "T06", "feature 385 D10: each start logged"
    assert task_start.main(["999", "T06"]) == 2
    assert task_start.main(["375"]) == 2
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/415-other"}))
    assert task_start.main(["375", "T06"]) == 0 and plan_door.active_task(root) == (d, "T06"), "405 T106: the started feature is named"


def test_a_wording_only_tick_is_refused_when_a_commit_changed_what_runs(tmp_path: pathlib.Path) -> None:
    """Feature 385 T118 (D138): the declaration is checked against the task's own commits since its `make task-start`."""

    def git(*a: str, when: str | None = None) -> None:
        env = {**os.environ, **({"GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when} if when else {})}
        subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True, env=env)

    git("init", "-q", "-b", "main")
    (tmp_path / "m.py").write_text("X = 1\n")
    git("add", "-A")
    git("commit", "-qm", "base", when="2026-01-01T00:00:00Z")
    sec = "## T05 - x\n\n### T05 Decisions\n\n**Wording only.** a comment.\n"
    d = tmp_path / "specs" / "385-x"
    assert "no `make task-start`" in wording.refusal(tmp_path, d, "T05", sec)
    (tmp_path / ".git" / "task-starts.jsonl").write_text(json.dumps({"feature": "385-x", "task": "T05", "utc": "2026-01-02T00:00:00Z"}) + "\n")
    (tmp_path / "m.py").write_text('X = 1\n"""Research: x - GUESS"""  # a comment\n')
    glossary = tmp_path / "l7r/diagram/interactive/assets/glossary"
    glossary.mkdir(parents=True)
    (glossary / "1-Word.json").write_text("{}\n")
    git("add", "-A")
    git("commit", "-qm", "words")
    assert wording.refusal(tmp_path, d, "T05", sec) == "", "a claim, a comment and a glossary entry are wording"
    assert wording.refusal(tmp_path, d, "T05", sec.replace("**Wording only.**", "**D10 - a rule.**")) == "", "not declared: not checked"
    (tmp_path / "m.py").write_text('X = 2\n"""Research: x - GUESS"""  # a comment\n')
    git("commit", "-qam", "a number")
    assert "m.py changed in what runs" in wording.refusal(tmp_path, d, "T05", sec)


def _arbiter_feature(tmp: pathlib.Path) -> pathlib.Path:
    d = tmp / "specs" / "385-x"
    d.mkdir(parents=True)
    (d / "plan.md").write_text("# plan\n\n## T17 - x\n\n### T17 Decisions\n\n**D1** the rule.\n")
    (d / "plan-review.json").write_text(json.dumps({"feature": "385-x", "blocks": {"### T17 Decisions": {"sha256": "old", "verdict": "BLOCKED"}}}))
    (d / "arbiter.jsonl").write_text("")
    return d


def _owed(d: pathlib.Path) -> bool:
    return subprocess.run([str(REPO / "scripts/gates/l7r-gate.sh"), "plan", "owed", str(d)], capture_output=True, check=False).returncode != 0


def test_recording_the_arbiter_s_accept_makes_it_the_plan_s_verdict(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ha = _load("hm_arbiter")
    root = tmp_path
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    d = _arbiter_feature(root)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/385-x"}))
    ha.trip(root, TRIG, "round", "spec-fidelity|plan:385-x#T17", "round 3 of T17's plan review")
    ruling = root / "ruling.json"
    ruling.write_text(json.dumps({"ruling": "accept", "why": "converged, wording only", "what": "the plan stands"}))
    monkeypatch.chdir(root)
    assert ha.main(["ruled", TRIG, str(ruling), "--as", "round-arbiter"]) == 0
    assert not _owed(d), "the accept recorded the plan CLEAR in the same command"


def test_an_asked_plan_review_s_accept_makes_it_the_plan_s_verdict(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 409: 408's `ask:408-plan-round3` accept named no review; and an asked accept goes to the feature the ask names (443)."""
    ha = _load("hm_arbiter")
    root = tmp_path
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    d = _arbiter_feature(root)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/385-x"}))
    monkeypatch.chdir(root)
    ruling = root / "ruling.json"
    ruling.write_text(json.dumps({"ruling": "continue", "why": "one more round is owed", "what": "run it"}))
    assert ha.main(["ask", "385-plan-round3", "may the plan stand without a third round?", "plan"]) == 0
    assert ha.main(["ruled", "ask:385-plan-round3", str(ruling), "--as", "round-arbiter"]) == 0
    assert _owed(d), "a continue records nothing CLEAR"
    ruling.write_text(json.dumps({"ruling": "accept", "why": "converged, wording only", "what": "the plan stands"}))
    assert ha.main(["ask", "385-plan-round4", "may the plan stand now it is fixed?", "plan"]) == 0
    assert ha.main(["ruled", "ask:385-plan-round4", str(ruling), "--as", "round-arbiter"]) == 0
    assert not _owed(d), "the asked plan review's accept is the plan's verdict"
    (root / "specs" / "427-y").mkdir()
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/427-y"}))
    (d / "plan.md").write_text((d / "plan.md").read_text() + "\n## Late\n\nA block changed after the accept.\n")
    assert _owed(d)
    assert ha.main(["ask", "385-plan-round5", "may the plan stand?", "plan"]) == 0
    assert ha.main(["ruled", "ask:385-plan-round5", str(ruling), "--as", "round-arbiter"]) == 0
    assert not _owed(d), "the accept is the named feature's verdict, whatever feature.json names"


def test_make_plan_verdict_arbiter_runs_only_the_accept() -> None:
    params = {"LAND", "TICK", "F", "T", "ID", "NOTE", "TEST", "ENGINE", "WRITE", "ARBITER", "FILE", "AS", "BLOCKS", "TASK"}
    env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "MAKEOVERRIDES") and k not in params}
    dry = subprocess.run(["make", "-n", "-C", str(REPO), "plan-verdict", "F=385", f"ARBITER={TRIG}"], capture_output=True, text=True, check=False, env=env).stdout
    line = next(ln for ln in dry.splitlines() if "l7r-gate.sh" in ln and "plan" in ln)
    assert f'arbiter-accept "385" "{TRIG}"' in line and "--as" not in line
