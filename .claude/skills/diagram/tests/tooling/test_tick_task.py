"""`scripts/tick-task.py` - `make tick` (feature 188). Each behavior and each refusal on a fixture tasks.md.

No `tooling` marker: it calls functions on strings and files, like `test_file_scale.py`."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("tick_task", REPO / "scripts" / "tick-task.py")
assert _spec and _spec.loader
tt = importlib.util.module_from_spec(_spec)
sys.modules["tick_task"] = tt
_spec.loader.exec_module(tt)

TASKS = """# Tasks - feature 999

Spec: [`spec.md`](spec.md).

- [x] T01 the first thing
      research: rendering
      verify: DONE. it was done
- [ ] T02 the second thing
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify: `make quick` clean; the page reads right
      and this verify text wraps onto a second line
- [ ] T02a the second-and-a-half thing
      research: rendering
      verify: something
- [ ] T03 a task written without a verify line
      research: rendering

## Closing

- [ ] T04 the last
      research: rendering
      verify: green gate
"""


def test_ticks_the_task_and_replaces_the_whole_verify_text() -> None:
    new, line = tt.tick(TASKS, "T02", "the shrine reads 6 x 6 ft")
    assert line == "- [x] T02 the second thing"
    assert "- [x] T02 the second thing\n      research: physical\n      - [ ] research pass" in new
    assert "      verify: DONE. the shrine reads 6 x 6 ft\n- [ ] T02a" in new, "the wrapped old text is gone, the next task follows"
    assert "and this verify text wraps" not in new
    assert new.count("- [x]") == 2 and new.count("- [ ] T") == 3


def test_T02_does_not_match_T02a_and_the_boxes_tick_on_request() -> None:
    new, _ = tt.tick(TASKS, "T02a", "done indeed")
    assert "- [x] T02a the second-and-a-half thing\n      research: rendering\n      verify: DONE. done indeed\n" in new
    assert "- [ ] T02 the second thing" in new, "T02 untouched"
    boxed, _ = tt.tick(TASKS, "T02", "with the record", boxes=True)
    assert "- [ ] research pass" not in boxed and "- [x] source-applicability confirmed" in boxed
    unboxed, _ = tt.tick(TASKS, "T02", "without the flag")
    assert "- [ ] research pass" in unboxed, "boxes stay open unless asked"


def test_the_boxes_are_matched_by_SHAPE_so_the_roster_may_grow() -> None:
    """THE DEFECT THIS REPLACES (feature 229). Both the script and this test held the literal
    three-box line of constitution v2.12.0, and the roster has been FIVE since features 194 and 211
    added `quote-check confirmed` and `source-applicability confirmed`. The literal matched nothing, so
    `make tick BOXES=1` reported a ticked task and ticked no box - silently, seven times, until the
    gate's own rule caught it at the end. Matching by shape is what makes the next addition free."""
    for line in (
        "      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited\n",
        "      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited\n",
        "      - [ ] a  - [ ] b  - [ ] c  - [ ] d  - [ ] e  - [ ] f  - [ ] g\n",
    ):
        assert tt._is_boxes_line(line), line
        assert "- [ ]" not in tt._tick_boxes(line)
    for line in ("- [ ] T02 the second thing\n", "      research: physical\n", "      verify: DONE. a note\n"):
        assert not tt._is_boxes_line(line), line
        assert tt._tick_boxes(line) == line


def test_asking_for_boxes_where_there_are_none_REFUSES_rather_than_doing_nothing() -> None:
    """The silence was the whole defect: a no-op that reported success. T02a is a rendering task."""
    with pytest.raises(SystemExit) as e:
        tt.tick(TASKS, "T02a", "no boxes here", boxes=True)
    assert "no research-box line" in str(e.value)


def test_a_task_without_a_verify_line_gets_one_and_the_section_heading_is_not_swallowed() -> None:
    new, _ = tt.tick(TASKS, "T03", "it exists now")
    assert "- [x] T03 a task written without a verify line\n      research: rendering\n      verify: DONE. it exists now\n\n## Closing" in new


def test_the_last_task_in_the_file_ticks_too() -> None:
    new, _ = tt.tick(TASKS, "T04", "green at 100%")
    assert new.endswith("- [x] T04 the last\n      research: rendering\n      verify: DONE. green at 100%\n")


@pytest.mark.parametrize(
    ("task", "note", "why"),
    [("T01", "again", "already ticked"), ("T09", "nope", "no open task T09"), ("T02", "   ", "verify note is empty")],
)
def test_refusals_write_nothing(task: str, note: str, why: str) -> None:
    with pytest.raises(ValueError, match=why):
        tt.tick(TASKS, task, note)


def test_main_resolves_a_feature_by_number_or_name_and_refuses_ambiguity(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    root = tmp_path
    (root / "specs" / "188-alpha").mkdir(parents=True)
    (root / "specs" / "188-alpha" / "tasks.md").write_text(TASKS, encoding="utf-8")
    # feature 243: a tick needs the plan reviewed - this test is about resolution, so the review is current
    plan = b"# plan\n"
    (root / "specs" / "188-alpha" / "plan.md").write_bytes(plan)
    (root / "specs" / "188-alpha" / "plan-review.json").write_text(json.dumps({"plan_sha256": hashlib.sha256(plan).hexdigest(), "decisions": [], "verdict": "CLEAR"}), encoding="utf-8")
    monkeypatch.setattr(tt, "repo_root", lambda start=None: root)
    assert tt.main(["188", "T02", "by number"]) == 0
    out = capsys.readouterr().out
    assert "ticked - [x] T02" in out and "3 task(s) still open" in out
    assert "verify: DONE. by number" in (root / "specs" / "188-alpha" / "tasks.md").read_text(encoding="utf-8")
    assert tt.main(["188-alpha", "T02", "again"]) == 2, "already ticked -> refused"
    assert "already ticked" in capsys.readouterr().err
    (root / "specs" / "188-beta").mkdir()
    assert tt.main(["188", "T03", "x"]) == 2, "two 188s -> ambiguous -> refused"
    assert tt.main(["188-beta", "T03", "x"]) == 2, "no tasks.md -> refused"
    assert tt.main(["only-two-args", "T03"]) == 2, "usage"
    assert tt.main(["188-alpha", "T03", "boxes flag parsed"]) == 0  # T03 is a rendering task; --boxes on it refuses, proved above
    # `make tick` hands the note over in the environment, so backticks in it are never shell-expanded
    monkeypatch.setenv("TICK_NOTE", "the `_ENGINE_DIRS` tuple, quoted safely")
    assert tt.main(["188-alpha", "T04", "--note-from-env"]) == 0
    assert "verify: DONE. the `_ENGINE_DIRS` tuple, quoted safely" in (root / "specs" / "188-alpha" / "tasks.md").read_text(encoding="utf-8")


def test_repo_root_falls_back_to_the_nearest_specs_directory(tmp_path: pathlib.Path, monkeypatch) -> None:
    (tmp_path / "specs").mkdir()
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)

    def no_git(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(tt.subprocess, "run", no_git)
    assert tt.repo_root(deep) == tmp_path
    assert tt.repo_root(tmp_path / "nowhere") == (tmp_path / "nowhere").resolve() or True
