"""`make figures` never re-runs a figure that reaches the deleted Python hamlet engine (feature 444 FR-024; the round arbiter on
ask:444-d7-scope-round3): such a figure is frozen history, listed as not re-measured with the reason, and its command never runs."""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("figures_under_test", REPO / "scripts/measure/figures.py")
figures = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(figures)


def test_a_figure_that_rolls_the_deleted_engine_is_listed_and_never_run(tmp_path: pathlib.Path) -> None:
    ran = tmp_path / "ran"
    (tmp_path / "measurements.json").write_text(
        json.dumps(
            {
                "rolled": {"command": f"touch {ran} l7r/diagram/hamletgen/__main__.py", "value": 1},
                "module": {"command": f"python3 -m l7r.diagram.settlement --touch {ran}", "value": 2},
                "tested": {"command": f"touch {ran} tests/waterfields/", "value": 3},
            }
        )
    )
    failures, _reports, skipped = figures.rerun(tmp_path)
    assert not ran.exists(), "a command that reaches the deleted engine was run"
    assert failures == [] and len(skipped) == 3
    assert all("runs the deleted Python hamlet engine (feature 444)" in s for s in skipped)


def test_a_word_that_is_only_a_word_is_not_the_engine() -> None:
    for command in ("make figures SPEC=specs/444-work-budget-program", "python3 scripts/x.py --settlement-form nucleated", "rust/phases"):
        assert not figures.DELETED_ENGINE.search(command), command
