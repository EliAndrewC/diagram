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

from l7r.diagram.settlement.homestead_parts.groves import BAMBOO_CULM

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
        assert f'stroke="{BAMBOO_CULM}"' not in stand and "url(#cover-bamboo" in stand, "a bamboo stand drawn mark by mark"
    # SC-002: every scrub or marsh tile in the lines right after the land, before any other ink
    lines = svg.split("\n")
    covers = [i for i, ln in enumerate(lines) if re.search(r'fill="url\(#cover-(grass|reed)', ln)]
    assert covers or not (M.get("commons") or M.get("marshes")), "non-vacuity: a map with scrub or marsh draws its tile"
    land = next(i for i, ln in enumerate(lines) if ln.startswith("<rect width=") and "fill=" in ln)
    # the cover slots right after the land: the tiles' <defs>, then seven covers (`Settlement._header`: the scrub and a pasture's
    # grass, the grass-only band and its thinned edge under a wood in either class - feature 328 wave 57 - and the marsh)
    assert all(land < i <= land + 8 for i in covers), f"a scrub or marsh tile above the land's eight cover slots: lines {covers}, land {land}"
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


def test_inashiros_toe_marsh_has_no_laid_corner_or_straight_run() -> None:
    """Feature 299 SC-001 - the two places the GM named on Inashiro: the toe marsh's top-left corner (laid as a right angle) and
    its right-hand edge (laid as a straight east-west line). On the recorded (drawn) outline, no corner on open ground is
    sharper than 120 degrees and no edge runs straight for long: no segment reaches two thirds of the wave's shortest length (the
    simplified wave's chords run to about 90 ft; the laid line ran 592), except where a field, a dike or the pond cut it (their own straight banks)."""
    import math

    from l7r.diagram.settlement.land.outline import WAVE_LENGTH_FT
    from tests.gate import _pool

    with open(_pool.obtain(os.path.join(_POOL, "hamlets", "inashiro", "inashiro.gen.py")), encoding="utf-8") as fh:
        M = json.load(fh)
    toe = next(m for m in M["marshes"] if m["role"] == "toe")
    ring = [(float(x), float(y)) for x, y in toe["poly"]]
    fields = [Polygon(f["outline"]).buffer(25.0) for f in M.get("fields") or [] if len(f.get("outline") or []) >= 3]
    pond = M.get("pond")
    from shapely.geometry import LineString, Point, box

    # the pond cuts the marsh as its own ellipse (`wet.pond_cut`): only the water and its reed ring are a cut-out here, so a box
    # round the pond - the building keep-out - would show as sharp corners and fail
    near_cut = [*fields] + ([Polygon([(pond[0] + (pond[2] + 10.0) * math.cos(a / 32 * math.pi), pond[1] + (pond[3] + 10.0) * math.sin(a / 32 * math.pi)) for a in range(64)])] if pond else [])
    view = M["meta"]["view"]

    frame = box(view[0], view[1], view[0] + view[2], view[1] + view[3])
    sharp, long_runs = [], []
    n = len(ring)
    for i in range(n):
        a, b, c = ring[i - 1], ring[i], ring[(i + 1) % n]
        if not frame.contains(Point(b)) or any(z.contains(Point(b)) for z in near_cut):
            continue
        v1, v2 = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        n1, n2 = math.hypot(*v1), math.hypot(*v2)
        if n1 and n2 and math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2))))) < 120.0:
            sharp.append(b)
        seg = LineString([b, c])
        if seg.length > WAVE_LENGTH_FT[0] * 2 / 3 and frame.contains(seg) and not any(z.intersects(seg) for z in near_cut):
            long_runs.append((b, c))
    assert not sharp, f"a sharp corner on open ground: {sharp[:5]}"
    assert not long_runs, f"a straight run on open ground: {long_runs[:5]}"
