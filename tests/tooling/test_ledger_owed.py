"""A ledger row for every pass of every check (feature 371).

The GM, 2026-10-10: *"a log of when our subagent checks find something that needs to be changed and when they don't, so that
we can see how often they are paying off"*. Every check's pass is logged when it returns, with its cost cells; a pass is
answered by a measured-table row carrying its check and those cells. These build a fixture log and ledger.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("ledger_owed", script("ledger_owed.py"))
assert _spec is not None and _spec.loader is not None
lo = importlib.util.module_from_spec(_spec)
sys.modules["ledger_owed"] = lo
_spec.loader.exec_module(lo)

_lint = importlib.util.spec_from_file_location("ledger_lint_for_owed", script("ledger_lint.py"))
assert _lint is not None and _lint.loader is not None
ll = importlib.util.module_from_spec(_lint)
_lint.loader.exec_module(ll)

HEAD = f"# ledger\n\n{ll.MEASURED_HEADING}\n\nprose\n\n| {' | '.join(ll.COLUMNS)} |\n|{'---|' * len(ll.COLUMNS)}\n"


def _pass(check: str = "glyph-check", wall: str = "80 s", tokens: str = "244k in (199k cached) / 7.8k out", subject: str = "copse on inashiro") -> dict[str, str]:
    return {"date": "2026-10-10", "check": check, "subject": subject, "agent": "a1", "wall": wall, "tokens": tokens}


def _row(check: str = "glyph-check", wall: str = "80 s", tokens: str = "244k in (199k cached) / 7.8k out") -> str:
    return f"| 2026-10-10 | {check} | copse on inashiro | PASS | caught nothing | nothing | - | nothing | {wall} | {tokens} |\n"


def test_a_pass_with_no_row_is_owed_and_one_with_its_row_is_not() -> None:
    """SC-001 / SC-002: the row answers by its check and its cost cells."""
    p = _pass()
    assert lo.unanswered([p], HEAD) == [p]
    assert lo.unanswered([p], HEAD + _row()) == []
    assert lo.unanswered([p], HEAD + _row(check="size-audit")) == [p], "another check's row with the same cells does not answer"


def test_two_same_day_rounds_are_told_apart_by_their_cells() -> None:
    """SC-003 / FR-005: one row cannot answer both rounds."""
    r1, r2 = _pass(wall="80 s"), _pass(wall="95 s", tokens="250k in (199k cached) / 8.1k out")
    assert lo.unanswered([r1, r2], HEAD + _row()) == [r2]


def test_the_cells_match_whatever_the_spacing() -> None:
    assert lo.unanswered([_pass()], HEAD + _row(tokens="244k in (199k cached)  /  7.8k out")) == []


def test_the_printed_row_carries_what_is_measured_and_leaves_the_judgment() -> None:
    """SC-004 / FR-003: date, check, subject and cost filled; the five judgment cells for the session."""
    row = lo.row_for(_pass())
    assert row == "| 2026-10-10 | glyph-check | copse on inashiro | ? | ? | ? | ? | ? | 80 s | 244k in (199k cached) / 7.8k out |"
    assert len(row.strip("|").split("|")) == len(ll.COLUMNS)


def test_the_log_is_read_line_by_line_and_a_bad_line_is_skipped(tmp_path: Path) -> None:
    log = tmp_path / "check-passes.jsonl"
    log.write_text(json.dumps(_pass()) + "\nnot json\n" + json.dumps(_pass(wall="95 s")) + "\n")
    assert [p["wall"] for p in lo.load_passes(log)] == ["80 s", "95 s"]
    assert lo.load_passes(tmp_path / "absent.jsonl") == []


@pytest.mark.parametrize(("ledger", "refuse", "rc"), [("", False, 0), ("", True, 1), ("row", True, 0)])
def test_the_command_reports_and_refuses_only_when_asked(tmp_path: Path, ledger: str, refuse: bool, rc: int) -> None:
    """FR-004: a report never fails; `--refuse` fails while a pass is unanswered, and names the row to add."""
    log, led = tmp_path / "check-passes.jsonl", tmp_path / "review-ledger.md"
    log.write_text(json.dumps(_pass()) + "\n")
    led.write_text(HEAD + (_row() if ledger else ""))
    r = subprocess.run([sys.executable, str(script("ledger_owed.py")), "--log", str(log), "--ledger", str(led), *(["--refuse"] if refuse else [])],
                       capture_output=True, text=True, check=False)
    assert r.returncode == rc, r.stderr + r.stdout
    if not ledger:
        assert "| 2026-10-10 | glyph-check | copse on inashiro | ? |" in r.stdout + r.stderr
        assert "LEDGER_ROWS_OK" in r.stdout + r.stderr
