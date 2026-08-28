"""The trunk road's default width is 30 ft everywhere - the drawn default and every manifest fallback agree (feature 144).

WHY: the GM (2026-08-28) raised the default from 26 ft after feature 143 read the Tokaido's 1604 standard as
5 ken (~29.5 ft). A fallback that disagrees with the default is a second, silent width, so this test scans
the engine for the old figure as well as pinning the constant.
"""

from __future__ import annotations

import re
from pathlib import Path

from l7r.diagram.settlement.structures.ground import ROAD_W_FT

ENGINE = Path(__file__).resolve().parents[1] / "l7r"


def test_the_road_default_is_thirty_feet() -> None:
    assert ROAD_W_FT == 30.0


def test_no_manifest_fallback_still_says_twenty_six() -> None:
    stale = [str(p.relative_to(ENGINE)) for p in ENGINE.rglob("*.py") if re.search(r"road_width\", 26\)|road_width\"\) or 26\.0", p.read_text())]
    assert stale == [], f"road_width fallbacks disagreeing with ROAD_W_FT: {stale}"
