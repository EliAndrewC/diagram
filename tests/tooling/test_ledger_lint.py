"""`scripts/reviews/ledger_lint.py` - every measured ledger row carries its check, class and cost (feature 294, FR-010)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("ledger_lint", REPO / "scripts/reviews/ledger_lint.py")
assert _spec and _spec.loader
ll = importlib.util.module_from_spec(_spec)
sys.modules["ledger_lint"] = ll
_spec.loader.exec_module(ll)

HEAD = f"# Ledger\n\n| old | row |\n\n{ll.MEASURED_HEADING}\n\n| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |\n|---|---|---|---|---|---|---|---|---|---|\n"
GOOD = "| 2026-10-02 | glyph-check | privy on inashiro | PASS | reads as a privy | nothing | - | - | 412 s | 3100k in (2900k cached) / 4.2k out |\n"


def test_a_measured_row_with_every_cell_passes_and_the_old_rows_are_not_read() -> None:
    assert ll.problems(HEAD + GOOD + "\n## Later\n\n| x | y |\n") == []
    assert ll.problems("no table here") == []


def test_each_missing_cell_is_named_by_its_line() -> None:
    bad = (
        "| 2026-10-02 | eyeball | x | PASS | y | judgment | yes | fixed | 412 s | 3100k in (2900k cached) / 4.2k out |\n"
        "| 2026-10-02 | glyph-check | x | PASS | y | style | maybe | fixed | ~7 min | lots |\n"
        "| 2026-10-02 | glyph-check | short |\n"
    )
    got = ll.problems(HEAD + bad)
    assert any("check 'eyeball'" in p for p in got)
    assert any("class 'style'" in p for p in got) and any("author missed? 'maybe'" in p for p in got)
    assert any("cost cells" in p for p in got) and any("3 cells" in p for p in got)
    assert all(p.startswith("line ") for p in got)


def test_main_reads_a_ledger_and_the_repository_s_own_is_clean(tmp_path: Path, capsys) -> None:
    f = tmp_path / "ledger.md"
    f.write_text(HEAD + "| 2026-10-02 | eyeball | x | PASS | y | judgment | yes | fixed | 4 s | 1k in (0k cached) / 0.1k out |\n")
    assert ll.main([str(f)]) == 1 and "eyeball" in capsys.readouterr().out
    assert ll.main([]) == 0, "the repository's own ledger"
