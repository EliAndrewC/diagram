"""Every hand-drawn Mode A sheet's captions stand where the one placer puts them (feature 266, FR-013, SC-006).

A hand-drawn sheet's captions are written by hand; `make seat-label` seats them by the cartographic standard. The GM
asked that the notice boards use the standard now and that every other label be able to - so the captions that stood
off their standard seat when the feature landed are recorded in `tests/fixtures/caption_ledger.json`, and each is
excused only while its sheet is unchanged. Revise a sheet and the ledger no longer covers it: every caption on it is
then held to its standard seat, and every `<text>` must carry a tag (spec D9).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from l7r.diagram.tools.seat_label import judge

SKILL = Path(__file__).resolve().parents[2]
LEDGER = json.loads((SKILL / "tests" / "fixtures" / "caption_ledger.json").read_text(encoding="utf-8"))


def hand_sheets() -> list[str]:
    """Every hand-drawn Mode A sheet in the pool: an SVG whose gen does not compose it (`emit_svg`)."""
    out = []
    for svg in sorted([*SKILL.glob("pool/magistracies/*/*.svg"), *SKILL.glob("pool/country-shrines/*/*.svg")]):
        gen = svg.with_suffix(".gen.py")
        if gen.exists() and "emit_svg" not in gen.read_text(encoding="utf-8"):
            out.append(str(svg.relative_to(SKILL)))
    return out


def test_the_census_finds_the_hand_drawn_sheets() -> None:
    sheets = hand_sheets()
    assert len(sheets) >= 4, f"the walk found {sheets} - it is looking in the wrong place"


@pytest.mark.parametrize("sheet", hand_sheets())
def test_every_caption_on_a_hand_drawn_sheet_is_at_its_standard_seat(sheet: str) -> None:
    wrong = judge((SKILL / sheet).read_text(encoding="utf-8"), LEDGER.get(sheet))
    assert not wrong, f"{sheet}: seat these with `make seat-label SHEET={sheet} WRITE=1`:\n  " + "\n  ".join(wrong)
