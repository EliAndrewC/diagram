"""THE BASE TREE, built once per state of the tree and extended as it grows (feature 387, plan D1).

`tree.admits` asks, of each candidate household way, whether the access tree with that way added keeps the lane law. It used to
rebuild the whole tree for every candidate - every record's host, every lane laid and drawn (1,886 `lay` calls for 88 candidates
at 40 households), every free end's junction and house (29,540 end-way pairs) - though none of it depends on the candidate: a
candidate is appended LAST, its host is the earliest run it stands on, and every earlier lane's drawn form depends only on its own
run and its host's. So this module keeps, for one state of the tree, the records, the root, the hosts, the laid lanes, each free
end's verdict, and the web's faces with each one's needle verdict; a corridor reserved since is appended (the records grow at
their end), anything else rebuilds it. A candidate then costs its own host (from a grid of the runs), its own laid lane, the ends
its lane or its house can change (from a grid of the ends), and the faces its lane meets.

THE VERDICT IS THE WHOLE TREE'S. Every answer here is the one `admits` computed over the whole tree; the equivalence is proved
call by call in the tests (`tests/soak/test_scale_equivalence_387.py` runs both on every candidate of the rolls).

Research: plumbing - NONE: how the tree's own verdicts (`tree.admits`' claims) are computed
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any, cast

from l7r.diagram.settlement import seg_dist
from l7r.diagram.settlement._geom.indexes import PointGrid

from ..consts import Poly, Pt
from . import law
from .corridors import ON_TREE_PX

_JOIN = law.JOIN_TOL
_HAIR = 0.01  # px: past noding's rounding, far under any face a needle test reads (`law.NODING_SPECK_FT`, 1 ft)


def _seg_items(tag: Any, pts: Sequence[Pt], pad: float) -> list[tuple[Any, ...]]:
    return [(tag, a, b, min(a[0], b[0]) - pad, min(a[1], b[1]) - pad, max(a[0], b[0]) + pad, max(a[1], b[1]) + pad) for a, b in zip(pts, pts[1:], strict=False)]


def _near_segs(grid: PointGrid, pts: Sequence[Pt], pad: float) -> list[Any]:
    """Every item filed in `grid` whose box comes within `pad` of one of `pts`' legs (a superset; the caller's test decides) -
    `pts` a way of two points or more, as every caller asks."""
    out: list[Any] = []
    for a, b in zip(pts, pts[1:], strict=False):
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        out += grid.near(cx, cy, max(abs(a[0] - b[0]), abs(a[1] - b[1])) / 2 + pad)
    return out


class Ends:
    """The free ends of a web's lanes (`law.fronting_ends`' reading): each end's junction - within `JOIN_TOL` of another way - and,
    for a free one, its nearest house (the first of the nearest, as `min` takes it) and whether it reaches that house's steading
    (`law.reach_to_steading`). Kept current as lanes are added; asked what one more lane and one more house would change. Three
    grids answer those questions without walking every end: the free ends' points, each free end's nearest-house circle (an end
    a new house can take is one whose circle holds it), and the houses; and each house's free ends are kept by house."""

    __slots__ = ("by_house", "circles", "egrid", "free", "houses", "hgrid", "segs")

    def __init__(self, houses: Sequence[Mapping[str, Any]]) -> None:
        self.houses = houses
        self.hgrid = PointGrid()
        self.hgrid.extend((k, float(h["x"]), float(h["y"]), float(h["x"]), float(h["y"]), float(h["x"]), float(h["y"])) for k, h in enumerate(houses))
        self.segs = PointGrid()  # every way's legs, padded by the junction gap
        self.egrid = PointGrid()  # the free ends, as filed (an end since joined is no longer in `free`)
        self.circles = PointGrid()  # each free end's nearest-house circle's box
        self.free: dict[tuple[int, int], tuple[Pt, int, float, bool]] = {}  # (lane, end) -> (point, house, its distance, reaches)
        self.by_house: dict[int, set[tuple[int, int]]] = {}

    def nearest(self, end: Pt, extra: Mapping[str, Any] | None = None) -> tuple[int, float]:
        """The index and distance of `end`'s nearest house - the first of the nearest - `extra` counted last."""
        best, dist = -1, math.inf
        if self.houses:
            r = 64.0
            while True:
                for k, x, y, *_ in self.hgrid.near(end[0], end[1], r):
                    d = math.hypot(end[0] - x, end[1] - y)
                    if d < dist or (d == dist and k < best):
                        best, dist = k, d
                if best >= 0 and dist <= r:  # every house nearer than the one found lies inside the box asked
                    break
                r *= 4.0
        if extra is not None:
            d = math.hypot(end[0] - float(extra["x"]), end[1] - float(extra["y"]))
            if d < dist:
                best, dist = len(self.houses), d
        return best, dist

    def joined(self, end: Pt, skip: int) -> bool:
        """Is `end` within the junction gap of a way other than lane `skip`?"""
        return any(k != skip and seg_dist(end[0], end[1], a, b) <= _JOIN for k, a, b, *_ in self.segs.near(end[0], end[1], 0.0))

    def _joined_by(self, p: Poly) -> set[tuple[int, int]]:
        """The free ends within the junction gap of the way `p`."""
        return {key for it in _near_segs(self.egrid, p, _JOIN) if (key := (it[0], it[1])) in self.free and law._min_dist(self.free[key][0], p) <= _JOIN}

    def add(self, i: int, lane: Mapping[str, Any], M: Mapping[str, Any]) -> None:
        """Lane `i` added to the web: every free end it now joins taken out, and its own ends judged."""
        p = law.lane_pts(lane)
        if len(p) >= 2:
            for key in self._joined_by(p):
                self.by_house[self.free.pop(key)[1]].discard(key)
            self.segs.extend(_seg_items(i, p, _JOIN))
        if lane.get("connector") or len(p) < 2:
            return
        for e, end in ((0, p[0]), (-1, p[-1])):
            if self.joined(end, i):
                continue
            h, d = self.nearest(end)
            self.free[(i, e)] = (end, h, d, h >= 0 and law.reach_to_steading(end, self.houses[h], M))
            self.by_house.setdefault(h, set()).add((i, e))
            self.egrid.extend([(i, e, end[0], end[1], end[0], end[1])])
            self.circles.extend([(i, e, end[0] - d, end[1] - d, end[0] + d, end[1] + d)] if d < math.inf else [])

    def counts(self) -> dict[int, int]:
        out: dict[int, int] = {}
        for _q, h, _d, reaches in self.free.values():
            if reaches:
                out[h] = out.get(h, 0) + 1
        return out

    def with_one_more(self, k: int, lane: Mapping[str, Any], house: Mapping[str, Any] | None, M: Mapping[str, Any]) -> dict[int, int]:
        """The free ends each house would discharge with lane `k` (and its `house`, counted last) added - `law.fronting_ends` on
        the trial web `M` - re-asking only the ends the addition can change: the free ends the new lane joins, those now nearer
        the new house, and those of a house the new one stands on (its yard counts for that steading now); then the new lane's
        own."""
        counts = self.counts()
        p = law.lane_pts(lane)
        joined = self._joined_by(p) if len(p) >= 2 else set()
        changed = set(joined)
        if house is not None:
            hx, hy = float(house["x"]), float(house["y"])
            changed |= {key for it in self.circles.near(hx, hy, 0.0) if (key := (it[0], it[1])) in self.free and math.hypot(self.free[key][0][0] - hx, self.free[key][0][1] - hy) < self.free[key][2]}
            if not self.houses:  # no house yet: every free end is the new house's
                changed |= set(self.free)
            for h, *_ in self.hgrid.near(hx, hy, 0.5):
                if math.dist((float(self.houses[h]["x"]), float(self.houses[h]["y"])), (hx, hy)) <= 0.5:
                    changed |= self.by_house.get(h, set())
        for key in changed:
            q, h, _d, reaches = self.free[key]
            if reaches:
                counts[h] -= 1
            if key in joined:
                continue  # discharged by its junction with the new lane
            h2, _d2 = self.nearest(q, house)
            if law.reach_to_steading(q, house if h2 == len(self.houses) and house is not None else self.houses[h2], M):
                counts[h2] = counts.get(h2, 0) + 1
        if not lane.get("connector") and len(p) >= 2:
            for end in (p[0], p[-1]):
                if self.joined(end, k):
                    continue
                h2, _d2 = self.nearest(end, house)
                if h2 < 0:
                    continue
                if law.reach_to_steading(end, house if h2 == len(self.houses) and house is not None else self.houses[h2], M):
                    counts[h2] = counts.get(h2, 0) + 1
        return counts


