"""FIND a spot and commit to it: the spiral searches, the two compaction slides, the nucleated garden-side choice, the legacy per-house solver.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.

Research: search and prefilter plumbing - NONE
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class PlacerMixin:
    _NUC_SIDES = ("SE", "SW", "E", "W")  # garden-side preference: sunny south strip first, walls as fallback
    """Research: garden side preference - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the sunny south corners first, the east and west walls after"""
