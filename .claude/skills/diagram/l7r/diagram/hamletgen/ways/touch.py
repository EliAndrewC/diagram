"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

from ..consts import (
    WEB_FABRIC_GAP,
    Poly,
    Pt,
)
from .clearance import _bends_badly, _clear_touch, may_write
from .fabric import _LANE_JOIN_FT, _draw_web
from .geom import _TOUCH_GAP, _components, _stop_at_network, _unretrace, polyline_len
from .route import _route, _unjog
from .sweeps import _FINE_CELL, _LINK_DIRECTNESS, _SERVE_FT


def _touch_junctions(
    s: Settlement,
    hard: list[Poly],
    walls: Sequence[Poly],
    water: list[tuple[Pt, Pt]],
    reach: float = _LANE_JOIN_FT,
    only_orphans: bool = False,
    final: bool = False,
    movable: Sequence[Poly] | None = None,
) -> int:
    """The LAST pass over the web: every lane end that stands NEAR another way is extended to TOUCH it.

    THE NETWORK WAS CONNECTED BY TOLERANCE AND DISCONNECTED IN INK (GM 2026-08-27, feature 133 T31:
    *"a bunch of random scattered lanes strewn about without much rhyme or reason ... a short section
    of lane, between three farmhouses. It does not really connect to anything on either end"*).
    Every pass here - the orphan-joiner, the stub trimmer, the service trim, the reach checks - treats
    an end within `_LANE_JOIN_FT` (30 ft) of another way as JOINED, so a web could pass every gate
    while its pieces stopped 29 px short of one another. On Inashiro that was nine lanes in six
    components. The research the web exists to honor says "interconnected" (research/homesteads.md),
    and a junction is a place where two treads meet, not two ends that nearly do.

    Straight when the last stretch is clear, routed when it is not; the lane's record and its ink are
    rewritten together (`reink_lane`). Ends that stop at a house or leave the map are left alone - a
    door path ends at its door. `lanes_form_one_network` holds the line. Returns the ends closed."""
    # A TOUCH MAY NOT PUSH A LANE INTO THE FABRIC IT WAS DRAWN CLEAR OF (feature 134 T50, 2026-08-29).
    # Every rung here tests the LINK it is about to draw, and none of them looks at the lane that comes
    # out - so a link that is itself legal, spliced on by `_unjog`/`_unretrace` or by moving another
    # lane's end onto a node, can leave a tread nearer a garden than the router ever put it. Traced on
    # cohort seed 18: the footpaths were drawn 5.2 ft clear of the nearest garden, survived the smoother
    # at 5.16, and came out of this pass at 1.21 - `features_do_not_overlap`, lanes x gardens. This is
    # the same shape as `_smooth_web`'s `_commit`, which refuses a rewrite that breaks the web into
    # another piece: judge the RESULT, not just the move. A rewrite may leave a lane no nearer the
    # fabric than it already was, or than its own keep-out allows - whichever is the more forgiving,
    # so a lane already inside the bar is never made worse but is not required to fix itself either.
    _fab = [poly for poly in walls if len(poly) >= 3]

    def _may_write(idx: int, new_pts: Sequence[Pt], lane_list: Sequence[Mapping[str, Any]]) -> bool:
        """This lane's rewrite rule - see `may_write`, which holds the body."""
        _old = [(float(x), float(y)) for x, y in (lane_list[idx].get("pts") or [])]
        return may_write(_old, new_pts, float(lane_list[idx].get("w") or 5.0), _fab)
        # (the two paragraphs that used to stand here are on `may_write`)

    closed = 0
    for _pass in range(3):  # a touch can bring another end into reach; converge
        lanes = s.M.get("lanes") or []
        moved = 0
        _skip: set[int] = set()
        if only_orphans:  # the post-smoothing call: a web already in one piece is left exactly as drawn
            _ways = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
            _comp = _components(_ways, 4.0)
            _seed = next((k for k, ln in enumerate(lanes) if ln.get("connector")), 0)
            _skip = {k for k in range(len(lanes)) if _comp and _comp[k] == _comp[_seed]}
        for i, ln in enumerate(lanes):
            if ln.get("connector") or len(ln.get("pts") or []) < 2 or i in _skip:
                continue
            pts = [(float(x), float(y)) for x, y in ln["pts"]]
            # ONLY WAYS THIS LANE DOES NOT ALREADY MEET (T32). Linking a free end to a way the lane
            # already runs through drew a 180-degree retrace - Inashiro's lane 7 went 20 ft west,
            # then back east over its own tread, because the way it "reached" was the one whose end
            # stood on it. A junction is made once.
            _my_segs = list(zip(pts, pts[1:], strict=False))
            _by_way: list[tuple[int, list[tuple[Pt, Pt]], Poly]] = []
            for k, o in enumerate(lanes):
                if k == i or len(o.get("pts") or []) < 2:
                    continue
                _op = [(float(x), float(y)) for x, y in o["pts"]]
                _os = list(zip(_op, _op[1:], strict=False))
                if any(seg_dist(v[0], v[1], a, b) <= 4.0 for v in _op for a, b in _my_segs) or any(seg_dist(v[0], v[1], a, b) <= 4.0 for v in pts for a, b in _os):
                    continue
                _by_way.append((k, _os, _op))
            if not _by_way:
                continue
            new = list(pts)
            for end in (0, -1):
                q = new[end]
                _best = min(
                    ((math.dist(q, z), z, k, _op) for k, _os, _op in _by_way for z in [min((seg_closest(q[0], q[1], a, b) for a, b in _os), key=lambda z: math.dist(q, z))]), key=lambda t: t[0]
                )
                d, foot, k, _op = _best
                _os_k = list(zip(_op, _op[1:], strict=False))
                # NOT BACK ONTO ITSELF (feature 150, Kuwabata seed 21): a 30 ft lane whose two ends
                # both stood near the same spot on a neighbor had its start touched there, and then
                # its end touched to the same foot - a lane closed into a 28 ft loop, which
                # `lanes_bend_like_paths` read as a hairpin and `_smooth_web` never saw (it ran
                # first). A foot within a few feet of the lane's OTHER end is its own junction, not a
                # new one; leave that end alone.
                if math.dist(foot, new[-1 if end == 0 else 0]) <= 6.0:
                    continue
                if d <= 2.0 or d > reach:
                    continue
                # AN END THAT ALREADY STANDS ON THE NETWORK IS A JUNCTION, NOT A FREE END (feature 137
                # T03, cohort seed 07): a door path whose end sat on another lane was linked onward to a
                # SECOND way, and the link ran back over the first lane's tread - a 9 ft zigzag at the
                # junction. `_by_way` excludes the ways this lane meets, so the test above cannot see it.
                if any(
                    seg_dist(q[0], q[1], a, b) <= _TOUCH_GAP
                    for _k, o in enumerate(lanes)
                    if _k != i and len(o.get("pts") or []) >= 2
                    for a, b in zip([(float(x), float(y)) for x, y in o["pts"]], [(float(x), float(y)) for x, y in o["pts"]][1:], strict=False)
                ):
                    continue
                # END MEETS END: two lanes whose ends stand near each other are ONE lane with a
                # hole in it, and the honest join is to run the other lane's end onto this one -
                # a link from tread to tread drew an 8 ft jog that read as a loop (T32). The other
                # lane's end is moved onto `q` when its last stretch stays legal.
                _oe = 0 if math.dist(foot, _op[0]) <= 4.0 else (-1 if math.dist(foot, _op[-1]) <= 4.0 else None)
                if _oe is not None and len(_op) >= 2 and not lanes[k].get("connector"):
                    _nb = _op[1] if _oe == 0 else _op[-2]
                    if _clear_touch(_nb, q, hard, walls, water, max(_TOUCH_GAP, float(lanes[k].get("w") or 5.0) / 2.0 + 2.0)) and math.dist(_nb, q) <= 2.0 * math.dist(_nb, _op[_oe]) + 4.0:
                        _np = list(_op)
                        _np[_oe] = q
                        if not _may_write(k, _np, lanes):
                            continue
                        lanes[k]["pts"] = [[round(x, 1), round(y, 1)] for x, y in _np]
                        s.reink_lane(k)
                        closed += 1
                        moved += 1
                        continue
                # THE LINK OWES ITS OWN LANE'S KEEP-OUT (feature 134 T50) - the same reasoning as the
                # string-pull's, one pass over: `houses_clear_of_lanes` sizes a way's keep-out from its
                # width, so a straight junction link drawn at a flat 4 ft puts a 5 ft tread 4.09 ft from
                # a farmhouse corner and the check reads a house standing in the lane (cohort seed 6).
                link = (
                    [q, foot]
                    if _clear_touch(q, foot, hard, walls, water, max(_TOUCH_GAP, float(ln.get("w") or 5.0) / 2.0 + 2.0))
                    else _route(q, foot, hard, walls, water, gap=WEB_FABRIC_GAP, pad_mult=2.0, cell=10.0)
                )
                if not link and d <= _LANE_JOIN_FT:
                    # A SHORT GAP GETS A SECOND, TIGHTER ATTEMPT (settlement-review 2026-08-29, error 1).
                    # The first attempt walks a 10 ft lattice at DOUBLE the fabric pad, which is right for a
                    # long route through other people's yards and too coarse for a few feet of slack: on
                    # Kuwabata the back lane came out in two pieces with a 25 ft hole between two rounded
                    # caps and a woodpile - 10 x 3.5 ft - standing 5.6 ft off the line between them. Every
                    # endpoint-reach test passed, because each piece reaches the network at its OTHER end,
                    # so nothing in the gate saw a severed back lane. A 10 ft obstacle should not cost 25 ft
                    # of way. Only for a gap already inside the join reach, and the result still has to pass
                    # `_may_write` - which judges the SPLICED lane's clearance and bend, not the link - so a
                    # tread this finds but should not have is still refused there.
                    link = _route(q, foot, hard, walls, water, gap=WEB_FABRIC_GAP, pad_mult=1.0, cell=5.0)
                if not link or polyline_len(link) > _LINK_DIRECTNESS * d:
                    continue
                link = _stop_at_network(link, [sg for _k, _os, _op in _by_way for sg in _os])
                _cand = _unjog(_unretrace((list(reversed(link[1:])) + new) if end == 0 else (new + link[1:])), hard, walls, water)
                if final:
                    # THE LANE ALREADY RUNS ONTO THE WAY (settlement-review 2026-08-28, Kuwabata lane 9): a lane
                    # that comes within the touch gap of the way it is being joined to PART-WAY along its last
                    # stretch, then runs on beside it, is ended where it first meets the way - not linked back
                    # from beyond it, which left two treads 5-9 ft apart enclosing a sliver of ground.
                    # Not conditioned on the bend rule: the V it left was 113 deg, legal to the gate and wrong on the sheet.
                    _run = list(reversed(new)) if end == 0 else list(new)  # oriented so the joining end is LAST
                    _cut_at: tuple[int, Pt] | None = None
                    for _si in range(len(_run) - 1):  # walk the whole lane toward the joining end; first contact wins
                        _a0, _b0 = _run[_si], _run[_si + 1]
                        _span0 = math.dist(_a0, _b0)
                        for _t in range(1, max(1, int(_span0 / 3.0))):
                            _sx, _sy = _a0[0] + (_b0[0] - _a0[0]) * _t * 3.0 / _span0, _a0[1] + (_b0[1] - _a0[1]) * _t * 3.0 / _span0
                            _f = min((seg_closest(_sx, _sy, a, b) for a, b in _os_k), key=lambda z: math.dist((_sx, _sy), z))
                            if (
                                math.dist((_sx, _sy), _f) <= _TOUCH_GAP and 6.0 < polyline_len([(_sx, _sy), *_run[_si + 1 :]]) <= 40.0
                            ):  # only a SHORT overrun is cut (Kuwabata's was 32 ft); a long run past a way it grazes is a route, not a hook
                                _cut_at = (_si, _f)
                                break
                        if _cut_at is not None:
                            break
                    if _cut_at is not None:
                        _run = _run[: _cut_at[0] + 1] + [_cut_at[1]]
                        _cand = list(reversed(_run)) if end == 0 else _run
                # A HAIRPIN AT THE DOOR, AND WHY THERE IS NO REPAIR HERE (feature 150, Kuwabata seed 21;
                # re-measured 2026-08-29 against main). This clone carried a repair for a lane whose last
                # 13 ft turned down toward a door and was then joined back UP to the way it had just left.
                # Feature 137 landed `_unjog`/`_unretrace` on the link above, which takes that step out
                # first, so the repair fired 0 times over Inashiro, the 5 tripwire seeds, the 48-seed
                # cohort and Kuwabata - 54 maps, no fires - and its own fixture no longer reaches it. Two
                # mechanisms for one defect; the splice is the one that runs, so the repair was removed
                # rather than left as unreachable code. Restore it only with a map that hairpins here.
                new = _cand
                closed += 1
                moved += 1
            if new != pts and _may_write(i, new, lanes):
                ln["pts"] = [[round(x, 1), round(y, 1)] for x, y in new]
                s.reink_lane(i)
        if not moved:
            break
    # ONE NETWORK OR NOTHING. Whatever still stands apart after the touches is joined to the main
    # network by a routed link from its nearest vertex (reach up to `_ORPHAN_REACH`), and a component
    # that cannot be joined is REMOVED - record and ink together, as `trim_lane_stubs` does - because a
    # fragment serving three houses and touching nothing is what the GM read as "random scattered
    # lanes"; if a house is left unserved by that, `farmhouses_reach_a_way` says so honestly.
    for _pass in range(4):
        lanes = s.M.get("lanes") or []
        ways = [[(float(x), float(y)) for x, y in ln["pts"]] for ln in lanes]
        comp = _components(ways, 4.0)
        seed = next((i for i, ln in enumerate(lanes) if ln.get("connector")), 0)
        # THE NETWORK IS THE BIGGEST PIECE, NOT THE CONNECTOR'S PIECE (feature 134 T50, 2026-08-29).
        # Anchoring on the connector reads a map with a detached ROAD as a map with a detached WEB:
        # measured on cohort seeds 13 and 17, where the connector alone failed to touch and this tail
        # then reported seven and six orphan lanes and spent all twelve of its passes trying to drag
        # the whole web across to the road, joining nothing. One short link from the road to the web
        # is the same repair and it is the one that exists - 24.1 ft on seed 13. The connector may be
        # the orphan; `lanes_form_one_network` measures whether the pieces are ONE, and it does not
        # care which of them moved to meet the other.
        _sizes: dict[int, int] = {}
        for _k in range(len(ways)):
            if len(ways[_k]) >= 2:
                _sizes[comp[_k]] = _sizes.get(comp[_k], 0) + 1
        main = max(_sizes, key=lambda c: (_sizes[c], c == comp[seed])) if _sizes else (comp[seed] if comp else None)
        orphans = [i for i in range(len(ways)) if comp[i] != main and len(ways[i]) >= 2]
        if not orphans:
            break
        main_segs = [sg for j in range(len(ways)) if comp[j] == main for sg in zip(ways[j], ways[j][1:], strict=False)]
        joined = False
        for i in sorted(orphans, key=lambda k: -polyline_len(ways[k])):
            cands = sorted(((math.dist(v, q), v, q) for v in ways[i] for q in [min((seg_closest(v[0], v[1], a, b) for a, b in main_segs), key=lambda z: math.dist(v, z))]), key=lambda c: c[0])
            for d, v, q in cands[:12]:
                if d > _ORPHAN_REACH:
                    break
                link = [v, q] if _clear_touch(v, q, hard, walls, water) else _route(v, q, hard, walls, water, gap=WEB_FABRIC_GAP, pad_mult=2.0, cell=10.0)
                if link and polyline_len(link) <= _LINK_DIRECTNESS * max(d, 1.0):
                    _join_piece(s, lanes, i, ways[i], v, link, hard, walls, water, main_segs)
                    joined = True
                    break
            if joined:
                break
        if not joined:
            # THE LADDER'S LAST TWO RUNGS (feature 137 T03, 2026-08-28). Tripwire seed 37 and 26 of 48
            # cohort seeds carried a piece the two rungs above could not link: a stub whose only way to
            # the spine is a slot between a house and a yard that the 7 ft fabric pad closes on both
            # sides. (1) Route again at the JUNCTION standard - `_TOUCH_GAP`, the margin a link into a
            # junction is already allowed to brush a fence at (see the note under `_ORPHAN_REACH`): a
            # lane and a plot fence share a line in a real village. (2) Failing that, DROP the piece -
            # but only when no farmhouse would be stranded by it: every house the piece serves (within
            # `_SERVE_FT` of its tread) must still stand within `_SERVE_FT` of some other way. A fragment
            # that serves no house nobody else reaches is a drawing, not a lane, and the network check
            # is right to want it gone; a fragment that IS a house's only way stays, visibly broken.
            for i in sorted(orphans, key=lambda k: -polyline_len(ways[k])):
                # ONE TARGET PER WAY, not one per vertex: the nearest point on the whole network is the
                # one the garden blocks; the L to the next way over is only ever found if it is offered.
                # ... dealt ROUND-ROBIN across the ways: sorting every (vertex, foot) pair by air
                # distance put the twelve nearest all on the way the garden blocks (measured on seed
                # 03: five vertices, one `q`, five refusals), and one pair per way lost the vertex
                # whose route round the garden did exist. So the four nearest ways each offer their
                # three best pairs, dealt best-first across the ways - twelve routes at most, and
                # the way the garden blocks still gets its second and third vertex (seed 03's U
                # routed from the second vertex, not the first).
                _main_ways = [ways[j] for j in range(len(ways)) if comp[j] == main and len(ways[j]) >= 2]
                _per_way = sorted(
                    (
                        sorted(
                            ((math.dist(v, q), v, q) for v in ways[i] for q in [min((seg_closest(v[0], v[1], a, b) for a, b in zip(w, w[1:], strict=False)), key=lambda z: math.dist(v, z))]),
                            key=lambda c: c[0],
                        )[:3]
                        for w in _main_ways
                    ),
                    key=lambda g: g[0][0],
                )[:4]
                cands = [g[r] for r in range(3) for g in _per_way if r < len(g)]
                # THE SHORTEST ROUTE WINS, NOT THE NEAREST TARGET (feature 137 T03, cohort seed 03): the
                # nearest vertex by air was 44 ft off across a garden, and the only route to it walked
                # round the garden AND a shed - a U of 66 + 36 + 54 ft enclosing the shed, which
                # `lanes_bend_like_paths` reads as a zigzag. The next candidate, 60 ft off, was an L
                # through the 17 ft slot between the two. So the first `_SHORTEST_OF` candidates that
                # route at all are compared by the length of their ROUTE, and the shortest is drawn.
                found: list[tuple[float, Pt, Poly]] = []
                for d, v, q in cands[:12]:
                    if d > _ORPHAN_REACH:
                        break
                    link = _route(v, q, hard, walls, water, gap=_TOUCH_GAP, pad_mult=2.0, cell=6.0)
                    if not link:  # (3) the DETOUR: around the yard or the house that walls the slot - a wider box, a longer leash
                        link = _route(v, q, hard, walls, water, gap=WEB_FABRIC_GAP, pad_mult=5.0, cell=10.0)
                    if link and polyline_len(link) <= _DETOUR_DIRECTNESS * max(d, 1.0):
                        found.append((polyline_len(link), v, link))
                        if len(found) >= _SHORTEST_OF:
                            break
                if not found:
                    # (4) AIM ALONG THE WAY, FINELY. See `_ALONG_STEP_FT`: the rungs above ask a way for
                    # its nearest point and plan on a lattice that charges 4 ft of slop to the corridor.
                    _along: list[tuple[float, Pt, Pt]] = []
                    for w in _main_ways:
                        _samples: list[Pt] = [w[0], w[-1]]
                        _acc = 0.0
                        for a, b in zip(w, w[1:], strict=False):
                            _seg = math.dist(a, b)
                            _t = _ALONG_STEP_FT - _acc
                            while _t < _seg:
                                _samples.append((a[0] + (b[0] - a[0]) * _t / _seg, a[1] + (b[1] - a[1]) * _t / _seg))
                                _t += _ALONG_STEP_FT
                            _acc = (_acc + _seg) % _ALONG_STEP_FT if _seg else _acc
                        for q in _samples:
                            v = min(ways[i], key=lambda z, _q=q: math.dist(z, _q))
                            _along.append((math.dist(v, q), v, q))
                    _along.sort(key=lambda c: c[0])
                    for d, v, q in _along[:_ALONG_CANDS]:
                        if d > _ORPHAN_REACH:
                            break
                        link = _route(v, q, hard, walls, water, gap=WEB_FABRIC_GAP, pad_mult=2.0, cell=_FINE_CELL)
                        if link and polyline_len(link) <= _DETOUR_DIRECTNESS * max(d, 1.0):
                            found.append((polyline_len(link), v, link))
                            if len(found) >= _SHORTEST_OF:
                                break
                if found:
                    _len, v, link = min(found, key=lambda t: t[0])
                    _join_piece(s, lanes, i, ways[i], v, link, hard, walls, water, main_segs)
                    joined = True
                    break
        if not joined:
            _others = [sg for j in range(len(ways)) if j not in orphans and len(ways[j]) >= 2 for sg in zip(ways[j], ways[j][1:], strict=False)]
            _houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])]

            def _near(pt: Pt, segs: list[tuple[Pt, Pt]]) -> float:
                return min((seg_dist(pt[0], pt[1], a, b) for a, b in segs), default=float("inf"))

            _dropped = 0
            _dropped_idx: list[int] = []
            for i in orphans:
                _mine = list(zip(ways[i], ways[i][1:], strict=False))
                _served = [h for h in _houses if _near(h, _mine) <= _SERVE_FT]
                if all(_near(h, _others) <= _SERVE_FT for h in _served):
                    lanes[i]["pts"] = []
                    s.reink_lane(i)
                    _dropped_idx.append(i)
                    _dropped += 1
            if _dropped:
                # AND THE HUSK GOES WITH THE INK (settlement-review, Sawada, feature 145). Emptying `pts` left a
                # lane record declaring a lane nothing draws - `lanes` counted 18 where 17 existed, and every
                # consumer that iterates them had to special-case it (a `pts[0]` would raise). This engine's own
                # rule for the copse says it plainly: a map that declares a feature it did not draw is the defect.
                # Removed back-to-front so the earlier indices stay valid; the count still goes to meta.
                for _i in sorted(_dropped_idx, reverse=True):
                    del lanes[_i]
                s.M["meta"]["lane_fragments_dropped"] = s.M["meta"].get("lane_fragments_dropped", 0) + _dropped
                joined = _dropped == len(orphans)
                if joined:
                    continue
        if not joined:
            # KEPT, not dropped. The first cut of this pass DELETED a piece it could not link, and
            # on Inashiro that stranded a farmhouse the piece was serving: `farmhouses_reach_a_way`
            # failed, the driver's re-roll loop (`driver.py`) took over, and the map that came out
            # was attempt four - a different connector heading and a different web, with nothing on
            # the map saying why. A lane that serves a house is worth more than a clean component
            # count; the disconnection stays visible through `lanes_form_one_network` instead.
            s.M["meta"]["lane_orphans"] = len(orphans)
            break
    return closed


