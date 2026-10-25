"""`make task-start` refuses a held feature's task - feature 417 T02 (plan D4, D9; FR-010)."""

from __future__ import annotations

import pathlib
import shutil
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "gates"))
import plan_hold  # noqa: E402

pytestmark = pytest.mark.tooling


def _feature(specs: pathlib.Path, name: str, status: str, tasks: str) -> pathlib.Path:
    d = specs / name
    d.mkdir(parents=True)
    (d / "spec.md").write_text(f"# Feature\n\n**Status**: {status}\n\n**Affects**: hamlet\n", encoding="utf-8")
    (d / "tasks.md").write_text(tasks, encoding="utf-8")
    return d


@pytest.fixture
def specs(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / ".specify").mkdir()
    shutil.copy(ROOT / ".specify" / "affects.json", tmp_path / ".specify" / "affects.json")
    _feature(tmp_path / "specs", "417-all-seeds-pass", "Draft", "- [ ] T01 measure\n      research: rendering\n")
    return tmp_path / "specs"


HELD = 'In progress; ON HOLD from 2026-10-24 until feature 417 (all seeds pass) closes - the GM: "on hold"'
TASKS = (
    "- [ ] T106 the wood shed's seat turned, in `l7r/diagram/settlement/homestead_parts/fixture_seats.py`\n"
    "      research: rendering\n"
    "- [ ] T107 the hook's message in `scripts/hooks/x-hooks.sh` reworded\n      research: rendering\n"
    "- [ ] T109 the shed turned by its roll (fixture_seats.wood_seat)\n      research: rendering\n"
    "- [ ] T110 the turn mended\n      research: rendering\n"
    "- [ ] T108 a physical task\n      research: physical\n"
)


def test_an_engine_task_of_a_held_feature_is_refused_naming_the_feature_it_waits_on_and_hold_ok_does_not_admit_it(specs):
    d = _feature(specs, "405-engine-findings", HELD, TASKS)
    # a path under l7r/; research: physical; a task not found; an engine module by its name, as 405's tasks name them; and a
    # task that names nothing (unsure counts as engine, plan D9)
    for task in ("T106", "T108", "T999", "T109", "T110"):
        why = plan_hold.refusal(d, task, None, "")
        assert "ON HOLD until 417-all-seeds-pass closes" in why and "no escape" in why
        assert plan_hold.refusal(d, task, None, "a reason given") == why


def test_a_task_whose_plan_section_names_an_engine_path_is_an_engine_task(specs):
    d = _feature(specs, "405-engine-findings", HELD, TASKS)
    assert "no escape" in plan_hold.refusal(d, "T107", "### T107 Decisions\n- D1 edits pool/hamlets/inashiro.gen.py", "x y")


def test_a_non_engine_task_of_a_held_feature_starts_only_with_hold_ok(specs):
    d = _feature(specs, "405-engine-findings", HELD, TASKS)
    why = plan_hold.refusal(d, "T107", "### T107 Decisions\n- D1 the hook's words", "")
    assert "HOLD_OK=" in why and "no escape" not in why
    assert plan_hold.refusal(d, "T107", None, "the GM asked for it now") == ""


def test_the_hold_ends_when_the_feature_it_waits_on_closes(specs):
    d = _feature(specs, "405-engine-findings", HELD, TASKS)
    (specs / "417-all-seeds-pass" / "tasks.md").write_text("- [x] T01 measure\n", encoding="utf-8")
    assert plan_hold.refusal(d, "T106", None, "") == ""


def test_a_feature_with_no_hold_in_its_status_is_not_held(specs):
    d = _feature(specs, "406-other", "In progress", TASKS)
    assert plan_hold.refusal(d, "T106", None, "") == ""


def test_the_three_held_claims_features_are_held_by_417_while_it_is_open_a_wrapped_status_line_included():
    for name in ("405-engine-findings-from-385", "372-match-the-research-remaining", "384-match-the-research-remainder"):
        by = plan_hold.holder(ROOT / "specs" / name)
        assert by is not None and by.name == "417-all-seeds-pass", name


def test_task_start_refuses_a_held_engine_task_and_starts_a_non_engine_one_with_hold_ok(specs, monkeypatch, capsys):
    import subprocess

    root = specs.parent
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    _feature(specs, "405-engine-findings", HELD, TASKS)
    monkeypatch.chdir(root)
    import plan_gate

    monkeypatch.delenv("HOLD_OK", raising=False)
    assert plan_gate.main(["task-start", "405", "T106"]) == 2
    assert "ON HOLD until 417-all-seeds-pass closes" in capsys.readouterr().err
    assert not (root / ".git" / "active-task").exists(), "a refused start marks nothing"
    monkeypatch.setenv("HOLD_OK", "the GM asked for it now")
    assert plan_gate.main(["task-start", "405", "T106"]) == 2, "no escape for an engine task"
    assert plan_gate.main(["task-start", "405", "T107"]) == 0
