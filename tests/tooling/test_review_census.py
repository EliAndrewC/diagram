"""`scripts/_review_census.py` - the ledger's totals by check, the spec's R0 by a command (feature 294, FR-013)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("review_census", REPO / "scripts" / "_review_census.py")
assert _spec and _spec.loader
rc = importlib.util.module_from_spec(_spec)
sys.modules["review_census"] = rc
_spec.loader.exec_module(rc)

R0 = [
    {"agent": "settlement-review", "runs": 5, "not_reviewable_runs": 2, "findings": {"geometric": 3, "judgment": 1, "paperwork": 2, "nothing": 0}, "author_missed_fixed": 2, "wall_min": 12},
    {"agent": "building-review", "runs": 1, "not_reviewable_runs": 0, "findings": {"nothing": 1}, "author_missed_fixed": 0, "wall_min": None},
]
LEDGER = (
    "# L\n\n## Review checks, measured (feature 294 on)\n\n"
    "| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |\n|---|---|---|---|---|---|---|---|---|---|\n"
    "| 2026-10-02 | glyph-check | privy | NEEDS-WORK | reads as a hut | judgment | yes | redrawn | 400 s | 3000k in (2800k cached) / 4.0k out |\n"
    "| 2026-10-02 | glyph-check | privy | NEEDS-WORK | a stale count | paperwork | no | fixed | 400 s | 3000k in (2800k cached) / 4.0k out |\n"
    "| 2026-10-03 | glyph-check | well | NOT-REVIEWABLE | - | nothing | - | - | 30 s | 100k in (90k cached) / 0.5k out |\n"
)


def test_the_old_rows_data_and_the_measured_rows_are_totalled_per_check() -> None:
    t = rc.tally(R0, LEDGER)
    s = t["settlement-review"]
    assert (s["runs"], s["not_reviewable"], s["geometric"], s["judgment"], s["author_missed"], s["wall_s"]) == (5, 2, 3, 1, 2, 720)
    g = t["glyph-check"]
    assert (g["runs"], g["not_reviewable"], g["judgment"], g["paperwork"], g["nothing"], g["author_missed"]) == (2, 1, 1, 1, 1, 1)
    assert g["wall_s"] == 430 and g["tokens_k"] == 3100, "a run's cost is counted once however many findings it has"
    out = rc.report(t)
    assert out.splitlines()[0].startswith("check | runs") and "settlement-review | 5 | 2 | 3 | 1 | 2 | 0 | 2 | 12 | 0.0" in out


def test_a_short_measured_row_is_skipped_and_main_reads_the_clone(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert rc.tally([], LEDGER + "| 2026-10-04 | glyph-check | short |\n")["glyph-check"]["runs"] == 2
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "review-ledger.md").write_text(LEDGER)
    assert rc.main(["--root", str(tmp_path)]) == 0
    assert "glyph-check | 2 | 1" in capsys.readouterr().out
    (tmp_path / "docs" / "review-ledger-r0.json").write_text(json.dumps(R0))
    rc.main(["--root", str(tmp_path)])
    assert "settlement-review | 5" in capsys.readouterr().out
