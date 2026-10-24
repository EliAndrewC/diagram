"""`scripts/gates/plan_gate.py` and the tick refusal, proven to fire (feature 243).

A plan's decisions are reviewed before its tasks are ticked. Each case is a rule a later session could
break without noticing: a missing plan passing, a stale review counting, a BLOCKED review ticking, a
typed verdict overriding its own rulings, a record written without the reviewer's declaration, a push
reading the working tree instead of what lands, and a bare escape token honored.
"""

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

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("_plan_gate", REPO / "scripts/gates/plan_gate.py")
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
sys.modules["_plan_gate"] = gate
_spec.loader.exec_module(gate)
_tt = importlib.util.spec_from_file_location("tick_task_for_gate", script("tick-task.py"))
assert _tt and _tt.loader
tt = importlib.util.module_from_spec(_tt)
_tt.loader.exec_module(tt)


@pytest.fixture(autouse=True)
def _own_bundles(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each test writes its plan bundles under its own `tmp_path` (feature 385 T51): `decide_prompt` wrote the shared
    `/tmp/l7r-check/plan-375-x-T05`, and two tests on two workers raced on it - a red gate that passed alone."""
    sys.path.insert(0, str(REPO / "scripts" / "gates"))
    import plan_bundle  # noqa: PLC0415 - the module `plan_gate` imports by this name

    monkeypatch.setattr(plan_bundle, "OUT", tmp_path / "l7r-check")


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
    (d / "request.md").write_text("# the request\n\n> the GM's words\n", encoding="utf-8")  # a bundle needs it (405 T30, D2)
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
    out = gate.record(d, {"plan_sha256": hashlib.sha256(PLAN).hexdigest(), "decisions": [NARROW_BAD]}, "spec-fidelity", today="2026-09-13")
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
    (tmp_path / "dev").mkdir(parents=True)
    ok, message = gate.tick_permitted(d, tmp_path, None)
    assert not ok and "no current CLEAR review" in message and "make plan-verdict" in message
    ok, message = gate.tick_permitted(d, tmp_path, "x")
    assert not ok and "needs a REASON" in message
    ok, message = gate.tick_permitted(d, tmp_path, "a superseded plan nobody implements")
    assert ok and "BYPASSED" in message
    entries = list((tmp_path / "dev" / "bypass-log").rglob("*.json"))
    assert len(entries) == 1 and "a superseded plan" in entries[0].read_text()
    assert sorted(_log_rules(tmp_path)) == sorted(["plan-review-missing", "PLAN_REVIEW_OK-no-reason", "plan-review-ok"])
    gate.record(d, current([]), "spec-fidelity")
    assert gate.tick_permitted(d, tmp_path, None) == (True, "")


def test_make_tick_refuses_and_writes_nothing_until_the_plan_is_reviewed(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
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
    (d / "report.md").write_text("# report\n")  # the last tick closes the feature: its report first (feature 375)
    assert tt.main(["243", "T02", "built"]) == 0
    assert "BYPASSED" in capsys.readouterr().out


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.com", *args], check=True, capture_output=True, text=True).stdout.strip()


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


PLAN_375 = b"# plan\n\n**D1 - the gatehouse.** Each sheet draws its gatehoue at 12 ft, and every tub stands by a door.\n**D2 - the bath.** The bath is 10 x 8 ft.\n"


@pytest.mark.parametrize(
    "edit",
    [
        ((b"gatehoue", b"gatehouse", True)),  # a misspelling
        (b"12 ft, and", b"12 ft,\n and", True),  # a re-wrap
        (b"stands by a door.", b"stands by a door;", True),  # punctuation
        (b"12 ft", b"14 ft", False),  # a number
        (b"every tub", b"each tub", False),  # a quantifier
        (b"stands by", b"never stands by", False),  # a word added, and a negation
        (b"10 x 8 ft.\n", b"10 x 8 ft.\n**D3 - a new decision.** A well by the kitchen.\n", False),  # a new decision
        (b"the gatehouse.", b"the gateway.", False),  # a different word, not a misspelling
    ],
    ids=["misspelling", "re-wrap", "punctuation", "number", "quantifier", "negation-added", "new-decision", "other-word"],
)
def test_a_verdict_survives_a_typo_and_nothing_more(tmp_path: pathlib.Path, edit: tuple) -> None:
    """Feature 375 FR-005(b), plan D6: an edit that adds or changes no decision keeps the verdict; any other voids it."""
    old, new, keeps = edit
    _git_init(tmp_path)
    d = feature(tmp_path, plan=PLAN_375)
    gate.record(d, current([WITHIN], plan=PLAN_375), "spec-fidelity")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "the reviewed plan")  # amendment 11 (D63): the earlier text is read from git
    assert "plan_text" not in json.loads((d / "plan-review.json").read_text()), "no copy of the plan in its verdict (FR-045)"
    assert gate.owed(d) is None
    (d / "plan.md").write_bytes(PLAN_375.replace(old, new))
    assert (gate.owed(d) is None) is keeps, f"{old!r} -> {new!r}"


def test_typo_scale_rules() -> None:
    assert gate.typo_only("a b c d", "a b c d")
    assert not gate.typo_only("teh cat sat on teh mat wiht ahat", "the cat sat on the mat with a hat")
    assert gate.typo_only("teh rule", "the rule") and not gate.typo_only("two gates", "ten gates")
    assert not gate.typo_only("wing 2", "wing 3") and not gate.typo_only("the dog", "the cat")
    assert gate._distance("ab", "ba") == 1 and gate._distance("kitten", "sitting") == 3
    review = {"plan_sha256": "x", "plan_text": "", "decisions": [], "verdict": "CLEAR"}
    assert gate.judge(b"anything", json.dumps(review))[0] == "plan-review-stale", "no text recorded: the hash decides, as before"


PLAN_TASKS = b"# plan\n\n**D1 - a decision.** Each tub by a door.\n\n## T05 the bath (amendment 1)\n\n- the bath 10 x 8 ft\n\n## T06 the wells\n\n- a well by the kitchen\n"


def _git_init(root: pathlib.Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)


def test_a_task_section_carries_its_own_decision_verdict(tmp_path: pathlib.Path) -> None:
    """Feature 375 FR-003(a), plan D3: decide first. A task's plan section is ruled on alone; a section with its own current
    verdict does not stale the plan-stage verdict, and a check for that task waits for it."""
    text = PLAN_TASKS.decode()
    secs = gate.task_sections(text)
    assert set(secs) == {"T05", "T06"} and secs["T05"].startswith("## T05") and "a well" not in secs["T05"]
    d = feature(tmp_path, plan=PLAN_TASKS)
    gate.record(d, current([WITHIN], plan=PLAN_TASKS), "spec-fidelity")
    sha = hashlib.sha256(secs["T05"].encode()).hexdigest()
    with pytest.raises(PermissionError):
        gate.record_task(d, "T05", {"section_sha256": sha, "decisions": []}, "main")
    with pytest.raises(ValueError, match="no section naming T09"):
        gate.record_task(d, "T09", {"section_sha256": sha, "decisions": []}, "spec-fidelity")
    with pytest.raises(ValueError, match="changed while"):
        gate.record_task(d, "T05", {"section_sha256": "x", "decisions": []}, "spec-fidelity")
    with pytest.raises(ValueError, match="must be a list"):
        gate.record_task(d, "T05", {"section_sha256": sha}, "spec-fidelity")
    assert gate.record_task(d, "T05", {"section_sha256": sha, "decisions": [WITHIN]}, "spec-fidelity")["verdict"] == "CLEAR"
    # ...the section's digest under the plan-stage key, as the reviewer's brief names it, is taken too (feature 374 wave 153: two
    # task reviews were refused for writing `plan_sha256`, which their MODE 4 JSON shape calls it)
    assert gate.record_task(d, "T05", {"plan_sha256": sha, "decisions": [WITHIN]}, "spec-fidelity")["verdict"] == "CLEAR"
    review = json.loads((d / "plan-review.json").read_text())
    assert gate.task_current(review, text, "T05") and not gate.task_current(review, text, "T06")
    grown = text.replace("- the bath 10 x 8 ft\n", "- the bath 10 x 8 ft\n- a second bath for guests\n")
    (d / "plan.md").write_text(grown)
    assert gate.owed(d)[0] == "plan-review-stale", "a new decision in a section its verdict no longer matches"
    gate.record_task(d, "T05", {"section_sha256": hashlib.sha256(gate.task_sections(grown)["T05"].encode()).hexdigest(), "decisions": [WITHIN]}, "spec-fidelity")
    assert gate.owed(d) is None, "the section's own verdict covers it; the plan-stage verdict stands"
    gate.record(d, current([WITHIN], plan=grown.encode()), "spec-fidelity")
    assert "T05" in json.loads((d / "plan-review.json").read_text())["tasks"], "a plan review keeps the task verdicts"
    assert gate.task_current({"tasks": {"T05": {"verdict": "BLOCKED"}}}, grown, "T05") is False


def test_a_check_waits_for_its_task_s_decisions(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "clone"
    _git_init(root)
    d = feature(root, plan=PLAN_TASKS, name="375-x")
    (d / "tasks.md").write_text("- [x] T04 done\n- [ ] T05 the bath\n- [ ] T07 docs\n")
    assert gate.decision_refusal(root) == "" and gate.active_task(root) == (None, ""), "no active feature: not this guard's"
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    assert gate.active_task(root) == (d, "T05")
    assert "T05: its plan section carries no current CLEAR decision verdict" in gate.decision_refusal(root)
    gate.record(d, current([WITHIN], plan=PLAN_TASKS), "spec-fidelity")
    assert gate.decision_refusal(root) == "", "a current CLEAR plan review read the section: it covers it"
    (d / "plan.md").write_bytes(PLAN_TASKS.replace(b"10 x 8 ft", b"12 x 9 ft"))
    assert "T05: its plan section" in gate.decision_refusal(root), "the section changed since: its own preflight"
    (d / "plan.md").write_bytes(PLAN_TASKS)
    (d / "plan-review.json").unlink()
    sha = hashlib.sha256(gate.task_sections(PLAN_TASKS.decode())["T05"].encode()).hexdigest()
    gate.record_task(d, "T05", {"section_sha256": sha, "decisions": []}, "spec-fidelity")
    assert gate.decision_refusal(root) == ""
    common = root / ".git"
    (common / "active-task").write_text(json.dumps({"feature": "375-x", "task": "T07"}))
    assert gate.active_task(root) == (d, "T07")
    assert "no section for this task" in gate.decision_refusal(root) and "plan-review" in gate.decision_refusal(root)
    gate.record(d, current([WITHIN], plan=PLAN_TASKS), "spec-fidelity")
    assert gate.decision_refusal(root) == "", "no section: the plan-stage verdict decides"
    prompt = gate.decide_prompt(d, "T05")
    assert "MODE 4: PLAN REVIEW of one task's section" in prompt and "MANIFEST.md" in prompt
    manifest = pathlib.Path(prompt.split("read ", 1)[1].split(" and the files", 1)[0])
    assert "TASK=T05" in manifest.read_text(), "the bundle says how to record it (amendment 11, D64)"
    (root / ".specify" / "feature.json").write_text("not json")
    assert gate.active_task(root) == (None, "")


def test_the_decide_commands(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "clone"
    _git_init(root)
    d = feature(root, plan=PLAN_TASKS, name="375-x")
    (d / "tasks.md").write_text("- [ ] T05 the bath\n- [ ] T06 the wells\n")  # T06 open, so its mark is honored (385 T54, D71)
    monkeypatch.chdir(root)
    assert gate.main(["decide", "375", "T05"]) == 0 and "MODE 4" in capsys.readouterr().out
    assert gate.main(["section-sha", "375", "T05"]) == 0
    sha = capsys.readouterr().out.strip()
    assert sha == hashlib.sha256(gate.task_sections(PLAN_TASKS.decode())["T05"].encode()).hexdigest()
    assert gate.main(["decide", "375", "T99"]) == 2
    assert gate.main(["task-start", "375", "T06"]) == 0 and json.loads((root / ".git" / "active-task").read_text())["task"] == "T06"
    assert json.loads((root / ".git" / "task-starts.jsonl").read_text().splitlines()[-1])["task"] == "T06", "feature 385 D10: each start logged"
    assert gate.main(["task-start", "999", "T06"]) == 2
    src = tmp_path / "v.json"
    src.write_text(json.dumps({"section_sha256": sha, "decisions": []}))
    assert gate.main(["record-task", "375", "T05", str(src), "--as", "spec-fidelity"]) == 0
    assert gate.main(["record-task", "375", "T05", str(src), "--as", "main"]) == 2
    assert gate.main(["record-task", "999", "T05", str(src), "--as", "spec-fidelity"]) == 2
    src.write_text("{}")
    assert gate.main(["record-task", "375", "T05", str(src), "--as", "spec-fidelity"]) == 1
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    assert gate.main(["decided", str(root)]) == 1 and "T06: its plan section" in capsys.readouterr().out
    assert d.is_dir()


def test_a_mark_naming_a_ticked_task_falls_back_to_the_first_open_task(tmp_path: pathlib.Path) -> None:
    """Feature 385 T54 (D71): `make task-start`'s mark wins while its task is open; once its task is ticked, the active task is the
    first open one, so a trigger never owes a ticked task its part B."""
    root = tmp_path / "clone"
    _git_init(root)
    d = feature(root, plan=PLAN_TASKS, name="375-x")
    (d / "tasks.md").write_text("- [x] T04 done\n- [ ] T05 the bath\n- [ ] T07 docs\n")
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    (root / ".git" / "active-task").write_text(json.dumps({"feature": "375-x", "task": "T07"}))
    assert gate.active_task(root) == (d, "T07"), "an open marked task wins"
    (root / ".git" / "active-task").write_text(json.dumps({"feature": "375-x", "task": "T04"}))
    assert gate.active_task(root) == (d, "T05"), "a ticked marked task falls back to the first open one"
    (root / ".git" / "active-task").write_text(json.dumps({"feature": "375-x", "task": "T99"}))
    assert gate.active_task(root) == (d, "T05"), "a task the list does not hold, too"


def test_a_task_s_own_heading_wins_its_section_over_a_mention() -> None:
    """Feature 385 T56 (D75): the umbrella "T04 to T10 - T48, T47's patch" took T10's, T47's and T48's preflights; a heading that
    begins with the id is that task's own section, and one that only names it is the fallback."""
    plan = "# plan\n\n## T04 to T10 - T48, T47's patch\n\numbrella\n\n## T10 - the split\n\n### T10 Decisions\n\nD74\n\n## T11 - the close\n"
    sec = gate.task_sections(plan)
    assert sec["T10"].startswith("## T10 - the split") and "D74" in sec["T10"] and "umbrella" not in sec["T10"]
    assert sec["T04"].startswith("## T04 to T10"), "T04 has no heading of its own: the mention stands"
    assert sec["T48"].startswith("## T04 to T10") and sec["T11"].startswith("## T11")


def test_an_archived_block_a_typo_from_its_reviewed_text_is_not_owed() -> None:
    """Feature 385 T65 (plan D84): T49's two blocks, renumbered by a typo after their review, refused T59's tick once archived."""
    body = "### T49 Decisions\n\n**D70 - the mark falls back.** When the mark names a ticked task.\n"
    review = {"blocks": {"preamble": {"sha256": gate.block_digest("# Plan\n"), "verdict": "CLEAR"}, "### T49 Decisions": {"sha256": gate.block_digest(body), "verdict": "CLEAR", "text": body}}}
    typo = body.replace("When the mark", "when the mark")
    changed = body.replace("falls back", "is refused")
    assert gate.block_status(review, "# Plan\n", set(), done=typo) == ([], [])
    assert gate.block_status(review, "# Plan\n", set(), done=changed)[0] == ["(removed) ### T49 Decisions"]
    assert gate.block_status(review, "# Plan\n", set(), done="")[0] == ["(removed) ### T49 Decisions"]


def test_ids_appended_to_the_lands_open_line_owe_no_review_and_a_reorder_does(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 385 T74 (plan D93): two reviews in hour 24 of ids `make task-add` had added. Run on task-add's own output."""
    body = "## Landing\n\n**Lands open**: T02, T03\n\nEach task lands when it closes.\n"
    review = {"blocks": {"preamble": {"sha256": gate.block_digest("# Plan\n\n"), "verdict": "CLEAR"}, "## Landing": {"sha256": gate.block_digest(body), "verdict": "CLEAR", "text": body}}}
    appended = body.replace("T02, T03", "T02, T03, T09")  # what task-add wrote until feature 405 T32 retired the line
    added = "# Plan\n\n" + appended
    assert gate.block_status(review, added, set())[0] == []
    reordered = "# Plan\n\n" + body.replace("T02, T03", "T03, T02")
    assert gate.block_status(review, reordered, set())[0] == ["## Landing"]
    dropped = "# Plan\n\n" + body.replace("T02, T03", "T02, T09")
    assert gate.block_status(review, dropped, set())[0] == ["## Landing"]
    more = "# Plan\n\n" + appended.replace("lands when it closes", "lands at once")
    assert gate.block_status(review, more, set())[0] == ["## Landing"], "anything else changed is owed as now"


def test_a_part_b_that_decides_nothing_owes_no_review_and_one_that_decides_does() -> None:
    """Feature 385 T75 (plan D94): T10's, T65's and T72's part Bs each took a review round and each decided nothing."""
    head = "### T05 part B (2026-10-19T00:30Z)"

    def pb(four: str, five: str, extra: str = "") -> str:
        return f"{head}\n\n1. **What is refusing?** Nothing.\n4. **Moving something earlier?** {four}\n5. **Tuning or changing?** {five}\n{extra}"

    plan = "# Plan\n\n**D10 - a rule.** x\n\n"
    review = {"blocks": {"preamble": {"sha256": gate.block_digest(plan), "verdict": "CLEAR"}}}
    quiet = pb("No.", "Neither - landing what was checked.", "6. **Test.** D10 holds.\n")
    assert gate.block_status(review, plan + quiet, set())[0] == []
    for loud in (pb("No.", "Changing: the rule widens."), pb("Yes - the wells move.", "Neither."), pb("No.", "Neither.", "7. **Next.** D11 - a new rule.\n")):
        assert gate.block_status(review, plan + loud, set())[0] == [head], loud


def test_a_quiet_part_b_leaves_its_task_s_section_reviewed() -> None:
    """Feature 385 T80 (plan D99): T78's part B moved its section's digest, and three reviewed blocks fell back to block reviews."""
    sec = "## T05 - x\n\n### T05 Approach (checklist part A)\n\n1. **G.** y\n\n### T05 Decisions\n\n**D10 - a rule.** z\n\n"
    plan = "# Plan\n\n" + sec
    review = {"tasks": {"T05": {"verdict": "CLEAR", "section_sha256": gate.digest(sec.encode()), "section_text": sec}}}
    quiet = "### T05 part B (2026-10-19T01:30Z)\n\n4. **Moving?** No.\n5. **Tuning or changing?** Neither.\n\n"
    loud = "### T05 part B (2026-10-19T01:30Z)\n\n4. **Moving?** No.\n5. **Tuning or changing?** Changing: wider.\n\n"
    for part_b, current in ((quiet, True), (loud, False)):
        text = plan.replace("### T05 Decisions", part_b + "### T05 Decisions")
        assert gate.task_current(review, text, "T05") is current, part_b


def test_a_pointer_repointed_to_a_recorded_split_leaves_the_section_reviewed() -> None:
    """The round arbiter's fix on hour:385-approach-checklist@28: T31 said "row 841 is T32" after the review moved that row to
    T95 (found working T31), and correcting the pointer owed T31 a third review."""
    sec = "## T31 - x\n\n### T31 Decisions\n\n**D113 - a rule.** Row 841 is its own task, T32 (FR-015).\n\n"
    review = {"tasks": {"T31": {"verdict": "CLEAR", "section_sha256": gate.digest(sec.encode()), "section_text": sec}}}
    split = "## T95 - the leg (found working T31, 2026-10-19; ranking row 841)\n\n**D117 - y.** z\n\n"
    other = "## T95 - the leg (ranking row 841)\n\n**D117 - y.** z\n\n"
    moved = sec.replace("T32", "T95")
    assert gate.task_current(review, "# Plan\n\n" + moved + split, "T31")
    assert not gate.task_current(review, "# Plan\n\n" + moved + other, "T31"), "no recorded split: owed"
    assert not gate.task_current(review, "# Plan\n\n" + sec.replace("T32", "T96") + split, "T31"), "another id: owed"
    loud = moved.replace("its own task", "a later task")
    assert not gate.task_current(review, "# Plan\n\n" + loud + split, "T31"), "a repoint with another change: owed"


def test_a_repoint_to_a_split_already_archived_leaves_the_section_reviewed(tmp_path: pathlib.Path) -> None:
    """The same fix, once T95 was ticked: its "found working T31" heading had moved to plan-done.md, and T31 was owed again."""
    sec = "## T31 - x\n\nRow 841 is T32.\n\n"
    review = {"tasks": {"T31": {"verdict": "CLEAR", "section_sha256": gate.digest(sec.encode()), "section_text": sec}}}
    (tmp_path / "plan.md").write_text("# Plan\n\n" + sec.replace("T32", "T95"))
    (tmp_path / "plan-done.md").write_text("## T95 - the leg (found working T31)\n\nz\n")
    history = gate.History(tmp_path / "plan.md")
    assert gate.task_current(review, (tmp_path / "plan.md").read_text(), "T31", history)
    (tmp_path / "plan-done.md").write_text("## T95 - the leg\n\nz\n")
    assert not gate.task_current(review, (tmp_path / "plan.md").read_text(), "T31", history), "no split recorded: owed"


def test_an_archive_line_inside_a_task_s_section_leaves_it_reviewed() -> None:
    """Feature 385 T82 (plan D102): ticking T78 and T80 left their archive line inside T79's section, and T79 was owed again."""
    sec = "## T05 - x\n\n### T05 Decisions\n\n**D10 - a rule.** z\n\n"
    review = {"tasks": {"T05": {"verdict": "CLEAR", "section_sha256": gate.digest(sec.encode()), "section_text": sec}}}
    line = "<!-- plan-archive: T06 to T07 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->\n"
    assert gate.task_current(review, "# Plan\n\n" + sec + line, "T05")
    assert not gate.task_current(review, "# Plan\n\n" + sec + "A new decision.\n", "T05")


def test_a_verdict_s_free_text_is_written_in_the_house_style_its_keys_as_given() -> None:
    """Feature 385 T88 (plan D109): T83's first gate went red on a reviewer's British word copied into plan-review.json."""
    brit = "gr" + "ey"
    got = gate.house_style([{"id": f"D1-{brit}", "class": "within", "why": f"a {brit} band, <q>a {brit} quoted</q>"}])
    assert got == [{"id": f"D1-{brit}", "class": "within", "why": f"a gray band, <q>a {brit} quoted</q>"}]
    assert gate.house_style(None) is None


def test_a_wording_only_section_owes_no_review_but_a_decision_or_a_deciding_part_b_does() -> None:
    """Feature 385 T118 (D137; amendment 10): T31, T103, T105 and T110 reworded only, and each paid a plan review."""
    sec = "## T05 - x\n\n### T05 Approach (checklist part A)\n\n1. **G.** y\n\n### T05 Decisions\n\n**Wording only.** a claim relabeled.\n\n"
    plan = "# Plan\n\n" + sec
    review = {"blocks": {"preamble": {"sha256": gate.block_digest("# Plan\n\n"), "verdict": "CLEAR"}}}
    assert gate.wording.wording_only(sec) and gate.block_status(review, plan, set())[0] == []
    decided = plan.replace("a claim relabeled.\n", "a claim relabeled.\n\n**D10 - a rule.** z\n")
    assert not gate.wording.wording_only(decided) and gate.block_status(review, decided, set())[0] != []
    loud = "### T05 part B (2026-10-19T01:30Z)\n\n4. **Moving?** No.\n5. **Tuning or changing?** Changing: wider.\n\n"
    assert gate.block_status(review, plan + loud, set())[0] == ["### T05 part B (2026-10-19T01:30Z)"]
    assert not gate.wording.wording_only("## T05 - x\n\n**Wording only.** not under a Decisions heading\n")


def test_a_wording_only_tick_is_refused_when_a_commit_changed_what_runs(tmp_path: pathlib.Path) -> None:
    """Feature 385 T118 (D138): the declaration is checked against the task's own commits since its `make task-start`."""
    w = gate.wording

    def git(*a: str, when: str | None = None) -> None:
        env = {**os.environ, **({"GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when} if when else {})}
        subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True, env=env)

    git("init", "-q", "-b", "main")
    (tmp_path / "m.py").write_text("X = 1\n")
    git("add", "-A")
    git("commit", "-qm", "base", when="2026-01-01T00:00:00Z")
    sec = "## T05 - x\n\n### T05 Decisions\n\n**Wording only.** a comment.\n"
    d = tmp_path / "specs" / "385-x"
    assert "no `make task-start`" in w.refusal(tmp_path, d, "T05", sec)
    (tmp_path / ".git" / "task-starts.jsonl").write_text(json.dumps({"feature": "385-x", "task": "T05", "utc": "2026-01-02T00:00:00Z"}) + "\n")
    (tmp_path / "m.py").write_text('X = 1\n"""Research: x - GUESS"""  # a comment\n')
    glossary = tmp_path / "l7r/diagram/interactive/assets/glossary"
    glossary.mkdir(parents=True)
    (glossary / "1-Word.json").write_text("{}\n")
    git("add", "-A")
    git("commit", "-qm", "words")
    assert w.refusal(tmp_path, d, "T05", sec) == "", "a claim, a comment and a glossary entry are wording"
    assert w.refusal(tmp_path, d, "T05", sec.replace("**Wording only.**", "**D10 - a rule.**")) == "", "not declared: not checked"
    (tmp_path / "m.py").write_text('X = 2\n"""Research: x - GUESS"""  # a comment\n')
    git("commit", "-qam", "a number")
    assert "m.py changed in what runs" in w.refusal(tmp_path, d, "T05", sec)


def test_the_decide_guard_reads_a_block_as_plan_delta_does() -> None:
    """405 T81 (D57): a blank line moved under a CLEAR block (another task's blocks appended below it) left plan-delta owing
    nothing but the decide guard's exact digest refusing the active task's checks. A typo-scale change from the reviewed
    text passes both; a real change passes neither."""
    reviewed = "### T77 Decisions\n\n**D55 - carries filed.** As written.\n"
    review = {"blocks": {"### T77 Decisions": {"verdict": "CLEAR", "sha256": gate.block_digest(reviewed), "text": reviewed}}}
    assert gate._section_clear(review, reviewed)
    assert gate._section_clear(review, reviewed + "\n"), "a blank line moved: a typo"
    assert not gate._section_clear(review, reviewed.replace("As written.", "A different decision entirely, three new words.")), "a real change"


def test_every_block_a_task_s_own_headings_open_is_its_section() -> None:
    """The GM 2026-10-24 (405 T26): T26's five `### T26 ...` blocks stood under no `## T26` heading, and only the first - its
    part A - was bundled for review; its re-answered Approach and its Decisions (D131) reached no reviewer. Every own block is
    kept, in plan order, and a block nested in one already kept is not counted twice."""
    text = (
        "# plan\n\n## T24, T26 - an umbrella\n\n### T26 Approach (checklist part A)\n\n1. a\n\n### T26 Decisions\n\n- **D1** x\n\n"
        "### T26 Approach (re-answered 2026-10-24T13:22Z)\n\n1. b\n\n### T26 Decisions (2026-10-24)\n\n- **D131** y\n\n"
        "## T07 - the knot\n\n### T07 Approach (checklist part A)\n\n1. c\n\n### T07 Decisions\n\n- **D126** z\n\n## T08 next\n"
    )
    secs = gate.task_sections(text)
    t26 = secs["T26"]
    assert "part A" in t26 and "**D1**" in t26 and "re-answered" in t26 and "**D131**" in t26, "every own block"
    assert t26.index("part A") < t26.index("D131") and "an umbrella" not in t26 and "T07" not in t26
    assert secs["T07"].startswith("## T07") and secs["T07"].count("### T07 Approach") == 1, "a nested block counted once"


def test_a_clear_task_section_records_its_blocks_reviewed(tmp_path: pathlib.Path) -> None:
    """The GM 2026-10-24 (405 T26): `make decide`'s CLEAR on a task's section also records each block inside it, so the landing
    no longer owes the same text a second, block review (`make plan-delta`); a block outside it, and a verdict not CLEAR, record
    nothing."""
    d = feature(tmp_path, plan=PLAN_TASKS)
    grown = PLAN_TASKS.decode().replace("- the bath 10 x 8 ft\n", "- the bath 10 x 8 ft\n- a second bath\n")
    (d / "plan.md").write_text(grown)
    sha = hashlib.sha256(gate.task_sections(grown)["T05"].encode()).hexdigest()
    narrowing = {**WITHIN, "class": "narrowing", "ruling": "NOT LEGITIMATE"}
    gate.record_task(d, "T05", {"section_sha256": sha, "decisions": [narrowing]}, "spec-fidelity")
    assert not json.loads((d / "plan-review.json").read_text()).get("blocks"), "a verdict not CLEAR records no block"
    gate.record_task(d, "T05", {"section_sha256": sha, "decisions": [WITHIN]}, "spec-fidelity")
    recorded = json.loads((d / "plan-review.json").read_text())["blocks"]
    assert set(recorded) == {k for k, _b, _a in gate.blocks(grown) if "T05" in k}, "the section's blocks, and no other"
    assert all(v["verdict"] == "CLEAR" for v in recorded.values())
