"""`make speckit-todo` - every feature not yet closed, by state (feature 330, FR-001 to FR-003, FR-009).

The GM, 2026-10-08: *"we then need some way to mechanically easily see what spec kit features are open"*. The script
reads `specs/` alone; these tests build a fixture tree holding one feature in each state.
"""

from __future__ import annotations

import importlib.util
import json
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
        ("**Owed at**: cities", ""),
        ("**Owed at**: townhouse", ""),
        ("no line at all", ""),
    ],
)
def test_an_overriding_stage_is_read_from_its_line(line: str, stage: str) -> None:
    """A word that only begins like a stage name names no stage."""
    assert st.owed_at(f"# Feature: x\n\n**Status**: Filed\n\n{line}\n") == stage


_VOCAB = {
    "stages": list(st.STAGES),
    "aliases": {"all settlements": ["hamlet", "village", "town", "provincial city", "capital"]},
    "tags": {
        "hamlet": {"stage": "now"},
        "village": {"stage": "village"},
        "town": {"stage": "town"},
        "provincial city": {"stage": "provincial city"},
        "capital": {"stage": "capital"},
        "magistracy": {"stage": "now"},
        "tooling": {"stage": "now"},
    },
}


def _tagged(root: Path, name: str, affects: str | None, extra: str = "") -> Path:
    if not (root / st.AFFECTS).is_file():
        (root / st.AFFECTS).parent.mkdir(parents=True, exist_ok=True)
        (root / st.AFFECTS).write_text(json.dumps(_VOCAB))
    d = _feature(root, name, "Filed", None, name)
    if affects is not None:
        (d / "spec.md").write_text((d / "spec.md").read_text() + f"\n**Affects**: {affects}\n{extra}")
    return d


@pytest.mark.parametrize(
    ("affects", "known", "unknown", "stage"),
    [
        ("town, provincial city", ("town", "provincial city"), (), "town"),
        ("Capital,  provincial city", ("capital", "provincial city"), (), "provincial city"),
        ("all settlements", ("hamlet", "village", "town", "provincial city", "capital"), (), "now"),
        ("magistracy, village", ("magistracy", "village"), (), "now"),
        ("village, villages", ("village",), ("villages",), "village"),
        ("town, town", ("town",), (), "town"),
    ],
)
def test_the_stage_is_the_earliest_among_the_tags(tmp_path: Path, affects: str, known: tuple[str, ...], unknown: tuple[str, ...], stage: str) -> None:
    """The GM, 2026-10-10: a farmhouse change touches every tier, so it is owed now; towns-and-cities is owed at towns."""
    f = st.feature(_tagged(tmp_path, "001-x", affects))
    assert (f.affects, f.unknown, f.owed) == (known, unknown, stage)


def test_an_owed_at_line_overrides_the_derived_stage(tmp_path: Path) -> None:
    f = st.feature(_tagged(tmp_path, "001-x", "tooling", "\n**Owed at**: village - its trigger is a village feature\n"))
    assert f.owed == "village"


def test_the_report_groups_each_state_by_stage_in_the_order_the_work_reaches_it(tmp_path: Path) -> None:
    for name, affects in (("001-city", "capital"), ("002-town", "town, capital"), ("003-now", "magistracy"), ("004-none", None)):
        _tagged(tmp_path, name, affects)
    out = st.report(tmp_path / "specs")
    assert out.index("owed at now (1)") < out.index("003-now") < out.index("owed at town (1)") < out.index("002-town")
    assert out.index("002-town") < out.index("owed at capital (1)") < out.index("001-city") < out.index("NO STAGE") < out.index("004-none")
    assert "owed at village" not in out, "an empty stage prints no heading"
    assert "002-town  002-town  [town, capital]" in out, "each line shows its tags"


def test_by_affects_lists_a_feature_under_each_of_its_tags(tmp_path: Path) -> None:
    _tagged(tmp_path, "001-both", "magistracy, town")
    _tagged(tmp_path, "002-none", None)
    out = st.report(tmp_path / "specs", by_affects=True)
    assert out.index("affects town (1)") < out.index("affects magistracy (1)") < out.index("NOTHING NAMED")
    assert out.count("001-both  001-both") == 2 and "affects hamlet" not in out
    r = subprocess.run([sys.executable, str(script("speckit-todo.py")), "--root", str(tmp_path), "--by-affects"], capture_output=True, text=True, check=False)
    assert r.returncode == 0 and "affects town (1)" in r.stdout


def test_check_names_the_open_features_with_no_tag_or_an_unknown_one_and_the_line_to_add(tmp_path: Path) -> None:
    _tagged(tmp_path, "001-open", None)
    _tagged(tmp_path, "002-typo", "hamlets")
    _tagged(tmp_path, "003-tagged", "village")
    _feature(tmp_path, "004-closed", "Withdrawn (GM)", None)
    r = subprocess.run([sys.executable, str(script("speckit-todo.py")), "--root", str(tmp_path), "--check"], capture_output=True, text=True, check=False)
    assert r.returncode == 1
    assert "specs/001-open/spec.md  (no **Affects** line)" in r.stderr and "specs/002-typo/spec.md  (unknown: hamlets)" in r.stderr
    assert "003-tagged" not in r.stderr and "004-closed" not in r.stderr
    assert "**Affects**: hamlet, magistracy" in r.stderr and "Tags: hamlet, village, town" in r.stderr and "all settlements" in r.stderr
    assert "A new tag is one entry in .specify/affects.json" in r.stderr
    for name in ("001-open", "002-typo"):
        (tmp_path / "specs" / name / "spec.md").write_text("# Feature: x\n\n**Status**: Filed\n\n**Affects**: hamlet\n")
    r = subprocess.run([sys.executable, str(script("speckit-todo.py")), "--root", str(tmp_path), "--check"], capture_output=True, text=True, check=False)
    assert (r.returncode, r.stderr) == (0, "")


def test_a_spec_with_no_spec_md_is_told_to_write_one(tmp_path: Path) -> None:
    _tagged(tmp_path, "001-tagged", "hamlet")
    d = tmp_path / "specs" / "002-bare"
    d.mkdir()
    msg = st.check_message(st.untagged(tmp_path / "specs"), st.vocabulary(tmp_path))
    assert "specs/002-bare/spec.md  (no spec.md - write one first)" in msg


def test_every_open_feature_in_the_repository_names_known_tags() -> None:
    """The GM, 2026-10-10: every open feature says what it affects, so the list can be read by stage and by tag."""
    assert st.check_message(st.untagged(REPO / "specs"), st.vocabulary(REPO)) == ""


def test_the_vocabulary_names_only_known_stages_and_its_aliases_only_known_tags() -> None:
    v = st.vocabulary(REPO)
    assert set(v.stage.values()) <= set(st.STAGES) and v.stage
    assert all(set(ts) <= set(v.stage) for ts in v.aliases.values())


def test_a_tree_with_no_specs_or_no_vocabulary_has_nothing_owed(tmp_path: Path) -> None:
    assert st.features(tmp_path / "specs") == [] and st.untagged(tmp_path / "specs") == []
    _feature(tmp_path, "001-x", "Filed", None)
    assert st.untagged(tmp_path / "specs") == [], "a repository without .specify/affects.json does not use the tags"
    assert st.check_message([]) == ""
