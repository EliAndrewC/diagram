"""The web settles itself: the LAST pass of `stage_web` (feature 287, M4).

WHY IT EXISTS. The web is some forty passes, each with its own partial guard - "no worse than it was", "the least bad",
"keep the orphan" - and nothing after them re-asks the rules the finished-map tests assert. So a rule held on the seeds the
tests roll and nothing stopped the next seed breaking it. This pass asks every rule of the lane law (`law.py`, the ONE
predicate per rule that the tests call too) of the web as it stands, and repairs what breaks one, until a whole round
changes nothing. It is the guarantee; the passes before it are best-effort drawing.

WHAT A REPAIR MAY DO. It only takes material AWAY from an ordinary lane - cuts a crossing, a fold or a foul out of it,
shortens an end, re-aims an end's last leg at the foot of its own previous vertex (never longer than the leg it replaces),
drops a piece that no longer joins the connector's network - or squares a crossing. It never cuts the TREE (`corridors.
is_tree`: the connector, whose hook alone it takes off, and the lanes step 4 draws); the one tree edit is step 3's, which
takes a tree lane away WHOLE where it alone carries a way out over the brook and back, and step 4 lays that reach again
only where it adds no such way out (`Lawful`); and a tree lane shorter than `law.FRAGMENT_FT` that earns nothing goes whole
as any lane does (`settle_fragments`, homes H40) - it reaches nothing step 4 owes. That is the termination argument:
every repair but the squaring strictly shortens the non-tree web, the squaring is idempotent (`checks.square_crossings`),
and step 4 adds a tree lane at most once per house, way target and field. Should the rounds run out, or a round change
nothing, with a rule still broken (`unsettled`, the whole law asked at the exit), the ORDINARY lanes still breaking one are
dropped whole, round by round, until none is (FR-005: a lane that cannot
be repaired is dropped; it is never kept as "the least bad"); a rule the tree alone still breaks is refused by name, never
mended by dropping a tree lane (`last_resort.py`).

THE REACH IS DRAWN HERE (step 4; ways W01, W03, homes H36). A lane a repair cuts may have been some farmhouse's only way,
and the web may never have reached one at all. The seating reserved a corridor from every door to the exit strip the
connector starts on (`settlement/rolling/access.py`, `track._cluster_gateway`) and judged the whole tree as lanes with
each (`tree.admits`), so the tree lanes owed - every unreached farmhouse's chain and the field's corridor - are drawn as
judged (`tree.settle_tree`), the ordinary lanes deferring to them (`tree.settle_defer`); a spur is laid to each way target
the network misses (a burial ground's edge), the shortest run that keeps the law (`Lawful`); and a tree lane the map no
longer needs is pruned (`tree.prune_the_tree`). This replaced the driver's re-roll (feature 287, FR-002).

THE CROSSINGS ARE SQUARED HERE (ways W11): the squaring `stage_crossings` did after the woods now runs as this pass's first
step, so every guarantee below is judged on the squared lane and no stage after the web rewrites one.

Research: settle plumbing - NONE: rounds, step order and bookkeeping; each rule is claimed at its predicate in law.py"""

from __future__ import annotations

import math
import time
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.overlap.registry import forbidden_segment
from l7r.diagram.settlement import rot_rect, seg_closest, seg_dist
from l7r.diagram.settlement._knobs import bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import flooded_ground
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes
from l7r.diagram.settlement.water_ways.lanes import behind_house, reaches_dooryard

from ..consts import WAY_END_REACH_FT, WEB_CLEARANCE, WEB_FABRIC_GAP, Poly, Pt
from . import law
from .arcs import arc_at, cut_around, sub_run  # noqa: F401 - re-exported: `settle.sub_run` and the rest are what tree.py and the tests name
from .checks import square_crossings, unreached_houses
from .clearance import kink_spans
from .corridors import (
    ACCESS_WIDTH,
    GroundIndex,
    _poly_box,
    building_quads,
    is_tree,
    round_the_gable,
    strands_only_ordinary,
    through_a_building,
)
from .fabric import _crosses_fabric, _homestead_polys, house_hit
from .geom import _TOUCH_GAP, _components, _trim_to_service, memo_ground, polyline_len, steading_footprints, worked_ground
from .joints import joints, rank_width
from .keeper import NOT_THE_SETTLES, unsettled  # noqa: F401 - re-exported: `settle.unsettled` is the exit question callers name
from .knots import settle_knots
from .reach import _draw_tree_lane, settle_field, settle_targets  # noqa: F401 - re-exported: callers and tests name these as `settle.<name>`
from .serve import shadowed_by
from .squaring import SQUARE_MARGIN_FT, SQUARE_PASSES, _pts, square_every_crossing, square_run, square_waters  # noqa: F401 - re-exported: callers and tests name these as `settle.<name>`
from .sweeps import _DOUBLED_DEG, along_tail, cut_at_tail
from .tree import left_to_the_tree, prune_the_tree, settle_defer, settle_tree, tree_faults
from .weld import weld_corner

SETTLE_ROUNDS = 8
"""Repair rounds before the lanes still breaking a rule are dropped whole. Each round runs every rule once; a measured
pool map settles in one or two (T55's measurement), so eight is a bound, not a tuning."""

CROSSING_GAP_FT = 2.0
"""How far past the water's edge each piece of a cut crossing stops - the lane ends on the bank, not in the water.

Research: a cut crossing ends on the bank - UNRESEARCHED: 2 ft past the water's edge"""

# ---- a lane as a run of arc length -----------------------------------------------------------------------------------


def _rounded(p: Poly) -> list[list[float]]:
    return [[round(a, 1), round(b, 1)] for a, b in p]


def apply_pieces(s: Any, edits: Mapping[int, list[Poly]]) -> int:
    """Replace each lane `i` of `edits` by its pieces - the first in place, record and ink together, the rest as new lanes of
    the same width and kind - and drop a lane left with no piece of 1 ft or more. Returns the lanes changed."""
    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    drops = []
    for i, pieces in edits.items():
        ln = lanes[i]
        keep = [q for q in pieces if len(q) >= 2 and polyline_len(q) >= 1.0]
        if not keep:
            drops.append(i)
            continue
        if not s.reshape_lane(ln, keep[0]):
            continue  # the matrix refuses what the cut would leave (feature 287 M8): the lane stands as it was
        s.reink_lane(i)
        for q in keep[1:]:
            s.lane(q, width=float(ln.get("w") or 3.0), clearance=WEB_CLEARANCE, worn=bool(ln.get("worn", True)))
            lanes[-1].update({key: ln[key] for key in ("role", "web") if key in ln})
    if drops:
        s.drop_lanes(drops)
    return len(edits)


def _ordinary(M: Mapping[str, Any]) -> list[int]:
    """The lanes a repair may cut: every lane but the tree (`is_tree` - the connector and the drawn access corridors)."""
    return [i for i, ln in enumerate(M.get("lanes") or []) if not is_tree(ln) and len(ln.get("pts") or []) >= 2]


# ---- step 2: a lane's own shape and its crossings ----------------------------------------------------------------------


Yards = list[tuple[Poly, Pt | None]]


