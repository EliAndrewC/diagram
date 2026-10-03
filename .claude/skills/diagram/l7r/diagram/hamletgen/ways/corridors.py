"""The access tree's roles and the runs the seating reserves (feature 287, plan M3; ways W01, W03).

The seating reserves, for every house it admits, a corridor a footpath wide from its door to a tree rooted at the EXIT
STRIP (`settlement/rolling/access.py`), and the field's corridor from the tree to the bund (`field_runs`,
`routed_field_runs`, threaded by `field_router`); no homestead seated after may cover one. The tree is judged whole as
lanes when each corridor is admitted, and drawn where the web owes it (`tree.py`). A TREE LANE (`is_tree`: the connector,
the exit strip, a corridor, a way target's spur, the field way) is never cut by a settle repair; an ordinary lane that breaks
a rule against one is cut instead (`tree.settle_defer`), and one the map no longer needs is pruned (`tree.prune_the_tree`).

Research: roles and indexing - NONE
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import edge_dist, point_in_poly, rot_rect, seg_dist, segments_cross
from l7r.diagram.settlement._geom.indexes import PointGrid

from ..consts import Poly, Pt
from . import law
from .bund import BRANCH_STEP_FT, BRANCH_WIDTH, run_on_target
from .checks import ford_crossing, unreached_houses
from .fabric import _homestead_polys
from .geom import WorkedGround, _components, polyline_len
from .route import _route

ACCESS_ROLE = "access"
"""The `role` a drawn corridor carries - read by `is_tree`, so no settle repair cuts it."""

ON_TREE_PX = 1.5
"""How near a corridor's target must stand to another corridor (or the exit strip) to be read as ON it: the record rounds
every point to 0.1 px, and a target is the exact foot on its host, so this is rounding room and nothing more."""

ACCESS_WIDTH = 3.0
"""A drawn corridor's tread, in ft: a footpath, the width `settle_the_web`'s door paths are drawn at.

