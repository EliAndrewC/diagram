"""The reserved corridors drawn (feature 287, plan M3's web half; ways W01).

WHY THIS REPLACES THE RE-ROLL. Whether a way can reach a farmhouse depended on fabric laid after the house was seated, so
the only reach guarantee the generator had was to build the map, find the stranded house, and build it again with that
ground forbidden (`driver.generate`'s old loop). The seating now reserves, for every house it admits, a corridor a footpath
wide from the house's door to a tree rooted at the EXIT STRIP (`settlement/rolling/access.py`), and no homestead seated
after may cover one. So a walkable run from every door to the exit strip exists by construction, and this module draws it
where the lanes do not reach the house: along the house's own corridor, on along the corridor its target stands on, and so
to the exit strip and along it to the connector's start - stopping at its FIRST CONTACT with the served network, so it
draws only the stretch the web lacked.

A DRAWN CORRIDOR IS A TREE LANE (`is_tree`): `settle_the_web` never cuts one, as it never cuts the connector. That is the
termination argument's other half - a settle round only ever takes material from ordinary lanes, and a corridor is drawn at
most once per house.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any

from l7r.diagram.overlap.registry import element_extents
from l7r.diagram.settlement import edge_dist, point_in_poly, rot_rect, seg_closest, seg_dist, segments_cross
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement.water_ways.lanes import behind_house

from ..consts import WEB_CLEARANCE, Poly, Pt
from . import law
from .bund import BRANCH_STEP_FT, BRANCH_WIDTH, run_on_target
from .checks import ford_crossing, served_network, unreached_houses
from .fabric import _homestead_polys, house_hit
from .geom import WorkedGround, polyline_len
from .route import _route
from .sweeps import _ALONG_FT

ACCESS_ROLE = "access"
"""The `role` a drawn corridor carries - read by `is_tree`, so no settle repair cuts it."""

ON_TREE_PX = 1.5
"""How near a corridor's target must stand to another corridor (or the exit strip) to be read as ON it: the record rounds
every point to 0.1 px, and a target is the exact foot on its host, so this is rounding room and nothing more."""

CONTACT_FT = _ALONG_FT
"""How near the drawn run must come to the served network to stop there and meet it: the run then ends on the foot of the
tread it met. The doubled-tread distance (`sweeps._ALONG_FT`, 14 ft), so a run that comes near enough a lane to read as
running on beside it (`law.doubled_tails`) meets it there instead (Mizuguchi's corridor ran up the exit strip 13 ft off
the skeleton lane when this was 12)."""

SAMPLE_FT = 2.0
"""The step the run is walked at in search of its first contact - finer than `CONTACT_FT` by six, so no contact is stepped
over."""

ACCESS_WIDTH = 3.0
"""A drawn corridor's tread, in ft: a footpath, the width `settle_the_web`'s door paths are drawn at."""

DOOR_STEP_FT = 7.0
"""How far a door may be stepped out from its wall so the drawn path clears the house (`off_the_wall`): the corridor's
reserved half-width (`access.ACCESS_HALF_FT`), so the stepped door is still on the reservation."""

TARGET_ROLE = "way target"
"""The `role` of a spur drawn to a way target (`meta.way_targets`: a burial ground's near edge) - a tree lane."""

FIELD_ROLE = "field way"
"""The `role` of the field path `settle_the_web` draws where no way of the hamlet's reaches the field - a tree lane."""

TREE_ROLES = (ACCESS_ROLE, TARGET_ROLE, FIELD_ROLE)

SPUR_TRIES = 120
"""How many spurs, shortest first, are offered to a way target or the field before the web says it has none: they leave
the network eight feet apart (`BRANCH_STEP_FT`), so 120 cover nearly a thousand feet of tread - the near stretch of every
lane round a small hamlet. Most are refused for meeting their lane at a needle's angle or at its end's fold (cohort seed
13's field: the forty nearest the bund all were)."""


def is_tree(ln: Mapping[str, Any]) -> bool:
    """Is this lane part of the tree no settle repair cuts - the connector, a drawn access corridor, a spur to a way
    target or the field way?"""
    return bool(ln.get("connector")) or ln.get("role") in TREE_ROLES


def _pt(q: Sequence[float]) -> Pt:
    return (float(q[0]), float(q[1]))


def _on(q: Pt, seg: Sequence[Sequence[float]]) -> bool:
    return seg_dist(q[0], q[1], _pt(seg[0]), _pt(seg[1])) <= ON_TREE_PX


def corridor_of(M: Mapping[str, Any], house: Pt) -> Mapping[str, Any] | None:
    """The reserved corridor recorded for the farmhouse centered at `house`, or None."""
    return next((c for c in M.get("access_corridors") or [] if c.get("of") and math.dist(_pt(c["of"]), house) <= ON_TREE_PX), None)


def connector_start(M: Mapping[str, Any]) -> Pt | None:
    """Where the connector begins - the root the exit strip leads to."""
    con = next((ln for ln in M.get("lanes") or [] if ln.get("connector") and len(ln.get("pts") or []) >= 2), None)
    return None if con is None else _pt(con["pts"][0])


def corridor_chain(M: Mapping[str, Any], house: Pt, to_connector: bool = True) -> Poly | None:
    """The reserved run from the house's door to the connector's start: the house's own corridor, then - from each target -
    on along the corridor that target stands on toward ITS target, until a target stands on the exit strip; then along the
    strip to the point of it nearest the connector's start, and to the start (not with `to_connector` False: the run ends
    where it reaches the strip). None where the house has no corridor."""
    rec = corridor_of(M, house)
    if rec is None:
        return None
    recs = M.get("access_corridors") or []
    exit_seg = M.get("access_exit")
    path: Poly = [_pt(rec["pts"][0]), _pt(rec["pts"][1])]
    seen = {id(rec)}
    while True:
        q = path[-1]
        if exit_seg and _on(q, exit_seg):
            break
        host = next((c for c in recs if id(c) not in seen and _on(q, c["pts"])), None)
        if host is None:
            return path
        seen.add(id(host))
        path.append(_pt(host["pts"][1]))
    start = connector_start(M)
    if start is not None and to_connector:
        foot = seg_closest(start[0], start[1], _pt(exit_seg[0]), _pt(exit_seg[1]))
        path += [foot, start]
    return [q for k, q in enumerate(path) if k == 0 or math.dist(q, path[k - 1]) > 1e-6]


def field_chain(M: Mapping[str, Any]) -> Poly | None:
    """The field's reserved corridor (`homesteads.stages.reserve_field_corridor`) as a run from the bund toward the network:
    its legs in the order the seating recorded them, then on along the exit strip to the connector's start, as a house's
    chain runs (`corridor_chain`). None where the seating reserved none."""
    legs = [c["pts"] for c in M.get("access_corridors") or [] if c.get("field") and len(c.get("pts") or ()) >= 2]
    if not legs:
        return None
    path: Poly = [(float(legs[0][0][0]), float(legs[0][0][1]))] + [(float(b[0]), float(b[1])) for _a, b in legs]
    start, strip = connector_start(M), M.get("access_exit")
    if start is not None and strip:
        a, b = (float(strip[0][0]), float(strip[0][1])), (float(strip[1][0]), float(strip[1][1]))
        path += [seg_closest(start[0], start[1], a, b), start]
    return [q for k, q in enumerate(path) if k == 0 or math.dist(q, path[k - 1]) > 1e-6]


def _dedup(run: Poly) -> Poly:
    return [p for j, p in enumerate(run) if j == 0 or math.dist(p, run[j - 1]) > 1e-6]


def contact_endings(path: Poly, k: int, q: Pt, foot: Pt) -> list[Poly]:
    """The ways a run meeting a tread at the contact `q` (on its segment `k`) may end on the tread's `foot`: from the
    contact square onto the tread, or - where that would put a second turn within a step of the first - from the vertex
    before it straight to the foot."""
    return [_dedup([*path[: k + 1], q, foot]), _dedup([*path[: k + 1], foot])]


def building_quads(M: Mapping[str, Any]) -> list[Poly]:
    """Every farm building's drawn quad - the houses, byres, field sheds and retirement houses, each turned as drawn."""
    return [
        rot_rect(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), float(r.get("rot") or 0.0))
        for key in ("houses", "byres", "farm_sheds", "retirement_houses")
        for r in M.get(key) or []
        if all(k in r for k in ("x", "y", "w", "h"))
    ]