def _join_piece(
    s: Settlement, lanes: list[dict[str, Any]], i: int, way: Poly, v: Pt, link: Poly, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], net: list[tuple[Pt, Pt]]
) -> None:
    """Join an orphan piece to the network: EXTEND the piece when the link leaves one of its ends, else
    draw the link as its own lane (the link left an interior vertex). A link drawn as a separate lane
    from a door path's end put TWO lane ends beside the same farmhouse - the door path's and the
    link's - and `lane_ends_front_different_houses` counted them (cohort seed 16, feature 137 T03).
    One way that reaches the network is one lane. The splice is passed through `_unretrace` and
    `_unjog`: a link leaving a piece's END may double back along the piece before it turns (cohort
    seed 14 - 13 ft out, 7 ft up, 13 ft back), and the piece's own vertex is the right start."""
    pts = [(float(x), float(y)) for x, y in way]
    link = _stop_at_network(link, net)

    # THE SPLICE MAY NOT PUSH THE LANE INTO THE FABRIC (feature 134 T50, 2026-08-29). The link itself is
    # tested before it gets here, but what is DRAWN is the link spliced onto the piece and then passed
    # through `_unretrace` and `_unjog` - and those take chords of their own, at the junction margin,
    # across ground the piece never occupied. Traced on cohort seed 18: footpaths drawn 5.2 ft clear of
    # the nearest garden came out of this at 1.21 ft, which `features_do_not_overlap` reads as lanes x
    # gardens. Same rule as `_smooth_web`'s `_commit` - judge the RESULT, not just the move - and the
    # same forgiveness: no nearer than it already was, or than its own keep-out asks, whichever is more
    # generous, so a lane already tight is never made worse and is not required to fix itself.
    _fab = [poly for poly in walls if len(poly) >= 3]
    _bar = max(_TOUCH_GAP, float(lanes[i].get("w") or 5.0) / 2.0 + 2.0)

    def _clear_of_fabric(run: Poly) -> float:
        if len(run) < 2 or not _fab:
            return float("inf")
        return min(seg_dist(q[0], q[1], a2, b2) for poly in _fab for q in poly for a2, b2 in zip(run, run[1:], strict=False))

    _was = _clear_of_fabric(pts)

    _bent_before = _bends_badly(pts)

    def _spliced(run: Poly) -> bool:
        if _clear_of_fabric(run) < min(_was, _bar) - 1e-9:
            return False
        if _bends_badly(run) and not _bent_before:
            return False  # see `_may_write`: the splice may not put a fold in a lane that had none
        lanes[i]["pts"] = [[round(x, 1), round(y, 1)] for x, y in run]
        s.reink_lane(i)
        return True

    # ...AND WHERE THE SPLICE IS REFUSED, THE LINK IS STILL DRAWN - as its own lane, which is what this
    # function already does for a link leaving an interior vertex. The link begins at `v`, a point on the
    # piece, and ends on the network, so the web is joined either way; what is lost is only the tidiness
    # of one lane rather than two. Refusing outright was measured and was worse: cohort seed 18 traded
    # `features_do_not_overlap` for `lanes_form_one_network`, and a settlement whose lanes do not meet is
    # the worse map.
    if pts and math.dist(v, pts[-1]) < 0.5:
        if not _spliced(_unjog(_unretrace(pts + list(link[1:])), hard, walls, water)):
            _draw_web(s, link, int(float(lanes[i].get("w", 3))), joins=True)
    elif pts and math.dist(v, pts[0]) < 0.5:
        if not _spliced(_unjog(_unretrace(list(reversed(link[1:])) + pts), hard, walls, water)):
            _draw_web(s, link, int(float(lanes[i].get("w", 3))), joins=True)
    else:
        _draw_web(s, link, int(float(lanes[i].get("w", 3))), joins=True)


