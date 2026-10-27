"""`scripts/task-add.py` - `make task-add` (feature 385 T64, plan D83): the next free id, the box before the GM-review box, the
plan section before the close."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("task_add", script("task-add.py"))
assert _spec and _spec.loader
ta = importlib.util.module_from_spec(_spec)
sys.modules["task_add"] = ta
_spec.loader.exec_module(ta)

TASKS = "# Tasks\n\n- [x] T01 one\n      research: rendering\n- [ ] T09 nine\n      research: rendering\n- [ ] GM review of the feature\n"
PLAN = "# Plan\n\n## T12 - a heading only the plan names\n\ntext\n\n## T11 - the close\n\nclose\n"


def _feature(tmp_path: pathlib.Path, monkeypatch) -> pathlib.Path:  # noqa: ANN001
    d = tmp_path / "specs" / "385-x"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(TASKS, encoding="utf-8")
    (d / "plan.md").write_text(PLAN, encoding="utf-8")
    (d / "plan-done.md").write_text("## T14 - archived\n", encoding="utf-8")
    monkeypatch.setattr(ta, "_tick", lambda: _Tick(tmp_path))
    return d


class _Tick:
    def __init__(self, root: pathlib.Path) -> None:
        self.root = root

    def repo_root(self) -> pathlib.Path:
        return self.root

    def spec_dir(self, root: pathlib.Path, feature: str) -> pathlib.Path | None:
        hits = sorted((root / "specs").glob(f"{feature}-*"))
        return hits[0] if len(hits) == 1 else None


def test_the_box_takes_the_next_free_id_and_lands_before_the_gm_review_box(tmp_path, monkeypatch, capsys) -> None:  # noqa: ANN001
    d = _feature(tmp_path, monkeypatch)
    sec = tmp_path / "sec.md"
    sec.write_text("## {T} - the new thing\n\n### {T} Decisions\n", encoding="utf-8")
    monkeypatch.setenv("TASK_TITLE", "the new thing")
    assert ta.main(["385", "--section", str(sec), "--physical"]) == 0
    assert "T15 filed" in capsys.readouterr().out  # past T14, named only in plan-done.md
    tasks = (d / "tasks.md").read_text(encoding="utf-8")
    assert tasks.index("- [ ] T15 the new thing\n      research: physical\n      - [ ] research pass") < tasks.index("- [ ] GM review")
    plan = (d / "plan.md").read_text(encoding="utf-8")
    assert plan.index("## T15 - the new thing\n\n### T15 Decisions") < plan.index("## T11 - the close")


def test_with_no_gm_box_or_close_both_go_at_the_end_and_bad_calls_refuse(tmp_path, monkeypatch, capsys) -> None:  # noqa: ANN001
    assert ta.add_box("- [ ] T01 a\n", "T02", "b", False).endswith("- [ ] T02 b\n      research: rendering\n")
    assert ta.add_section("# Plan", "T02", "## {T} - b").endswith("# Plan\n\n## T02 - b\n\n")
    _feature(tmp_path, monkeypatch)
    monkeypatch.delenv("TASK_TITLE", raising=False)
    assert ta.main(["385"]) == 2  # no title
    monkeypatch.setenv("TASK_TITLE", "x")
    assert ta.main(["999"]) == 2 and ta.main(["385", "--section", str(tmp_path / "missing.md")]) == 2
    assert "is not a file" in capsys.readouterr().err


def test_an_id_quoted_in_a_title_is_not_a_task_s_id(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T31 (D3): 405's titles quote "(385 T147)", and next_id gave T148-T154 where T28-T35 were next."""
    d = tmp_path / "specs" / "405-x"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text("- [x] T08 (385 T111) moved\n- [ ] T09 (385 T147) moved, see T147\n", encoding="utf-8")
    (d / "plan.md").write_text("## T09 - its plan, citing 385 T126\n", encoding="utf-8")
    assert ta.next_id(d) == "T10"


def test_a_task_filed_mid_feature_carries_no_lands_open_mark(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 405 T32 (D4, the GM 2026-10-20: no Lands open line): only the task being worked holds a landing, so a new
    task needs no mark and no line - an old line is left as it is, unread."""
    d = _feature(tmp_path, monkeypatch)
    (d / "plan.md").write_text("# Plan\n\n**Lands open**: T09, T12\n\n## T11 - the close\n", encoding="utf-8")
    monkeypatch.setenv("TASK_TITLE", "a fix")
    assert ta.main(["385"]) == 0
    assert "**Lands open**: T09, T12\n" in (d / "plan.md").read_text(encoding="utf-8")
    assert "- [ ] T15 a fix\n" in (d / "tasks.md").read_text(encoding="utf-8")


def test_a_task_filed_with_no_section_gets_the_template_with_its_red_exit_and_alone_off_table(tmp_path, monkeypatch, capsys) -> None:  # noqa: ANN001
    """Feature 426 D6: T48's and T50's plan reviews each blocked a round on item 6's red exit and the table of each step alone."""
    d = _feature(tmp_path, monkeypatch)
    monkeypatch.setenv("TASK_TITLE", "x")
    assert ta.main(["385"]) == 0 and "the template" in capsys.readouterr().out
    plan = (d / "plan.md").read_text(encoding="utf-8")
    assert "### T15 Approach (checklist part A)" in plan and ta.RED_EXIT in plan
    assert "| step | alone off: fixed and pinned | fresh block vs HEAD |" in plan


def test_a_section_without_the_red_exit_is_filed_with_a_warning_naming_the_wording(tmp_path, monkeypatch, capsys) -> None:  # noqa: ANN001
    _feature(tmp_path, monkeypatch)
    sec = tmp_path / "sec.md"
    sec.write_text("### {T} x\n\n6. **The exits.** Red: set down.\n", encoding="utf-8")
    monkeypatch.setenv("TASK_TITLE", "x")
    assert ta.main(["385", "--section", str(sec)]) == 0
    assert "has no red exit through `make arbiter-ask`" in capsys.readouterr().err
    sec.write_text("### {T} x\n\n6. **The exits.** " + ta.RED_EXIT + "\n", encoding="utf-8")
    assert ta.main(["385", "--section", str(sec)]) == 0 and "no red exit" not in capsys.readouterr().err


def test_every_task_asks_whether_it_is_performance_work_and_PERF_writes_the_checklist(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 435 D2: the memory aid on every task - one line asking - and `--performance` (`make task-add PERF=1`) appending
    the checklist's six questions as prompts, after the section, never in place of it."""
    d = _feature(tmp_path, monkeypatch)
    monkeypatch.setenv("TASK_TITLE", "x")
    assert ta.main(["385"]) == 0
    plan = (d / "plan.md").read_text(encoding="utf-8")
    assert "**Performance work?**" in plan and "Performance checklist" not in plan
    assert ta.main(["385", "--performance"]) == 0
    plan = (d / "plan.md").read_text(encoding="utf-8")
    assert "### T16 Performance checklist (docs/performance-checklist.md" in plan and "Removes work, or only moves it?" in plan
    assert plan.index("### T16 Approach (checklist part A)") < plan.index("### T16 Performance checklist"), "after the section"
    assert "--performance" not in (d / "tasks.md").read_text(encoding="utf-8"), "the flag is no task's title"