def through_a_building(run: Poly, quads: Sequence[Poly]) -> bool:
    """Does any leg of `run` cross a building's wall, or stand inside one? `house_hit` asks only whether a building's
    CORNERS or center come near the tread, so a leg passing clean through a house between its corners reads as clear (a
    gable carry through a neighbor's house did, measured on a constructed pair) - a tree lane is asked this as well."""
    for quad in quads:
        if any(point_in_poly(p[0], p[1], quad) for p in run):
            return True
        if any(segments_cross(a, b, quad[k], quad[(k + 1) % 4]) for a, b in zip(run, run[1:], strict=False) for k in range(4)):
            return True
    return False


def _poly_box(poly: Sequence[Sequence[float]]) -> tuple[float, float, float, float]:
    return (min(float(p[0]) for p in poly), min(float(p[1]) for p in poly), max(float(p[0]) for p in poly), max(float(p[1]) for p in poly))


def _file_segments(grid: PointGrid, courses: Sequence[Sequence[Sequence[float]]]) -> None:
    for course in courses:
        pts = [(float(p[0]), float(p[1])) for p in course]
        grid.extend((a, b, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for a, b in zip(pts, pts[1:], strict=False))


class GroundIndex:
    """The ground a corridor's lawful-ground test reads (`settle.Lawful.on_lawful_ground`), INDEXED ONCE per standing
    manifest (dev/performance.md, "build the blocked ground once"): the seating asks it of every corridor it tries - seed
    17, 1,686 runs - and each walked every water course, every field and dry-plot outline and every farmstead part.

    It only PRUNES: `water_near` says whether any water segment comes within a pad of a run (no crossing fault and no
    squaring without one), `open_ground` asks whether the run crosses an outline edge near it (`settle.open_ground_rings`), and `near` hands back
    the parts of a registry whose boxes come within a pad of the run, in registry order - the exact tests then decide on
    those, and a part left out stands beyond every distance they measure."""

    def __init__(self, waters: Sequence[Sequence[Sequence[float]]], rings: Sequence[Sequence[Sequence[float]]], parts: Mapping[str, Sequence[tuple[Any, tuple[float, float, float, float]]]]) -> None:
        self.water = PointGrid(64.0)
        _file_segments(self.water, [w for w in waters if len(w) >= 2])
        self.edges = PointGrid(64.0)
        _file_segments(self.edges, [[*r, r[0]] for r in rings if len(r) >= 2])
        self.parts = {k: list(v) for k, v in parts.items()}
        self.grids: dict[str, PointGrid] = {}
        for kind, items in self.parts.items():
            g = self.grids[kind] = PointGrid(64.0)
            g.extend((n, *box) for n, (_item, box) in enumerate(items))

    @staticmethod
    def _query(grid: PointGrid, run: Sequence[Pt], pad: float) -> list[Any]:
        out: list[Any] = []
        for a, b in zip(run, run[1:], strict=False):
            x0, y0, x1, y1 = min(a[0], b[0]) - pad, min(a[1], b[1]) - pad, max(a[0], b[0]) + pad, max(a[1], b[1]) + pad
            out += [it for it in grid.near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2) if not (it[-2] < x0 or it[-4] > x1 or it[-1] < y0 or it[-3] > y1)]
        return out

    def water_near(self, run: Sequence[Pt], pad: float) -> bool:
        """Does any water segment's box come within `pad` of a segment's box of the run? False rules out a crossing (pad 0)
        and any vertex or leg within `pad` of the water."""
        return bool(self._query(self.water, run, pad))

    def open_ground(self, run: Sequence[Pt]) -> bool:
        """Does the run cross no outline edge filed (a field, a dry plot, a marsh)?"""
        return not any(segments_cross(a, b, c, d) for a, b in zip(run, run[1:], strict=False) for c, d, *_box in self._query(self.edges, [a, b], 0.0))

    def near(self, kind: str, run: Sequence[Pt], pad: float) -> list[Any]:
        """The `kind` parts whose boxes come within `pad` of the run, in the order they were filed."""
        items = self.parts[kind]
        return [items[n][0] for n in sorted({it[0] for it in self._query(self.grids[kind], run, pad)})]


