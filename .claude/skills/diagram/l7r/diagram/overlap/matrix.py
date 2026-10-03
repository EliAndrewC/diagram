"""The overlap MATRIX (was: shared gate helpers, overlap policy): matrix_violations, check_ring_road_clear, matrix_extents, GridIndex, forest_reveal_x, torii_halfbox, FOREST_REVEAL_FT, CANOPY_STRUCT_KEYS, ... - bodies verbatim from check_village.py (feature 024 package split; SCC-packed, see split_package.py).

Research: matrix plumbing - NONE: extraction, indexing and pair tests over the taxonomy
"""

import math
from collections.abc import Mapping
from typing import Any

from l7r.diagram.settlement import torii_halfbox as torii_halfbox  # the engine's own box, no mirror to keep in sync (feature 268)

from .registry import box_of, element_extents, elements, pair_forbidden, private_well
from .taxonomy import (
    _MATRIX_PERMISSIVE,
    OVERLAP_CLASS,
    Poly,
    point_in_poly,
    poly_dist,
    seg_dist,
    segments_cross,
)


def matrix_violations(M: Mapping[str, Any]) -> list[tuple[str, str, float, float]]:
    """Every FORBIDDEN overlap on the map, as (key_a, key_b, x, y).

    The same two functions the registry of what stands asks at record time (feature 287 M8, `registry.py`): the
    extractor `element_extents` and the pair test `pair_forbidden`, whose conditional permissions depend on the two
    RECORDS rather than on their classes alone (an annex on its own parent, two annexes of one household, a trade
    work's private well inside its own court). The finished map is judged by what the placer was held to."""
    ext = matrix_extents(M)
    priv = {pw for w_ in M.get("wells", []) or [] if (pw := private_well(w_))}
    boxes = [box_of(p) for _k, p, _i, _pa in ext]
    # CLAMP THE INDEX BOX TO THE CANVAS. GridIndex.add inserts under every cell an item's bbox touches, so one feature
    # reaching far off-map costs a dict entry per 120 px in BOTH axes. A malformed map is not hypothetical - a fixture
    # planting a wall vertex at 9,000,000 on a 3,200 px canvas is ~5.6 BILLION cells (found the hard way, 2026-07-26).
    # The index only PRUNES - every surviving pair is still tested against the real polygons - so clamping changes no
    # verdict for anything on the map. Clamp for BOTH insert and query: `near_rect` walks the cells of the box it is GIVEN.
    _mx_w = float(M.get("meta", {}).get("W") or 4000)
    _mx_h = float(M.get("meta", {}).get("H") or 4000)

    def _mx_clamp(b: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        return (max(b[0], -_mx_w), max(b[1], -_mx_h), min(b[2], _mx_w * 2), min(b[3], _mx_h * 2))

    cboxes = [_mx_clamp(b) for b in boxes]
    gi = GridIndex(120)
    for idx, cb in enumerate(cboxes):
        if cb[2] < cb[0] or cb[3] < cb[1]:
            continue  # wholly off the canvas - nothing on the map can meet it
        gi.add(cb[0], cb[1], cb[2], cb[3], idx)
    out: list[tuple[str, str, float, float]] = []
    for i, ei in enumerate(ext):
        cbi = cboxes[i]
        if cbi[2] < cbi[0] or cbi[3] < cbi[1]:
            continue
        for j in gi.near_rect(*cbi):
            if j <= i:
                continue
            if pair_forbidden(ei, ext[j], priv, boxes[i], boxes[j]):
                pi = ei[1]
                out.append((ei[0], ext[j][0], round(sum(q[0] for q in pi) / len(pi)), round(sum(q[1] for q in pi) / len(pi))))
    return out


def matrix_extents(M: Mapping[str, Any]) -> list[tuple[str, list[tuple[float, float]], Any, Any]]:
    """Every DRAWN extent on the map as (key, polygon, own_id, parent_id): `element_extents` over every record of every
    key the matrix tests (permissive classes are never extracted - see `registry.element_extents` for why the ink and
    not the envelope)."""
    out: list[tuple[str, list[tuple[float, float]], Any, Any]] = []
    for k, cls in OVERLAP_CLASS.items():
        if cls in _MATRIX_PERMISSIVE:
            continue
        for o_ in elements(k, M.get(k)):
            out.extend(element_extents(k, o_, M))
    return out


class GridIndex:
    """A uniform-grid spatial index for the "what is near here?" queries several checks make
    THOUSANDS of times against the same features. Each item is inserted under every cell its
    influence bbox touches; a query returns only the items in the queried cell(s), which is a
    superset of the true neighbors, so the caller still runs its exact test - the index prunes,
    it never decides.

    WHY (profiled 2026-07-25, after a feature spent an hour and the gate was suspected): the
    naive form is a full scan per query, and two checks were doing exactly that.
    `city_fan_heads_quilted` tested each of ~3,000 canal-side sample points against EVERY plot
    polygon and ditch on the map - 14M segment-distance calls, ~58% of Tango's 17s gate.
    `structures_clear_of_trees` tested every structure against every drawn crown - 1,049 x 7,440
    on Tango. Both are point-vs-local-geometry questions, so pruning to the local cell is a pure
    constant-factor win with identical verdicts (the gate's whole regression corpus is replayed
    against the pre-index results to prove that).

    Cell size is the one tuning knob: too small wastes memory on cell lists, too large stops
    pruning. Pick it near the size of the features being indexed."""

    __slots__ = ("cell", "bins")

    def __init__(self, cell: float) -> None:
        self.cell = max(float(cell), 1.0)
        self.bins: dict[tuple[int, int], list[Any]] = {}

    def add(self, x0: float, y0: float, x1: float, y1: float, payload: Any) -> None:
        """Index `payload` under every cell its influence bbox touches."""
        c = self.cell
        for gx in range(int(x0 // c), int(x1 // c) + 1):
            for gy in range(int(y0 // c), int(y1 // c) + 1):
                self.bins.setdefault((gx, gy), []).append(payload)

    def near(self, x: float, y: float) -> list[Any]:
        """Candidates whose influence bbox may reach (x, y). Empty list when nothing is close."""
        return self.bins.get((int(x // self.cell), int(y // self.cell)), [])

    def near_rect(self, x0: float, y0: float, x1: float, y1: float) -> list[Any]:
        """Candidates near any part of a rect, de-duplicated by identity (an item spanning several
        of the queried cells is returned once)."""
        c = self.cell
        seen: dict[int, Any] = {}
        for gx in range(int(x0 // c), int(x1 // c) + 1):
            for gy in range(int(y0 // c), int(y1 // c) + 1):
                for it in self.bins.get((gx, gy), ()):
                    seen[id(it)] = it
        return list(seen.values())


def forest_reveal_x(forest: Poly, edge: Any, reveal: float, w: float) -> list[float]:
    """Mirror of settlement.forest_reveal_x (keep in sync): the x-values a canvas-filling FOREST
    contributes to the frame. The wood is drawn to the canvas edge, but the crop reveals only the
    tree line plus `reveal` px of canopy behind it - deeper in it is identical crowns, and holding
    the frame open for them is wasted image. This is the crop rule, so crop_hugs_content (which
    gates how tight the crop is) has to measure by exactly the same rule.

    Research: forest crop - CONVENTION: the frame shows the tree line and a strip of canopy behind it
    """
    if not edge:
        return [min(max(p[0], 0), w) for p in forest]
    ex = [min(max(p[0], 0), w) for p in edge]
    return ex + [min(x + reveal, w) for x in ex]


FOREST_REVEAL_FT = 110.0  # mirrors settlement.FOREST_REVEAL_FT - how deep the crop reveals a canvas-filling wood
"""Research: forest reveal - CONVENTION: 110 ft of canopy behind the tree line"""

# Mirrors settlement._CANOPY_STRUCT_KEYS (keep in sync): every ROOFED structure a tree may not be drawn on.
CANOPY_STRUCT_KEYS = (
    "houses",
    "farm_fixtures",
    "buildings",
    "storehouses",
    "flophouses",
    "byres",
    "farm_sheds",
    "retirement_houses",
    "religious",
    "shrines",
    "manors",
    "ministries",
    "inspection_stations",
    "merchant_estates",
    "fire_towers",
    "drum_towers",
    "breweries",
    "pawnshops",
    "bathhouses",
    "oil_presses",
    "kilns",
    "farriers",
    "mausoleums",
    "gate_structs",
    "wall_towers",
    "martial_halls",
    "dojos",
)
"""Research: no crown on a roof - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: a clump stands against a building, never on it"""

# Martial training in a provincial city (GM 2026-07-25). The first two mirror
# settlement.DOJO_SAMURAI_FRAC / DOJO_PER_SAMURAI - keep in sync, they are the roll the gate holds
# the map to. RANGE_FT is the kyudo standard 28 m shot (92 ft), rounded down to the ~90 ft clear
# lane the Mode A azuchi already uses. QUARTER_PX is "in or against the samurai neighborhood" at the
# city rung (3 ft/px -> ~780 real ft, about a quarter's width), not a precise siting rule.
DOJO_SAMURAI_FRAC = 0.10
"""Research: dojo samurai share - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: 0.10, mirrored from the settlement"""

DOJO_PER_SAMURAI = 200
"""Research: private dojo count - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: one for every 200 resident samurai"""

DOJO_RANGE_FT = 90.0
"""Research: archery lane - research/questions/0164-drill-grounds-archery-ranges-and-riding-grounds-jiaochang-yaba-baba.drawing.html: 90 ft, the 28 m kyudo shot rounded down"""

DOJO_QUARTER_PX = 260.0
"""Research: dojo near the samurai quarter - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: within 260 px, about 780 ft at the city rung"""


def poly_gap(a: Poly, b: Poly) -> float:
    """Minimum distance between two polygons; 0.0 if they overlap, touch, or one contains the other."""
    na, nb = len(a), len(b)
    if any(point_in_poly(x, y, b) for x, y in a) or any(point_in_poly(x, y, a) for x, y in b):
        return 0.0
    if any(segments_cross(a[i], a[(i + 1) % na], b[j], b[(j + 1) % nb]) for i in range(na) for j in range(nb)):
        return 0.0
    return min(min(poly_dist(x, y, b) for x, y in a), min(poly_dist(x, y, a) for x, y in b))


def edge_dist(px: float, py: float, poly: Poly) -> float:
    return min(seg_dist(px, py, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def polyline_len(poly: Poly) -> float:
    return sum(math.hypot(poly[i + 1][0] - poly[i][0], poly[i + 1][1] - poly[i][1]) for i in range(len(poly) - 1))
