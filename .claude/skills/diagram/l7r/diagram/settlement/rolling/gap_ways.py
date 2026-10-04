"""THE WAYS LAID IN THE GAPS (feature 318, Amendments 2 and 3, plan D12-D13).

The GM, 2026-10-03: *"if there is a minimum distance between homesteads then doesn't that guarantee that it will always be
possible to put a lane connecting the path to the lane network?"* - and, told it would cost time, *"I still want A for how it
shapes the map, based on that research finding"*: the record's own reading of a clustered village's lanes as the gaps left
between the house plots (research/questions/0081-village-lanes.html, a GUESS - no page states it; Smith 1899 is the nearest,
houses first and the paths worn after).

So no way is searched while houses are seated: the growth parts every two homesteads by a lane's threading gap
(`growth.grow_gap`), each seat asks only whether its yard opens onto lane ground (`SeatRegion.opens`), and once the last house
stands this module lays every household's way ONCE, in the gaps:

1. LANE GROUND as one raster over the cluster (`lane_layers`): the homesteads held off by the corridor's half-width - counted
   per cell, so a household's own search can lift its own - the reserved wood seats by the lane gap, and the site's ground by
   the free-ground raster, its uncertain cells asked exactly (`access.site_samples_clear` via the corridor's own test).
2. ONE FLOOD from the way out (the exit strip, the field's corridor): the cheapest walk to every cell, each step dearer beside
   blocked ground so a way keeps to the middle of its gap (`flood`).
3. Each household, nearest the way out first: a small search out of its own homestead from its dooryard doors, off its house,
   beds, outbuildings and fixtures (`way_out`), traced back along the flood to the way out - or to a way already laid, joined
   at a T where it comes within `JOIN_FT` (`trace`) - pulled taut and admitted by the corridor's own predicate
   (`access.admitted`: its legs, then the whole tree's lane law). The first admitted of its exits is reserved and recorded as
   the household's corridor, exactly as the seating recorded one before, so the web draws it unchanged.
4. A household none of its exits gives an admitted way is reached across the yard of the nearest household with a way: THE
   PINCH (`pinch`), the GM: *"it's okay for people to cut through neighbors' yards in a pinch"*.

A household seated at a tight seat (feature 317) is tried too: a way laid for it ends its passage where it stands (FR-001).

Research:
    the ways laid in the gaps - GUESS research/questions/0081-village-lanes.drawing.html: the lanes as the gaps left between the house plots, the record's own reading, no page stating it
    raster, flood and search plumbing - NONE: the cells, steps and marks the passes above are built from
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._geom import Pt, seg_closest
from .access import _standing_memo, admitted, doors_of, doubles_back, fixtures_clear, house_clear, house_gap, legs, parts_clear, reserve, site_samples_clear, standing_ground
from .route import taut

if TYPE_CHECKING:
    from ..core import Settlement

#: The lane raster's cell, in px: the 6 ft band a way's line has between two homesteads parted by the threading gap always holds a
#: cell's center (MEASURED, research R4: 4 px reached as many houses and cost 0.3 s more a map; 6 px left houses unreached).
GAP_CELL = 5.0
"""Research: lane raster cell - NONE: a raster's resolution, measured (specs/318-grow-outward-no-restart/research.md R4)"""
#: How far past the homesteads the raster runs, in px: room for a way round the cluster's outside.
GAP_MARGIN_PX = 160.0
"""Research: lane raster margin - NONE: the raster's extent"""
#: The flood runs this far past the last household's ring, in px: room for a household's search to choose among its exits.
FLOOD_PAST_PX = 400.0
"""Research: flood extent - NONE: a search breadth"""
#: How much dearer a step beside blocked ground is - the share of blocked cells within `CENTER_CELLS` of it, times this: a way
#: keeps to the middle of its gap (a GUESS for a worn path's taking the open middle of the ground between two plots).
CENTER_WEIGHT = 3.0
"""Research: a way keeps to the middle of its gap - GUESS: a step beside blocked ground counted up to four times dearer"""
CENTER_CELLS = 3
"""Research: the middle of a gap - NONE: the neighborhood the weight reads, in cells"""
#: The ring about a homestead where its search meets the flood, in cells past the corridor's half-width.
RING_CELLS = 4
"""Research: a homestead's ring - NONE: the search's extent about the homestead, in cells"""
#: How many distinct ways out a household tries (MEASURED, research R4: one way out reached every house on 5 of 9 maps, six on 6).
GAP_TRIES = 6
"""Research: ways out tried - NONE: a search breadth, measured (research R4)"""
#: The most legs a way may take (`route.taut`): a gap way bends at plot corners, more often than a straight path does.
GAP_LEGS = 12
"""Research:
    a way bends at plot corners - research/questions/0081-village-lanes.html: the record's own reading, "a lane runs straight between plot corners and bends at one"
    at most twelve legs - NONE: a search breadth, the taut pull's cap
"""
#: A way coming within this of a way already laid joins it there, at a T, rather than running beside it: under the shadow rule's
#: 30 ft (`WEB_SHADOW_FT`, a way beside another past a pitch), MEASURED (research R4: 10 of 14 refusals were the doubled band).
JOIN_FT = 25.0
"""Research: ways join at a T - UNRESEARCHED: a 25 ft join radius, under the 30 ft shadow; the T itself is the drawing page's"""
#: ...and where a way joined there breaks the tree's lane law, it is tried joined farther off (`JOIN_FAR_FT`), then run on to the way
#: out, the first the law admits taken (MEASURED, research R5).
JOIN_FAR_FT = 45.0
"""Research: a farther join - UNRESEARCHED: a way joins a way laid before it at a T; tried 45 ft off where the nearer join breaks the lane law"""