BOW_OFFSETS_FT = (15.0, 25.0, 40.0, 60.0)
"""How far to one side a corridor is bowed round a building standing on it (`bowed_round`), tried nearest first: a byre or
a field shed seated after the corridor was reserved stands on its line (cohort seeds 10, 17 and Kashikawa, measured: a
15 x 18 ft building across the reserved strip), and a gentle bow - one apex beside the building - is the path feet wear
round it. The largest is past the widest farm building's half-length and its margin. A map drawing convention."""


def bowed_round(run: Poly, quads: Sequence[Poly]) -> list[Poly]:
    """The ways `run` may be bowed round the first building one of its legs crosses: that leg given one apex beside the
    building, either side, at each of `BOW_OFFSETS_FT` past the building's own reach from the leg - nearest first. A turn of
    the run standing INSIDE a building (a corridor's target, on which a store was seated - Kashikawa's kura on the junction
    of two corridors) is moved off it instead: to each of the building's corners, `BOW_OFFSETS_FT` out along its diagonal.
    [] where no leg crosses a building."""
    for k in range(1, len(run) - 1):
        hit = next((q for q in quads if point_in_poly(run[k][0], run[k][1], q)), None)
        if hit is not None:
            cx, cy = sum(c[0] for c in hit) / 4.0, sum(c[1] for c in hit) / 4.0
            moves = [(c[0] + (c[0] - cx) / (math.dist(c, (cx, cy)) or 1.0) * off, c[1] + (c[1] - cy) / (math.dist(c, (cx, cy)) or 1.0) * off) for off in BOW_OFFSETS_FT for c in hit]
            return [[*run[:k], m, *run[k + 1 :]] for m in sorted(moves, key=lambda m: math.dist(m, run[k]))]
    for k, (a, b) in enumerate(zip(run, run[1:], strict=False)):
        hit = next((q for q in quads if through_a_building([a, b], [q])), None)
        if hit is None or math.dist(a, b) < 1e-6:
            continue
        ux, uy = (b[0] - a[0]) / math.dist(a, b), (b[1] - a[1]) / math.dist(a, b)
        t = sum(((c[0] - a[0]) * ux + (c[1] - a[1]) * uy) for c in hit) / 4.0
        out = []
        for off in BOW_OFFSETS_FT:
            for side in (1.0, -1.0):
                reach = max(side * ((c[0] - a[0]) * -uy + (c[1] - a[1]) * ux) for c in hit)
                d = max(reach, 0.0) + off
                apex = (a[0] + ux * t - uy * side * d, a[1] + uy * t + ux * side * d)
                out.append([*run[: k + 1], apex, *run[k + 1 :]])
        return out
    return []


BOW_DEPTH = 2
"""How many buildings one corridor may be bowed round (`lawful_run`) - each bow is one apex; two cover a corridor passing a
byre and a shed of the same steading."""

