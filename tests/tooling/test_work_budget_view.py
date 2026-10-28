"""`scripts/measure/work_budget_view.py` - the work budget's standing record in view (feature 443 T04, FR-007, SC-004).

`make land` on engine code and `make speckit-todo` under feature 444's row print the whole roll's line, every stage's status and
the stages that moved between the two newest runs.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("work_budget_view", script("work_budget_view"))
assert _spec is not None and _spec.loader is not None
wv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wv)

RECORD = """# The work budget

| stage | ops @10 | ops @40 | per thing @40 | exponent | calls @40 | budget @40 | ratio | status |
|---|---|---|---|---|---|---|---|---|
| web | 1 | 2,000 | 10 | 1.10 | 5 | 1,500 | 1.3x | budgeted |
| track | 1 | 300 | 3 | 0.90 | 5 | - | - | unbudgeted |
| sink | 1 | 30 | 3 | 0.90 | 5 | - | - | unbudgeted |
| **the whole roll** | 2 | 2,330 | 10 | 1.05 | 15 | - | - | unbudgeted |
"""


def _run(root: Path, stamp: str, web: float, track: float) -> None:
    (root / "dev" / "work-budget").mkdir(parents=True, exist_ok=True)
    stages = {"web": {"per": {"40": {"ops": web}}}, "track": {"per": {"40": {"ops": track}}}, "roll": {"per": {"40": {"ops": web + track}}}}
    (root / "dev" / "work-budget" / f"{stamp}-k.json").write_text(json.dumps({"summary": {"stages": stages}}))


def test_the_summary_holds_the_roll_every_stage_and_what_moved(tmp_path: Path) -> None:
    (tmp_path / "dev").mkdir()
    (tmp_path / "dev" / "work-budget.md").write_text(RECORD)
    _run(tmp_path, "20261028T000000Z", 2100, 300)
    out = wv.lines(tmp_path)
    assert out[0] == "work budget (dev/work-budget.md): the whole roll 2,330 counted operations @40, exponent 1.05, budget -, unbudgeted"
    assert "  budgeted (1): web (1.3x)" in out and "  unbudgeted (2): track, sink" in out
    assert out[-1] == "  moved since the previous run (@40): none", "one run: nothing to compare"
    _run(tmp_path, "20261028T010000Z", 2000, 300)
    assert wv.lines(tmp_path)[-1] == "  moved since the previous run (@40): web 2,100 -> 2,000", "only the stage that moved, the roll left out"


def test_no_record_says_how_to_make_one(tmp_path: Path) -> None:
    assert wv.lines(tmp_path) == ["work budget: no standing record yet - `make work-budget` writes dev/work-budget.md"]


def test_speckit_todo_prints_the_record_under_feature_444(tmp_path: Path) -> None:
    """SC-004: the standing record read in `make speckit-todo`'s output, under 444's row."""
    spec = importlib.util.spec_from_file_location("speckit_todo_wb", script("speckit-todo.py"))
    assert spec is not None and spec.loader is not None
    st = importlib.util.module_from_spec(spec)
    sys.modules["speckit_todo_wb"] = st
    spec.loader.exec_module(st)
    (tmp_path / "dev").mkdir()
    (tmp_path / "dev" / "work-budget.md").write_text(RECORD)
    for name in ("443-tooling", "444-work-budget-program"):
        (tmp_path / "specs" / name).mkdir(parents=True)
        (tmp_path / "specs" / name / "spec.md").write_text("# Feature Specification: x\n\n**Status**: Draft\n")
    lines = st.report(tmp_path / "specs", clones=False).splitlines()
    at = next(i for i, ln in enumerate(lines) if "444-work-budget-program" in ln)
    assert lines[at + 1].strip().startswith("work budget (dev/work-budget.md): the whole roll 2,330")
    out: list[str] = ["  443-tooling  x"]
    st.budget_under_444(out, tmp_path)
    assert out == ["  443-tooling  x"], "no 444 row: nothing printed"


def test_land_prints_the_same_summary() -> None:
    spec = importlib.util.spec_from_file_location("land_wb", script("land.py"))
    assert spec is not None and spec.loader is not None
    lb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lb)
    root = Path(__file__).resolve().parents[2]
    assert lb.work_budget_lines(root) == wv.lines(root)
