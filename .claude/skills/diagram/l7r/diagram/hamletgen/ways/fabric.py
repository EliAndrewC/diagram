"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Callable, Sequence

from l7r.diagram.settlement import Settlement, edge_dist, rot_rect, seg_closest, seg_dist, segments_cross
from l7r.diagram.sitegen.geom import centroid, unit

from ..consts import (
    BUNDLE_PITCH,
    WEB_CLEARANCE,
    WEB_REACH_FT,
    Poly,
    Pt,
)
from ..plan import SitePlan
from .geom import _TOUCH_GAP, _nearest_seg, _reach, polyline_len


class _margin_frame:  # noqa: N801 - used as a callable coordinate map, not as a type
    """OUTLINE COORDINATES for the stretch of field margin this cluster fronts.

    `f(arc, standoff)` maps a point given as (distance walked along the field edge, distance out
    from it) to screen. It is the same walk `front_row` makes - the outline vertices within the
    cluster's lateral reach, ordered along the margin, each offset outward on the local normal - and
    it exists for the same reason: the margin CURVES, so anything meant to run parallel to the field
    has to be built on the edge itself rather than ruled straight across it.

    Read `.arc` for the total length of that stretch, which is the domain the web is laid over."""

    def __init__(self, plan: SitePlan, span: float, near: Sequence[Pt] = ()) -> None:
        env, seat = plan.envelope, plan.seat
        ax, ay = seat["along"]
        cen = centroid(env)
        # ONE CONTIGUOUS RUN OF THE OUTLINE, WALKED FROM THE CLUSTER OUTWARD - not a filter.
        #
        # The envelope is a closed RING, so any test applied vertex-by-vertex admits the far side of
        # the field as readily as the near one, and the arc then snakes down one flank of the fan,
        # round the end and back up the other: 3,060 ft of "margin" for an 808 ft cluster, which
        # over-generated laterals three to one and laid them where no house stands. A half-plane
        # test off the seat's outward normal fixes that and breaks something else - a CRESCENT
        # cluster wraps around the field, its far arm sits where the normal points elsewhere, and it
        # was cut out of the frame entirely, so those houses could not be reached at any price.
        #
        # Walking instead of filtering settles both. Start at the outline vertex nearest the seat and
        # step each way while the outline is still near the settlement: the run is contiguous by
        # construction, so it can never jump the field, and it follows a crescent round for exactly
        # as far as the crescent goes. The walk looks a few vertices AHEAD before giving up, because
        # a crescent's two arms are separated by margin that no house stands near, and stopping at
        # the first far vertex stops between the arms. `near` is the placed house centers - measured,
        # not predicted, because by the time the web is laid they exist.
        anchor = seat["anchor"]
        limit = max(span, BUNDLE_PITCH)

        def close_enough(q: Pt) -> bool:
            if near:
                return min(math.dist(q, h) for h in near) <= limit
            return bool(abs((q[0] - anchor[0]) * ax + (q[1] - anchor[1]) * ay) <= span)

        n_env = len(env)
        look = 12

        def worth_continuing(i: int, step: int) -> bool:
            return any(close_enough(env[(i + step * k) % n_env]) for k in range(1, look + 1))

        # THE WALK MAY NOT LAP THE FIELD. Bounded by arc as well as by vertex count: on a compact
        # outline the look-ahead can carry the walk right round the ring and back to where it began,
        # and a frame that laps has no single answer for `project` - two stretches of it sit on top
        # of each other, so a point maps to whichever the scan met first. Half the ring is the most
        # margin any one cluster can honestly front.
        ring = sum(math.dist(env[i], env[(i + 1) % n_env]) for i in range(n_env))
        cap = ring * 0.5
        start = min(range(n_env), key=lambda i: math.dist(env[i], (seat["cx"], seat["cy"])))
        walked = 0.0
        lo = start
        while (start - lo) < n_env - 1 and walked < cap and worth_continuing(lo, -1):
            walked += math.dist(env[(lo - 1) % n_env], env[lo % n_env])
            lo -= 1
        hi = start
        while (hi - start) < n_env - 1 and walked < cap and worth_continuing(hi, +1):
            walked += math.dist(env[hi % n_env], env[(hi + 1) % n_env])
            hi += 1
        pts = [env[i % n_env] for i in range(lo, hi + 1)]
        if len(pts) < 2:  # pragma: no cover - a band always spans several outline vertices
            pts = [(seat["cx"], seat["cy"]), (seat["cx"] + ax, seat["cy"] + ay)]
        self.pts = pts
        self.cum = [0.0]
        for i in range(len(pts) - 1):
            self.cum.append(self.cum[-1] + math.dist(pts[i], pts[i + 1]))
        self.arc = self.cum[-1]
        # The outward normal at each vertex, averaged over the two edges meeting there and oriented
        # AWAY from the field's centroid - the settlement is outside the crop, and a standoff that
        # pointed inward would lay every web lane in the rice.
        self.nrm: list[Pt] = []
        for i, p in enumerate(pts):
            nx, ny = 0.0, 0.0
            for a, b in ((pts[max(0, i - 1)], p), (p, pts[min(len(pts) - 1, i + 1)])):
                if a != b:
                    ex, ey = unit(-(b[1] - a[1]), b[0] - a[0])
                    nx, ny = nx + ex, ny + ey
            nx, ny = unit(nx, ny) if (nx or ny) else (1.0, 0.0)
            if nx * (p[0] - cen[0]) + ny * (p[1] - cen[1]) < 0:
                nx, ny = -nx, -ny
            self.nrm.append((nx, ny))

    def project(self, p: Pt) -> tuple[float, float]:
        """The inverse of `__call__`: a screen point as (arc along the margin, standoff out from it).

        By nearest sample on the centerline rather than by solving, because the margin is a
        polyline with corners and the nearest-point problem there has no closed form worth writing.
        The samples are one every 10 ft, which is a tenth of the reach anything is measured against."""
        n = max(2, int(self.arc / 10.0))
        best = (0.0, 0.0, float("inf"))
        for i in range(n + 1):
            a = self.arc * i / n
            q = self(a, 0.0)
            d = math.dist(p, q)
            if d < best[2]:
                best = (a, d, d)
        return (best[0], best[1])

    def __call__(self, arc: float, standoff: float) -> Pt:
        t = min(max(arc, 0.0), self.arc)
        i = max(0, min(len(self.pts) - 2, next((k for k in range(len(self.cum) - 1) if self.cum[k + 1] >= t), len(self.pts) - 2)))
        run = self.cum[i + 1] - self.cum[i]
        u = 0.0 if run <= 0 else (t - self.cum[i]) / run
        px = self.pts[i][0] + (self.pts[i + 1][0] - self.pts[i][0]) * u
        py = self.pts[i][1] + (self.pts[i + 1][1] - self.pts[i][1]) * u
        nx = self.nrm[i][0] + (self.nrm[i + 1][0] - self.nrm[i][0]) * u
        ny = self.nrm[i][1] + (self.nrm[i + 1][1] - self.nrm[i][1]) * u
        nx, ny = unit(nx, ny) if (nx or ny) else self.nrm[i]
        return (px + nx * standoff, py + ny * standoff)