BOW_WIDTH = 32
"""How many bowed candidates a level of `lawful_run` asks at most - `BOW_OFFSETS_FT` twice over, both sides, for each of
the level before's."""


def lawful_run(run: Poly, quads: Sequence[Poly], vet: Callable[[Poly], bool], depth: int = BOW_DEPTH, norm: Callable[[Poly], Poly] = lambda r: r) -> Poly | None:
    """`run` where `vet` (the web's `Lawful`) admits it, else the first of its bows round the buildings standing on it
    (`bowed_round`, up to `depth` buildings) that `vet` admits; None when none does."""
    frontier = [run]
    for _ in range(depth + 1):
        for cand in frontier:
            if vet(c := norm(cand)):
                return c
        frontier = [b for cand in frontier for b in bowed_round(cand, quads)][:BOW_WIDTH]
    return None


GABLE_MARGIN_FT = 6.0
"""How far off its gable wall a path carried round a house runs (`round_the_gable`): clear of the eaves by more than a
tread's half-width and the house-hit margin (`house_hit`: 1.5 + 2 ft), and inside the dooryard reach (12 ft) at the front
corner, so the carried end reaches the dooryard (`reaches_dooryard`). A map drawing convention."""


def round_the_gable(pts: Poly, house: Mapping[str, Any], far: bool = False, keep_end: bool = False) -> Poly:
    """`pts`, whose LAST point stands behind `house` (water W57), carried round the nearer gable to the front: its last
    point replaced by a point `GABLE_MARGIN_FT` off that gable's back corner and one as far off its front corner, in the
    band before the front face - the dooryard (`reaches_dooryard`). By the back corner, not straight to the gable's middle:
    a run from behind the house to its mid-gable cuts the back corner (cohort seeds 42, 43, 55 and 60, measured: every such
    run fouled its own house). The gable taken is the one on the side the end stands (the side the lane came from, on a
    tie); `far` takes the other, where a neighbor's garden stands along the nearer (cohort seed 55). `keep_end` keeps the
    last point and runs on from it instead - the stretch before it may carry other ways' junctions (cohort seed 31)."""
    th = math.radians(float(house.get("rot") or 0.0))
    c, sn = math.cos(th), math.sin(th)
    hx, hy, hw, hh = float(house["x"]), float(house["y"]), float(house["w"]) / 2, float(house["h"]) / 2

    def local(q: Pt) -> float:
        return (q[0] - hx) * c + (q[1] - hy) * sn

    def world(lx: float, ly: float) -> Pt:
        return (hx + lx * c - ly * sn, hy + lx * sn + ly * c)

    lx = local(pts[-1])
    side = math.copysign(1.0, lx if abs(lx) > 1e-6 else (local(pts[-2]) if len(pts) >= 2 else 1.0)) * (-1.0 if far else 1.0)
    x = side * (hw + GABLE_MARGIN_FT)
    return [*(pts if keep_end else pts[:-1]), world(x, -hh - GABLE_MARGIN_FT), world(x, hh + GABLE_MARGIN_FT)]


DOOR_TRIM_FT = 40.0
"""How far along its run a corridor's door end may be taken back where the door stands in or against an outbuilding (a
kura or a shed seated against the house after the corridor was reserved - cohort seeds 32, 53 and 60, measured: the wall
door 0-3 ft inside a 16 x 11 ft store): the run then starts past it, still inside `WEB_REACH_FT` of the house. A map drawing
convention."""

DOOR_TRIM_STEP_FT = 4.0
"""The step the door end is taken back in (`door_ends`): the clip's own 4 ft grain."""


