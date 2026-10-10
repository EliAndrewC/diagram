"""`make speckit-todo` - every feature not yet closed, by state (feature 330, FR-001 to FR-003, FR-009).

The GM, 2026-10-08: *"we then need some way to mechanically easily see what spec kit features are open"*. The script
reads `specs/` alone; these tests build a fixture tree holding one feature in each state.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("speckit_todo", script("speckit-todo.py"))
assert _spec is not None and _spec.loader is not None
st = importlib.util.module_from_spec(_spec)
sys.modules["speckit_todo"] = st
_spec.loader.exec_module(st)

REPO = Path(__file__).resolve().parents[2]


def _feature(root: Path, name: str, status: str | None = "Draft", tasks: str | None = None, title: str = "A thing") -> Path:
    d = root / "specs" / name
    d.mkdir(parents=True)
    if status is not None:
        (d / "spec.md").write_text(f"# Feature Specification: {title}\n\n**Status**: {status}\n\nbody\n")
    if tasks is not None:
        (d / "tasks.md").write_text(tasks)
    return d


@pytest.mark.parametrize(
    ("status", "tasks", "state"),
    [
        ("Filed - from an old backlog entry", None, "filed"),
        ("Draft", "# tasks\n\nno boxes yet\n", "filed"),
        ("Draft", "- [ ] T01 a\n- [ ] T02 b\n", "planned"),
        ("Draft", "- [x] T01 a\n- [ ] T02 b\n", "in progress"),
        ("Draft", "- [x] T01 a\n- [X] T02 b\n", "closed"),
        ("Done (2026-10-08): the commits show it", "- [ ] T01 a\n", "closed"),
        ("Superseded by 316 (2026-10-02)", None, "closed"),
        ("SUPERSEDED by feature 316", None, "closed"),
        ("withdrawn (GM 2026-10-07)", "- [x] T01 a\n- [ ] T02 b\n", "closed"),
        ("Implemented 2026-08-16", "- [x] T01 a\n- [ ] T02 b\n", "in progress"),
    ],
)
def test_the_state_follows_the_tasks_and_the_closing_words(tmp_path: Path, status: str, tasks: str | None, state: str) -> None:
    d = _feature(tmp_path, "001-x", status, tasks)
    assert st.feature(d).state == state


def test_an_indented_box_is_part_of_its_task_not_a_task(tmp_path: Path) -> None:
    d = _feature(tmp_path, "001-x", "Draft", "- [x] T01 a\n  - [ ] research pass\n")
    f = st.feature(d)
    assert (f.state, f.ticked, f.total) == ("closed", 1, 1)


def test_a_feature_with_no_spec_is_listed_and_says_so(tmp_path: Path) -> None:
    d = _feature(tmp_path, "275-village-burial-ground", status=None)
    (d / "request.md").write_text("the GM's words\n")
    f = st.feature(d)
    assert f.state == "filed" and f.no_spec and f.title == "village-burial-ground"


def test_a_checkbox_form_it_cannot_read_leaves_the_feature_open(tmp_path: Path) -> None:
    """A parsing miss must show up as open work, never as finished work (spec edge case)."""
    d = _feature(tmp_path, "001-x", "Draft", "* [x] T01 a starred box\n")
    assert st.feature(d).state == "filed"


def test_the_closing_words_are_stated_once() -> None:
    assert st.CLOSING == ("done", "superseded by", "withdrawn")


def test_the_report_lists_open_features_by_state_and_counts_them(tmp_path: Path) -> None:
    _feature(tmp_path, "001-filed-one", "Filed", None, "Filed one")
    _feature(tmp_path, "002-planned-one", "Draft", "- [ ] T01\n", "Planned one")
    _feature(tmp_path, "003-going", "Draft", "- [x] T01\n- [ ] T02\n- [ ] T03\n", "Going")
    _feature(tmp_path, "004-done", "Draft", "- [x] T01\n", "Done one")
    _feature(tmp_path, "005-dropped", "Withdrawn (GM 2026-10-07)", None, "Dropped one")
    _feature(tmp_path, "196-a", "Filed", None, "Same number A")
    _feature(tmp_path, "196-b", "Filed", None, "Same number B")
    out = st.report(tmp_path / "specs")
    assert "001-filed-one  Filed one" in out and "002-planned-one  Planned one  0/1" in out
    assert "003-going  Going  1/3" in out
    assert "004-done" not in out and "005-dropped" not in out
    assert "196-a" in out and "196-b" in out, "two features sharing a number are both listed, by directory"
    assert out.index("FILED") < out.index("PLANNED") < out.index("IN PROGRESS")
    assert out.rstrip().splitlines()[-1] == "open: 3 filed, 1 planned, 1 in progress; closed: 2"


def test_all_adds_the_closed_features_with_their_reason(tmp_path: Path) -> None:
    _feature(tmp_path, "004-done", "Draft", "- [x] T01\n", "Done one")
    _feature(tmp_path, "005-dropped", "Withdrawn (GM 2026-10-07)", None, "Dropped one")
    out = st.report(tmp_path / "specs", show_closed=True)
    assert "CLOSED" in out and "004-done  Done one  every task ticked" in out
    assert "005-dropped  Dropped one  Withdrawn (GM 2026-10-07)" in out


def test_the_command_line_reads_only_specs_and_exits_zero(tmp_path: Path) -> None:
    _feature(tmp_path, "001-x", "Filed", None)
    r = subprocess.run([sys.executable, str(script("speckit-todo.py")), "--root", str(tmp_path)], capture_output=True, text=True, check=False)
    assert r.returncode == 0 and "001-x" in r.stdout
    r = subprocess.run([sys.executable, str(script("speckit-todo.py")), "--root", str(tmp_path), "--all"], capture_output=True, text=True, check=False)
    assert r.returncode == 0 and "CLOSED" in r.stdout


def test_the_real_tree_answers_in_under_two_seconds() -> None:
    """FR-003 / SC-001, measured on the repository's own specs/."""
    t0 = time.perf_counter()
    out = st.report(REPO / "specs")
    assert time.perf_counter() - t0 < 2.0
    assert out.rstrip().splitlines()[-1].startswith("open: ")