class Faces:
    """The faces of a web's treads (`law.web_faces`) with each one's needle verdict, and the rule that answers a changed web from
    them: a face that meets none of the changed lanes' lines - old or new - is the same face in both webs, so the changed web
    holds a needle exactly when a needle face of this web meets none of them, or a face of the changed web that meets one is a
    needle (plan D1/D2b). The changed web is still noded and polygonized whole; only the faces the change meets are judged."""

    __slots__ = ("faces",)

    def __init__(self, lanes: Sequence[Mapping[str, Any]]) -> None:
        self.faces = [(f, law.is_needle(f)) for f in law.web_faces(law.web_lines({"lanes": list(lanes)}))]

    def count(self) -> int:
        """How many needle faces this web holds (`len(law.needle_loops(...))`)."""
        return sum(1 for _f, thin in self.faces if thin)

    def needles_with(self, lanes: Sequence[Mapping[str, Any]], changed: Sequence[Poly]) -> int:
        """How many needle faces the web `lanes` holds, this web changed by the lines `changed` (each changed lane's old and new)."""
        from shapely.geometry import LineString, MultiLineString

        lines = [LineString(p) for p in changed if len(p) >= 2]
        if not lines:
            return self.count()
        # ...BUFFERED BY A HAIR: noding moves a crossing a few ulps off the line it lies on, and a face whose edge runs along a
        # changed line read as not meeting it (the unit test's seed 6). Taking in a face near the change is exact - it is judged
        # in the changed web, and left out of the kept faces alike - so the hair can only re-judge more, never less.
        touched = MultiLineString(lines).buffer(_HAIR)
        kept = sum(1 for f, thin in self.faces if thin and not f.intersects(touched))
        mine = [f for f in law.web_faces(law.web_lines({"lanes": list(lanes)})) if f.intersects(touched)]
        return kept + sum(1 for f in mine if law.is_needle(f))


