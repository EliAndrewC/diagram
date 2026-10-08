"""The sheet audit reads a filled rectilinear path as the rects it covers (feature 283)."""

from __future__ import annotations

from l7r.diagram.tools import pack_audit as pa

COURT = "url(#court-earth)"


def _rect(x: float, y: float, w: float, h: float, fill: str) -> str:
    mark = ' id="precinct"' if fill == COURT else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{mark}/>'


def _svg(*bodies: str) -> str:
    return "<svg>" + "".join(bodies) + "</svg>"


def test_a_rectilinear_path_is_read_as_the_rects_it_covers() -> None:
    """Feature 283: an L-shaped or holed ground drawn as a path was invisible to every fills-based check."""
    from l7r.diagram.tools.pack_audit import parse as P

    ell = P._path_rects('<path d="M 0 10 H 20 V 0 H 40 V 30 H 0 Z" fill="url(#garden-stipple)"/>')
    assert sorted((r.x, r.y, r.w, r.h) for r in ell) == [(0, 10, 40, 20), (20, 0, 20, 10)]
    holed = P._path_rects('<path d="M 0 0 H 30 V 30 H 0 Z M 10 10 V 20 H 20 V 10 Z" fill-rule="evenodd" fill="#fff"/>')
    assert sum(r.w * r.h for r in holed) == 900 - 100
    assert P.path_rings("M 0 0 L 10 10 L 0 10 Z") is None, "a diagonal edge"
    assert P.path_rings("M 0 0 q 3 -8 -2 -14") is None, "a curve or a relative step"
    assert P.path_rings("H 10 V 10") is None, "no move to start from"
    assert P.path_rings("M 0 0 H 10") is None, "too few corners to close a ground"
    assert P._path_rects('<path d="M 0 0 H 10 V 10 H 0 Z" fill="none" stroke="#000"/>') == []
    plan = pa.parse_svg(_svg(_rect(0, 0, 300, 300, COURT), '<path d="M 10 10 H 50 V 50 H 10 Z" fill="url(#garden-stipple)"/>'))
    assert any(r.fill == "url(#garden-stipple)" and r.w == 40 for r in plan.open_features)