def _homestead_polys(s: Settlement) -> list[tuple[Poly, Pt | None, str]]:
    """Every drawn thing a homestead puts on the ground, as (polygon, the house it belongs to).

    The OWNER matters for one job only, and it is the job that needs it most: a footpath to an
    outlying steading has to be allowed to leave that steading's own yard. Without the owner the
    path starts at the door, immediately meets its own threshing yard, and is clipped to nothing -
    which is how eight houses stayed unreachable while a path to each was being drawn and thrown
    away. `of` on a yard/garden/shed records its house's center, so the association is already in
    the manifest and does not have to be re-derived geometrically.

    Houses are rotated rects and are read as their real corners (x, y ARE the center here, the same
    convention `rect_corners` uses in the gate); the area features already record an outline."""
    out: list[tuple[Poly, Pt | None, str]] = []
    for h in s.M.get("houses", []):
        c = (float(h["x"]), float(h["y"]))
        out.append((rot_rect(c[0], c[1], float(h["w"]), float(h["h"]), float(h.get("rot", 0.0))), c, "houses"))
    for key in ("threshing_yards", "gardens"):
        for rec in s.M.get(key, []):
            own = rec.get("of")
            owner = (float(own[0]), float(own[1])) if own else None
            # BOTH EXTENTS, because they are not the same shape and the gate reads the wider one. A
            # garden records a `poly` (the bed outline) AND a rect, and the rect runs a couple of
            # feet proud of the poly on a side or two. Clearing only the poly left about eight inches
            # between a web lane and the rect - and the overlap matrix sizes EVERY lane at 6 ft wide
            # whatever its own record says, so eight inches was an overlap. That was 7 of 24 cohort
            # seeds, all of them `lanes` vs `gardens`.
            if rec.get("poly"):
                out.append(([(float(a), float(b)) for a, b in rec["poly"]], owner, key))
            if rec.get("w"):
                out.append((rot_rect(float(rec["x"]), float(rec["y"]), float(rec["w"]), float(rec["h"]), float(rec.get("rot", 0.0))), owner, key))
    # PER-HOUSE GROVES ARE FABRIC TOO (feature 126). A yashikirin belongs to its farmstead and is
    # planted with it, so a lane may no more be drawn through one than through the house - which is
    # what `groves_clear_of_lanes` says. It was missing from this list because it could not matter
    # while the lanes were laid FIRST and the groves grew around them; with the lanes drawn last,
    # every non-nucleated map cut treads through its own shelter belts.
    for rec in s.M.get("groves", []):
        if rec.get("poly"):
            out.append(([(float(a2), float(b2)) for a2, b2 in rec["poly"]], None, "groves"))
    for key in ("village_groves", "commons"):
        out.extend(([(float(a), float(b)) for a, b in rec["poly"]], None, key) for rec in s.M.get(key, []) if rec.get("poly"))
    for w in s.M.get("wells", []):
        # THE DRAWN radius, not the recorded one. A wellhead records `r` (the shaft) and `vr` (the
        # curb and apron actually inked), and `vr` is the bigger of the two - built from `r` alone
        # the obstacle was a diamond inside the glyph, and a web lane passed 13 ft from the center
        # with the matrix quite rightly calling it an overlap. Octagon rather than diamond for the
        # same reason: a four-point ring inscribed in a circle understates it by 30%.
        r = max(float(w.get("r", 8.0)), float(w.get("vr", 0.0)))
        out.append(([(float(w["x"]) + r * math.cos(math.pi * k / 4), float(w["y"]) + r * math.sin(math.pi * k / 4)) for k in range(8)], None, "wells"))
    for key in ("farm_sheds", "byres"):
        for r in s.M.get(key, []):
            own = r.get("of")
            out.append((rot_rect(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), float(r.get("rot", 0.0))), (float(own[0]), float(own[1])) if own else None, key))
    return out


