"""The plan-lint before every plan review (feature 430 T05, D5; the GM 2026-10-26, item 5): a figure with a unit anywhere, the red
exit, an approach block per task, `make plan-delta` writing no bundle while one refuses, and the approach block that decides
nothing."""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "gates"))
import plan_gate  # noqa: E402
import plan_lint  # noqa: E402
import plan_sections  # noqa: E402

RED = "Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`."


def _approach(task: str, item6: str = RED, item2: str = "D1; FR-001.", item9: str = "Its tests red without D1.") -> str:
    items = [
        "The goal, in the world.** n/a",
        f"The constraints.** {item2}",
        "Where each comes from.** FR-001.",
        "Do they describe the world here?** Yes.",
        "The order.** n/a.",
        f"The exits.** {item6}",
        "The search smell.** None.",
        "The budget.** One landing.",
        f"Done, measured.** {item9}",
        "Before moving a constant.** n/a.",
        "Before fitting things into room.** n/a.",
    ]
    return f"### {task} Approach (checklist part A)\n\n" + "\n".join(f"{i}. **{t}" for i, t in enumerate(items, 1)) + "\n"


def test_a_figure_with_a_unit_anywhere_needs_a_label() -> None:
    """Item 4 alone was read before; the day's plan reviews found "580 lines"-style figures elsewhere, in a Decision."""
    assert "takes 48 s" in plan_lint.unlabeled_unit_figure("**D3 - x.** The check takes 48 s on a landing.\n")
    assert plan_lint.unlabeled_unit_figure("**D3 - x.** It takes 48 s, measured 2026-10-24 (feature 415 T03).\n") == ""
    assert plan_lint.unlabeled_unit_figure("**D3 - x.** It takes 48 s (observed 2026-10-24, method: the run log).\n") == ""
    assert plan_lint.unlabeled_unit_figure("**D3 - x.** It takes 48 s (`m:cover-time`).\n") == ""
    assert plan_lint.unlabeled_unit_figure("**D3 - x.** Run `sleep 48 s` in a span.\n") == "", "a code span names, it measures nothing"


def test_an_approach_block_without_the_red_exit_is_refused() -> None:
    assert plan_lint.missing_red_exit(_approach("T01")) == ""
    assert plan_lint.missing_red_exit(_approach("T01", item6="Green: landed.")) == "T01"
    assert "make arbiter-ask" in plan_lint.refusal(REPO / "specs" / "nonexistent", _approach("T01", item6="Green: landed."))


def _spec(tmp_path: Path, plan: str, tasks: str) -> Path:
    d = tmp_path / "specs" / "999-x"
    d.mkdir(parents=True)
    (d / "plan.md").write_text(plan, encoding="utf-8")
    (d / "tasks.md").write_text(tasks, encoding="utf-8")
    return d


def test_each_open_task_owes_an_approach_block_once_the_plan_holds_one(tmp_path: Path) -> None:
    tasks = "- [ ] T01 a\n- [ ] T02 b\n- [x] T03 c\n"
    d = _spec(tmp_path, "# Plan\n\n" + _approach("T01"), tasks)
    assert plan_lint.tasks_without_approach(d, (d / "plan.md").read_text()) == ["T02"], "T03 is ticked"
    old = _spec(tmp_path / "old", "# Plan\n\n## Decisions\n", tasks)
    assert plan_lint.tasks_without_approach(old, (old / "plan.md").read_text()) == [], "a plan from before the checklist"
    opted = _spec(tmp_path / "opted", "# Plan\n\n**Approach checklist**: docs/approach-checklist.md\n", tasks)
    assert plan_lint.tasks_without_approach(opted, (opted / "plan.md").read_text()) == ["T01", "T02"]


def test_plan_delta_writes_no_bundle_while_a_block_refuses(tmp_path: Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    """SC-004: no plan review is dispatched on a block the lint refuses - `make plan-delta` writes no bundle to dispatch it on."""
    d = _spec(tmp_path, "# Plan\n\n## Decisions\n\n**D1 - x.** The check takes 48 s on a landing.\n\n" + _approach("T01"), "- [ ] T01 a\n")
    monkeypatch.setattr(plan_gate, "resolve", lambda f: d)
    assert plan_gate.main(["delta", "999"]) == 1
    err = capsys.readouterr().err
    assert "no bundle written" in err and "48 s" in err, err


def test_an_approach_block_of_template_wording_and_ids_decides_nothing() -> None:
    plan = "**D1 - a rule.** x\n"
    assert plan_sections.decides_nothing("### T01 Approach (checklist part A)", _approach("T01", item6=_template6()), plan)


def _template6() -> str:
    return plan_sections._template_answers()[6]


def test_an_approach_block_in_its_own_words_or_with_a_number_owes_review() -> None:
    """The plan review's round 2: a rule stated in prose, or a number with no unit ("9 of the 11"), is a decision."""
    plan = "**D1 - a rule.** x\n"
    key = "### T01 Approach (checklist part A)"
    assert not plan_sections.decides_nothing(key, _approach("T01", item6=_template6(), item2="D1; the lanes keep 9 ft."), plan)
    assert not plan_sections.decides_nothing(key, _approach("T01", item6=_template6(), item9="select 9 of the 11 failures."), plan)
    assert not plan_sections.decides_nothing(key, _approach("T01", item6=RED), plan), "item 6 in the block's own words"
    assert not plan_sections.decides_nothing(key, _approach("T01", item6=_template6(), item2="D7."), plan), "D7 is defined nowhere"


def test_decide_and_plan_delta_name_an_owed_claims_triage(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 430 T07 (D7; research R2): nothing held the triage back but the session's own order - it is now named at the
    review's dispatch, so it runs beside the review."""

    class Done:
        def __init__(self, out: str) -> None:
            self.stdout = out

    monkeypatch.setattr(plan_gate.subprocess, "run", lambda *a, **k: Done("3\n"))
    assert "claims owed a triage: 3 - `make claims-triage`" in plan_gate.triage_hint(tmp_path)
    monkeypatch.setattr(plan_gate.subprocess, "run", lambda *a, **k: Done("0\n"))
    assert plan_gate.triage_hint(tmp_path) == ""
    monkeypatch.setattr(plan_gate.subprocess, "run", lambda *a, **k: Done("Traceback ...\n"))
    assert plan_gate.triage_hint(tmp_path) == "", "claims that cannot be read name nothing"


def test_a_coverage_rule_is_no_figure() -> None:
    """Feature 427's plan, the first this lint read after landing: "100% coverage of the new module" is the project's rule, not
    a measurement to label."""
    assert plan_lint.unlabeled_unit_figure("- **X**: ruff, 100% coverage of the new module the day it lands.\n") == ""
    assert "47%" in plan_lint.unlabeled_unit_figure("- **X**: the check covers 47% of the lines.\n"), "a measured share still needs its label"


def test_a_sentence_wrapped_across_lines_is_read_whole() -> None:
    """Feature 427's plan: "... the memory watch has since read the shared cap at 9.1-9.3 of 10 GB" wrapped onto a second line,
    its label on the first; read line by line, the figure stood alone."""
    wrapped = "**D1 - x.** The default, observed 2026-10-26, method: the memory watch, read the shared cap at\n9.3 of 10 GB.\n"
    assert plan_lint.unlabeled_unit_figure(wrapped) == ""
    assert "10 GB" in plan_lint.unlabeled_unit_figure("- one item.\n- the cap is 10 GB.\n"), "a list item is its own sentence"
