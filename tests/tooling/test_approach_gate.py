"""`scripts/gates/approach_gate.py` - a task's Approach answered before its tick, and again after a trigger (feature 385 T02,
plan D8 and D9). Each refusal and each trigger's floor, on fixture plans; the tick, the arbiter's ruling, the cohort and the
plan-delta re-review each call it."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

from tests._scripts import script


def _load(name: str, as_: str):  # noqa: ANN202 - a module loaded by path
    path = script(name)
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(as_, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[as_] = mod
    spec.loader.exec_module(mod)
    return mod


ag = _load("approach_gate", "approach_gate")
tt = _load("tick-task.py", "_tick_task_approach")
pg = _load("plan_gate", "_plan_gate_approach")

CHECKLIST = """# Checklist

## A. At task start

1. **The goal.** x
2. **The constraints.** y
3. **Where from.** z

## B. When the work resists

1. **What refuses.** a
2. **Again.** b

## C. Habits

1. **Edit once.** c
"""
PLAN = """# Plan


## T01 - the first

### T01 Approach (checklist part A)

1. **The goal.** a lane.
2. **The constraints.** the law.
3. **Where from.** R.

### T01 Decisions

**D1 - the lane.** It is laid after the houses.

## T02 - the second

### T02 Approach (checklist part A)

1. **The goal.** a well.
3. **Where from.** O.

### T02 Decisions