# How near a footpath's far end must come to an existing way to count as joining it. This is
# `lanes_reach_something`'s own way-reach, deliberately: a path that gets this close IS connected as
# far as the gate is concerned, and demanding better only threw away paths that served their house.
_LANE_JOIN_FT = 30.0  # inside lanes_reach_something's own 40 ft, with room to spare for a rounded end

# A GAP THIS SHORT BETWEEN TWO NEAR-COLLINEAR ENDS IS ONE WAY DRAWN AS TWO. 150 ft is about a
# household and a half of frontage - far enough that a real interruption (a wellhead, a bed, a
# clump) has somewhere to sit, close enough that the eye reads the two pieces as one street with a
# hole in it. The bearing bound is tighter than the fan rule's: these ends have to point AT each
# other, not merely lie alongside.
# THE SHORTEST THING THAT IS STILL A WAY. `_LANE_MIN_FT` (71) is the floor for a lane the
# homesteads FRONT and is right for one; a door path is legitimately about 65 ft and would be deleted
# by it. But there is a floor below which nothing is a way at all: Sawada shipped 4 ft, 12 ft and
# 20 ft fragments, left behind when the end-trim pulled a path back to its last serving point. A
# 4 ft mark fronts nobody and reads as a speck of clipping debris. 30 ft is under half a door path.
_WEB_MIN_FT = 30.0


