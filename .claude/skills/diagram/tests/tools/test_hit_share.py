"""Feature 294 B6: who answers the pointer over each class's visible ink (`tools/hit_share.py`)."""

from __future__ import annotations

import pytest

from l7r.diagram.tools import hit_share

pytestmark = pytest.mark.renders  # it renders tiny synthetic id maps on purpose

SVG = (
    '<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">'
    '<rect width="40" height="40" fill="#EFE3C2"/>'
    '<g class="f f-byre" data-k="byre"><rect x="2" y="2" width="10" height="10" fill="#8B7355"/></g>'
    '<g class="f f-mulberry-dike" data-k="mulberry dike"><rect x="20" y="20" width="10" height="10" fill="#557755"/>'
    '<polygon class="hit" points="0,0 8,0 8,12 0,12" fill="none" style="pointer-events: fill"/></g>'
    '<g class="f f-marsh" data-k="marsh"><polygon class="hit" points="32,32 38,32 38,38" fill="none" style="pointer-events: fill"/></g>'
    "</svg>"
)


def test_a_region_over_another_class_takes_its_share_and_is_named() -> None:
    """Seeded: the recorded case's shape - a lifted region polygon over another class's ink (a sty under a sluice's box)."""
    got = hit_share.shares(SVG)
    assert got is not None
    share, thief, n = got["byre"]
    assert n == 100 and abs(share - 0.4) < 0.05 and thief == "mulberry dike"
    assert got["mulberry dike"][0] == 1.0 and got["mulberry dike"][1] is None
    assert "marsh" not in got, "a class with no visible ink has no share to measure"


def test_the_page_svg_and_the_hit_geometry_are_found() -> None:
    assert hit_share.page_svg("<html><body>" + SVG + "</body></html>") == SVG
    assert hit_share.page_svg("<html></html>") is None
    stripped = hit_share.without_hits(SVG + '<g class="hit" fill="none" style="pointer-events: fill"><rect x="1"/></g><path class="hit" style="pointer-events: stroke"/>')
    assert "pointer-events" not in stripped and 'class="hit"' not in stripped


def test_a_page_with_no_class_groups_or_no_renderer_has_no_shares(monkeypatch: pytest.MonkeyPatch) -> None:
    assert hit_share.shares('<svg id="map" xmlns="http://www.w3.org/2000/svg"></svg>') is None
    monkeypatch.setattr(hit_share.raster, "id_map", lambda *_a, **_k: (None, {}))
    assert hit_share.shares(SVG) is None