**D2 - the well.** By the lane.
"""
TASKS = "- [ ] T01 the first\n      research: rendering\n      verify: x\n- [ ] T02 the second\n      research: rendering\n      verify: y\n- [ ] T03 the third\n      research: rendering\n      verify: z\n"


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True, capture_output=True, text=True).stdout


def feature(tmp: pathlib.Path, plan: str = PLAN, git: bool = False) -> tuple[pathlib.Path, pathlib.Path]:
    root = tmp / "repo"
    d = root / "specs" / "999-x"
    d.mkdir(parents=True)
    if git:
        _git(root, "init", "-q")
    (root / "docs").mkdir()
    (root / "docs" / "approach-checklist.md").write_text(CHECKLIST)  # every feature's checklist (feature 385 T11, D157)
    (d / "plan.md").write_text(plan)
    (d / "tasks.md").write_text(TASKS)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/999-x"}))
    return root, d


def test_the_checklist_s_items_are_read_by_part() -> None:
    assert ag.part_items(CHECKLIST, "A") == [1, 2, 3]
    assert ag.part_items(CHECKLIST, "B") == [1, 2]
    assert ag.part_items(CHECKLIST, "D") == []
    assert ag.parse_utc("### T01 part B (2026-10-17T21:40Z)") == ag.parse_utc("2026-10-17T21:40:00Z")
    assert ag.parse_utc("no stamp") is None


def test_a_task_is_ticked_only_with_every_part_a_item_answered(tmp_path: pathlib.Path) -> None:
    root, d = feature(tmp_path)
    assert ag.refusal(d, root, "T01") is None
    assert "item(s) 2 unanswered" in str(ag.refusal(d, root, "T02"))
    why = str(ag.refusal(d, root, "T03"))
    assert "no `### T03 Approach` block" in why and "(1, 2, 3)" in why
    # feature 385 T11 (D157): one checklist for every plan, with no line to name it - and only a tree without it is not asked
    (d / "plan.md").write_text(PLAN + "\n**Approach checklist**: `specs/999-x/thin.md`\n")
    assert "no `### T03 Approach` block" in str(ag.refusal(d, root, "T03")), "a line naming another file no longer counts"
    (root / "docs" / "approach-checklist.md").unlink()
    assert ag.refusal(d, root, "T03") is None, "a tree without the checklist is not asked"


def test_make_tick_asks_the_approach_gate(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    root, d = feature(tmp_path)
    plan = (d / "plan.md").read_bytes()
    (d / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan).hexdigest(), "decisions": [], "verdict": "CLEAR"}))
    monkeypatch.setattr(tt, "repo_root", lambda start=None: root)
    assert tt.main(["999", "T02", "x"]) == 2
    assert "item(s) 2 unanswered" in capsys.readouterr().err
    assert tt.main(["999", "T01", "x"]) == 0


def test_a_trigger_owes_a_block_stamped_after_it(tmp_path: pathlib.Path) -> None:
    root, d = feature(tmp_path, git=True)
    msg = ag.owe(root, "999-x", "T01", "hour:999-x@2", "B", now="2026-10-17T21:40:00Z")
    assert "part B - when the work resists" in msg and "`### T01 part B (2026-10-17T21:40Z)`" in msg
    ag.owe(root, "999-x", "T01", "hour:999-x@2", "B", now="2026-10-17T22:00:00Z")
    assert len(ag.owed_entries(root)) == 1, "a trigger is owed once"
    assert "no block stamped after it" in str(ag.refusal(d, root, "T01"))
    early = PLAN + "\n### T01 part B (2026-10-17T21:00Z)\n\n1. x\n2. y\n"
    (d / "plan.md").write_text(early)
    assert "no block stamped after it" in str(ag.refusal(d, root, "T01")), "a block from before the trigger answers nothing"
    (d / "plan.md").write_text(PLAN + "\n### T01 part B (2026-10-17T21:45Z)\n\n1. the lane law\n")
    assert "item(s) 2 unanswered" in str(ag.refusal(d, root, "T01"))
    (d / "plan.md").write_text(PLAN + "\n### T01 part B (2026-10-17T21:45Z)\n\n1. the lane law\n2. R, checked\n")
    assert ag.refusal(d, root, "T01") is None
    assert ag.refusal(d, root, "T02") is not None and "D9" not in str(ag.refusal(d, root, "T02")), "another task owes nothing"


def test_an_hour_or_red_gate_ruling_owes_the_active_task_part_b(tmp_path: pathlib.Path) -> None:
    root, d = feature(tmp_path, git=True)
    assert ag.ruled(root, "ask:something", now="2026-10-17T21:40:00Z") is None, "an ask's ruling owes nothing"
    assert ag.ruled(root, "hour:999-x@3", now="2026-10-17T21:40:00Z") is not None
    assert ag.ruled(root, "red-gate@2", now="2026-10-17T21:41:00Z") is not None
    assert [r["task"] for r in ag.owed_entries(root)] == ["T01", "T01"], "the first open task of the active feature"
    (d / "plan.md").write_text(PLAN.replace("T01", "T09"))  # feature 385 T11 (D157): a trigger asks every plan, no opt-in line
    assert ag.ruled(root, "hour:999-x@4") is not None, "D9's part B reaches a plan that names no checklist"
    (root / "docs" / "approach-checklist.md").unlink()
    assert ag.ruled(root, "hour:999-x@5") is None, "a tree without the checklist is not asked"


def _rec(utc: str, commit: str, verdicts: dict[int, str], households=None) -> dict:  # noqa: ANN001
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
    # 2 passed at m1; 3 failed at its newest baseline (m2); 4 failed at m1 (the later pass is not earlier); 5 passed only off main
    assert ag.newly_failing(now, earlier, main) == [2]
    # feature 385 T04: a roll over an uncommitted engine diff is no baseline - seed 3's newest m2 record is dirty, so m1's pass is
    dirty = {**_rec("20261017T1500Z", "m2", {3: "fail"}), "engine_diff": "abc"}
    assert ag.newly_failing(now, [*earlier, dirty], main) == [2], "the dirty fail would have hidden nothing here"
    assert ag.newly_failing(now, [_rec("20261017T1000Z", "m1", {3: "pass"}), {**_rec("20261017T1500Z", "m1", {3: "fail"}), "engine_diff": "abc"}], main) == [3]


def test_a_cohort_with_a_newly_failing_seed_owes_part_b(tmp_path: pathlib.Path) -> None:
    root, _d = feature(tmp_path, git=True)
    (root / "f").write_text("x")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    _git(root, "branch", "-M", "main")
    head = _git(root, "rev-parse", "HEAD").strip()
    logs = root / "dev" / "cohort-log"
    logs.mkdir(parents=True)
    assert ag.cohort(root) is None, "no record, nothing owed"
    (logs / "20261017T1000Z-a.json").write_text(json.dumps(_rec("20261017T1000Z", head, {7: "pass", 8: "fail"})))
    (logs / "20261017T2000Z-a.json").write_text(json.dumps(_rec("20261017T2000Z", "feedface", {7: "fail", 8: "fail"})))
    msg = str(ag.cohort(root, now="2026-10-17T20:01:00Z"))
    assert "seed(s) 7 newly failing" in msg and "part B" in msg
    (logs / "20261017T2100Z-a.json").write_text(json.dumps(_rec("20261017T2100Z", "feedface", {8: "fail"})))
    assert ag.cohort(root) is None, "a seed failing at the baseline too, rolled as diagnosis, fires nothing"


def test_a_decisions_block_re_reviewed_after_a_clear_owes_the_approach_again(tmp_path: pathlib.Path) -> None:
    root, d = feature(tmp_path, git=True)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "plan")

    def review() -> dict:
        text = (d / "plan.md").read_text()
        sha = {k: pg.block_digest(b) for k, b, _at in pg.blocks(text)}["### T01 Decisions"]
        return pg.record_blocks(d, {"blocks": {"### T01 Decisions": sha}, "decisions": []}, "spec-fidelity", today="2026-10-17")

    assert "approach_owed" not in review(), "a first review owes nothing"
    (d / "plan.md").write_text(PLAN.replace("It is laid after", "It is layd after"))
    _git(root, "commit", "-qam", "typo")
    assert "approach_owed" not in review(), "a typo owes nothing"
    (d / "plan.md").write_text(PLAN.replace("It is laid after the houses.", "It is laid first, then the houses beside it."))
    _git(root, "commit", "-qam", "re-decided")
    got = review()
    assert len(got["approach_owed"]) == 1 and "re-answered" in got["approach_owed"][0]
    assert "no block stamped after it" in str(ag.refusal(d, root, "T01"))
    assert pg.redecided_tasks(d / "plan.md", {"## Other": {"verdict": "CLEAR", "sha256": "x"}}, {"## Other": "y"}) == []


def test_the_command_line(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    root, _d = feature(tmp_path, git=True)
    monkeypatch.chdir(root)
    assert ag.main(["owed", "999", "T02"]) == 1 and "unanswered" in capsys.readouterr().out
    assert ag.main(["owed", "999", "T01"]) == 0
    assert ag.main(["ruled", "hour:999-x@9"]) == 0 and "approach owed" in capsys.readouterr().out
    assert ag.main(["cohort"]) == 0
    assert ag.main(["bogus"]) == 2


def test_a_re_decide_reviewed_with_its_re_answered_approach_owes_nothing_more(tmp_path: pathlib.Path) -> None:
    """Feature 385 T03: the re-answered block reviewed in the same round as the re-decide is the fresh answer D9 asks for."""
    root, d = feature(tmp_path, git=True)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "plan")

    def review(keys: list[str]) -> dict:
        text = (d / "plan.md").read_text()
        digests = {k: pg.block_digest(b) for k, b, _at in pg.blocks(text)}
        return pg.record_blocks(d, {"blocks": {k: digests[k] for k in keys}, "decisions": []}, "spec-fidelity", today="2026-10-17")

    review(["### T01 Decisions"])
    new = PLAN.replace("It is laid after the houses.", "It is laid first, then the houses beside it.")
    new = new.replace("## T02 - the second", "### T01 Approach (re-answered 2026-10-17T22:10Z)\n\n1. a\n2. b\n3. c\n\n## T02 - the second")
    (d / "plan.md").write_text(new)
    _git(root, "commit", "-qam", "re-decided with its answer")
    got = review(["### T01 Decisions", "### T01 Approach (re-answered 2026-10-17T22:10Z)"])
    assert "approach_owed" not in got


def test_the_heading_owe_asks_for_passes_at_a_trigger_with_seconds(tmp_path: pathlib.Path) -> None:
    """Feature 385 T27 (plan D49): `owe` prints the heading to the minute, and a trigger at 10:25:14 refused T05's
    `### T05 part B (2026-10-18T10:25Z)` - the very heading it had asked for - as stamped before it."""
    root, d = feature(tmp_path, git=True)
    msg = ag.owe(root, "999-x", "T01", "hour:999-x@12", "B", now="2026-10-18T10:25:14Z")
    head = msg.split("`")[1]
    assert head == "### T01 part B (2026-10-18T10:25Z)"
    (d / "plan.md").write_text(PLAN + f"\n{head}\n\n1. the lane law\n2. R, checked\n")
    assert ag.refusal(d, root, "T01") is None, "the heading it asked for answers it"
    (d / "plan.md").write_text(PLAN + "\n### T01 part B (2026-10-18T10:24Z)\n\n1. the lane law\n2. R, checked\n")
    assert "no block stamped after it" in str(ag.refusal(d, root, "T01")), "a minute earlier still refuses"


def test_a_part_b_stamped_after_the_clock_is_refused() -> None:
    """Feature 385 T50 (the round arbiter's fix on hour:385-approach-checklist@18): a part B stamped later than the current UTC
    minute is refused, naming it and the clock; one stamped at the minute or before passes."""
    plan = "### T08 part B (2026-10-18T16:40Z)\n\n1. x\n\n### T46 part B (2026-10-18T16:31Z)\n\n1. y\n"
    assert ag.future_stamps(plan, now="2026-10-18T16:31:59Z") == ["### T08 part B (2026-10-18T16:40Z)"]
    why = ag.future_refusal(plan, now="2026-10-18T16:31:59Z")
    assert why is not None and "16:31Z" in why and "T08 part B (2026-10-18T16:40Z)" in why
    assert ag.future_refusal(plan, now="2026-10-18T16:40:00Z") is None, "at the minute it was stamped"
    assert ag.future_refusal("### T08 Approach (checklist part A)\n", now="2026-10-18T16:31:00Z") is None, "an unstamped part A"


def test_part_a_holds_the_constant_and_the_arithmetic_items_and_an_approach_without_them_is_refused() -> None:
    """Feature 385 T76 (plan D95; the GM's approved change 7 of the 2026-10-18 step-back): numbered, so the gate holds them."""
    text = (pathlib.Path(__file__).resolve().parents[2] / "docs" / "approach-checklist.md").read_text(encoding="utf-8")
    items = ag.part_items(text, "A")
    assert items == list(range(1, 12))
    assert "**Before moving a constant.**" in text and "**Before fitting things into room.**" in text
    old_answer = "\n".join(f"{n}. **x.** answered" for n in range(1, 10))
    assert ag.unanswered(old_answer, items) == [10, 11]


def test_a_trigger_charges_every_task_in_flight_not_only_the_last_started(tmp_path: pathlib.Path) -> None:
    """Feature 405 (the GM 2026-10-21): batch 11 started T26 then T103, and the cohort T26's change failed owed part B to T103 alone,
    so the "why not just make it bigger?" question was answered about the wrong change. Every open task started since the
    feature's last tick is charged; a task ticked, or started before that tick, is not."""
    root, d = feature(tmp_path, git=True)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "999-x: T00 ticked (make land)", "--date=2026-10-17T10:00:00Z")
    tick = int(_git(root, "log", "-1", "--format=%ct").strip())
    stamp = lambda s: __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime(tick + s))  # noqa: E731
    starts = [("T03", -60), ("T01", 60), ("T02", 120)]
    (ag.git_dir(root) / "task-starts.jsonl").write_text("".join(json.dumps({"feature": "999-x", "task": t, "utc": stamp(s)}) + "\n" for t, s in starts))
    (ag.git_dir(root) / "active-task").write_text(json.dumps({"feature": "999-x", "task": "T02"}))
    assert ag.in_flight(root, d, "T02") == ["T02", "T01"], "T03 was started before the last tick"
    msg = str(ag.ruled(root, "hour:999-x@3", now="2026-10-17T21:40:00Z"))
    assert "T02 owes" in msg and "T01 owes" in msg
    assert sorted(r["task"] for r in ag.owed_entries(root)) == ["T01", "T02"]
    (d / "tasks.md").write_text(TASKS.replace("- [ ] T01", "- [x] T01"))
    assert ag.in_flight(root, d, "T02") == ["T02"], "a ticked task is not in flight"
