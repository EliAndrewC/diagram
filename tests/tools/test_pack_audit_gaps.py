"""The aligned-gap finder never pairs two buildings across a third (feature 335, FR-014): `_blocked` compared the third
building's y-extent with the gap's x-interval in the horizontal case."""

from __future__ import annotations

import os

import pytest

from l7r.diagram.tools import pack_audit as pa

COURT = "url(#court-earth)"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _rect(x: float, y: float, w: float, h: float, fill: str) -> str:
    mark = ' id="precinct"' if fill == COURT else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{mark}/>'


def _svg(*bodies: str) -> str:
    return "<svg>" + "".join(bodies) + "</svg>"


def test_aligned_gaps_horizontal_blocked_far_down_the_sheet() -> None:
    """Feature 335 (FR-014): the blocking test compared the third building's y-extent with the gap's x-interval, so the test
    above passed only because its numbers overlap both ways; three buildings in a row lower down were paired across the
    middle one (Ochiba's nagaya to its second storehouse, a 28.7 ft "gap" with the first storehouse standing in it)."""
    plan = pa.parse_svg(
        _svg(
            _rect(0, 0, 300, 400, COURT),
            _rect(10, 300, 40, 60, "#C9A57A"),
            _rect(100, 300, 40, 60, "#C9A57A"),
            _rect(65, 300, 20, 60, "#C9A57A"),
        )
    )
    assert not any(g.orient == "H" and g.ft == pytest.approx(16.7, abs=0.5) for g in pa.aligned_gaps(plan))


def test_aligned_gaps_on_ochiba_pair_no_buildings_across_a_third() -> None:
    """Feature 335 (FR-014): every gap Ochiba's audit reports has nothing built standing between its pair."""
    with open(os.path.join(ROOT, "pool", "magistracies", "ochiba-magistracy", "ochiba-magistracy.svg"), encoding="utf-8") as fh:
        plan = pa.parse_svg(fh.read())
    assert not any(g.orient == "H" and g.ft == pytest.approx(28.7, abs=0.1) for g in pa.aligned_gaps(plan))
