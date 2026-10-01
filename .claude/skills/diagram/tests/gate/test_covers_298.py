"""Feature 298 SC-001 / SC-002 on the shipped hamlets: the scrub's grass, the marsh's reeds and the bamboo stands are tiles, not
glyphs; the scrub and marsh tiles lie at the bottom of the stack, right above the land; and no scrub tile covers a swept
clearing."""

from __future__ import annotations

import glob
import json
import os
import re

import pytest
from shapely.geometry import Polygon

_POOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pool")
_GLYPHS = {
    "grass blade": r'<g stroke="#A7A860"',
    "brush dot": r'fill="#94A063"',
    "reed": r'<g stroke="#6E9377"',
    "wet tint": r'fill="#9FBBAE"',
    "glint": r'<ellipse[^>]*fill="#C2D6CE"',
}


def _pattern_free(svg: str) -> str:
    """The ink outside the <pattern> tiles - where a glyph drawn one by one would be."""
    return re.sub(r"<pattern .*?</pattern>", "", svg, flags=re.S)


@pytest.mark.parametrize("gen", sorted(glob.glob(os.path.join(_POOL, "hamlets", "*", "*.gen.py"))), ids=os.path.basename)
def test_the_covers_are_tiles_at_the_bottom_and_leave_the_clearings_bare(gen: str) -> None:
    from tests.gate import _pool

    manifest_path = _pool.obtain(gen)
    with open(manifest_path, encoding="utf-8") as fh:
        M = json.load(fh)
    with open(manifest_path[: -len(".json")] + ".svg", encoding="utf-8") as fh:
        svg = fh.read()
    ink = _pattern_free(svg)
    found = {name: len(re.findall(pat, ink)) for name, pat in _GLYPHS.items()}
    assert not any(found.values()), f"a cover glyph drawn one by one: {found}"
    for stand in re.findall(r'<g class="bamboo">(.*?)</g>', ink, flags=re.S):
        assert "#9AAE3C" not in stand and "url(#cover-bamboo" in stand, "a bamboo stand drawn mark by mark"
    # SC-002: every scrub or marsh tile in the lines right after the land, before any other ink
    lines = svg.split("\n")
    covers = [i for i, ln in enumerate(lines) if re.search(r'fill="url\(#cover-(grass|reed)', ln)]
    assert covers or not (M.get("commons") or M.get("marshes")), "non-vacuity: a map with scrub or marsh draws its tile"
    land = next(i for i, ln in enumerate(lines) if ln.startswith("<rect width=") and "fill=" in ln)
    assert all(land < i <= land + 4 for i in covers), f"a scrub or marsh tile above the land's four cover slots: lines {covers}, land {land}"
    # ...and no scrub tile on a swept clearing
    clearings = [Polygon(c["poly"]).buffer(0) for c in M.get("clearings") or [] if len(c.get("poly") or []) >= 3]
    for rec in M.get("commons") or []:
        shape = Polygon()
        for ring in rec.get("cover") or []:
            shape = shape.symmetric_difference(Polygon(ring).buffer(0)) if len(ring) >= 3 else shape  # even-odd: holes bare
        for c in clearings:
            assert shape.intersection(c).area < 2.0, "a scrub tile on a swept clearing"
    # FR-006: the trees are still drawn one by one
    assert M.get("tree_crowns"), "the crowns are recorded and drawn individually"