_STEPS = ((-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, math.sqrt(2.0)), (1, 1, math.sqrt(2.0)), (-1, 1, math.sqrt(2.0)), (1, -1, math.sqrt(2.0)))
"""Research: plumbing - NONE: the eight steps between raster cells and their lengths"""


class Layers:
    """Lane ground over the cluster (`lane_layers`): cell centers `cx`, `cy`; `cover`, how many homesteads hold each cell off;
    `spans`, each homestead box's cell span (`id(box)` keyed); `site`, the site's ground and the wood seats.

    Research: lane ground - research/questions/0081-village-lanes.drawing.html: a lane keeps its clearance off every homestead, crop and water (the woodlots' seats: UNRESEARCHED)
    """

    def __init__(self, x0: float, y0: float, nx: int, ny: int, cell: float) -> None:
        """Research: plumbing - NONE: the raster's arrays, empty"""
        import numpy as np

        self.x0, self.y0, self.nx, self.ny, self.cell = x0, y0, nx, ny, cell
        self.cx = x0 + (np.arange(nx) + 0.5) * cell
        self.cy = y0 + (np.arange(ny) + 0.5) * cell
        self.cover = np.zeros((nx, ny), np.int16)
        self.site = np.zeros((nx, ny), bool)
        self.spans: dict[int, tuple[int, int, int, int]] = {}

    def span(self, x0: float, y0: float, x1: float, y1: float) -> tuple[int, int, int, int]:
        """The cells whose centers lie in the box.

        Research: plumbing - NONE: raster indexing
        """
        import numpy as np

        return int(np.searchsorted(self.cx, x0)), int(np.searchsorted(self.cx, x1)), int(np.searchsorted(self.cy, y0)), int(np.searchsorted(self.cy, y1))

    def cell_of(self, p: Pt) -> tuple[int, int] | None:
        """The cell holding `p`, or None off the raster.

        Research: plumbing - NONE: raster indexing
        """
        i, j = int((p[0] - self.x0) // self.cell), int((p[1] - self.y0) // self.cell)
        return (i, j) if 0 <= i < self.nx and 0 <= j < self.ny else None

    def at(self, c: tuple[int, int]) -> Pt:
        """Research: plumbing - NONE: a cell's center"""
        return (float(self.cx[c[0]]), float(self.cy[c[1]]))

    def blocked(self) -> Any:
        """Research: plumbing - NONE: the two layers combined"""
        return self.site | (self.cover > 0)


def lane_layers(s: Settlement, boxes: Sequence[Any], segs: Sequence[tuple[Pt, Pt]], half: float, cell: float = GAP_CELL) -> Layers:
    """Lane ground over the homesteads `boxes` (`(cx, cy, w, h)`) and the way out `segs`, `GAP_MARGIN_PX` round them.

    Research: lane ground - research/questions/0081-village-lanes.drawing.html: a way keeps the corridor's half-width off every homestead and to ground the site admits; the lane gap off the woodlots' seats is UNRESEARCHED
    Research: the half-width from the way's line - GUESS: 7 ft from the way's line, so a 3 ft tread's edge stands 5.5 ft off a fence the page holds 7 ft clear
    """
    import numpy as np

    xs = [b[0] - b[2] / 2 for b in boxes] + [p[0] for a, b in segs for p in (a, b)]
    ys = [b[1] - b[3] / 2 for b in boxes] + [p[1] for a, b in segs for p in (a, b)]
    xe = [b[0] + b[2] / 2 for b in boxes] + [p[0] for a, b in segs for p in (a, b)]
    ye = [b[1] + b[3] / 2 for b in boxes] + [p[1] for a, b in segs for p in (a, b)]
    x0, y0 = max(0.0, min(xs) - GAP_MARGIN_PX), max(0.0, min(ys) - GAP_MARGIN_PX)
    x1, y1 = min(float(s.W), max(xe) + GAP_MARGIN_PX), min(float(s.H), max(ye) + GAP_MARGIN_PX)
    L = Layers(x0, y0, int((x1 - x0) // cell) + 1, int((y1 - y0) // cell) + 1, cell)
    for b in boxes:
        sp = L.span(b[0] - b[2] / 2 - half, b[1] - b[3] / 2 - half, b[0] + b[2] / 2 + half, b[1] + b[3] / 2 + half)
        L.cover[sp[0] : sp[1], sp[2] : sp[3]] += 1
        L.spans[id(b)] = sp
    wood = getattr(s, "_wood", None)
    if wood is not None:  # the households' reserved wood seats, held off by the lane gap
        g = float(wood.lane_gap)
        for bucket in wood.seats.buckets.values():
            for sx, sy, *_ in bucket:
                i0, i1, j0, j1 = L.span(sx - g, sy - g, sx + g, sy + g)
                L.site[i0:i1, j0:j1] |= (L.cx[i0:i1, None] - sx) ** 2 + (L.cy[None, j0:j1] - sy) ** 2 < g * g
    fg = getattr(s, "_free_ground", None)
    if fg is not None:  # the free-ground raster's surely taken and surely clear cells, the rest asked exactly
        fg.lines_edge_points([])  # its state array, built once
        ki = np.floor((L.cx - fg.x0) / fg.cell).astype(np.int64)
        kj = np.floor((L.cy - fg.y0) / fg.cell).astype(np.int64)
        gi, gj = np.meshgrid(ki, kj, indexing="ij")
        inside = (gi >= 0) & (fg.nx > gi) & (gj >= 0) & (fg.ny > gj)
        state = np.zeros((L.nx, L.ny), np.int8)
        state[inside] = fg._state[gi[inside], gj[inside]]
        L.site |= state == 1
        for a, b in zip(*np.nonzero((state == 0) & ~L.site), strict=True):
            if not site_samples_clear(s, [L.at((int(a), int(b)))]):
                L.site[a, b] = True
    return L


def flood(L: Layers, segs: Sequence[tuple[Pt, Pt]], rings: Sequence[tuple[int, int, int, int]]) -> tuple[Any, Any]:
    """The cheapest walk from the way out `segs` to every cell of lane ground (`dist`) and each cell's step back (`pred`): 8-way,
    no diagonal cutting a blocked corner, each step dearer beside blocked ground (`CENTER_WEIGHT`); stopped `FLOOD_PAST_PX` past
    the first time every ring (a homestead's cell span) has been reached.

    Research: a way keeps to the middle of its gap - GUESS research/questions/0081-village-lanes.drawing.html: a worn path takes the shortest or easiest way; the open middle of the ground between plots
    """
    import numpy as np

    blocked = L.blocked()
    r = CENTER_CELLS
    sat = np.pad(np.pad(blocked.astype(np.int32), r).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    w = 2 * r + 1
    near = sat[w:, w:] - sat[:-w, w:] - sat[w:, :-w] + sat[:-w, :-w]
    weight = 1.0 + CENTER_WEIGHT * near / float(w * w)
    dist = np.full((L.nx, L.ny), np.inf)
    pred = np.full((L.nx, L.ny, 2), -1, np.int32)
    heap: list[tuple[float, int, int]] = []
    for a, b in segs:
        n = max(1, int(math.dist(a, b) / L.cell) + 1)
        for t in range(n + 1):
            c = L.cell_of((a[0] + (b[0] - a[0]) * t / n, a[1] + (b[1] - a[1]) * t / n))
            if c is not None and dist[c] > 0:
                dist[c] = 0.0
                heap.append((0.0, c[0], c[1]))
    heapq.heapify(heap)
    owner: dict[tuple[int, int], list[int]] = {}
    for k, (i0, i1, j0, j1) in enumerate(rings):
        for i in range(i0, i1):
            for j in range(j0, j1):
                owner.setdefault((i, j), []).append(k)
    need, stop = set(range(len(rings))), math.inf
    while heap:
        d, i, j = heapq.heappop(heap)
        if d > stop:
            break
        if need and (i, j) in owner:
            need.difference_update(owner[(i, j)])
            if not need:
                stop = d + FLOOD_PAST_PX
        if d > dist[i, j]:
            continue
        for di, dj, ln in _STEPS:
            u, v = i + di, j + dj
            if 0 <= u < L.nx and 0 <= v < L.ny and not blocked[u, v] and not (di and dj and (blocked[i + di, j] or blocked[i, j + dj])):
                nd = d + ln * L.cell * float(weight[u, v])
                if nd < dist[u, v]:
                    dist[u, v] = nd
                    pred[u, v] = (i, j)
                    heapq.heappush(heap, (nd, u, v))
    return dist, pred


def way_out(L: Layers, dist: Any, doors: Sequence[Pt], area: tuple[int, int, int, int], open_here: Any) -> tuple[list[tuple[float, int, int]], dict[Any, Any]]:
    """A household's search out of its own homestead: from its `doors` over the cells of `area` its own test admits (`open_here`)
    to the flood's cells, 8-way with no corner cut. Returns its exits `(walk + flood, i, j)`, cheapest first, and each cell's
    step back (a door's cell steps back to the door itself).

    Research: a way leaves its own homestead from its dooryard - research/questions/0081-village-lanes.drawing.html: forecourt, the yard's far edge, the flanks past the gable; off its own house, beds and fixtures
    """
    i0, i1, j0, j1 = area
    seen: dict[tuple[int, int], bool] = {}

    def ok(c: tuple[int, int]) -> bool:
        if c not in seen:
            seen[c] = bool(math.isfinite(dist[c]) or open_here(c))
        return seen[c]

    best: dict[tuple[int, int], float] = {}
    back: dict[Any, Any] = {}
    heap: list[tuple[float, int, int]] = []
    for door in doors:
        c = L.cell_of(door)
        if c is not None and c not in best:
            best[c], back[c] = 0.0, door
            heap.append((0.0, c[0], c[1]))
    heapq.heapify(heap)
    exits: list[tuple[float, int, int]] = []
    while heap:  # a cell popped again at a worse distance only re-offers a worse exit, which the picking passes over
        d, i, j = heapq.heappop(heap)
        if math.isfinite(dist[i, j]):
            exits.append((d + float(dist[i, j]), i, j))
            continue  # out on the lane ground: the flood takes it from here
        for di, dj, ln in _STEPS:
            u, v = i + di, j + dj
            if not (i0 <= u < i1 and j0 <= v < j1 and 0 <= u < L.nx and 0 <= v < L.ny) or not ok((u, v)):
                continue
            if di and dj and not (ok((i + di, j)) and ok((i, j + dj))):
                continue
            nd = d + ln * L.cell
            if nd < best.get((u, v), math.inf):
                best[(u, v)], back[(u, v)] = nd, (i, j)
                heapq.heappush(heap, (nd, u, v))
    exits.sort()
    return exits, back


def trace(L: Layers, dist: Any, pred: Any, laid: Any, start: tuple[int, int], tree_segs: Sequence[tuple[Pt, Pt]], joins: Any) -> tuple[list[Pt], Pt]:
    """The way on from the exit cell `start`: back along the flood to the way out, or to where it first comes within `JOIN_FT` of
    a way already laid (`laid`) and the leg onto it is clear (`joins(here, foot)`). Returns the cells' points after `start` and
    the point on the tree it joins.

    Research: ways join at a T - research/questions/0081-village-lanes.drawing.html: a lane meets another at a T, never beside it
    Research: join reach - UNRESEARCHED: a way joins an earlier one it comes within `JOIN_FT` of
    """
    path: list[Pt] = []
    u, v = start
    while True:
        here = L.at((u, v))
        if laid[u, v] or dist[u, v] == 0:
            foot = min((seg_closest(here[0], here[1], a, b) for a, b in tree_segs), key=lambda z: math.dist(z, here))
            if dist[u, v] == 0 or joins(here, foot):
                return path, foot
        u, v = (int(x) for x in pred[u, v])
        path.append(L.at((u, v)))


def mark_laid(L: Layers, laid: Any, run: Sequence[Pt], r: int) -> None:
    """Mark the cells within `r` cells of the way `run` as laid (a later way joins it there).

    Research: plumbing - NONE: raster marking for `trace`'s join
    """
    for a, b in legs(tuple(run)):
        n = max(1, int(math.dist(a, b) / L.cell) + 1)
        for t in range(n + 1):
            i, j = int((a[0] + (b[0] - a[0]) * t / n - L.x0) // L.cell), int((a[1] + (b[1] - a[1]) * t / n - L.y0) // L.cell)
            laid[max(0, i - r) : max(0, i + r + 1), max(0, j - r) : max(0, j + r + 1)] = True


def pinch(rec: dict[str, Any], others: Sequence[dict[str, Any]]) -> bool:
    """Reach the household `rec` across the yard of the nearest household with a way of its own (`others`, each with a laid
    corridor): recorded as feature 317's passage is (`reached_across`, `passage_depth`, the walk from its house to that yard),
    with `passage_kind` "pinch" - the walk not drawn. False where no household has a way.

    Research: reached across a neighbor's yard in a pinch - CANON: the GM's ruling of 2026-10-03, "it's okay for people to cut through neighbors' yards in a pinch"; the adjoining-land condition of an ordinary passage does not bind it
    """
    hx, hy = float(rec["x"]), float(rec["y"])
    near = min(others, key=lambda o: math.hypot(float(o["x"]) - hx, float(o["y"]) - hy), default=None)
    if near is None:
        return False
    yard = ((near.get("geom") or {}).get("boxes") or {}).get("yard") or (float(near["x"]), float(near["y"]))
    rec["reached_across"] = [round(float(near["x"]), 1), round(float(near["y"]), 1)]
    rec["passage_depth"] = 1
    rec["passage"] = [[round(hx, 1), round(hy, 1)], [round(float(yard[0]), 1), round(float(yard[1]), 1)]]
    rec["passage_kind"] = "pinch"
    return True


def lay_the_ways(s: Settlement) -> tuple[int, int]:
    """Lay every household's way in the gaps, once every house stands (the module's account). Returns (passages ended, pinches).
    Nothing where no access tree stands (a form that builds none).

    Research:
        each household's way laid once every house stands - GUESS research/questions/0081-village-lanes.drawing.html: the lanes as the gaps between the house plots, worn after the houses; the corridor's own tests and the tree's lane law admit each
        households' ways laid in order, nearest the way out first - GUESS: a search order, so a nearer household's way is there for a farther one to join
        a household no way reaches is pinched across its nearest reached neighbor's yard - research/questions/0081-village-lanes.drawing.html: reached across a neighbor's land, whose own way is always drawn
        a passage a laid way makes unnecessary is ended - research/questions/0081-village-lanes.drawing.html: one that a way reaches is given it and is no longer reached across its neighbor
        a later way's join reach - UNRESEARCHED: an earlier way within `JOIN_FT` (25 ft), then `JOIN_FAR_FT` (45 ft)
        a way's search ring - NONE: each way sought within the corridor's half-width and `RING_CELLS` cells round its homestead, a bound on the search
    """
    tree = getattr(s, "_access", None)
    houses = [h for h in (s.M.get("houses") or []) if h.get("geom") and h["geom"].get("bbox") is not None]
    if tree is None or not houses:
        return 0, 0
    half = float(tree.half)
    boxes = list(s.placed)
    segs = list(tree.segs)
    L = lane_layers(s, boxes, segs, half)
    ring = half + RING_CELLS * L.cell
    rings = [L.span(b[0] - b[2] / 2 - ring, b[1] - b[3] / 2 - ring, b[0] + b[2] / 2 + ring, b[1] + b[3] / 2 + ring) for b in (h["geom"]["bbox"] for h in houses)]
    dist, pred = flood(L, segs, rings)
    import numpy as np

    lays = [np.zeros((L.nx, L.ny), bool) for _ in range(3)]  # joined near, joined far, run on to the way out (never marked)
    memo = _standing_memo(s)[1]
    hgap = house_gap(s)
    radii = (int(s.px(JOIN_FT) // L.cell), int(s.px(JOIN_FAR_FT) // L.cell))
    nearest = {id(h): float(dist[i0:i1, j0:j1].min()) if i1 > i0 and j1 > j0 else math.inf for h, (i0, i1, j0, j1) in zip(houses, rings, strict=True)}
    ended = pinched = 0
    unreached: list[dict[str, Any]] = []
    for rec, area in sorted(zip(houses, rings, strict=True), key=lambda hr: nearest[id(hr[0])]):
        got = _way_for(s, L, dist, pred, lays, rec, area, half, hgap, memo)
        if got is None:
            if not rec.get("reached_across"):
                unreached.append(rec)
            continue
        reserve(s, got, (float(rec["x"]), float(rec["y"])))
        rec["geom"]["access"] = got
        for laid, r in zip(lays, radii, strict=False):
            mark_laid(L, laid, got, r)
        if rec.pop("reached_across", None) is not None:  # ...a passage the finished map makes unnecessary, ended where it stands
            rec.pop("passage_depth", None)
            rec.pop("passage", None)
            ended += 1
    reached = [h for h in houses if h["geom"].get("access") is not None]
    for rec in unreached:
        pinched += pinch(rec, reached)
    return ended, pinched


def _way_for(
    s: Settlement, L: Layers, dist: Any, pred: Any, lays: Sequence[Any], rec: dict[str, Any], area: tuple[int, int, int, int], half: float, hgap: float, memo: dict[Any, Any]
) -> tuple[Pt, ...] | None:
    """The household `rec`'s admitted way: up to `GAP_TRIES` distinct exits from its own homestead (`way_out`), each traced
    (`trace`) joined near, joined far and run on to the way out (`lays`), pulled taut and admitted (`access.admitted`); its own
    homestead set aside from what stands while it is asked.

    Research:
        joined near, then far, then run on to the way out - GUESS research/questions/0081-village-lanes.drawing.html: each household's way runs along the gaps to the track out or to a way laid before it, which it joins at a T
        a way leaves its own homestead from its dooryard - research/questions/0081-village-lanes.drawing.html: its way leaves its dooryard round its own garden beds and fixtures
    """
    geom = rec["geom"]
    own = geom["bbox"]
    sp = L.spans.get(id(own))

    def open_here(c: tuple[int, int]) -> bool:
        if L.site[c]:
            return False
        n = int(L.cover[c]) - (1 if sp is not None and sp[0] <= c[0] < sp[1] and sp[2] <= c[1] < sp[3] else 0)
        q = L.at(c)
        return n <= 0 and house_clear(q, q, geom, hgap) and parts_clear(s, q, q, geom) and fixtures_clear(s, q, q, geom)

    k = next((n for n, b in enumerate(s.placed) if b is own), None)
    if k is not None:
        s.placed.pop(k)
    try:

        def leg_ok(a: Pt, b: Pt) -> bool:
            return house_clear(a, b, geom, hgap) and fixtures_clear(s, a, b, geom) and parts_clear(s, a, b, geom) and standing_ground(s, a, b, memo)

        exits, back = way_out(L, dist, doors_of(geom, half), area, open_here)
        picked: list[tuple[int, int]] = []
        for _, i, j in exits:
            if len(picked) >= GAP_TRIES:
                break
            if any(abs(i - a) + abs(j - b) < RING_CELLS for a, b in picked):
                continue
            picked.append((i, j))
            local, c = [], (i, j)
            while isinstance(back[c], tuple) and len(back[c]) == 2 and isinstance(back[c][0], int):
                local.append(L.at(c))
                c = back[c]
            local.append(L.at(c))
            door = back[c]
            for laid in lays:
                path, foot = trace(L, dist, pred, laid, (i, j), s._access.segs, lambda here, f: standing_ground(s, here, f, memo))
                pts = [door, *reversed(local), *path]
                if math.dist(foot, pts[-1]) > 1e-6:
                    pts.append(foot)
                run = taut(pts, leg_ok, doubles_back, GAP_LEGS)
                drawn = admitted(s, run, geom, memo) if run is not None else None
                if drawn is not None:
                    return drawn
        return None
    finally:
        if k is not None:
            s.placed.insert(k, own)