def door_ends(run: Poly, house: Mapping[str, Any] | None, yard: Sequence[Sequence[float]] | None = None, width: float = ACCESS_WIDTH) -> list[Poly]:
    """The door ends a corridor's run may be drawn with, in preference order. A door behind its house (`access.doors_of`
    offers every wall) is left round the gable from the front instead - the nearer gable, then the farther (water W57: the
    path serves the house at its dooryard, never ends behind it). Otherwise the door as reserved, then the run taken back
    from it `DOOR_TRIM_STEP_FT` at a time, up to `DOOR_TRIM_FT`, for a door an outbuilding now stands on - and last, the run
    from where it leaves the house's own threshing yard (`yard`, its drawn quad) for good (`past_the_yard`), which a yard
    wider than the trims reach needs."""
    if house is not None and behind_house(house, run[0]):
        return [round_the_gable(run[::-1], house)[::-1], round_the_gable(run[::-1], house, far=True)[::-1]]
    total = polyline_len(run)
    ends = [run] + [trimmed for k in range(1, int(DOOR_TRIM_FT // DOOR_TRIM_STEP_FT) + 1) if len(trimmed := sub_run_from(run, k * DOOR_TRIM_STEP_FT)) >= 2 and k * DOOR_TRIM_STEP_FT < total]
    past = past_the_yard(run, yard, width) if yard is not None and len(yard) >= 3 else None
    return ends + ([past] if past is not None and past not in ends else [])


YARD_EXIT_PAD_FT = 1.0
"""How far past its own threshing yard's edge, beyond the tread's half-width, a door end is taken back to (`past_the_yard`):
the overlap matrix asks a tread `PLACER_MARGIN_PX` (0.2) wider than drawn and the record rounds to 0.1, so a foot is
room for both. A map drawing convention."""


def past_the_yard(run: Poly, yard: Sequence[Sequence[float]], width: float = ACCESS_WIDTH) -> Poly | None:
    """`run` from where its tread leaves the house's own threshing yard `yard` (its quad, `own_yard`) for good: the arc past the
    last point within the tread's half-width and `YARD_EXIT_PAD_FT` of the yard. The overlap matrix forbids a way on a
    yard, its own household's too (a path arrives at its dooryard and does not cross it), and the door stands in the yard's
    middle (`access.doors_of`) - so where the yard is wider than `DOOR_TRIM_FT` reaches, every trimmed end still stood on it
    (cohort seed 39 under feature 284's probes, measured: an 81-mat yard 76 x 53 ft, the corridor leaving along its long
    axis, and the house was left with no way). The seating reserved the corridor leaving its yard once (`access.
    leaves_its_yard`), so the run past it is reserved ground. None where the run never comes that near the yard or ends
    on it."""
    from shapely.geometry import LineString, Point, Polygon

    line = LineString(run)
    inside = line.intersection(Polygon([(float(q[0]), float(q[1])) for q in yard]).buffer(width / 2.0 + YARD_EXIT_PAD_FT))
    if inside.is_empty:
        return None
    s0 = max(line.project(Point(c)) for g in getattr(inside, "geoms", [inside]) for c in g.coords)
    if s0 >= line.length - 1.0:
        return None
    return sub_run_from(run, s0)


def own_yard(M: Mapping[str, Any], house: Pt) -> Poly | None:
    """The threshing yard of the house centered at `house` (`threshing_yards`, by its `of`) as the overlap matrix reads it
    (`registry.element_extents`: its turned rect, which stands up to 3 ft wider than the drawn `poly` - cohort seed 39's
    81-mat yard, measured), or None."""
    rec = next((y for y in M.get("threshing_yards") or [] if y.get("of") and math.dist(_pt(y["of"]), house) <= ON_TREE_PX), None)
    ext = element_extents("threshing_yards", rec, M) if rec is not None else []
    return [(float(q[0]), float(q[1])) for q in ext[0][1]] if ext else None


def sub_run_from(p: Poly, s0: float) -> Poly:
    """The run `p` from arc length `s0` on."""
    out: Poly = []
    acc = 0.0
    for a, b in zip(p, p[1:], strict=False):
        d = math.dist(a, b)
        if acc + d > s0 and d > 0:
            if not out:
                t = max(0.0, (s0 - acc) / d)
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            out.append(b)
        acc += d
    return _dedup(out)


def off_the_wall(chain: Poly, house: Mapping[str, Any], width: float = ACCESS_WIDTH) -> Poly:
    """`chain` with its door stepped out from the house's own wall until its first leg clears the house (`house_hit`): a
    door the seating took off a wall (`access.doors_of`) stands 2 ft outside it, closer than a tread's half-width and its
    margin, so the drawn path would graze its own eaves (Kashikawa's west-wall door, 2.4 ft off the corner). The step is
    along the line from the house's center through the door, at most `DOOR_STEP_FT` - inside the corridor's reserved half
    width, so the path stays on reserved ground."""
    door, c = chain[0], (float(house["x"]), float(house["y"]))
    d = math.dist(door, c)
    if len(chain) < 2 or d < 1e-6:
        return chain
    ux, uy = (door[0] - c[0]) / d, (door[1] - c[1]) / d
    for k in range(int(DOOR_STEP_FT) + 1):
        q = (door[0] + ux * k, door[1] + uy * k)
        if not house_hit([q, chain[1]], width, [house]):
            return [q, *chain[1:]]
    return chain


def contacts(path: Poly, segs: Sequence[tuple[Pt, Pt]], reach: float = CONTACT_FT, step: float = SAMPLE_FT, spacing: float = 0.0) -> Iterator[Poly]:
    """Every way `path` may stop and meet the network `segs`, in order along it: at each point within `reach` of a tread
    where it can meet that tread as the law asks - no kink (`law.bends_badly`), no needle, hook or fold at the joint
    (`law.meets_clean`) - the run up to there, ending on the tread's foot. One per point, and, with `spacing`, none within
    that arc length of the last one handed back."""
    if not segs:
        return
    last, walked = -math.inf, 0.0
    for k, (a, b) in enumerate(zip(path, path[1:], strict=False)):
        d = math.dist(a, b)
        n = max(1, int(math.ceil(d / step)))
        for m in range(n + 1):
            q = (a[0] + (b[0] - a[0]) * m / n, a[1] + (b[1] - a[1]) * m / n)
            at = walked + d * m / n
            if at - last < spacing:
                continue
            u, v = min(segs, key=lambda sg: seg_dist(q[0], q[1], sg[0], sg[1]))
            if seg_dist(q[0], q[1], u, v) > reach:
                continue
            foot = seg_closest(q[0], q[1], u, v)
            run = next((r for r in contact_endings(path, k, q, foot) if len(r) >= 2 and not law.bends_badly(r) and law.meets_clean(r, [u, v])), None)
            if run is not None:
                last = at
                yield run
        walked += d


def first_contact(path: Poly, segs: Sequence[tuple[Pt, Pt]], reach: float = CONTACT_FT, step: float = SAMPLE_FT) -> Poly | None:
    """`path` up to its first point within `reach` of the network `segs` where it can meet the tread it comes to as the law
    asks (`contacts`), ending on that tread's foot; None when it never comes that near."""
    return next(contacts(path, segs, reach, step), None)


def samples_along(segs: Sequence[tuple[Pt, Pt]], step: float = BRANCH_STEP_FT) -> list[Pt]:
    """Points every `step` along the segments `segs` - where a spur may leave the network."""
    out: list[Pt] = []
    for a, b in segs:
        n = max(1, int(math.dist(a, b) // step))
        out.extend((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1))
    return out


def spur_runs(segs: Sequence[tuple[Pt, Pt]], target: Pt, limit: int = SPUR_TRIES) -> list[Poly]:
    """The straight spurs from the network `segs` to `target`, shortest first, at most `limit` - the candidates the web
    lays to a way target (a burial ground's edge) until one keeps the law."""
    pts = sorted(samples_along(segs), key=lambda q: math.dist(q, target))
    return [[q, target] for q in pts[:limit] if math.dist(q, target) > 1.0]


def field_runs(segs: Sequence[tuple[Pt, Pt]], grounds: Sequence[WorkedGround], half: float, brook: Sequence[Pt] = (), fords: Sequence[Pt] = (), limit: int = SPUR_TRIES) -> list[Poly]:
    """The field paths from the network `segs` on to the bund: from each point of the network, nearest the ground first, to
    the point where it runs on to the worked ground's edge (`run_on_target`) - straight, or, where the straight run crosses
    the brook, over it square at the ford that makes the walk shortest (`ford_crossing`, the landings `bridges()` decks)
    and on to the bund from the far landing. The paddy's first and then the dry hem's, at most `limit` per ground, each
    ground's shortest first."""
    out: list[Poly] = []
    pts = samples_along(segs)
    for ground in grounds:
        runs: list[Poly] = []
        for q in pts:
            tgt = run_on_target(q, ground, half, reach=math.inf)
            if tgt is None:
                continue
            land = ford_crossing(q, tgt, brook, fords) if len(brook) >= 2 else []
            far = run_on_target(land[1], ground, half, reach=math.inf) if land else None
            if land and far is not None:
                # a network point standing on the near landing - the end of a way already walked to the ford - is where the
                # crossing starts, not a leg of its own
                runs.append([q, land[1], far] if math.dist(q, land[0]) <= ON_TREE_PX else [q, land[0], land[1], far])
            else:
                runs.append([q, tgt])
        out += sorted(runs, key=polyline_len)[:limit]
    return out


ROUTED_FIELD_TRIES = 4
"""How many fords (nearest the network first) a ROUTED field way is tried over (`routed_field_runs`) once no straight run
keeps the law - each a router call on the web's own lattice, so a handful (cohort seed 13: every straight run from the
network fouled a steading or met its lane at a needle)."""


def routed_field_runs(
    segs: Sequence[tuple[Pt, Pt]], ground: WorkedGround, half: float, route: Callable[[Pt, Pt], Poly], brook: Sequence[Pt] = (), fords: Sequence[Pt] = (), limit: int = ROUTED_FIELD_TRIES
) -> list[Poly]:
    """Field ways threaded by the web's router (`route`, `route._route` over the steadings and the hard ground): from the
    network to the near landing of each of the `limit` fords nearest it, over the ford square, and on from the far landing
    to the bund - or, with no brook, from the network point nearest the ground straight to its run-on target, threaded.
    Legs the router finds no way for are left out."""
    pts = samples_along(segs)
    if not pts:
        return []
    out: list[Poly] = []
    if len(brook) < 2 or not fords:
        q = min(pts, key=ground.dist)
        tgt = run_on_target(q, ground, half, reach=math.inf)
        leg = route(q, tgt) if tgt is not None else []
        return [leg] if len(leg) >= 2 else []
    for f in sorted(fords, key=lambda c: min(math.dist(c, q) for q in pts))[:limit]:
        u, v = min(zip(brook, brook[1:], strict=False), key=lambda ab: seg_dist(f[0], f[1], ab[0], ab[1]))
        d = math.dist(u, v) or 1.0
        nx, ny = -(v[1] - u[1]) / d, (v[0] - u[0]) / d
        ends = [(f[0] + nx * FORD_LANDING_FT, f[1] + ny * FORD_LANDING_FT), (f[0] - nx * FORD_LANDING_FT, f[1] - ny * FORD_LANDING_FT)]
        near, far = sorted(ends, key=lambda e: min(math.dist(e, q) for q in pts))
        q = min(pts, key=lambda p: math.dist(p, near))
        tgt = run_on_target(far, ground, half, reach=math.inf)
        if tgt is None:
            continue
        leg1, leg3 = route(q, near), route(far, tgt)
        if len(leg1) >= 2 and len(leg3) >= 2:
            out.append(_dedup([*leg1, *leg3]))
    return out


def routed_on(trunk: Poly, segs: Sequence[tuple[Pt, Pt]], route: Callable[[Pt, Pt], Poly]) -> Poly | None:
    """`trunk` carried on by `route` from its last point to the nearest point of the network `segs`, up to its first contact
    with it (`first_contact`); None where there is no network or no route."""
    near = min((seg_closest(trunk[-1][0], trunk[-1][1], a, b) for a, b in segs), key=lambda f: math.dist(f, trunk[-1]), default=None)
    leg = route(trunk[-1], near) if near is not None else []
    return first_contact(_dedup([*trunk, *leg[1:]]), segs) if len(leg) >= 2 else None


FORD_LANDING_FT = 22.0
"""A ford's landing stands this far off the brook square to its reach (`checks.ford_crossing`'s own `landing`)."""


def _lawful_contact(
    run: Poly | None, rec: Mapping[str, Any] | None, quads: Sequence[Poly], vet: Callable[[Poly], bool], norm: Callable[[Poly], Poly] = lambda r: r, yard: Sequence[Sequence[float]] | None = None
) -> Poly | None:
    """The first of `run`'s door ends (`door_ends`, `yard` the house's own) that `vet` admits once `norm` (the web's squaring)
    has made it what would be drawn, bowed round a building on it where need be (`lawful_run`); None for no run, or none
    admitted."""
    if run is None or len(run) < 2 or polyline_len(run) < 1.0:
        return None
    return next((r for c in door_ends(run, rec, yard) if (r := lawful_run(c, quads, vet, norm=norm)) is not None), None)


LATER_CONTACTS = 12
"""How many of the reserved run's later contacts with the network (`contacts`, `CONTACT_FT` apart) are offered once its
first is refused (`draw_corridors`): cohort seed 8 under feature 284's probes, measured - the run's first contact stood just
past a channel it crossed, and squared there the crossing and the contact made a kink; farther along the exit strip the
same run met the network clean. A dozen reach some 170 ft along the network, past any crossing's square legs."""


def dooryard(house: Mapping[str, Any]) -> Pt:
    """Where a path to a farmhouse ends at its dooryard: the threshing yard's middle where the house records one, else a
    point `GABLE_MARGIN_FT` before the middle of its front face (`reaches_dooryard`'s band)."""
    yard = (house.get("geom") or {}).get("yard")
    if yard is not None:
        return (float(yard[0]), float(yard[1]))
    th = math.radians(float(house.get("rot") or 0.0))
    d = float(house["h"]) / 2 + GABLE_MARGIN_FT
    return (float(house["x"]) - math.sin(th) * d, float(house["y"]) + math.cos(th) * d)


def draw_corridors(s: Any, vet: Callable[[Poly], bool] = lambda _run: True, route: Callable[[Pt, Pt], Poly] | None = None, norm: Callable[[Poly], Poly] = lambda r: r) -> int:
    """Step 4 of `settle_the_web` (ways W01): for every farmhouse the served network does not reach (`unreached_houses`),
    the reserved run from its door (`corridor_chain`) drawn up to its first contact with the network - once per house, as a
    tree lane, where `vet` (the web's `lawful`) admits it once squared (`norm`) - its door end taken back as far as past its
    own threshing yard where need be (`door_ends`). Where it does not, the run's later contacts (`contacts`, at most
    `LATER_CONTACTS`); then the web's router (`route`) carries the reserved run on from the exit strip, and failing that
    threads a way from the house's own dooryard (`dooryard`) to the network. A house none of these reaches is recorded on
    the manifest (`meta.access_refused`) and not drawn to - never a least-bad run (FR-005); the roll's reach verdict names
    it (research R9: cohort seeds 8 and 39 under feature 284's probes reached it; with the yard and later-contact ends
    both are reached, and cohort 1-60 plain passes). Returns the corridors drawn."""
    M = s.M
    far = unreached_houses(M)
    if not far:
        return 0
    lanes = M.get("lanes") or []
    drawn = {tuple(ln["of"]) for ln in lanes if ln.get("role") == ACCESS_ROLE and ln.get("of")}
    segs = served_network(lanes)
    quads = building_quads(M) + law.fixture_quads(M)  # a building or a farmstead fixture on the corridor is bowed round
    n = 0
    for x, y, _d in far:
        rec = next((h for h in M.get("houses") or [] if math.dist((float(h["x"]), float(h["y"])), (x, y)) <= 1.0), None)
        house = _pt((rec["x"], rec["y"])) if rec is not None else (float(x), float(y))
        key = (round(house[0], 1), round(house[1], 1))
        if key in drawn:
            continue
        chain = corridor_chain(M, house)
        chain = off_the_wall(chain, rec) if rec is not None and chain is not None else chain
        yard = own_yard(M, house)
        run = _lawful_contact(first_contact(chain, segs), rec, quads, vet, norm, yard) if chain is not None else None
        if run is None and chain is not None:
            # ...AND WHERE ITS FIRST CONTACT IS REFUSED, THE LATER ONES of the run squared as it would be drawn (cohort seed 8
            # under the probes: squared at the channel just before its first contact, the run kinked there)
            later = contacts(norm(chain), segs, spacing=CONTACT_FT)
            run = next((r for c in itertools.islice(later, LATER_CONTACTS) if (r := _lawful_contact(c, rec, quads, vet, norm, yard)) is not None), None)
        if run is None and route is not None and chain is not None:
            # ...AND WHERE THE RESERVED RUN MEETS THE NETWORK NOWHERE THE LAW ALLOWS - the connector started off the strip
            # (its track bent round the field or took the dry exit, cohort seeds 15 and 41: 72 ft off it), or the run turns
            # back on itself at the strip - the web's router carries it on from where it reached the strip to the nearest
            # point of the network
            trunk = off_the_wall(corridor_chain(M, house, to_connector=False) or chain, rec) if rec is not None else chain
            run = _lawful_contact(routed_on(trunk, segs, route), rec, quads, vet, norm, yard)
        if run is None and route is not None and rec is not None:
            # ...AND WHERE EVEN THAT IS REFUSED - the reserved door walled in by the house's own fixtures (cohort seed 4: its
            # privy on one gable and its bath and coop on the other, the reserved door behind the house) - the router threads
            # a way from the dooryard itself to the nearest point of the network
            run = _lawful_contact(routed_on([dooryard(rec)], segs, route), rec, quads, vet, norm, yard)
        if run is None:
            refused = M["meta"].setdefault("access_refused", [])
            if list(key) not in refused:
                refused.append(list(key))
            continue
        s.lane([(round(x, 1), round(y, 1)) for x, y in run], width=ACCESS_WIDTH, clearance=WEB_CLEARANCE, worn=True)
        s.M["lanes"][-1].update({"role": ACCESS_ROLE, "of": list(key)})
        drawn.add(key)
        segs = [*segs, *zip(run, run[1:], strict=False)]
        n += 1
    return n


def field_router(s: Any, brook: Poly) -> Callable[[Pt, Pt], Poly]:
    """The web's router (`route._route`) as a field way threads it: walled by the steadings' built ground (not the commons
    or the groves - a path crosses ground cover), hard against the field, the dry hem and the marsh, and kept off the brook
    but at its fords (the straggler footpath's own terms, `serve._serve_stragglers`)."""
    M = s.M
    hard = [[(float(a), float(b)) for a, b in f["outline"]] for f in M.get("fields") or [] if f.get("outline")]
    hard += [[(float(a), float(b)) for a, b in d["poly"]] for d in M.get("dry_plots") or [] if d.get("poly")]
    hard += [[(float(a), float(b)) for a, b in m["poly"]] for m in M.get("marshes") or [] if len(m.get("poly") or ()) >= 3 and m.get("role") != "defense"]
    fabric = [(poly, own, kind) for poly, own, kind in _homestead_polys(s) if kind not in ("commons", "village_groves")]
    # ...AND EVERYTHING THE OVERLAP MATRIX FORBIDS A WAY ON (feature 287 M8), read from the registry of what stands: the
    # burial ground, a kura, a sty, a fixture - the ground the law will refuse the run for, walled before it is routed
    st = getattr(M, "standing", None)
    matrix = [(e[1], e[3] if e[3] is not None else e[2], e[0]) for e in st.forbidding("lanes")] if st is not None else []  # a part by its household, a house by itself
    houses = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []]
    water = list(zip(brook, brook[1:], strict=False))

    def route(a: Pt, b: Pt) -> Poly:
        # A PATH LEAVES ITS OWN DOORYARD: the threshing yard of the house the route starts at is not a wall to it (a route from
        # a dooryard starts inside it, and every cell round it was walled), nor the house itself where the route starts within
        # the router's gap of its wall (a house with no yard: its dooryard is a step off the front) - the web draws the run
        # from the yard's edge (`door_ends`) and the law refuses a tread on the house (`house_hit`); its beds, sheds and
        # fixtures and every other steading's are walls, as the matrix holds them
        own = min((c for c in houses if math.dist(c, a) <= law.DOORSTEP_FT), key=lambda c: math.dist(c, a), default=None)

        def mine(owner: Any, kind: str, poly: Poly) -> bool:
            if own is None or owner is None or math.dist((float(owner[0]), float(owner[1])), own) > 1.5:
                return False
            return kind == "threshing_yards" or (kind == "houses" and (point_in_poly(a[0], a[1], poly) or edge_dist(a[0], a[1], poly) <= GABLE_MARGIN_FT + FIELD_ROUTE_GAP_FT))

        walls = [poly for poly, owner, kind in [*fabric, *matrix] if not mine(owner, kind, poly)]
        return _route(a, b, hard, walls, water, gap=FIELD_ROUTE_GAP_FT)

    return route


FIELD_ROUTE_GAP_FT = BRANCH_WIDTH / 2.0 + 3.0
"""How far the routed field way keeps off the steadings: the field path's half-tread and the 2 ft `house_hit` pads a tread
by, and a foot to spare - at the footpath's own 4 ft the router drew a 5 ft path 4.3 ft off a house corner and the law
(`fouled_segment`) refused it."""