@pytest.mark.parametrize(("status", "closed"), [("Done (2026-10-08): x", True), ("Withdrawn (GM)", True), ("Superseded by 316", True), ("Implemented", False), ("Draft", False), (None, False)])
def test_closed_by_status_reads_the_status_line_alone(tmp_path: Path, status: str | None, closed: bool) -> None:
    """The push's in-progress refusal keeps its own open-box test and asks only this (plan D8, review round 4)."""
    d = _feature(tmp_path, "001-x", status, "- [ ] T01 open\n")
    assert st.closed_by_status(d) is closed
    r = subprocess.run([sys.executable, str(script("speckit-todo.py")), "--closed-by-status", str(d)], capture_output=True, text=True, check=False)
    assert r.stdout.strip() == ("yes" if closed else "no")


@pytest.mark.parametrize(
    ("line", "stage"),
    [
        ("**Owed at**: town", "town"),
        ("**Owed at**: Provincial city - the governor's mansion", "provincial city"),
        ("**Owed at:** now", "now"),
        ("**Owed at**: [now | village | town | provincial city | capital - the earliest stage that needs it]", ""),
        ("**Owed at**: cities", ""),
        ("**Owed at**: townhouse", ""),
        ("no line at all", ""),
    ],
)
def test_the_stage_is_read_from_its_line(line: str, stage: str) -> None:
    """The template's placeholder and a word that only begins like a stage name no stage (the GM, 2026-10-10)."""
    assert st.owed_at(f"# Feature: x\n\n**Status**: Filed\n\n{line}\n") == stage


def test_the_report_groups_each_state_by_stage_in_the_order_the_work_reaches_it(tmp_path: Path) -> None:
    for name, owed in (("001-city", "capital"), ("002-town", "town"), ("003-now", "now"), ("004-none", None)):
        d = _feature(tmp_path, name, "Filed", None, name)
        if owed:
            (d / "spec.md").write_text((d / "spec.md").read_text() + f"\n**Owed at**: {owed}\n")
    out = st.report(tmp_path / "specs")
    assert out.index("owed at now (1)") < out.index("003-now") < out.index("owed at town (1)") < out.index("002-town")
    assert out.index("002-town") < out.index("owed at capital (1)") < out.index("001-city") < out.index("NO STAGE") < out.index("004-none")
    assert "owed at village" not in out, "an empty stage prints no heading"


def test_check_names_the_open_features_with_no_stage_and_the_line_to_add(tmp_path: Path) -> None:
    _feature(tmp_path, "001-open", "Filed", None)
    _feature(tmp_path, "002-closed", "Withdrawn (GM)", None)
    d = _feature(tmp_path, "003-staged", "Filed", None)
    (d / "spec.md").write_text((d / "spec.md").read_text() + "\n**Owed at**: village\n")
    r = subprocess.run([sys.executable, str(script("speckit-todo.py")), "--root", str(tmp_path), "--check"], capture_output=True, text=True, check=False)
    assert r.returncode == 1
    assert "specs/001-open/spec.md" in r.stderr and "002-closed" not in r.stderr and "003-staged" not in r.stderr
    assert "**Owed at**: now | village | town | provincial city | capital" in r.stderr
    assert "a thing two tiers need is owed at the earlier one" in r.stderr
    (tmp_path / "specs" / "001-open" / "spec.md").write_text("# Feature: x\n\n**Status**: Filed\n\n**Owed at**: now\n")
    r = subprocess.run([sys.executable, str(script("speckit-todo.py")), "--root", str(tmp_path), "--check"], capture_output=True, text=True, check=False)
    assert (r.returncode, r.stderr) == (0, "")


def test_every_open_feature_in_the_repository_names_its_stage() -> None:
    """The GM, 2026-10-10: every open feature says when it is owed, so the list can be read by stage."""
    assert st.check_message(st.unstaged(REPO / "specs")) == ""


def test_a_tree_with_no_specs_directory_has_nothing_owed(tmp_path: Path) -> None:
    assert st.features(tmp_path / "specs") == [] and st.check_message(st.unstaged(tmp_path / "specs")) == ""
