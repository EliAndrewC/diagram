"""`spec-lint`, proven to fire (feature 236, the GM's item 5, FR-010 and FR-011).

Each of the four checks was written by breaking the rule in `scripts/spec-lint.py` and watching a case
here go red - the project's standing requirement for a guard. The quiet half matters as much: a lint
that fired on the number claim or on the mid-feature milestone push would refuse the very protocol the
root `CLAUDE.md` requires, so the no-`tasks.md` cases are here as regression cases.

No `tooling` marker: it writes small files in a tmp directory and calls functions.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("spec_lint", REPO / "scripts" / "spec-lint.py")
assert _spec and _spec.loader
lint = importlib.util.module_from_spec(_spec)
sys.modules["spec_lint"] = lint
_spec.loader.exec_module(lint)

GOOD = """# Feature 999

## Summary

The gate took 91 min before this, measured in `research.md` R1.

## Functional requirements

**FR-001** A thing.

**FR-001a** A narrower thing.

## Success criteria

**SC-001** (FR-001, FR-001a) Both hold.
**SC-002** (spec-wide) The gate is green.

## Decisions recorded

**D1** The 22 ft figure stayed out of the rule (`research.md` R2).

## Review history

Round 1 said 6.7 m and the measurement withdrew it.
"""


def _feature(tmp_path: pathlib.Path, spec: str = GOOD, tasks: str = "- [ ] T01 the thing (FR-001)\n", research: str | None = None) -> pathlib.Path:
    d = tmp_path / "specs" / "999-a-feature"
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(spec)
    if tasks is not None:
        (d / "tasks.md").write_text(tasks)
    if research is not None:
        (d / "research.md").write_text(research)
    return d


def test_the_correct_form_is_quiet(tmp_path: pathlib.Path) -> None:
    assert lint.lint(_feature(tmp_path)) == []


def test_check_1_a_measured_figure_with_no_pointer(tmp_path: pathlib.Path) -> None:
    d = _feature(tmp_path, GOOD.replace(", measured in `research.md` R1", ""))
    assert any("no pointer" in x and "91 min" in x for x in lint.lint(d))


def test_check_1_leaves_a_count_with_no_unit_alone(tmp_path: pathlib.Path) -> None:
    """ "20 rounds" and "FR-001" are counts, not measurements - asking them for a method is noise."""
    d = _feature(tmp_path, GOOD.replace("The gate took 91 min before this, measured in `research.md` R1.", "Twenty rounds of review, and 8 of them mechanical."))
    assert lint.lint(d) == []


def test_check_1_exempts_the_sections_that_narrate(tmp_path: pathlib.Path) -> None:
    """Review history exists to say what a round found, figures and all."""
    d = _feature(tmp_path, GOOD.replace("Round 1 said 6.7 m and the measurement withdrew it.", "Round 1 said 6.7 m, 22 ft and 91 min, all withdrawn."))
    assert lint.lint(d) == []


def test_check_2_a_withdrawn_figure_still_standing(tmp_path: pathlib.Path) -> None:
    d = _feature(tmp_path, GOOD.replace("**FR-001** A thing.", "**FR-001** Keep the 22 ft clearance."), research="WITHDRAWN: the 22 ft clearance\n")
    assert any("withdrawn text still standing" in x for x in lint.lint(d))


def test_check_2_lets_the_reversal_be_narrated(tmp_path: pathlib.Path) -> None:
    """Decisions recorded and Review history are where a reversal is written down."""
    d = _feature(tmp_path, research="WITHDRAWN: the 22 ft figure stayed out\n")
    assert lint.lint(d) == []


def test_check_2_refuses_a_marker_too_short_to_be_safe(tmp_path: pathlib.Path) -> None:
    """A bare number as the marked text would ban that number from the whole record."""
    d = _feature(tmp_path, research="WITHDRAWN: 22 ft\n")
    assert any("twelve characters" in x for x in lint.lint(d))


def test_check_2_reaches_the_whole_tree(tmp_path: pathlib.Path) -> None:
    """FR-010c: the scan is tree-wide - all five survivals that motivated it were outside `specs/`."""
    d = _feature(tmp_path, research="WITHDRAWN: the 22 ft clearance\n")
    (tmp_path / "specs" / "998-elsewhere").mkdir(parents=True)
    (tmp_path / "specs" / "998-elsewhere" / "spec.md").write_text("## Summary\n\nthe 22 ft clearance\n")
    # the last is EXTENSIONLESS: a Makefile is where this project writes operative prose and figures,
    # and a suffix roster quietly dropped it (the amendment review's finding)
    for name, body in (
        ("docs/outside.md", "the 22 ft clearance\n"),
        ("CLAUDE.md", "a rule resting on the 22 ft clearance\n"),
        ("scripts/tool.py", '"""Keeps the 22 ft clearance."""\n'),
        ("Makefile", '\t: "the 22 ft clearance"\n'),
    ):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(body)
    got = lint.lint(d, tree_root=tmp_path)
    for where in ("998-elsewhere", "outside.md", "CLAUDE.md", "tool.py", "Makefile"):
        assert any(where in x for x in got), f"{where} carries withdrawn text and is not named: {got}"


def test_check_2_leaves_a_verbatim_record_alone(tmp_path: pathlib.Path) -> None:
    """A frozen corpus and a run log are records of what happened, not claims still standing."""
    d = _feature(tmp_path, research="WITHDRAWN: the 22 ft clearance\n")
    for name in ("scripts/fixtures/corpus.json", "dev/run-log/a.json"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text('{"cmd": "the 22 ft clearance"}\n')
    assert lint.lint(d, tree_root=tmp_path) == []


def test_check_2_reads_the_marker_only_where_it_opens_a_line(tmp_path: pathlib.Path) -> None:
    """The sentence DESCRIBING the marker must not declare one - the scan is tree-wide now."""
    d = _feature(tmp_path, research="A `research.md` may mark text WITHDRAWN: <text> like this.\n")
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "outside.md").write_text("<text> like this.\n")
    assert lint.lint(d, tree_root=tmp_path) == []


def test_check_3_an_fr_no_criterion_names(tmp_path: pathlib.Path) -> None:
    d = _feature(tmp_path, GOOD.replace("(FR-001, FR-001a)", "(FR-001)"))
    assert any("FR-001a is named by no success criterion" in x for x in lint.lint(d))


def test_check_3_reads_a_lettered_id_as_its_own(tmp_path: pathlib.Path) -> None:
    """`FR-007a` is not a mention of `FR-007`; the grammar is three digits plus an optional letter."""
    assert lint._ID.findall("see FR-001a and SC-002") == [("FR", "001a"), ("SC", "002")]


def test_check_3_a_criterion_that_names_nothing(tmp_path: pathlib.Path) -> None:
    d = _feature(tmp_path, GOOD.replace("**SC-002** (spec-wide) The gate is green.", "**SC-002** The gate is green."))
    assert any("names no FR" in x for x in lint.lint(d))


def test_check_4_a_task_citing_an_id_the_spec_lost(tmp_path: pathlib.Path) -> None:
    d = _feature(tmp_path, tasks="- [ ] T01 the thing (FR-404)\n")
    assert any("FR-404" in x for x in lint.lint(d))


def test_a_freshly_claimed_spec_with_no_tasks_passes(tmp_path: pathlib.Path) -> None:
    """FR-010a: the number claim and the milestone push carry exactly this shape."""
    d = _feature(tmp_path, "# Feature 999\n\n## Summary\n\nIt took 91 min.\n\n## Functional requirements\n\n**FR-001** A thing.\n", tasks=None)
    (d / "tasks.md").unlink(missing_ok=True)
    assert lint.lint(d) == []


def test_this_feature_s_own_spec_passes_checks_1_and_3() -> None:
    """FR-010b: a rule its author's own document fails is either wrong or the document is."""
    own = REPO / "specs" / "236-catch-mistakes-early-and-cheaply"
    assert (own / "spec.md").is_file()
    assert lint.check_figures(own / "spec.md") == []
    assert lint.check_orphans(own / "spec.md") == []


def test_selftest_passes() -> None:
    lint.selftest()