_ORPHAN_REACH = 150.0  # ft: how far a stranded piece may be linked back to the network before it is left as it is
_SHORTEST_OF = 3  # the detour rung compares this many routable targets by route length before drawing one
_DETOUR_DIRECTNESS = 8.0  # the last rung may walk round a yard: up to 8x the straight gap (a 29 ft gap -> a 230 ft way round)
# AIMING ALONG A WAY, ON A FINER LATTICE - the rung below the detour (feature 134 T50, 2026-08-28).
# Two things kept the joiner from a route that plainly exists, measured on tripwire seed 27 by grid
# search over that map's own footprints:
#   1. EVERY candidate aims at a way's NEAREST point, so a way whose nearest point happens to be the
#      walled one is written off whole. Seed 27's stub sits 31 ft from lane 2's corner with a garden
#      and a farmhouse closing the slot; nine points further along that SAME lane were reachable.
#   2. `_route` plans on a lattice and inflates its clearance by half a cell's diagonal
#      (`gap + cell * 0.71`) so that "this cell is free" means every point in it is clear. That is
#      load-bearing - it is what stopped lanes planned at 7 ft from being drawn at 4 - but it is
#      charged against the CORRIDOR: at cell 6 the junction rung really demands 8.26 ft and at cell 10
#      the detour rung 14.1 ft, through a gap about 7 ft wide. Nothing fitted at either. At a 3 ft cell
#      the same standard costs 6.13 ft and the ways round open up.
# So this rung samples targets along each main way and plans them finely. It runs ONLY after the
# ladder above has failed, so a piece that joins today joins by exactly the same route it did before.
_ALONG_STEP_FT = 40.0  # a sample every 40 ft: finer than the shortest link worth drawing, coarse enough to stay cheap
_ALONG_CANDS = 8  # routes attempted at the fine cell, nearest first - the cost bound on a rung that only runs for a stranded piece