def _fabric(s: Any) -> tuple[Yards, list[Mapping[str, Any]]]:
    yards = [(poly, owner) for poly, owner, kind in _homestead_polys(s) if kind in ("threshing_yards", "gardens")]
    return yards, list(s.M.get("houses") or [])


def theirs(p: Poly, yards: Yards, houses: Sequence[Mapping[str, Any]]) -> list[Poly]:
    """The yards and gardens a lane along `p` may not come near: all but those within `law.DOORSTEP_FT` of one of its ENDS.

    Research:
        a lane arrives at its own dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: its way leaves its dooryard round its own beds and fixtures
        the dooryards it arrives among - UNRESEARCHED: every steading within `DOORSTEP_FT` of either end exempt from the fence clearance, the dooryards it arrives among"""
    own = [(float(h["x"]), float(h["y"])) for h in houses if min(math.dist(p[0], (float(h["x"]), float(h["y"]))), math.dist(p[-1], (float(h["x"]), float(h["y"])))) <= law.DOORSTEP_FT]
    return [poly for poly, owner in yards if owner is None or all(math.dist(owner, c) > 1.0 for c in own)]


def fouled_segment(
    p: Poly, width: float, houses: Sequence[Mapping[str, Any]], yards: Yards, solid: Sequence[tuple[float, float, float, float]], fixtures: Sequence[Poly] = (), M: Any = None
) -> int | None:
    """The first segment of `p` that fouls the fabric: ink on a farmhouse (`house_hit`), within `WEB_FABRIC_GAP` of another
    household's yard or garden (`law.fouls_fabric`, `theirs`), a long leg through a building's box (`law.breaks_mid_run`),
    a tread over a farmstead fixture, the lane's own household's too (`law.over_a_fixture`), or a tread the overlap matrix
    forbids on what stands on `M` (`registry.forbidden_segment`, feature 287 M8: a yard, a garden, a well, a burial
    ground - its own household's too, since a path arrives at its dooryard and does not cross it).

    Research:
        no tread on a farmhouse - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html
        off another household's yard or garden - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the line within `WEB_FABRIC_GAP`, 7 ft
        no long leg through a building - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: `law.breaks_through`
        off the fixtures - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: its own household's too
        what the overlap matrix forbids - NONE: each pair is claimed in the matrix"""
    near = theirs(p, yards, houses)
    over = law.over_a_fixture(p, width, fixtures) if fixtures else None
    matrix = forbidden_segment(M, "lanes", p, width) if M is not None else None
    for k, (a, b) in enumerate(zip(p, p[1:], strict=False)):
        if k in (over, matrix):
            return k
        if house_hit([a, b], width, houses) or _crosses_fabric([a, b], near, WEB_FABRIC_GAP):
            return k
        if law.breaks_through([a, b], solid):
            return k
    return None


def _crossing_fault(M: Mapping[str, Any], i: int, p: Poly, wet: Sequence[Poly]) -> list[Poly] | None:
    """The pieces lane `i` is cut into for its first crossing fault, or None: a brook crossed twice (the stretch between the
    two crossings goes), a crossing off a ford, off square after the squaring, or where no deck seats (the crossing goes).

    Research:
        brook crossed twice - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the stretch between goes
        crossed off a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the crossing goes
        crossed off square - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html,
            research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the crossing goes
        a crossing no deck seats - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: squared, else cut"""
    ftpx = float((M.get("meta") or {}).get("ftpx") or 1.0)
    gap = CROSSING_GAP_FT / ftpx
    for brook in law._brooks(M):
        xs = law.crossing_points(p, brook)
        if len(xs) >= 2:
            (k0, x0), (k1, x1) = xs[0], xs[1]
            return [q for q in (sub_run(p, 0.0, arc_at(p, k0, x0) - _cut_gap(M, x0) - gap), sub_run(p, arc_at(p, k1, x1) + _cut_gap(M, x1) + gap, polyline_len(p))) if q]
    lone = {**M, "lanes": [M["lanes"][i]]}
    for _j, k, x in law.off_ford_at(lone):
        return cut_around(p, arc_at(p, k, x), _cut_gap(M, x) + gap)
    for water in ("brook", "channel"):
        for _j, k, x, _off in law.oblique_at(lone, water):
            return cut_around(p, arc_at(p, k, x), _cut_gap(M, x) + gap)
    ln = M["lanes"][i]
    width = float(ln.get("w") or 3.0)
    waters = bridge_crossed_waters(M)
    for k, x in law.undeckable_at(p, width, waters, ftpx, wet, M):
        # A CROSSING NO DECK SEATS is squared to the water it crosses first - a square deck is the shortest, and the
        # one most likely to land on the bank (the field path over its canal, R3) - and cut only if even that will not seat
        for wpts, ww in waters:
            course = [(float(q[0]), float(q[1])) for q in wpts]
            if len(course) >= 2 and any(math.dist(x, y) < 1.0 for _k, y in law.crossing_points(p, course)):
                sq = square_crossings(p, course, float(ww) / 2 + SQUARE_MARGIN_FT / ftpx)
                if sq != p and not law.undeckable_at(sq, width, waters, ftpx, wet, M):
                    return [sq]
        return cut_around(p, arc_at(p, k, x), _cut_gap(M, x) + gap)
    return None


