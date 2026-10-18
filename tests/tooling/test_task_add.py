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