class TreeBase:
    """The base tree for one state (see the module docstring): records, root, hosts, laid lanes, their ends and faces.

    Research: track out's width as judged - research/questions/0081-village-lanes.drawing.html: the track out's stub judged at 6 ft, the track out as drawn (`tree.admits`' own)"""

    __slots__ = ("_judged", "drawn_of", "ends", "host", "key", "lanes", "recs", "root", "runs", "stub", "view")

    def __init__(self, key: tuple[Any, ...], recs: Sequence[Mapping[str, Any]], root: Poly | None, view: Mapping[str, Any], lay: Callable[[Poly], Poly]) -> None:
        """The base built from `recs`, appended one by one, with the track out's stub as `tree.admits` judged it.

        Research: track out's width as judged - research/questions/0081-village-lanes.drawing.html: the track out's stub judged at 6 ft, the track out as drawn"""
        self.key, self.root, self.view = key, root, view
        self.recs: list[Mapping[str, Any]] = []
        self.host: list[int | None] = []
        self.drawn_of: dict[int, Poly] = {-1: root} if root is not None else {}
        self.lanes: list[dict[str, Any]] = []
        self.runs = PointGrid()  # every record's legs, for the host of the next
        self.stub: list[dict[str, Any]] = [{"pts": root, "w": 6.0, "connector": True}] if root is not None else []  # the track out as drawn
        self.ends = Ends(view.get("houses") or [])
        for n, ln in enumerate(self.stub):
            self.ends.add(-1 - n, ln, view)
        self._judged: tuple[Faces, list[dict[str, Any]], Faces] | None = None  # judged lazily, once per state, on the first candidate
        for r in recs:
            self.append(r, lay)

    def host_of(self, q: Pt) -> int | None:
        """The host of a run ending at `q`: -1 on the root, else the earliest run it stands on (`tree.hosts`), else None."""
        root = self.root
        if root is not None and any(seg_dist(q[0], q[1], a, b) <= ON_TREE_PX for a, b in zip(root, root[1:], strict=False)):
            return -1
        hits = [j for j, a, b, *_ in self.runs.near(q[0], q[1], 0.0) if seg_dist(q[0], q[1], a, b) <= ON_TREE_PX]
        return min(hits) if hits else None

    def lane_for(self, r: Mapping[str, Any], h: int | None, lay: Callable[[Poly], Poly]) -> tuple[Poly, dict[str, Any]]:
        from .tree import _rounded, lane_record

        pts = _rounded(lay(r["pts"]))
        return pts, lane_record(r, pts, self.drawn_of.get(h) if h is not None else None)

    def append(self, r: Mapping[str, Any], lay: Callable[[Poly], Poly]) -> None:
        """A record the tree has reserved since this base was built, appended (the tree grows at its end)."""
        i = len(self.recs)
        h = self.host_of(r["pts"][-1])
        pts, lane = self.lane_for(r, h, lay)
        self.recs.append(r)
        self.host.append(h)
        self.drawn_of[i] = pts
        self.lanes.append(lane)
        self.runs.extend(_seg_items(i, r["pts"], ON_TREE_PX))
        self.ends.add(i, lane, self.view)
        self._judged = None

    def judged(self) -> tuple[Faces, list[dict[str, Any]], Faces]:
        """The base web's faces, its lanes with their ends joined as the web will join them (`tree.as_joined`), and those faces."""
        from .tree import _trial, as_joined

        if self._judged is None:
            joined = as_joined(_trial(self.view, lanes=[*self.lanes, *self.stub]), self.lanes)
            self._judged = (Faces([*self.lanes, *self.stub]), joined, Faces(joined))
        return self._judged