def _cut_gap(M: Mapping[str, Any], x: Pt) -> float:
    """Half the width of the widest recorded water within reach of the crossing `x` - where its bank stands."""
    near = [
        float(w) / 2
        for wpts, w in bridge_crossed_waters(M)
        if len(wpts) >= 2 and min(seg_dist(x[0], x[1], (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in zip(wpts, wpts[1:], strict=False)) <= float(w)
    ]
    return max(near, default=3.0)


def _unkinked(p: Poly, span: tuple[str, int, int]) -> list[Poly]:
    """A run that doubles back keeps its longer arm; one that kinks loses the stretch between its two turns.

    Research: no hairpin or zigzag - research/questions/0081-village-lanes.drawing.html: longer arm kept, or the turns' stretch cut"""
    kind, ka, kb = span
    if kind == "doubles back":
        head, tail = p[: ka + 1], p[ka:]
        return [max(head, tail, key=polyline_len)]
    return [q for q in (p[: ka + 1], p[kb:]) if len(q) >= 2]


def settle_shapes(s: Any) -> int:
    """Step 2: cut from every ordinary lane what breaks its own shape or its crossings (ways W07, W09, W11, W12, W18, W19),
    and take a hook off the connector's end. One fault per lane per round; the next round asks again.

    Research:
        a lane's end loses its hook - research/questions/0081-village-lanes.drawing.html: re-laid as a T where it joins a way, else cut
        no hairpin or zigzag - research/questions/0081-village-lanes.drawing.html: cut as `_unkinked` cuts it
        crossings and fouls - NONE: claimed at `_crossing_fault` and `fouled_segment`"""
    M = s.M
    lanes = M.get("lanes") or []
    yards, houses = _fabric(s)
    solid = law.solid_boxes(M)
    fixtures = law.fixture_quads(M)
    wet = flooded_ground(M)
    edits: dict[int, list[Poly]] = {}
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if len(p) < 2 or (is_tree(ln) and not ln.get("connector")):
            continue
        ends = law.hooked(p)
        if ends:
            # A HOOK is a lane overshooting the way it joins and bending back onto it: re-laid as a T on that way where it
            # joins one (so the web stays one network), else its hook leg is taken off
            seq = _as_end(p, ends[0])
            j = joined_way(lanes, i, seq[-1])
            edits[i] = [_back(reaimed(seq, _pts(lanes[j]), bool(lanes[j].get("connector"))) if j is not None else seq[:-1], ends[0])]
            continue
        if ln.get("connector"):
            continue
        spans = kink_spans(p)
        if spans:
            edits[i] = _unkinked(p, spans[0])
            continue
        pieces = _crossing_fault(M, i, p, wet)
        if pieces is not None:
            edits[i] = pieces
            continue
        k = fouled_segment(p, float(ln.get("w") or 3.0), houses, yards, solid, fixtures, M)
        if k is not None:
            edits[i] = [q for q in (p[: k + 1], p[k + 1 :]) if len(q) >= 2]  # the fouling segment goes; a lane of one goes whole
    return apply_pieces(s, edits)


# ---- step 3: the ways out ----------------------------------------------------------------------------------------------


def settle_way_outs(s: Any) -> int:
    """Step 3 (ways W08): while some household's way out crosses one brook more than once (`law.way_out_carriers`), cut the
    crossing nearest that household out of the ordinary lane that carries it. WHERE ONLY TREE LANES CARRY IT (a corridor, a
    spur or the field way, laid when a lane since cut gave that household a shorter way out), the first of them goes whole:
    step 4 lays its reach again under `Lawful`, which refuses a lane that adds such a way out - so the tree is no exemption
    from the rule, only from the cutting.

    Research: no way out over and back - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html"""
    M = s.M
    lanes = M.get("lanes") or []
    carriers = law.way_out_carriers(M, departure_routes(M))
    for i, k, y in carriers:
        if not is_tree(lanes[i]):
            p = _pts(lanes[i])
            return apply_pieces(s, {i: cut_around(p, arc_at(p, k, y), _cut_gap(M, y) + CROSSING_GAP_FT)})
    if carriers:
        s.drop_lanes([carriers[0][0]])
        return 1
    return 0


# ---- step 4: where lanes end and meet ----------------------------------------------------------------------------------


def joined_way(lanes: Sequence[Mapping[str, Any]], i: int, q: Pt) -> int | None:
    """The index of the nearest OTHER lane whose tread the point `q` stands on (within `law.JOIN_TOL`), or None."""
    best: tuple[float, int | None] = (law.JOIN_TOL, None)
    for j, ln in enumerate(lanes):
        o = _pts(ln)
        if j == i or len(o) < 2:
            continue
        d = min(seg_dist(q[0], q[1], u, v) for u, v in zip(o, o[1:], strict=False))
        if d <= best[0]:
            best = (d, j)
    return best[1]


def _as_end(p: Poly, end: int) -> Poly:
    """`p` oriented so the named end (-1 last, 0 first) is its last point."""
    return p if end == -1 else p[::-1]


def _back(q: Poly, end: int) -> Poly:
    return q if end == -1 else q[::-1]


def _foot(q: Pt, tread: Poly) -> Pt:
    """The point of the run `tread` nearest `q`."""
    return min((seg_closest(q[0], q[1], u, v) for u, v in zip(tread, tread[1:], strict=False)), key=lambda f: math.dist(q, f))


meets_clean = law.meets_clean


def reaimed(seq: Poly, tread: Poly, connector: bool = False) -> Poly:
    """`seq` (ending on the way `tread`) re-laid to meet it cleanly (`meets_clean`): from the last vertex before its end
    whose leg to its foot on the tread keeps the law, that leg - never longer than what it replaces, since a foot is the
    nearest point; a vertex already standing on the tread simply ends the lane there. With no such vertex the last leg is
    dropped.

    Research: a lane meets another as a T - research/questions/0081-village-lanes.drawing.html: the end re-laid, never longer"""
    for m in range(len(seq) - 2, -1, -1):
        b = seq[m]
        f = _foot(b, tread)
        cand = seq[: m + 1] if math.dist(b, f) <= _TOUCH_GAP else [*seq[: m + 1], f]
        if len(cand) >= 2 and cand != seq and meets_clean(cand, tread, connector):
            return cand
    return seq[:-1]


def settle_ends(s: Any) -> int:
    """Step 4: the joints and the ends (ways W05, W10, W16, W20, W21, W22) - each fixed by shortening, never lengthening.

    ONE FIX PER MEETING PER ROUND: a repair names every lane it involves (the lane it edits and the way it meets), and a
    later repair touching any of them waits for the next round. Two repairs made at once on the two sides of one joint -
    Kashikawa's field path re-aimed off a needle while the lane it continued was re-aimed off the fold at the same point -
    each assumed the other side stood still, and the web came apart there.

    Research:
        lanes met end to end read as one - research/questions/0081-village-lanes.drawing.html: a needle, fold or hairpin re-laid as a T
        no doubled tail - CONVENTION: the end cut back to where it came alongside the way
        no fan of stubs at a door - UNRESEARCHED: past two ends at one house, the farther cut back past the doorstep
        a lane ends at the dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end behind a house carried round
            its gable where lawful, else backed off (`off_the_back`)"""
    M = s.M
    lanes = M.get("lanes") or []
    edits: dict[int, list[Poly]] = {}
    touched: set[int] = set()

    def claim(involved: set[int], i: int, pieces: list[Poly]) -> None:
        if not involved & touched and not is_tree(lanes[i]):
            edits[i] = pieces
            touched.update(involved)

    for ci, i, end in law.connector_hairpin_ends(lanes):
        claim({ci, i}, i, [_back(reaimed(_as_end(_pts(lanes[i]), end), _pts(lanes[ci]), connector=True), end)])
    for i, end, k, _u, _v in law.needle_ends(lanes):
        claim({i, k}, i, [_back(reaimed(_as_end(_pts(lanes[i]), end), _pts(lanes[k]), bool(lanes[k].get("connector"))), end)])
    for i, ei, j, ej in law.folded_joint_pairs(lanes):
        # the SHORTER record of the two that has a vertex to fall back to is re-aimed as a T on the other; two bare legs
        # folded on each other lose the shorter
        x, y = _as_end(_pts(lanes[i]), ei), _as_end(_pts(lanes[j]), ej)
        both = sorted(((polyline_len(q), m, q, e, o) for m, q, e, o in ((i, x, ei, y), (j, y, ej, x)) if not is_tree(lanes[m])), key=lambda c: c[0])
        bent = [c for c in both if len(c[2]) >= 3]
        if not both:
            continue
        if bent:
            _len, m, seq, me, other = bent[0]
            claim({i, j}, m, [_back(reaimed(seq, other), me)])
        else:
            claim({i, j}, both[0][1], [])
    for i in law.doubled_tails(M):
        p = _pts(lanes[i])
        # ...at whichever end runs on beside the way (`doubled_tails` asks both): the first end is cut as the last end of the
        # lane reversed, and turned back
        for j, o in enumerate(lanes):
            op = _pts(o)
            if j == i or len(op) < 2:
                continue
            hit = next(((q, k, back) for q, back in ((p, False), (p[::-1], True)) if (k := along_tail(q, op, deg=_DOUBLED_DEG)) is not None), None)
            if hit is not None:
                q, k, back = hit
                cut = cut_at_tail(q, k, op)
                claim({i, j}, i, [cut[::-1] if back else cut])
                break
    houses = M.get("houses") or []
    for h, ends in law.fronting_ends(M).items():
        c = (float(houses[h]["x"]), float(houses[h]["y"]))
        # ...the tree's ends kept first (a tree lane is never cut; the ordinary lanes defer to it), then the nearer
        for i, end in sorted(ends, key=lambda ie: (not is_tree(lanes[ie[0]]), math.dist(c, _pts(lanes[ie[0]])[ie[1]])))[law.DOORSTEP_MAX :]:
            seq = _as_end(_pts(lanes[i]), end)
            walk = next((polyline_len(seq[: k + 1]) for k in range(len(seq) - 1, -1, -1) if math.dist(seq[k], c) > law.DOORSTEP_FT), 0.0)
            claim({i}, i, [_back(sub_run(seq, 0.0, walk), end)] if walk > 0 else [])
    # AN END BEHIND A HOUSE IS CARRIED ROUND THE GABLE TO ITS FRONT, OR CUT (water W57): where the carried run keeps the law
    # (`Lawful`, asked without the lane it replaces) the end runs on round the nearer gable into the dooryard band, or the
    # farther; otherwise the end is taken back only as far as it stands behind the house (`off_the_back`) - never a whole
    # leg: cohort seed 31's backbone lane lost its 200 ft last leg to a cut, and fifteen houses hanging off that leg were
    # stranded - and the next round asks what the shortened end reaches (a dangling end is trimmed to service, a house left
    # unreached is its corridor's). Each lane's first such end only, one repair per round.
    lawful: Lawful | None = None
    for i, end, h in law.ends_behind(M, memo_ground(s, "worked", worked_ground)):
        if i in touched or is_tree(lanes[i]):
            continue
        seq = _as_end(_pts(lanes[i]), end)
        lawful = lawful or Lawful(s)
        width = float(lanes[i].get("w") or 3.0)
        gables = [round_the_gable(seq, houses[h], far=far, keep_end=keep) for keep in (False, True) for far in (False, True)]
        carries = [c for c in gables if lawful(c, width, skip=i)]
        # ...PREFERRING A REPAIR THAT SPLITS NOTHING (`keeps_the_network`): a carry, then the back-off; where each would leave
        # another way's end hanging, the carry or the back-off all the same - the rule holds, and a house the split strands is
        # its corridor's
        others = [sg for k, o in enumerate(lanes) if k != i for sg in zip(_pts(o), _pts(o)[1:], strict=False)]
        options = [_back(q, end) for q in (*carries, off_the_back(seq, houses[h], others))]
        # ...judged against the web WITH this round's earlier repairs made: two carries each harmless alone can together
        # take a junction's both sides (cohort seed 31's lanes 8 and 10, carried round one gable to one point)
        work = with_edits(M, edits)
        claim({i}, i, [next((q for q in options if keeps_the_network(work, i, [q])), options[0])])
    if edits:
        return apply_pieces(s, edits)
    return settle_dangling(s)


BACK_OFF_STEP_FT = 2.0
"""The step an end behind a house is taken back in (`off_the_back`)."""


def off_the_back(seq: Poly, house: Mapping[str, Any], others: Sequence[tuple[Pt, Pt]] = ()) -> Poly:
    """`seq`, whose last point stands behind `house` (water W57), taken back along itself to the first point that no longer
    does - beside the house, at its dooryard, or past `WAY_END_REACH_FT` from it, where the end is no longer the house's
    to reach - or to its last junction (a point within `law.JOIN_TOL` of another way's `others` segment), which is the
    stub's own end: the design's "trimmed back to the last way junction", so no way that joins the lane is cut off it. []
    where no such point is left (the lane stands wholly behind the house).

    Research:
        a lane ends at the dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: backed off to beside the house,
            its dooryard, 60 ft from it or its last junction"""
    c, total = (float(house["x"]), float(house["y"])), polyline_len(seq)
    walk = total
    while walk > 0.0:
        run = sub_run(seq, 0.0, walk)
        q = run[-1] if run else seq[0]
        if math.dist(q, c) > WAY_END_REACH_FT or not behind_house(house, q) or reaches_dooryard(house, q) or any(seg_dist(q[0], q[1], a, b) <= law.JOIN_TOL for a, b in others):
            return run
        walk -= BACK_OFF_STEP_FT
    return []


def settle_dangling(s: Any) -> int:
    """Every ordinary lane is trimmed to service (`_trim_to_service`, at the law's own segment set): an end that reaches
    nothing but the way it left (W16), and an end served by a house alone that runs on past it (the road to nowhere, H41 -
    `_trim_to_service` stops it at its closest approach). No exemption for a house the lane alone reaches - that house is
    the corridor's. A lane the law still calls dangling after its trim goes whole.

    Research: an end reaches something seen - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: trimmed to service, else dropped"""
    M = s.M
    lanes = M.get("lanes") or []
    ground, steadings = memo_ground(s, "worked", worked_ground), steading_footprints(M)
    bad = {i for i, _e in law.dangling_lane_ends(M, ground)}
    ways = [_pts(ln) for ln in lanes]
    centers = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []]
    edits: dict[int, list[Poly]] = {}
    for i in _ordinary(M):
        others = [sg for k, o in enumerate(ways) if k != i and len(o) >= 2 for sg in zip(o, o[1:], strict=False)]
        trimmed = _trim_to_service(ways[i], others, centers, ground, (), steadings)
        if len(trimmed) < 2 or (i in bad and trimmed == ways[i]):
            edits[i] = []  # ...and one its trim cannot mend goes whole, as this docstring always said (feature 297: Inashiro's
            # two-point skeleton lane dangled through every round and the last resort dropped it - research R11)
        elif trimmed != ways[i] and (i in bad or polyline_len(ways[i]) - polyline_len(trimmed) > TRIM_GRAIN_FT):
            edits[i] = [trimmed]
    return apply_pieces(s, edits) if edits else 0


def settle_shadows(s: Any) -> int:
    """AN ORDINARY LANE RUNNING BESIDE ANOTHER WAY PAST A PITCH GOES (`shadowed_by`, `_lay_web_lane`'s own refusal - a lane
    that shadows another is a doubled band): of the two, the shorter ordinary lane where the web keeps its networks without
    it (`keeps_the_network`), one a round. Asked of the finished web because the join and touch passes lay lanes no shadow
    test sees (feature 293 on 291: a touch lane of Kashikawa's ran 106 ft within 30 ft of a join-orphans remnant, the two
    diverging at 22 degrees from one corner to one street).

    Research: no doubled band - UNRESEARCHED: of two ways side by side past a pitch, the shorter ordinary lane goes"""
    ways = [_pts(ln) for ln in s.M.get("lanes") or []]
    ordinary = set(_ordinary(s.M))
    for i in range(len(ways)):  # ...a tree lane too, beside an ordinary one: a door path is tree, the lane it doubles not
        if (j := shadowed_by(ways, i)) is not None:
            for k in sorted({i, j} & ordinary, key=lambda n: polyline_len(ways[n])):
                if keeps_the_network(s.M, k, []) or left_to_the_tree(s.M, k):  # ...a house it reached gets its reserved way
                    return apply_pieces(s, {k: []})
                if strands_only_ordinary(s.M, k):  # ...or with the ordinary lanes it alone joined (`strands_only_ordinary`)
                    return drop_stranding(s, k)
    return 0


def drop_stranding(s: Any, k: int) -> int:
    """Lane `k` taken away with the ordinary lanes it alone joined to the network (`settle_network`); where that took the
    web's way to the field, the field path is drawn again as `stage_web` drew it (`bund.a_way_onto_the_bund`, 269 B04), and
    the rounds settle it - Kashikawa's field path left with its link, and the field had no way (feature 304).

    Research: the field reached - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the field path drawn again"""
    from .bund import a_way_onto_the_bund  # bund.py reads this module's neighbors; imported where it is used

    reached = not law.field_unreached(s.M)
    n = apply_pieces(s, {k: []}) + settle_network(s)
    if reached and law.field_unreached(s.M):
        s.M.setdefault("meta", {})["field_path"] = a_way_onto_the_bund(s)
    return n


def settle_street_ends(s: Any) -> int:
    """A ROW'S STREET, a tree lane no trim cuts, has an end the lane law calls dangling cut back to its last joint
    (`end_to_its_joint`); returns the streets cut. The web cuts each street to its outermost joints before the settle
    (`trim_streets`), and a repair or the last resort's drop can take the lane that stood at that joint (feature 293 on 291:
    cohort seed 903's street ended in a knot of stubs 191 ft past its nearest farm, each counted as reaching the next until
    the law stopped counting a way an end walked away from; the knot dropped, the street's end served nothing and the web
    was refused).

    Research: an end reaches something seen - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a street's dangling end cut to its last joint"""
    from .street import end_to_its_joint  # street.py imports this module's `Lawful`; imported where it is used

    M = s.M
    lanes = M.get("lanes") or []
    if not any(ln.get("street_index") is not None for ln in lanes):
        return 0
    ways = [_pts(ln) for ln in lanes]
    edits: dict[int, list[Poly]] = {}
    for i, e in law.dangling_lane_ends(M, memo_ground(s, "worked", worked_ground)):
        if lanes[i].get("street_index") is None:
            continue
        run = edits[i][0] if i in edits else ways[i]
        cut = end_to_its_joint(run, [o[k] for j, o in enumerate(ways) if j != i and len(o) >= 2 for k in (0, -1)], _TOUCH_GAP, e)
        if len(cut) >= 2 and cut != run:
            edits[i] = [cut]
    return apply_pieces(s, edits) if edits else 0


TRIM_GRAIN_FT = 1.0
"""A trim that takes less than this off a lane whose ends the law already calls served is the record's own rounding, not a
trim, and changes nothing; on a lane the law calls dangling any trim is taken."""


# ---- step 5: every join touches, then one network -----------------------------------------------------------------------


def settle_joins(s: Any) -> int:
    """Every join that stops short (`law.near_misses`: a free end making for a way within its reach, over walkable ground)
    is carried onto that way - it ends ON the tread it joins (homes H37), and a way drawn as two across a hole is one again
    (H38; the span may not run along a tread, H39). The only step that adds tread, and only to close a hole, once per end:
    an end it closes is no longer free. Before the network rule, so a piece the ink tolerance would drop is joined first.

    Research:
        ends that nearly meet are joined - research/questions/0081-village-lanes.drawing.html: carried onto the way
        a join taken back - UNRESEARCHED: an ordinary end whose join breaks a rule against a tree lane, or the overlap matrix refuses, taken back 5 ft past the join's reach (`JOIN_BACK_PAD_FT`), the settle's trims then pulling it to what it serves"""
    edits: dict[int, list[Poly]] = {}
    # A TREE LANE'S END IS CARRIED ONTO ITS WAY AS ANY LANE'S IS: the span only adds tread, over walkable ground, meeting the
    # way clean (`law.near_misses`), and the lane it reaches is an ordinary one the tree's joint then binds
    lanes = s.M.get("lanes") or []
    for i, end, f in law.near_misses(s.M):
        if i in edits:
            continue
        p = _pts(lanes[i])
        joined = [*p, f] if end == -1 else [f, *p]
        # ...BUT AN ORDINARY LANE WHOSE JOIN WOULD BREAK A RULE AGAINST A TREE LANE DEFERS: it is taken back out of the join's
        # reach instead - the deference would cut the join again, and the two passes took turns until the rounds ran out
        # (cohort seed 25 under the probes). AND SO DOES ONE WHOSE JOIN THE OVERLAP MATRIX REFUSES (feature 318, Kuwabata): the
        # law's walkable span reads the centerline 4 ft off a yard or garden, the matrix the whole tread, so a span the law
        # called walkable was refused at the write (`reshape_lane`) every round and the end left short of its way until the
        # web was refused - an end whose span is blocked is two ways, each ending at what it serves (`law.near_misses`)
        if not is_tree(lanes[i]) and (not _join_admitted(s, lanes[i], joined) or any(k == i for k, _q in tree_faults(with_edits(s.M, {i: [joined]})))):
            seq = _as_end(p, end)
            edits[i] = [_back(sub_run(seq, 0.0, polyline_len(seq) - law.JOIN_REACH_FT - JOIN_BACK_PAD_FT), end)]
            continue
        edits[i] = [joined]
    return apply_pieces(s, edits) if edits else 0


def _join_admitted(s: Any, ln: Mapping[str, Any], joined: Poly) -> bool:
    """Would the overlap matrix admit lane `ln` rewritten along `joined` - the question `reshape_lane` asks at the write,
    asked first so a refused join is taken back rather than left short (`settle_joins`, feature 318).

    Research: plumbing - NONE: the registry's own admission, at the record's 0.1 px
    """
    return bool(s.admits("lanes", {**ln, "pts": [[round(float(x), 1), round(float(y), 1)] for x, y in joined]}, ignore=ln))


JOIN_BACK_PAD_FT = 5.0
"""How far past a join's reach (`law.JOIN_REACH_FT`) an ordinary end that defers to a tree lane is taken back
(`settle_joins`), so it no longer makes for the way it stopped short of.

Research: a deferring end taken back - UNRESEARCHED: 5 ft past the join's reach"""


def settle_needles(s: Any) -> int:
    """Step 5b (homes H39): a way drawn twice round a needle of grass, or along the same ground (`law.needle_loops`), is
    opened - the shortest ordinary lane on the needle loses its stretch along it (the pieces either side kept), so the
    other way is the one walked. The cut must SPLIT NOTHING - the web in no more networks and no farmhouse newly unreached
    (cohort seed 31: a cut taken at the needle's corner took the junction three lanes hung from, and nine lanes fell off the
    network with thirteen houses) - so the shortest lane whose cut keeps both is cut, and a needle no cut opens that way
    waits for the next round. One cut a round; a needle bounded by the tree alone is left to the tree (it is drawn once per
    house and meets the network at its first contact, so it closes no loop of its own).

    Research:
        needle of grass opened - CONVENTION: the shortest ordinary lane on it loses its stretch along it
        a sliver welded shut - CONVENTION: a corner moved onto the tread beside it (`weld.weld_corner`)"""
    from shapely.geometry import LineString

    M = s.M
    lanes = M.get("lanes") or []
    for face, bounding in law.needle_loops(M):
        for i in sorted((k for k in bounding if not is_tree(lanes[k])), key=lambda k: polyline_len(_pts(lanes[k]))):
            rest = LineString(_pts(lanes[i])).difference(face.exterior.buffer(1.0))
            parts = [rest] if rest.geom_type == "LineString" else list(getattr(rest, "geoms", []))
            pieces = [[(float(x), float(y)) for x, y in g.coords] for g in parts if g.geom_type == "LineString" and not g.is_empty]
            if keeps_the_network(M, i, pieces):
                return apply_pieces(s, {i: pieces})
        if (welded := weld_corner(lanes, face, bounding)) is not None:  # a sliver where two ways meet: one vertex, no face (`weld.py`)
            return apply_pieces(s, {k: [p] for k, p in welded.items()})
    return 0


def with_edits(M: Mapping[str, Any], edits: Mapping[int, Sequence[Poly]]) -> dict[str, Any]:
    """`M` as `apply_pieces` would leave it after `edits`, its lane indices kept: each edited lane's first piece in place (a
    lane with none left empty rather than removed) and the further pieces appended."""
    lanes = [dict(ln) for ln in M.get("lanes") or []]
    extra = []
    for i, pieces in edits.items():
        lanes[i]["pts"] = [list(q) for q in pieces[0]] if pieces else []
        extra += [{"pts": [list(q) for q in p]} for p in pieces[1:]]
    return {**M, "lanes": [*lanes, *extra]}


def keeps_the_network(M: Mapping[str, Any], i: int, pieces: Sequence[Poly]) -> bool:
    """Would lane `i` redrawn as `pieces` SPLIT NOTHING - the web in no more networks (`law.lane_networks`), no farmhouse
    newly unreached (`unreached_houses`), and every other lane joined to the connector's network still joined to it
    (`connector_component`, what `settle_network` keeps)? A repair that moves a lane's end asks it: another way's end on the
    stretch it moves is left hanging otherwise (cohort seed 31: a backbone's end carried round a gable took the tread three
    lanes stood on, and nine lanes fell off the network with thirteen houses).

    Research: one network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a repair splits nothing and strands no farmhouse"""
    lanes = M.get("lanes") or []
    joined = connector_component(lanes)
    others = [k for k in range(len(lanes)) if k != i]
    trial = {**M, "lanes": [*(lanes[k] for k in others), *({"pts": q} for q in pieces if len(q) >= 2 and polyline_len(q) >= 1.0)]}
    kept = connector_component(trial["lanes"])
    if sum(1 for n, k in enumerate(others) if k in joined and n in kept) != len(joined - {i}):
        return False  # the cheap question first: the reach below grows the served network lane by lane
    return law.lane_networks(trial) <= law.lane_networks(M) and len(unreached_houses(trial)) <= len(unreached_houses(M))


def connector_component(lanes: Sequence[Mapping[str, Any]]) -> set[int]:
    """The lanes joined to the connector's network at the ink tolerance (`law.JOIN_TOL`) - what `settle_network` keeps."""
    live = [i for i, ln in enumerate(lanes) if len(ln.get("pts") or []) >= 2]
    labels = _components([_pts(lanes[i]) for i in live], law.JOIN_TOL)
    roots = {labels[n] for n, i in enumerate(live) if lanes[i].get("connector")}
    return {i for n, i in enumerate(live) if labels[n] in roots}


def settle_fragments(s: Any) -> int:
    """A fragment that earns nothing (`law.short_fragments`) is dropped (homes H40) - one a round, since two fragments can
    each be redundant only while the other stands. A TREE lane too, the connector aside (`short_fragments` never names it):
    a corridor drawn to a house a lane since reaches, or a spur whose target another way now serves, earns nothing, and
    the rule is FRAGMENT_FT for every lane (Kashikawa's lane 17, a 28.8 ft access corridor, and Mizuguchi's lane 11, 16.1
    ft, stayed drawn while the tree was exempt - research R9). Dropping it cuts nothing another way needs, so the
    termination argument stands: the drop shortens the web, and `short_fragments` names only a lane whose loss leaves no
    house, target or field newly unreached, so step 4 does not draw it again.

    Research: debris - UNRESEARCHED: a lane under 30 ft that earns nothing goes, a tree lane too"""
    gone = law.short_fragments(s.M, memo_ground(s, "worked", worked_ground))[:1]  # the web's one ground (the perf-audit of 308)
    if gone:
        s.drop_lanes(gone)
    return len(gone)


def rewidth(s: Any, i: int, width: float) -> None:
    """Lane `i` drawn at `width`: its record, and its ink re-laid at that width (the old ink blanked) where the settlement
    keeps ink - a stand-in with no ink has only the record."""
    ln = s.M["lanes"][i]
    ln["w"] = width
    ink = getattr(s, "_lane_ink", None)
    if ink is None:
        return
    for z in ink[i]:
        for part in ("edge", "bed", "top"):
            if s.ground[z].get(part):
                s.ground[z][part] = ""
    ink[i] = s._lane_ink_at(ln["pts"], width, bool(ln.get("worn")), ln)


def settle_widths(s: Any) -> int:
    """One way keeps one width (homes H42), and each way its rank's: a lane its role ranks (`joints.rank_width`: a household's
    way 3 ft, the field spur 5) is drawn at its rank whatever it meets end to end - feature 328 wave 4's glyph-check of
    Inashiro found a household's way and the spur widened to a 6 ft link's tread, a 6 ft lane hanging off a 3 ft footpath. A
    chain of lanes meeting end to end (`joints`) draws its unranked members at its widest ranked member's rank, or its widest
    member's where none is ranked - in either case at its narrowest where that would foul the fabric (`fouled_segment`). No
    tread is widened onto a steading; a step left is where one rank meets another (`law.width_steps`).

    Research: one width a way - research/questions/0081-village-lanes.drawing.html: each way at its rank's width (3 ft footpath, 5 ft field spur), the rest of a chain at its widest rank, the narrowest where that fouls"""
    lanes = s.M.get("lanes") or []
    changed = 0
    for k, ln in enumerate(lanes):
        r = rank_width(ln)
        if r is not None and not ln.get("connector") and float(ln.get("w") or 3.0) != r:
            rewidth(s, k, r)
            changed += 1
    par = list(range(len(lanes)))

    def find(k: int) -> int:
        while par[k] != k:
            k = par[k]
        return k

    for i, _ei, j, _ej in joints(lanes):
        par[find(i)] = find(j)
    yards, houses = _fabric(s)
    solid = law.solid_boxes(s.M)
    fixtures = law.fixture_quads(s.M)
    for root in {find(i) for i in range(len(lanes)) if find(i) != i}:
        chain = [k for k in range(len(lanes)) if find(k) == root]
        free = [k for k in chain if rank_width(lanes[k]) is None]
        widths = [float(lanes[k].get("w") or 3.0) for k in chain]
        ranks = [w for k, w in zip(chain, widths, strict=True) if k not in free]
        wide = max(ranks or widths)
        target = wide if all(fouled_segment(_pts(lanes[k]), wide, houses, yards, solid, fixtures, s.M) is None for k in free) else min(widths)
        for k in free:
            if float(lanes[k].get("w") or 3.0) != target:
                rewidth(s, k, target)
                changed += 1
    return changed


def settle_network(s: Any) -> int:
    """Step 5 (ways W17): drop every lane not in the connector's network at the ink tolerance (`law.JOIN_TOL`).

    Research: one network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane off the connector's network dropped"""
    lanes = s.M.get("lanes") or []
    live = [i for i, ln in enumerate(lanes) if len(ln.get("pts") or []) >= 2]
    labels = _components([_pts(lanes[i]) for i in live], law.JOIN_TOL)
    if len(set(labels)) <= 1:
        return 0
    roots = {labels[n] for n, i in enumerate(live) if lanes[i].get("connector")}
    if not roots:
        roots = {max(set(labels), key=lambda lb: sum(polyline_len(_pts(lanes[live[n]])) for n, x in enumerate(labels) if x == lb))}
    gone = [i for n, i in enumerate(live) if labels[n] not in roots]
    s.drop_lanes(gone)
    return len(gone)


# ---- step 4b: the reach the web owes - a corridor, a way target, the field ----------------------------------------------


def open_ground_rings(M: Mapping[str, Any]) -> list[Poly]:
    """The outlines a lawful run may not cross (`GroundIndex.open_ground`): every field outline, dry plot and marsh - the
    ground `law.span_walkable` refuses a span, less the water, which a crossing fault judges (a decked or forded crossing is
    a lawful one).

    Research: off crop and marsh - research/questions/0081-village-lanes.drawing.html: field outlines, dry plots, marsh"""
    rings = [[(float(a), float(b)) for a, b in f["outline"]] for f in M.get("fields") or [] if f.get("outline")]
    rings += [[(float(a), float(b)) for a, b in d["poly"]] for d in M.get("dry_plots") or [] if d.get("poly")]
    rings += [[(float(a), float(b)) for a, b in m["poly"]] for m in M.get("marshes") or [] if len(m.get("poly") or ()) >= 3 and m.get("role") != "defense"]
    return rings


MEET_REACH_FT = 60.0
"""The lanes a new run is asked to meet cleanly are those whose box comes within this of its box: past every reach a joint
rule measures (a needle's 20 ft leg, a doubled tread's 14 ft, a join's 40 ft) - so the lanes left out cannot meet it."""


def _box(p: Poly, pad: float) -> tuple[float, float, float, float]:
    return (min(q[0] for q in p) - pad, min(q[1] for q in p) - pad, max(q[0] for q in p) + pad, max(q[1] for q in p) + pad)


class Lawful:
    """Would a run, drawn as a new lane of a given width, keep every per-lane rule of the law - no kink or hook, no crossing
    fault, no foul of the fabric, no field, dry plot or marsh underfoot (`open_ground_rings`) - and meet the ways it comes near
    as the law asks: no needle, fold or hairpin at either end, no tail doubled along a way, either way round - and, for a
    TREE lane (`tree`), no household's way out left crossing the brook twice (`law.adds_a_way_out_crossing`)? The ONE
    question the web asks before it adds a tree lane, since a tree lane is never cut afterwards. The map's fabric, water
    and wet ground are read once, when it is built, for every run a step asks about. The way-out clause is the tree's
    alone: an ordinary lane re-laid by a repair is cut by step 3 if it carries such a way out, and the route it asks costs
    two walks of the whole web a run (measured 30-60 ms on cohort seeds 3 and 12, most of the settle's time when every
    re-laid end asked it).

    Research: the lane law asked of a new lane - NONE: each clause claimed at `on_lawful_ground` and `__call__`"""

    def __init__(self, s: Any, tree: bool = False) -> None:
        self.M = s.M
        self.tree = tree
        self.wet = flooded_ground(s.M)
        self.yards, self.houses = _fabric(s)
        self.solid = law.solid_boxes(s.M)
        self.fixtures = law.fixture_quads(s.M)
        self.buildings = building_quads(s.M)
        self.ground = memo_ground(s, "worked", worked_ground)
        self._index: GroundIndex | None = None

    @property
    def index(self) -> GroundIndex:
        """The ground `on_lawful_ground` reads, indexed on first use (`corridors.GroundIndex`): the waters a crossing fault
        or the squaring reads, the outlines a run may not cross (`open_ground_rings`), and the fabric the foul tests read."""
        if self._index is None:
            M = self.M
            waters = [*law._brooks(M), *law.water_courses(M, "channel"), *(w for w, _ww in bridge_crossed_waters(M)), *(c for c, _h in square_waters(M))]
            houses = [(h, _poly_box(rot_rect(float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"]), float(h.get("rot", 0.0))))) for h in self.houses]
            self._index = GroundIndex(
                waters,
                open_ground_rings(M),
                {
                    "houses": houses,
                    "yards": [(y, _poly_box(y[0])) for y in self.yards if y[0]],
                    "solid": [(b, b) for b in self.solid],
                    "fixtures": [(q, _poly_box(q)) for q in self.fixtures],
                    "buildings": [(q, _poly_box(q)) for q in self.buildings],
                },
            )
            self._square_pad = max((h for _c, h in square_waters(M)), default=0.0) + 1.0
        return self._index

    def squared(self, run: Poly) -> Poly:
        """`square_run(self.M, run)`, skipped where no water the squaring reads comes within its reach of the run - there it
        changes nothing (no crossing to square, no vertex within a water's half-width to drop)."""
        return square_run(self.M, run) if self.index.water_near(run, self._square_pad) else list(run)

    def on_lawful_ground(self, run: Poly, width: float) -> bool:
        """THE GROUND HALF - what a run keeps whatever lanes the web draws beside it: no kink or hook, no crossing fault (a
        brook crossed off a ford or twice, a crossing off square, one no deck seats), no foul of a farmhouse, another
        household's yard or garden, a building or a farmstead fixture, no field, dry plot or marsh underfoot. The seating asks
        this of a corridor before it admits a house (`corridor_on_lawful_ground`), so the web can always draw what it
        reserved.

        Research:
            bends like a path - research/questions/0081-village-lanes.drawing.html: no kink or hook
            crossings - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: `_crossing_fault`
            nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no foul of house, yard, building, fixture
            off crop and marsh - research/questions/0081-village-lanes.drawing.html: no field, dry plot or marsh underfoot"""
        if len(run) < 2 or law.hooked(run) or kink_spans(run):
            return False
        # every test below reads only what stands near the run (`index`, `GroundIndex`): a crossing fault needs a crossing,
        # and each foul a part within its own reach of the run - so the parts beyond it are left out, not the verdict
        ix = self.index
        if ix.water_near(run, 1.0) and _crossing_fault({**self.M, "lanes": [{"pts": _rounded(run), "w": width}]}, 0, run, self.wet) is not None:
            return False
        houses = ix.near("houses", run, max(width / 2.0 + 2.0, law.DOORSTEP_FT) + 1.0)  # ...the doorstep's reach: `theirs` reads it
        fouled = fouled_segment(run, width, houses, ix.near("yards", run, WEB_FABRIC_GAP + 1.0), ix.near("solid", run, 1.0), ix.near("fixtures", run, width / 2.0 + law.FIXTURE_PAD_FT + 1.0), self.M)
        return fouled is None and ix.open_ground(run) and not through_a_building(run, ix.near("buildings", run, 1.0))

    def __call__(self, run: Poly, width: float, skip: int | None = None) -> bool:
        """`skip`: the lane `run` would replace, left out of what it is asked to meet.

        Research:
            lanes meet as a T - research/questions/0081-village-lanes.drawing.html: no needle, fold or hairpin at either end
            an end reaches something seen - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no dangling end, none behind a house
            no doubled tail - CONVENTION: either way round
            no way out over and back - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: tree lanes"""
        M = self.M
        if not self.on_lawful_ground(run, width):
            return False
        lanes = [ln for k, ln in enumerate(M.get("lanes") or []) if k != skip]
        x0, y0, x1, y1 = _box(run, MEET_REACH_FT)
        near = [ln for ln in lanes if len(ln.get("pts") or []) >= 2 and not ((b := _box(_pts(ln), 0.0))[2] < x0 or b[0] > x1 or b[3] < y0 or b[1] > y1)]
        tl, k = [*near, {"pts": run, "w": width}], len(near)
        if any(k in (n, m) for n, _e, m, _u, _v in law.needle_ends(tl)) or any(k in (a, b) for a, _ea, b, _eb in law.folded_joint_pairs(tl)):
            return False
        if any(n == k for _c, n, _e in law.connector_hairpin_ends(tl)):
            return False
        # ...AND EACH END SERVES SOMETHING, NOT FROM BEHIND A HOUSE (the lane law's `dangling_lane_ends`, water W57's
        # `ends_behind`): a tree lane is never trimmed afterwards, so an end it would leave in open ground or behind a back
        # wall is refused here
        trial = {**M, "lanes": tl}
        if any(n == k for n, _e in law.dangling_lane_ends(trial, self.ground)) or any(n == k for n, _e, _h in law.ends_behind(trial, self.ground)):
            return False
        if any(along_tail(p, q, deg=_DOUBLED_DEG) is not None for o in (_pts(ln) for ln in near) for p, q in ((run, o), (run[::-1], o), (o, run), (o[::-1], run))):
            return False
        # ...AND IT HANDS NO HOUSEHOLD A WAY OUT OVER THE BROOK AND BACK (ways W08): a way out is a route through the whole
        # web, so it is asked last, of the lanes the run would join - a tree lane is never cut for it afterwards
        return not (self.tree and law.adds_a_way_out_crossing(M, run, width, lanes))


def corridor_on_lawful_ground(M: Mapping[str, Any], run: Poly, width: float = ACCESS_WIDTH, lawful: Lawful | None = None) -> bool:
    """THE SEATING'S QUESTION (feature 287, plan M3): would a corridor along `run`, squared at its water crossings
    (`square_run`), stand on lawful ground (`Lawful.on_lawful_ground`) on the manifest as it stands? One predicate, asked by
    the seating before it admits a house and by the web before it draws the corridor. A caller asking many runs of one manifest
    hands in its `Lawful(SimpleNamespace(M=M))`, indexed once (feature 314: 145 runs, each indexing it again, 3.0 of 5.8 s).

    Research: the seating's corridor - NONE: the ground half of `Lawful`, claimed there"""
    import types

    ix = lawful or Lawful(types.SimpleNamespace(M=M))
    return ix.on_lawful_ground(ix.squared(run), width)  # `squared`: `square_run`, skipped where no water comes near the run


def settle_reach(s: Any) -> int:
    """Step 4: the reach the web owes - every household's way (laid in the gaps, `gap_ways`, feature 318), drawn as the gap
    pass judged them (`tree.settle_tree`); a spur to each way target (`settle_targets`); and the field way where no way
    reaches the field (`settle_field`).

    Research:
        every farmhouse served - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every household's way, laid once the last house stands, drawn as a lane of its own
        the field reached - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a way runs to the field's bund
        a path runs to the graves - UNRESEARCHED: claimed at `settle_targets`"""
    drawn = settle_tree(s)  # every household's way, reached or not (feature 318, `tree.owed`); each drawn once
    if not (unreached_houses(s.M) or law.unreached_targets(s.M) or law.field_unreached(s.M)):
        return drawn
    lawful = Lawful(s, tree=True)
    return drawn + settle_tree(s) + settle_targets(s, lawful) + settle_field(s, lawful)


def settle_husks(s: Any) -> int:
    """Drop every lane record that draws nothing (ways W04)."""
    gone = law.husks(s.M)
    if gone:
        s.drop_lanes(gone)
    return len(gone)


# ---- the loop ----------------------------------------------------------------------------------------------------------


STEPS = (
    settle_husks,
    square_every_crossing,
    settle_shapes,
    settle_way_outs,
    settle_ends,
    settle_street_ends,
    settle_shadows,
    settle_joins,
    settle_needles,
    settle_reach,
    settle_defer,
    settle_network,
    settle_fragments,
    prune_the_tree,
    settle_knots,
    settle_widths,
    settle_husks,
)


def settle_the_web(s: Any, rounds: int = SETTLE_ROUNDS) -> dict[str, Any]:
    """Repair the web until every rule of the lane law holds (see the module docstring) and report what it took: `rounds`,
    `seconds`, `changed` (lane edits), `dropped` (ORDINARY lanes the last resort dropped whole - never a tree lane,
    `last_resort.py`), and `unreached_before` / `_after` (`unreached_houses`, the houses the corridor is owed). A web that
    only the tree could mend, or that leaves a farmhouse or the reserved field unreached, is refused by name
    (`last_resort.WebRefused`) - the map is not produced, and nothing is recorded as a failure on it (FR-005)."""
    from .last_resort import last_resort, refuse_unreached

    t0 = time.perf_counter()
    before = len(unreached_houses(s.M))
    changed = dropped = done = 0
    settled = False
    while done < rounds and not settled:
        done += 1
        n = sum(step(s) for step in STEPS)
        changed += n
        settled = not n
    # (feature 297, research R12: later rounds asking the law and running only the steps for what it named broken were measured
    # SLOWER on two of three pool maps - the law asked each round cost more than the steps it skipped - and were withdrawn)
    if not settled or unsettled(s.M, memo_ground(s, "worked", worked_ground)):
        dropped = last_resort(s)
    # ...AND NO HOUSE OR RESERVED FIELD IS SHIPPED UNREACHED, whichever way the settle ended (ways W01, W03): refused here,
    # so the driver has no unreached house to record (`meta.roll_failures`, deleted with its writer)
    refuse_unreached(s.M)
    return {
        "rounds": done,
        "seconds": round(time.perf_counter() - t0, 3),
        "changed": changed,
        "dropped": dropped,
        "unreached_before": before,
        "unreached_after": len(unreached_houses(s.M)),
        "targets_unreached": len(law.unreached_targets(s.M)),
        "field_unreached": law.field_unreached(s.M),
    }
