"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: lane web plumbing - NONE"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement.rolling.gap_ways import KNOT_FT

from .geom import _components

_KNOT_FT = KNOT_FT  # ends of different lanes this close are one junction, not several - the seating's figure (`gap_ways.KNOT_FT`)
"""Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft meet at one node"""


def web_pieces(lanes: Sequence[Mapping[str, Any]]) -> int:
    """How many connected pieces the lane web is in - a lane of fewer than two points is not a piece.

    LIFTED OUT OF `_smooth_web` (feature 146, GM 2026-08-28: *"if something is only available as an inner
    function in a closure, then you can move it out into its own function to make it more unit testable"*).
    It closed over `lanes` alone and is a pure count, so a test can hand it three dicts instead of building
    a settlement, a fabric and a water list to reach it."""
    ways = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    comp = _components(ways, 4.0)
    return len({comp[m] for m in range(len(ways)) if len(ways[m]) >= 2})