Research: footpath width - research/questions/0081-village-lanes.drawing.html: 3 ft"""

TARGET_ROLE = "way target"
"""The `role` of a spur drawn to a way target (`meta.way_targets`: a burial ground's near edge) - a tree lane."""

FIELD_ROLE = "field way"
"""The `role` of the field's reserved corridor drawn where no way of the hamlet's reaches the field - a tree lane."""

STRIP_ROLE = "exit strip"
"""The `role` of the exit strip drawn as a lane, from its innermost attachment out to the connector - a tree lane."""

TREE_ROLES = (ACCESS_ROLE, TARGET_ROLE, FIELD_ROLE, STRIP_ROLE)

SPUR_TRIES = 120
"""How many spurs, shortest first, are offered to a way target or the field before the web says it has none: they leave
the network eight feet apart (`BRANCH_STEP_FT`), so 120 cover nearly a thousand feet of tread - the near stretch of every
lane round a small hamlet. Most are refused for meeting their lane at a needle's angle or at its end's fold (cohort seed
13's field: the forty nearest the bund all were)."""


def is_tree(ln: Mapping[str, Any]) -> bool:
    """Is this lane part of the tree no settle repair cuts - the connector, the exit strip, a drawn access corridor, a spur
    to a way target or the field way? ...OR A ROW VILLAGE'S STREET, or the path from a grove farm's front door (`serves`):
    a row's planned streets and each farm's own way to its street are its tree, laid for its farms as a nucleated seat's
    corridors are (feature 291 on 287). Cut as ordinary lanes, a farm's short path read as a fragment the street reached
    past, and the street's tail as a dangling end, so the settle trimmed Mizuguchi's street back farm by farm and left four
    farms unreached.

    Research:
        the access tree kept - research/questions/0081-village-lanes.drawing.html: every farmhouse served, the track out
            and the field way kept whole
        a row's streets kept - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: in a row
            village the road comes before the houses"""
    return bool(ln.get("connector")) or ln.get("role") in TREE_ROLES or bool(ln.get("street")) or bool(ln.get("serves"))


def _on_the_connector(lanes: Sequence[Mapping[str, Any]], idx: Sequence[int]) -> set[int]:
    """The lanes of `idx` joined to the connector's network at the ink tolerance (`law.JOIN_TOL`)."""
    live = [k for k in idx if len(lanes[k].get("pts") or []) >= 2]
    labels = _components([law.lane_pts(lanes[k]) for k in live], law.JOIN_TOL)
    roots = {labels[n] for n, k in enumerate(live) if lanes[k].get("connector")}
    return {k for n, k in enumerate(live) if labels[n] in roots}


def strands_only_ordinary(M: Mapping[str, Any], i: int) -> bool:
    """Would taking lane `i` away leave off the connector's network only ORDINARY lanes, and no farmhouse unreached that the
    web reaches now? Those lanes are then what the settle drops as off the network (`settle.settle_network`), and the reach
    they carried, if the map owes it, is drawn again as the tree (`settle.settle_reach`). False where nothing is stranded:
    `settle.keeps_the_network` answers that case.

    WHY (feature 304, on T03): a lane running beside another way past a pitch is taken away by the settle only where the web
    keeps its networks without it (`settle_shadows`). Kashikawa's field path, kept once its tip was set on the bund again,
    was joined to the street by a 350 ft link (`sweeps._join_orphan_ways`, the first join pass); the farm door path laid
    after it (`serve.lay_door_paths`, a tree lane bound for its own street) ran 204 ft within 30 ft of it, and the squared
    ford at the path's head made a Z across its joint with the link. The link was the only way joining the path, so it
    stayed - a doubled band the settle could see and not mend. Refusing the link where it would shadow was tried first and
    could not fire: the door path it doubles is laid after it.

    Research:
        one network - research/questions/0081-village-lanes.drawing.html: lanes stranded off the connector's network
            dropped where no farmhouse loses its way"""
    lanes = M.get("lanes") or []
    before = _on_the_connector(lanes, range(len(lanes)))
    lost = before - _on_the_connector(lanes, [k for k in range(len(lanes)) if k != i]) - {i}
    if not lost or any(is_tree(lanes[k]) for k in lost):
        return False
    trial = {**M, "lanes": [ln for k, ln in enumerate(lanes) if k != i and k not in lost]}
    return len(unreached_houses(trial)) <= len(unreached_houses(M))


def _pt(q: Sequence[float]) -> Pt:
    return (float(q[0]), float(q[1]))


def connector_start(M: Mapping[str, Any]) -> Pt | None:
    """Where the connector begins - the root the exit strip leads to."""
    con = next((ln for ln in M.get("lanes") or [] if ln.get("connector") and len(ln.get("pts") or []) >= 2), None)
    return None if con is None else _pt(con["pts"][0])


def _dedup(run: Poly) -> Poly:
    return [p for j, p in enumerate(run) if j == 0 or math.dist(p, run[j - 1]) > 1e-6]


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
    gable carry through a neighbor's house did, measured on a constructed pair) - a tree lane is asked this as well.

    Research: nothing built on a lane - research/questions/0081-village-lanes.drawing.html: no leg through a building"""
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


GABLE_MARGIN_FT = 6.0
"""How far off its gable wall a path carried round a house runs (`round_the_gable`): clear of the eaves by more than a
tread's half-width and the house-hit margin (`house_hit`: 1.5 + 2 ft), and inside the dooryard reach (12 ft) at the front
corner, so the carried end reaches the dooryard (`reaches_dooryard`). A map drawing convention.

Research: gable margin - UNRESEARCHED: 6 ft off the gable wall, labeled a drawing convention here"""


def round_the_gable(pts: Poly, house: Mapping[str, Any], far: bool = False, keep_end: bool = False) -> Poly:
    """`pts`, whose LAST point stands behind `house` (water W57), carried round the nearer gable to the front: its last
    point replaced by a point `GABLE_MARGIN_FT` off that gable's back corner and one as far off its front corner, in the
    band before the front face - the dooryard (`reaches_dooryard`). By the back corner, not straight to the gable's middle:
    a run from behind the house to its mid-gable cuts the back corner (cohort seeds 42, 43, 55 and 60, measured: every such
    run fouled its own house). The gable taken is the one on the side the end stands (the side the lane came from, on a
    tie); `far` takes the other, where a neighbor's garden stands along the nearer (cohort seed 55). `keep_end` keeps the
    last point and runs on from it instead - the stretch before it may carry other ways' junctions (cohort seed 31).

    Research:
        a path reaches the front - research/questions/0081-village-lanes.drawing.html: a lane ends at the dooryard
        round the nearer gable by its back corner - UNRESEARCHED"""
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


def samples_along(segs: Sequence[tuple[Pt, Pt]], step: float = BRANCH_STEP_FT) -> list[Pt]:
    """Points every `step` along the segments `segs` - where a spur may leave the network."""
    out: list[Pt] = []
    for a, b in segs:
        n = max(1, int(math.dist(a, b) // step))
        out.extend((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1))
    return out


def spur_runs(segs: Sequence[tuple[Pt, Pt]], target: Pt, limit: int = SPUR_TRIES) -> list[Poly]:
    """The straight spurs from the network `segs` to `target`, shortest first, at most `limit` - the candidates the web
    lays to a way target (a burial ground's edge) until one keeps the law.

    Research: shortest straight spur - research/questions/0081-village-lanes.drawing.html: a worn path takes the shortest way"""
    pts = sorted(samples_along(segs), key=lambda q: math.dist(q, target))
    return [[q, target] for q in pts[:limit] if math.dist(q, target) > 1.0]


def field_runs(segs: Sequence[tuple[Pt, Pt]], grounds: Sequence[WorkedGround], half: float, brook: Sequence[Pt] = (), fords: Sequence[Pt] = (), limit: int = SPUR_TRIES) -> list[Poly]:
    """The field paths from the network `segs` on to the bund: from each point of the network, nearest the ground first, to
    the point where it runs on to the worked ground's edge (`run_on_target`) - straight, or, where the straight run crosses
    the brook, over it square at the ford that makes the walk shortest (`ford_crossing`, the landings `bridges()` decks)
    and on to the bund from the far landing. The paddy's first and then the dry hem's, at most `limit` per ground, each
    ground's shortest first.

    Research:
        field path to the bund - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: from the network on to
            the paddy's edge, shortest first
        over the brook at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: square,
            at the ford that makes the walk shortest
        dry hem after the paddy - research/questions/0081-village-lanes.drawing.html: the spur stops at the hem's edge, offered only after the paddy's"""
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
    Legs the router finds no way for are left out.

    Research:
        field path to the bund - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: threaded round the
            steadings when no straight run keeps the law
        over the brook at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the
            fords nearest the network, crossed square"""
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


FORD_LANDING_FT = 22.0
"""A ford's landing stands this far off the brook square to its reach (`checks.ford_crossing`'s own `landing`).

Research:
    square at the ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the path runs
        square to the brook through the landing
    ford landing - UNRESEARCHED: 22 ft each side of the brook"""


def field_router(s: Any, brook: Poly) -> Callable[[Pt, Pt], Poly]:
    """The web's router (`route._route`) as a field way threads it: walled by the steadings' built ground (not the commons
    or the groves - a path crosses ground cover), hard against the field, the dry hem and the marsh, and kept off the brook
    but at its fords (the terms the straggler footpaths kept until feature 287 dropped them).

    Research:
        off the crop and marsh - research/questions/0081-village-lanes.drawing.html: the field, the dry hem and the marsh hard
        across ground cover - UNRESEARCHED: the commons and the groves are not walls to a path
        the brook at its fords - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        nothing built on a lane - research/questions/0081-village-lanes.drawing.html: every steading part a wall but the
            path's own dooryard"""
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
(`fouled_segment`) refused it.

Research: field way off the steadings - research/questions/0081-village-lanes.drawing.html: 5.5 ft, the half-tread and 3 ft"""