_KEYED = ("houses", "threshing_yards", "byres", "farm_sheds", "gardens")
"""The registries a base tree's verdicts read besides its records: the houses and their steadings' parts (`law.reach_to_steading`)."""


def base_for(base: Any, M: Mapping[str, Any], lay: Callable[[Poly], Poly]) -> TreeBase:
    """The base tree of `M` as it stands, kept on `base` (the seating's `Lawful`): the one kept if nothing it read has changed, that
    one with the records reserved since appended if the tree only grew at its end, else a new one. What it read is held by the
    registries' own versions (`indexes.Indexed`) and the root and water by value; a registry that is not versioned (a plain
    manifest, a test's) is never trusted - the base is rebuilt."""
    from .tree import _root, square_waters_of, tree_records

    root = _root(M)
    regs = tuple(M.get(k) for k in _KEYED)
    static = (tuple(root) if root else None, square_waters_of(M), tuple(getattr(r, "version", None) for r in regs))
    versioned = all(hasattr(r, "version") for r in regs)
    kept = base.__dict__.get("_tree_base")
    recs = tree_records(M)
    same = versioned and kept is not None and kept.key[0] == static and all(a is b for a, b in zip(kept.key[1], regs, strict=True))
    if same and len(recs) >= len(kept.recs) and all(recs[i] == kept.recs[i] for i in range(len(kept.recs))):  # the tree only grew
        for r in recs[len(kept.recs) :]:
            kept.append(r, lay)
        return cast("TreeBase", kept)
    from .tree import _trial

    tb = TreeBase((static, regs), recs, root, _trial(M), lay)
    if versioned:
        base.__dict__["_tree_base"] = tb
    return tb