def _net_segs(s: Settlement) -> list[tuple[Pt, Pt]]:
    """Every drawn way on the map right now, as segments.

    A CONNECTED-COMPONENT MODE was added here and reverted with the rest of the connectivity work.
    It restricted the result to the component the connector is on, which is what "reached" really
    means and what the gate says in its own words ("THE NETWORK, NOT ANY LINE ON THE GROUND ... a
    house served only by an isolated stub is not served"). It was RIGHT about its defect - seed 9's
    `farmhouses_reach_a_way` comes back without it - and wrong about its blast radius: with it and
    its four companions in place the cohort went 44 -> 31, and reverting all five moved it to 30.
    Worth re-attempting deliberately one day, not by accident."""
    return [((float(p[0]), float(p[1])), (float(q[0]), float(q[1]))) for ln in s.M.get("lanes", []) for p, q in zip(ln["pts"], ln["pts"][1:], strict=False)]


_PASS = "web"  # the web pass drawing right now, recorded on every lane it makes (feature 137 T04: provenance)


def _pass(name: str) -> None:
    """Name the pass about to draw, so a lane on the sheet can say who made it (`role`)."""
    global _PASS  # noqa: PLW0603 - one module-level tag, set by stage_web between its passes
    _PASS = name


def _hits_a_steading(s: Settlement, pts: Poly, width: int) -> bool:
    """Would a lane of this width, drawn along `pts`, put ink on a farmhouse footprint?

    The measure `houses_clear_of_lanes` uses: the house's DRAWN rectangle (rotation included) against the
    tread, which is the polyline widened by half its stroke. No tolerance either way - the check allows the
    overlap none, so neither does this.
    """
    # MIRROR THE CHECK'S WINDOW, NOT JUST ITS FORMULA (this skill's CLAUDE.md). `houses_clear_of_lanes`
    # tests the house's four ROTATED CORNERS PLUS ITS CENTER against each lane segment at
    # `w / 2 + 2` - the center is in the list so a lane narrower than a house cannot thread between the
    # corners. The first cut of this helper used a quad-versus-segment overlap at half the tolerance, and
    # so passed paths the gate still failed: same intent, different window, which is exactly the drift
    # the rule exists to stop.
    half = width / 2.0 + 2.0
    for h in s.M.get("houses") or []:
        quad = rot_rect(float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"]), float(h.get("rot", 0.0)))
        probes = [*quad, (float(h["x"]), float(h["y"]))]
        for i in range(len(pts) - 1):
            if any(seg_dist(px, py, pts[i], pts[i + 1]) < half for px, py in probes):
                return True
    return False


def _draw_web(s: Settlement, pts: Poly, width: int = 3, houses: Sequence[Pt] = (), joins: bool = False) -> bool:
    """Draw a web lane, unless it is debris. See `_WEB_MIN_FT`.

    SHORT IS NOT THE SAME AS USELESS, and conflating them cost more than the debris did. A blunt
    length floor refuses the door path of a steading that sits close to the network - which is
    exactly the house that most needs one - and the 48-seed sweep went from 6 unreached-house seeds
    to 17 the moment the floor went in. So a short run is refused only when it EARNS nothing: if it
    brings a house inside the reach that is outside it now, it is a way, whatever its length."""
    if len(pts) < 2:
        return False
    # A JOIN LINK IS EXEMPT FROM THE DEBRIS FLOOR (feature 134 T50, 2026-08-29). The floor asks what a
    # run EARNS in service - does it bring a house inside the reach - and a link earns nothing by that
    # measure, because the house it belongs to is already served by the piece the link is joining. Its
    # job is the junction, and it is short precisely because it is the shortest way to make one. Left
    # under the floor the link was simply discarded and the piece stayed orphaned, which is how cohort
    # seed 18 traded an overlap for `lanes_form_one_network`.
    # A JOIN LINK IS ALLOWED TO BRUSH A FENCE. IT IS NOT ALLOWED THROUGH A HOUSE (feature 155).
    # The exemption above lets a short link be drawn, and the link is routed at `_TOUCH_GAP` (4 px)
    # rather than `WEB_FABRIC_GAP` (7) because "a lane and a plot fence share a line in a real village".
    # That reasoning is about FENCES. A farmhouse is not a fence: `houses_clear_of_lanes` allows a lane
    # no overlap with a steading at all, so a 4 px routing margin plus the tread's own half-width plus
    # the straightening `_unjog` does afterwards can and did put a link's ink on a house corner -
    # sawada shipped an 8.6 px stub 2 px into one (1826, 2438) and kashikawa a 45 px link 3 px into
    # another (2136, 2762), both from the 2026-08-29 pool sweep, both gating red on main.
    #
    # A refused link leaves its piece orphaned, and that is the trade this engine already made once and
    # documented: `lanes_form_one_network` reports a disconnection the reader can see, while a lane
    # drawn through a farmhouse is a map that looks finished and is wrong. The piece is kept and the
    # gate says so, which is the same ruling as the orphan joiner's "KEPT, not dropped".
    if joins and _hits_a_steading(s, pts, width):
        return False
    if not joins and polyline_len(pts) < _WEB_MIN_FT:
        segs = _net_segs(s)
        earns = any(_reach(h, pts) <= WEB_REACH_FT and (not segs or min(seg_dist(h[0], h[1], a, b) for a, b in segs) > WEB_REACH_FT) for h in houses)
        if not earns:
            return False
    s.lane(pts, width=width, clearance=WEB_CLEARANCE, worn=True)
    if s.M.get("lanes"):
        s.M["lanes"][-1]["role"] = _PASS  # provenance: which pass drew it (feature 137 T04)
    # Flagged so `lane_frontage` does not offer seats along it. A web lane is SERVICE - it threads
    # behind and between the steadings - and inviting new houses onto the way that exists to reach
    # the old ones is how the cluster starts sprawling again.
    s.M["lanes"][-1]["web"] = True
    return True


def _pull_back_to_service(run: Poly, segs: Sequence[tuple[Pt, Pt]], houses: Sequence[Pt], inside: Callable[[Pt], bool], fabric: Sequence[Poly] = (), gap: float = _TOUCH_GAP) -> Poly:
    """Pull a CONNECTOR's inside-the-canvas end back to where it last meets the settlement.

    A connector is exempt from `_trim_to_service` because it legitimately runs off the frame - and
    that exemption, applied to both its ends, is what let feature 128 ship a blind stub. With the
    track drawn after the houses, `_thread_the_fabric` clips its inner end at the fabric; the web is
    laid later still, so at clip time there is no junction to stop at and the tread simply ends in
    open ground. Measured by review across the live tier: overshoot past the innermost junction was
    0.0 ft on all four hamlets before this feature, and afterwards 191.5 ft on Mizuguchi and 252.8 ft
    on Sawada. The gate cannot see it - `lanes_reach_something` is the rule for exactly this and it
    skips anything flagged `connector`, because a connector's end is normally off-canvas.

    So: only an end INSIDE the canvas is pulled back, and only as far as the first point that reaches
    the network. The off-canvas end is never touched, because reaching the frame is the connector's
    other job (`connector_lane_runs_off_edge`). An end that finds nothing to reach is LEFT ALONE
    rather than deleted - a hamlet whose track genuinely joins nothing is a real map to look at, not
    a map to silently shorten, and Kashikawa is currently that map."""

    # A CONNECTOR ARRIVES AT THE WAYS, NOT MERELY NEAR A HOUSE, which is the one place its rule is
    # stricter than `lanes_reach_something`'s. That check accepts a farmhouse within 90 ft, and it is
    # right to for an internal lane - a house FRONTS the lane it stands on. A road from the next
    # valley does not front anything: it meets the village's lanes, and the houses meet those. Left
    # with the house clause in, Mizuguchi's tread stopped 85.5 ft from a house center - inside the
    # 90 ft bar, so nothing trimmed - and 164 ft past the lane it should have joined, which is
    # exactly the picture the review objected to: a track petering out in the grass.
    # A second copy of the trim pass's `serves` predicate stood here with no callers at all - dead since
    # this function stopped deciding whether an end reaches and started walking it to the closest
    # approach instead. Removed (feature 146); the live one is in `_trim_blunt_ends` above.
    out = list(run)
    for _end in (0, -1):
        pts = out if _end == 0 else out[::-1]
        # An end that ALREADY reaches is still walked, not skipped: reaching within the join bar and
        # TOUCHING are different pictures, and Kashikawa's tread stopped 6 ft short of the lane it
        # met - inside every check's tolerance and visibly a gap at 1 px = 1 ft.
        if not inside(pts[0]):
            continue
        # WALK ON TO THE CLOSEST APPROACH, THEN TOUCH. Cutting at the FIRST point inside the join bar
        # leaves the tread stopping `_LANE_JOIN_FT` short of the way it is joining - measured at 27.3
        # ft on Mizuguchi and 28.6 on Sawada, which at 1 px = 1 ft is a plainly visible hole. The bar
        # is what makes a junction FINDABLE; it is not where the ink should end. So keep sampling
        # while the distance is still falling, then snap the surviving end onto the nearest segment,
        # which is the same "a junction is contact" rule `_lay_web_lane` applies to a web lane.
        cut: Pt | None = None
        best = float("inf")
        seg_at: tuple[Pt, Pt] | None = None
        k_at = 0
        # EVERY approach that joins, not only the closest one (feature 134 T50). The closest is still
        # preferred - it is the first one tried - but when it is the one that fouls a steading, a
        # slightly longer approach that does not is a far better answer than abandoning the junction.
        opts: list[tuple[float, Pt, tuple[Pt, Pt], int]] = []
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            steps = max(1, int(math.dist(a, b) / 4.0))
            for j in range(steps + 1):
                q = (a[0] + (b[0] - a[0]) * j / steps, a[1] + (b[1] - a[1]) * j / steps)
                d, sg = _nearest_seg(q, segs)
                if d <= _LANE_JOIN_FT and sg is not None:
                    opts.append((d, q, sg, k))
                if d < best:
                    best, cut, seg_at, k_at = d, q, sg, k
                elif cut is not None and best <= _LANE_JOIN_FT:
                    break  # past the closest approach and already joined - stop here
            if cut is not None and best <= _LANE_JOIN_FT and best < _nearest_seg(pts[k + 1], segs)[0]:
                break
        if cut is not None and seg_at is not None and best <= _LANE_JOIN_FT:
            for _d, _q, _sg, _k in sorted(opts, key=lambda t: t[0]):
                _snap = seg_closest(_q[0], _q[1], _sg[0], _sg[1])
                _try = [_snap, *pts[_k + 1 :]] if _end == 0 else [*pts[_k + 1 :][::-1], _snap]
                if len(_try) >= 2 and not (fabric and _crosses_fabric(_try, fabric, gap)):
                    cut, seg_at, k_at = _q, _sg, _k
                    break
            cut = seg_closest(cut[0], cut[1], seg_at[0], seg_at[1])
            cand = [cut, *pts[k_at + 1 :]] if _end == 0 else [*pts[k_at + 1 :][::-1], cut]
            # THE SNAP MAY NOT UNDO THE THREADING (feature 134 T50, 2026-08-28). This moves the
            # connector's inner end onto the lane it joins, and until now it did so with no idea what
            # else is standing there - while `_thread_the_fabric`, which ran earlier in the same
            # stage, had already routed and clipped that very end clear of every steading. So the
            # last pass to touch the run quietly put back what the pass before it existed to remove:
            # on cohort seed 18 the threaded end stood 18.0 ft off the nearest fabric and the snap
            # landed it 0.8 ft from a garden's corner, well inside the 6 ft the overlap matrix gives
            # every lane, and `features_do_not_overlap` read it as lanes x gardens. The junction is
            # worth having, but not at the price of drawing through the vegetables: take the snap
            # only when it does not foul anything the threading had cleared.
            if not fabric or not _crosses_fabric(cand, fabric, gap) or _crosses_fabric(out, fabric, gap):
                out = cand
    return out


def _fabric_hits(run: Poly, fabric: Sequence[Poly], gap: float) -> int:
    """HOW MANY steadings this run would foul - a count, so a sweep with no clean option can rank.

    PROXIMITY, NOT CROSSING, and the distinction is the whole reason this exists. `path_violations`
    asks `crosses_poly`, which is the right question for a crop: a track either enters the paddy or
    it does not. It is the wrong question for a farmstead, because the lane is DRAWN WITH A WIDTH and
    the overlap matrix sizes every lane at 6 ft whatever its own record says - so a centerline that
    passes a garden without crossing it still puts the tread through the vegetables. Mizuguchi's
    connector crossed nothing at all and was 0.2 px from a garden rect; every bearing in the sweep
    scored a clean zero, and the ranking this was added to make had nothing to rank."""
    return sum(1 for poly in fabric if _crosses_fabric(run, [poly], gap))


def _crosses_fabric(run: Poly, fabric: Sequence[Poly], gap: float) -> bool:
    """Does this polyline pass within `gap` of anything already standing?

    The clip is not self-verifying: `clip_to_clear` shortens a run at the first obstruction, and a
    run that re-enters the fabric further along comes back shorter and still crossing. Checking the
    RESULT is what turns "we tried" into "it is clear", and it is the difference between the caller
    knowing to take a detour and the caller believing it is done.

    IT MUST MEASURE FROM BOTH SHAPES, and the first version measured from only one. Testing crossings
    plus `edge_dist` at the RUN'S OWN VERTICES is blind to the commonest case there is: a steading
    standing beside the MIDDLE of a long segment, close enough to be overlapped but not close enough
    to any vertex to be seen. A connector crosses a hamlet in three or four points, so its segments
    run 700 px and more, and everything the cluster owns sits nearer their midpoints than their ends.
    Inashiro hid it - its offending steadings happened to straddle the line, so `segments_cross`
    caught them - and Mizuguchi did not: the connector shipped 0.2 px from a garden and 14.6 px from
    a farmhouse while this returned False at a gap of 0.5. So the poly's own vertices are measured
    against each segment as well, which is the half that closes it."""
    for poly in fabric:
        for k in range(len(run) - 1):
            a, b = run[k], run[k + 1]
            for j in range(len(poly)):
                c, d = poly[j], poly[(j + 1) % len(poly)]
                if segments_cross(a, b, c, d):
                    return True
                if seg_dist(c[0], c[1], a, b) < gap:
                    return True
            if edge_dist(a[0], a[1], poly) < gap or edge_dist(b[0], b[1], poly) < gap:
                return True
    return False
