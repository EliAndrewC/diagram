"""Crossings, from a single span to the footbridge net over a channel system.

Split from settlement/city.py by feature 113 - see settlement/city/CLAUDE.md for the index.

Research: plumbing - NONE
"""

import math
from typing import TYPE_CHECKING, Any, cast

from .._geom import (
    CARRIED_LANDING_FLOOR_FT,
    LANDING_FT,
    PLANK_ABUTMENT,
    PLANK_BANK_REACH,
    PLANK_VILLAGE_REACH,
    PointGrid,
    Pt,
    boxed_grid,
    boxed_polys,
    boxes_meeting,
    point_in_poly,
    quad_hits_poly,
    quad_hits_seg,
    seg_dist,
    seg_intersect,
    segments_cross,
)
from .._knobs import Knob, bridge_carried_ways, bridge_crossed_waters, register_knob

if TYPE_CHECKING:
    from ..core import Settlement


# ---- footbridge geometry ------------------------------------------------------------------
# Three pure helpers, hoisted out of `channel_footbridges` by feature 113. They close over
# nothing and are shared by that method's slide loop and the two predicates it now delegates to;
# nesting them was a third of what made that method 195 lines, and hid the fact that they are
# ordinary geometry rather than anything footbridge-specific.


def _at_arc(pts: Any, seg: Any, s: float) -> Any:  # point + heading (deg) at arc-length s along the polyline
    acc = 0.0
    for i, sl in enumerate(seg):
        if acc + sl >= s or i == len(seg) - 1:
            fr = (s - acc) / sl if sl else 0.0
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            return (ax + (bx - ax) * fr, ay + (by - ay) * fr, math.degrees(math.atan2(by - ay, bx - ax)))
        acc += sl


def _deck_quad(cx: float, cy: float, w: float, h: float, deg: float) -> list[Pt]:
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]


def _quad_box(quad: Any) -> tuple[float, float, float, float]:
    """A deck quad's box (x0, y0, x1, y1) - what `boxes_meeting` asks the keep-outs (feature 306)."""
    xs, ys = [q[0] for q in quad], [q[1] for q in quad]
    return min(xs), min(ys), max(xs), max(ys)


def _quads_overlap(p: Any, q: Any) -> bool:  # separating-axis rect overlap (a deck must not sit on a home; the placer is the guarantee since feature 158)
    for poly in (p, q):
        for i in range(4):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % 4]
            nx, ny = -(y2 - y1), (x2 - x1)
            pa = [nx * x + ny * y for x, y in p]
            qa = [nx * x + ny * y for x, y in q]
            if max(pa) < min(qa) or max(qa) < min(pa):
                return False
    return True


def _deck_corners_clear(p: Any, rot_deg: float, span: float, rw: float, wpts: Any, need: float) -> bool:
    """Is every corner of this deck clear of the WHOLE crossed course - the question the gate asks?

    Module-level rather than a closure inside `bridges()`: it is called from two nested loops there,
    and capturing their loop variables is exactly what ruff's B023 exists to catch.

    It mirrors `bridges_span_their_water`, which measures each of the four corners against EVERY
    segment of the crossed polyline - not against the one segment the way cuts. That difference is
    the whole reason this has to be asked at all: the span formula in `bridges()` solves the crossing
    against that one segment, so a course bending back toward a corner is water the formula never
    saw."""
    _r = math.radians(rot_deg)
    _c, _s = math.cos(_r), math.sin(_r)
    return all(
        min(seg_dist(p[0] + _qu * _c * span / 2 - _qv * _s * rw / 2, p[1] + _qu * _s * span / 2 + _qv * _c * rw / 2, wpts[k2], wpts[k2 + 1]) for k2 in range(len(wpts) - 1)) >= need
        for _qu, _qv in ((-1, -1), (-1, 1), (1, -1), (1, 1))
    )


def seat_deck(p: Pt, rot: float, span: float, rw: float, wpts: Any, need: float, water_seg: tuple[Pt, Pt]) -> tuple[float, float, bool]:
    """Find a deck that actually clears the water at this crossing: grow it along the way, and failing that
    SKEW it toward square and grow again. Returns (rotation, span, seated).

    LIFTED OUT OF `bridges` (feature 146, GM 2026-08-28 on inner functions and testability). The skew
    fallback sat four loops deep inside a method that scans every way against every watercourse, so the
    only way to reach it was to roll a map with a near-parallel crossing on it - cohort seed 47 was the
    one that ever did. Lifted, the whole decision is seven plain numbers.

    WHY SKEW AND NOT MORE GROWTH (2026-08-19): the growth loop lengthens the deck ALONG THE WAY, and at a
    near-parallel crossing that drives its ends further along the water instead of clear of it, so no
    ceiling on the growth could ever have worked. A real bridge is built as square to the stream as the
    road allows - the track bends onto the deck - which the deck's own seating already permits
    BRIDGE_ROT_TOL = 8 deg between deck and way, so 7 deg of skew needs no rule change: it took seed 47
    from an effective 16.6 deg to 23.6 and the span required from 44.6 px to about 31.

    Seating unchanged is the point: the skew is reached ONLY when plain growth failed, so every deck that
    seats today seats identically. When nothing seats, the ORIGINAL span comes back and the caller draws
    it anyway - an undersized deck that `bridges_span_their_water` then fails is better than none, because
    the check names it.

    Research:
        deck grown until its corners clear - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: up to 14 steps of 12% of the span
        skewed toward square - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: at most 7 deg, inside the 8 deg a deck may lie off its way
    """
    for grow in range(14):
        wider = span * (1.0 + 0.12 * grow)
        if _deck_corners_clear(p, rot, wider, rw, wpts, need):
            return rot, wider, True
    wa, wb = water_seg
    wb_deg = math.degrees(math.atan2(wb[1] - wa[1], wb[0] - wa[0]))
    toward = (wb_deg + 90.0 - rot + 90.0) % 180.0 - 90.0  # signed, toward square
    for sk in (2.0, 4.0, 6.0, 7.0):
        cand_rot = rot + math.copysign(sk, toward or 1.0)
        for grow in range(14):
            wider = span * (1.0 + 0.12 * grow)
            if _deck_corners_clear(p, cand_rot, wider, rw, wpts, need):
                return cand_rot, wider, True
    return rot, span, False


DECK_SPAN_DEFAULT_FT = 20.0
"""A deck that records no span is read as this long when asking whether it covers a crossing.

Research: unrecorded span - NONE: a fallback for reading a record
"""


def deck_covers(deck: Any, x: float, y: float) -> bool:
    """Does this deck's own span reach the point (x, y)? ONE predicate (feature 287, ways W02): `bridges()` and `bridge()`
    skip a crossing only when a standing deck covers it, and the lane law (`law.unbridged_crossings`) asks the same."""
    return math.hypot(float(deck["x"]) - x, float(deck["y"]) - y) <= float(deck.get("span", DECK_SPAN_DEFAULT_FT))


def flooded_ground(M: Any) -> list[list[Pt]]:
    """The rice a deck may not land on: every field's drawn paddy plots (feature 287, ways W13). A carried deck runs
    `LANDING_FT` onto dry ground past each bank; where the bank is a bund with flooded rice just beyond it, that landing ran
    onto the paddy (R3: the field path's canal deck, its end 7 ft into the rice).

    Research: no deck lands in the rice - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: every corner on dry ground
    """
    return [[(float(a), float(b)) for a, b in r] for f in (M.get("fields") or []) for r in (f.get("plot_rings") or []) if len(r) >= 3]


def _lands_dry(p: Pt, rot: float, span: float, rw: float, wet: Any) -> bool:
    """Does no corner of this deck stand inside a flooded plot (`flooded_ground`)?"""
    if not wet:
        return True
    corners = _deck_quad(p[0], p[1], span, rw, rot)
    for ring in wet:
        x0, x1 = min(q[0] for q in ring), max(q[0] for q in ring)
        y0, y1 = min(q[1] for q in ring), max(q[1] for q in ring)
        if any(x0 <= cx <= x1 and y0 <= cy <= y1 and point_in_poly(cx, cy, ring) for cx, cy in corners):
            return False
    return True


SUPPLY_ROLES = ("main", "branch", "lateral")
"""The ditches a footplank is laid on: the ones that carry water OUT to the paddies - a comb's main and branches, and the
laterals (a comb's field ditches, and a polder's inner ring canal and the field ditches off it, which the manifest records as
`lateral`). The record's reason (research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html, "Plank bridges over farm ditches (itabashi)", and its rendering, "How our maps draw plank bridges over farm ditches (itabashi)"): the plank is the board laid
where a bund path meets an IRRIGATION ditch, with cultivated ground, the settlement or a walked dike on both banks; "the
drainage ditches at a field's foot and the diagonal drains along its outer boundary" carry none. A polder's ring canal is its
distribution canal, inside the dike with paddies beyond it (research/archetypes/110: "inner ring canal -> field ditches ->
paddies"), so it is a supply ditch, not a drain. The collector, the drain and the feeder are not.

Research: planks on supply ditches only - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html, research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html: main, branch and lateral
"""

PLANK_DITCH_FT = 24.0
"""A footplank this near a recorded field ditch is on that ditch; farther, it crosses no recorded ditch at all.

Research: ditch association reach - NONE: 24 ft
"""


def plank_ditch(pt: Pt, ditches: Any) -> tuple[float, Any]:
    """(distance, role) of the recorded field ditch nearest `pt` - infinity and None where there is none."""
    best: tuple[float, Any] = (math.inf, None)
    for d in ditches or []:
        poly = [(float(q[0]), float(q[1])) for q in d.get("poly") or []]
        if len(poly) < 2:
            continue
        dist = min(seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))
        if dist < best[0]:
            best = (dist, d.get("role"))
    return best


def plank_on_supply(pt: Pt, ditches: Any) -> bool:
    """Is a footplank at `pt` on a supply ditch (`SUPPLY_ROLES`) - its nearest recorded ditch within `PLANK_DITCH_FT` and a
    main, a branch or a lateral? ONE predicate (feature 287, ways W14): `channel_footbridges` refuses a seat that fails it,
    and the lane law's `plank_faults` reads it.

    Research: planks on supply ditches only - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html
    """
    dist, role = plank_ditch(pt, ditches)
    return dist < PLANK_DITCH_FT and role in SUPPLY_ROLES


class UndeckableCrossing(ValueError):
    """A way reached `bridges()` crossing water where no deck seats. The web's last pass (`settle_the_web`) cuts every such
    crossing out of the lanes it may cut (feature 287, ways W12), so reaching here is a defect in the engine, not a map."""


def crossing_deck(ra: Pt, rb: Pt, rw: float, wa: Pt, wb: Pt, ww: float, wpts: Any, ftpx: float, wet: Any = ()) -> tuple[Pt, float, float, bool]:
    """The deck `bridges()` lays where the way segment `ra`-`rb` (width `rw`) crosses the water segment `wa`-`wb` of the
    course `wpts` (width `ww`): (crossing point, rotation, span, seated). The two segments are known to cross.

    LIFTED OUT OF `bridges` (feature 287, M1) so the lane law (`hamletgen/ways/law.py:deck_seats`) asks the SAME question
    the placer answers, rather than a restatement of it: one predicate per rule, read by the placer and by its test.

    The span SOLVES the oblique crossing (GM 2026-08-09: the old flat +28px slack was eaten by obliquity and left deck
    CORNERS at the water's edge). Along the deck the water is ww/sin wide, the deck's own width adds rw*|cos|/sin before a
    corner clears the bank, and past that every corner runs LANDING_FT of real feet onto dry ground (see the constant for the
    research). sin is clamped: segments_cross guarantees a genuine crossing, but a near-parallel graze would otherwise ask
    for an absurd deck.

    ...AND THE DECK IS GROWN UNTIL ITS CORNERS ACTUALLY CLEAR THE WATER (2026-08-12). The formula above solves the crossing
    against the ONE segment the way cuts, and clamps sin at 0.25 so a near-parallel graze cannot ask for an absurd deck.
    Both are reasonable and both under-size a deck where the watercourse BENDS near the crossing: the check
    (`bridges_span_their_water`) measures every corner against the whole crossed POLYLINE, so a neighboring segment curving
    back toward a corner is water the formula never saw. Rather than model that, ask the same question the check asks and
    lengthen until the answer is yes (`seat_deck`).

    ...AND IT LANDS DRY (feature 287, ways W13): a deck whose corner stands in a flooded plot (`wet`, `flooded_ground`) is
    not seated as the carried form; the crossing is tried again in the footplank's form - the local width plus the short
    `PLANK_ABUTMENT`, landing at the footplank's floor - which is what a farmer lays where a bund path meets a canal
    (research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html), and failing that it is not seated at all, so the web's last pass cuts the crossing.

    Research:
        oblique span solved - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: (ww + rw|cos|)/sin
        landing past each bank - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: LANDING_FT (10 ft) onto dry ground
        near-parallel clamp - NONE: sin floored at 0.25
        footplank form where the landing meets rice - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html: local width plus PLANK_ABUTMENT, a 2 ft corner floor
    """
    # segments_cross is True only for a genuine (non-parallel) crossing, so seg_intersect always returns a point here
    p = cast(Pt, seg_intersect(ra, rb, wa, wb))
    rot = math.degrees(math.atan2(rb[1] - ra[1], rb[0] - ra[0]))
    _rl = math.hypot(rb[0] - ra[0], rb[1] - ra[1]) or 1.0
    _wl = math.hypot(wb[0] - wa[0], wb[1] - wa[1]) or 1.0
    _cs = ((rb[0] - ra[0]) * (wb[0] - wa[0]) + (rb[1] - ra[1]) * (wb[1] - wa[1])) / (_rl * _wl)
    _sn = max(math.sqrt(max(0.0, 1.0 - _cs * _cs)), 0.25)
    _span = (ww + rw * abs(_cs)) / _sn + 2 * LANDING_FT / ftpx
    _need = ww / 2 + CARRIED_LANDING_FLOOR_FT / ftpx  # the check's own carried-way floor
    rot_used, span, seated = seat_deck(p, rot, _span, rw, wpts, _need, (wa, wb))
    if seated and not _lands_dry(p, rot_used, span, rw, wet):
        _plank = (ww + rw * abs(_cs)) / _sn + PLANK_ABUTMENT
        rot_used, span, seated = seat_deck(p, rot, _plank, rw, wpts, ww / 2 + 2.0 / ftpx, (wa, wb))
        seated = seated and _lands_dry(p, rot_used, span, rw, wet)
    return p, rot_used, span, seated


def undeckable_at(pts: Any, width: float, waters: Any, ftpx: float = 1.0, wet: Any = (), M: Any = None) -> list[tuple[int, Pt]]:
    """(segment index, crossing point) for every crossing of `waters` (`bridge_crossed_waters`) by a way along `pts` where
    no deck seats (`crossing_deck`, the very solve `bridges()` makes) - or where the registry of what stands on `M` refuses
    the deck as `bridge()` would record it (`deck_admitted`, feature 287 M8). THE ONE PREDICATE: the lane law asks it of a
    finished web (`hamletgen/ways/law.py`), the web's last pass cuts what it names, and a settlement rolled without that
    pass cuts its lanes by it before `bridges()` (`cut_undeckable_lanes`, feature 287)."""
    out = []
    for k, (ra, rb) in enumerate(zip(pts, pts[1:], strict=False)):
        for wpts, ww in waters:
            wp = [(float(q[0]), float(q[1])) for q in wpts]
            for wa, wb in zip(wp, wp[1:], strict=False):
                if segments_cross(ra, rb, wa, wb):
                    p, rot, span, seated = crossing_deck(ra, rb, width, wa, wb, float(ww), wp, ftpx, wet)
                    if not seated or not deck_admitted(M, p, rot, span, width):
                        out.append((k, p))
    return out


def deck_admitted(M: Any, p: Pt, rot: float, span: float, width: float) -> bool:
    """Does the registry of what stands on `M` admit a deck at `p` as `bridge()` records it (feature 287 M8)? Another deck
    it would stand on is not asked here: `bridges()` merges a deck into the one standing there (`_reseat_to_cover`). True
    where `M` carries no registry."""
    st = getattr(M, "standing", None)
    if st is None:
        return True
    rec = {"x": round(p[0], 1), "y": round(p[1], 1), "rot": round(rot, 1), "span": round(span, 1), "w": round(width, 1)}
    return not [c for c in st.conflicts("bridges", rec) if c[1] != "bridges"]


#: How far past the water's edge each piece of a lane cut at an undeckable crossing stops, in ft - the lane ends on the
#: bank, not in the water (`settle_the_web`'s own `CROSSING_GAP_FT`).
CUT_GAP_FT = 2.0
"""Research: lane end short of unbridged water - UNRESEARCHED: 2 ft past the bank"""


def _sub_run(pts: list[Pt], s0: float, s1: float) -> list[Pt]:
    """The part of the polyline `pts` between arc lengths `s0` and `s1`, clamped to it."""
    out: list[Pt] = []
    acc = 0.0
    for a, b in zip(pts, pts[1:], strict=False):
        d = math.dist(a, b)
        if d > 0 and acc + d >= s0 and acc <= s1:
            t0, t1 = max(0.0, (s0 - acc) / d), min(1.0, (s1 - acc) / d)
            for t in (t0, t1) if not out else (t1,):
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        acc += d
    return out


def cut_at(pts: list[Pt], k: int, p: Pt, gap: float) -> list[list[Pt]]:
    """The way `pts` with the stretch within `gap` (along it) of `p`, a point on its segment `k`, taken out: the pieces
    either side, each dropped if it keeps no length."""
    at = sum(math.dist(u, v) for u, v in zip(pts[: k + 1], pts[1 : k + 1], strict=False)) + math.dist(pts[k], p)
    total = sum(math.dist(u, v) for u, v in zip(pts, pts[1:], strict=False))
    pieces = (_sub_run(pts, 0.0, at - gap) if at - gap > 0 else [], _sub_run(pts, at + gap, total) if at + gap < total else [])
    return [q for q in pieces if len(q) >= 2 and sum(math.dist(u, v) for u, v in zip(q, q[1:], strict=False)) >= 1.0]


# THE DITCH CROSSING'S FORM IS A KNOB (269 B21; research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html, and research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html, "Plank bridges over farm ditches
# (itabashi)"). Three forms of crossing over small water are attested and the record cannot say which was laid over a
# paddy ditch: a SINGLE LOG (or one board, the same object in the Chinese definition), LOGS UNDER TRODDEN EARTH (the
# earthen bridge, the common bridge of pre-Edo Japan), and a PLANKED DECK. So a settlement lays all its ditch crossings
# in one form, rolled per map from its seed and declared as `meta.footbridge_form`. The EVEN chance is a GUESS: no
# source gives the forms' shares for a farm ditch, and the one proportion read (river bridges) would make the plank far
# rarer than earth over logs. Where and at what width a crossing is laid does not change with the form, so the deck's
# recorded box is the same for all three and only the glyph differs. `plank` is the default because it is the glyph
# every map drew before the knob, so a settlement that resolves no form draws what it always did.
FOOTBRIDGE_FORMS = ("log", "earthen", "plank")
"""Research: three ditch-crossing forms - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html: a single log, logs under trodden earth, a planked deck"""
FOOTBRIDGE_FORM = register_knob(Knob("footbridge_form", list(FOOTBRIDGE_FORMS), default="plank"))
"""The settlement's ditch-crossing form.

Research:
    one form per settlement - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: rolled from the map's seed
    even shares - GUESS
    plank as the default - NONE: what a settlement that resolves no form draws
"""


def deck_glyph(x: float, y: float, rot: float, span: float, deck_w: float, form: str = "plank") -> str:
    """The SVG of one crossing's deck, centered on (x, y) and running along `rot` for `span` - by its FORM (269 B21,
    research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html). The three draw inside the same `span` x `deck_w` box, so every check that reads the deck's
    record reads the same geometry whatever the roll:

    - `plank`: the planked timber deck, seams across it and a dark rail down each side (the glyph before the knob);
    - `log`: one round trunk, bark brown and rounded at the ends, narrower than the box - a log bridge is a single
      trunk about a foot or so through, so it fills seven tenths of the deck's width with a highlight along its crown;
    - `earthen`: a deck of trodden earth, the earth's own color between two dark edges, the ends of the logs under it
      ticked along each side - no seams and no rails, which is what tells it from the planked deck at a glance.

    Research:
        one glyph per form - CONVENTION: seams and rails, a rounded trunk, trodden earth with log ends
        log at seven tenths of the deck - CONVENTION
    """
    hl, hw = span / 2, deck_w / 2
    g = [f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.1f})">']
    if form == "log":
        r = hw * 0.7
        g.append(f'<rect x="{-hl:.1f}" y="{-r:.1f}" width="{span:.1f}" height="{2 * r:.1f}" rx="{r:.1f}" fill="#8A6A44" stroke="#4E3820" stroke-width="0.9"/>')  # the trunk
        g.append(f'<line x1="{-hl + r:.1f}" y1="{-r * 0.3:.1f}" x2="{hl - r:.1f}" y2="{-r * 0.3:.1f}" stroke="#B08A5C" stroke-width="0.6"/>')  # its crown catching the light
    elif form == "earthen":
        g.append(f'<rect x="{-hl:.1f}" y="{-hw:.1f}" width="{span:.1f}" height="{deck_w:.1f}" rx="1" fill="#BFA274" stroke="#6B5130" stroke-width="1.0"/>')  # the trodden earth
        step = max(3.0, span / 7)  # the log ends showing along each edge
        sx = -hl + step / 2
        while sx < hl:
            for ey in (-hw, hw):
                g.append(f'<line x1="{sx:.1f}" y1="{ey - 0.8:.1f}" x2="{sx:.1f}" y2="{ey + 0.8:.1f}" stroke="#6B5130" stroke-width="0.8"/>')
            sx += step
    else:
        g.append(f'<rect x="{-hl:.1f}" y="{-hw:.1f}" width="{span:.1f}" height="{deck_w:.1f}" rx="2" fill="#B68D5A" stroke="#5A3F1E" stroke-width="1.6"/>')  # the planked timber deck
        step = max(7, span / 8)  # plank seams across the deck
        sx = -hl + step
        while sx < hl - 1:
            g.append(f'<line x1="{sx:.1f}" y1="{-hw:.1f}" x2="{sx:.1f}" y2="{hw:.1f}" stroke="#5A3F1E" stroke-width="0.7" opacity="0.55"/>')
            sx += step
        g.append(f'<rect x="{-hl:.1f}" y="{-hw - 2.4:.1f}" width="{span:.1f}" height="2.6" fill="#5A3F1E"/>')  # the two side rails
        g.append(f'<rect x="{-hl:.1f}" y="{hw - 0.2:.1f}" width="{span:.1f}" height="2.6" fill="#5A3F1E"/>')
    g.append("</g>")
    return "".join(g)


class BridgesMixin:
    def bridge(self: Settlement, x: float, y: float, rot: float, span: float, deck_w: float, form: str = "plank") -> int:  # type: ignore[misc]
        """A timber BRIDGE carrying a road (or town street) over a watercourse - a stream, an
        irrigation channel, or the city moat at a gate. Centered on the crossing (x, y); the deck
        runs along `rot` (the road's bearing, degrees) for `span` px (long enough to reach both
        banks) and is `deck_w` wide (the carried road's width). Drawn on the TOP layer so it sits
        ABOVE the water and the roadbed. Records M['bridges']. `form` is the deck's glyph (`deck_glyph`): a carried
        way's deck is always planked; `channel_footbridges` passes the settlement's rolled ditch-crossing form.

        Research:
            one deck per crossing - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a deck within the tolerance that covers the point stands for it
            carried deck always planked - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html, research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html
            deck drawn over the water - CONVENTION: the top layer
            merge tolerance - NONE: half the span, between 4 and 12 px
        """
        # ONE DECK PER CROSSING, enforced HERE so every caller is covered (GM 2026-07-26): the
        # road-crossing pass in bridges(), the plank pass in channel_footbridges(), and any gen that
        # hand-places a deck for a crossing one of those also finds. Minami carried two decks over the
        # Hayakawa 3px apart, and honda/hoshigaoka/kikuta each carried two footplanks at the SAME
        # point - a way that crosses a stream where a channel joins it is one bridge on the ground.
        # None of it was caught because bridges were invisible to the overlap matrix (FIXTURE was a
        # blanket permission); bridges x bridges is a violation now. Tolerance scales with the deck so
        # two genuinely distinct footplanks a few px apart still both draw.
        # ...AND ONLY A DECK THAT COVERS THE CROSSING stands for it (feature 287, ways W02): a deck within the tolerance whose
        # own span does not reach the point leaves the crossing unbridged (`deck_covers`, the lane law's reading).
        _btol = max(4.0, min(12.0, span * 0.5))
        for _b in self.M.get("bridges", []):
            if math.hypot(_b["x"] - x, _b["y"] - y) <= _btol and deck_covers(_b, x, y):
                return int(_b["z"])
        z = self.add_top(deck_glyph(x, y, rot, span, deck_w, form), cls="footbridge")  # every plank and deck over water is one class (feature 134)
        self.M.setdefault("bridges", []).append({"x": round(x, 1), "y": round(y, 1), "rot": round(rot, 1), "span": round(span, 1), "w": round(deck_w, 1), "z": z})
        return z

    def bridges(self: Settlement) -> int:  # type: ignore[misc]
        """Auto-span every place a way CROSSES a watercourse with a s.bridge(), oriented ALONG the
        way. Call AFTER all ways (road, ring road, streets, lanes) AND all water (streams, channels,
        the cargo canal, the moat) are placed - a watercourse added later would leave an unbridged
        crossing (which the `roads_bridge_water` check then flags). Returns the number of bridges
        drawn. Historically a walled city's approach road crossed the moat on a bridge at each gate,
        and a country road crossed a stream on a timber bridge.

        SOLVE THE CROSSING, NEVER EYEBALL IT (GM 2026-07-27, Minami's cargo-basin bridge). A deck
        hand-placed at design coordinates goes crooked and slides off its crossing the moment the
        geometry around it is re-derived: Minami's canal bridge sat 17 px east of where the ring
        road actually met the canal and 39 deg off its bearing, so the road simply ran through the
        water beside it (Nagahara's was 15 px / 24 deg off, the same way). Both were hand-placed
        because this pass could not SEE the crossing - the RING ROAD was not a carried way here and
        the cargo CANAL was not a watercourse - so both are scanned now, and the checks
        `roads_bridge_water` re-derives the same crossings from the
        manifest. Anything this pass finds is aligned by construction; hand-place a deck only for a
        crossing this pass genuinely cannot see, and expect the alignment check to test it.

        Research:
            every crossing bridged - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: each carried way over each crossed water
            deck along the way - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html
            one deck per crossing place - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a covered crossing skipped, a near one merged
            unseated crossing - NONE: raised as an engine defect
        """
        wet = flooded_ground(self.M)
        n = 0
        for ra, rb, rw, wa, wb, ww, wpts in way_water_crossings(bridge_carried_ways(self.M), bridge_crossed_waters(self.M)):
            # the crossing SOLVED, never eyeballed - lifted to `crossing_deck` (feature 287) so the lane law asks the same question
            p, _rot_used, _span, _seated = crossing_deck(ra, rb, rw, wa, wb, ww, wpts, self.ftpx, wet)
            # A CROSSING ALREADY DECKED IS NOT DECKED AGAIN - judged by whether a standing deck COVERS it
            # (`deck_covers`, feature 287 ways W02), not by whether it lies within half the NEW deck's span:
            # that radius skipped a plank crossing 12 ft along the brook from a 30 ft deck that did not reach
            # it, and the lane crossed unbridged.
            if any(deck_covers(b2, p[0], p[1]) for b2 in self.M.get("bridges", [])):
                continue
            # NO UNDERSIZED DECK IS DRAWN (feature 287, ways W12, FR-005). `seat_deck` hands back the
            # original span when nothing seats; this pass drew it and `bridges_span_their_water` named it.
            # The web's last pass now cuts every crossing no deck seats before any deck is laid, so a way
            # that reaches here unseated is an engine defect, raised rather than drawn.
            if not _seated or not deck_admitted(self.M, p, _rot_used, _span, rw):
                raise UndeckableCrossing(f"no deck seats where a way crosses water at ({p[0]:.0f}, {p[1]:.0f})")
            # ...AND A DECK THAT WOULD STAND ON ANOTHER is merged into it: the standing deck is re-seated
            # long enough to cover both crossings, rather than the second being skipped (and left
            # unbridged) or drawn on top of the first (`features_do_not_overlap`).
            near = [b2 for b2 in self.M.get("bridges", []) if not b2.get("foot") and math.dist((p[0], p[1]), (float(b2["x"]), float(b2["y"]))) < _span * 0.5]
            if near:
                self._reseat_to_cover(near[0], p)
                continue
            # ONE DECK PER CROSSING PLACE (feature 126: two decks drawn on top of one another on four
            # cohort seeds once orphan links ran alongside existing ways). A real crossing is a PLACE, not
            # a per-way entitlement: two tracks converging on the same plank use the plank - the covered
            # skip and the merge above are that rule, each now leaving no crossing undecked.
            self.bridge(p[0], p[1], _rot_used, _span, rw)
            n += 1
        return n

    def cut_undeckable_lanes(self: Settlement) -> int:  # type: ignore[misc]
        """Cut every lane at every crossing where no deck seats (`undeckable_at`, the predicate `bridges()` raises on), so a
        settlement rolled without the web's last pass (`roll_village`) never hands `bridges()` a crossing it cannot deck
        (feature 287, ways W12). Each cut takes the crossing and `CUT_GAP_FT` past each bank out of the lane - the pieces
        either side kept, the first in place - so every cut strictly shortens the lane and the loop ends. Returns the cuts.

        Research: a lane stops at water it cannot bridge - UNRESEARCHED: cut CUT_GAP_FT past each bank
        """
        waters, wet = bridge_crossed_waters(self.M), flooded_ground(self.M)
        cuts = 0
        i = 0
        while i < len(self.M.get("lanes") or []):
            ln = self.M["lanes"][i]
            pts = [(float(x), float(y)) for x, y in ln.get("pts") or []]
            bad = undeckable_at(pts, float(ln.get("w", 6)), waters, self.ftpx, wet, self.M)
            if not bad:
                i += 1
                continue
            k, p = bad[0]
            near = max(
                (float(ww) / 2 for wpts, ww in waters if any(seg_dist(p[0], p[1], (float(u[0]), float(u[1])), (float(v[0]), float(v[1]))) <= float(ww) for u, v in zip(wpts, wpts[1:], strict=False))),
                default=3.0,
            )
            pieces = cut_at(pts, k, p, near + CUT_GAP_FT / self.ftpx)
            cuts += 1
            if not pieces:
                self.drop_lanes([i])
                continue
            ln["pts"] = [[round(x, 1), round(y, 1)] for x, y in pieces[0]]
            self.reink_lane(i)
            for q in pieces[1:]:
                self.lane(q, width=float(ln.get("w", 6)), clearance=float(ln.get("clearance", 22)), worn=bool(ln.get("worn")))
        return cuts

    def _reseat_to_cover(self: Settlement, deck: dict[str, Any], p: Pt) -> None:  # type: ignore[misc]
        """Lengthen a standing deck along its own bearing until it reaches `p` - a second crossing close enough that its own
        deck would stand on this one (feature 287, ways W02) - and redraw it, record and ink together.

        Research: two crossings, one deck - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: lengthened to reach both
        """
        deck["span"] = round(max(float(deck["span"]), 2.0 * math.dist((float(deck["x"]), float(deck["y"])), p) + 2.0), 1)
        self.top[int(deck["z"]) - self.TOPZ] = deck_glyph(float(deck["x"]), float(deck["y"]), float(deck["rot"]), float(deck["span"]), float(deck["w"]), str(deck.get("form", "plank")))

    def channel_footbridges(self: Settlement, spacing: float = 320, min_len: float = 140, plank_w: float | None = None, seg_caps: Any = None) -> int:  # type: ignore[misc]
        """Standalone plank FOOTBRIDGES across the SUPPLY ditches (main, branch, lateral - never the collector, the drain
        or the feeder, `SUPPLY_ROLES`), where field-workers cross a ditch while
        walking the paddy bunds - NOT carried by any lane (people reach them along the earthen bunds, so no
        path leads to them). Any ditch stretch longer than `min_len` gets a plank about MIDWAY; a long stretch
        gets one roughly every `spacing` px, evenly spaced along it. Each plank crosses PERPENDICULAR to the
        ditch, spanning its local width plus a short abutment. Call AFTER the field ditches are recorded. Bridges
        draw on the TOP layer (over the water). Records via `bridge()` into M['bridges'] (tagged 'foot'); returns
        the count. DECK WIDTH: an itabashi footplank is a single-file crossing (~3-4 ft), drawn 4 ft at the map's scale
        (`plank_w` defaults to `px(4)`; feature 328 wave 5 - it was a fixed 2 px, 2 ft on a hamlet) and NARROWER than a cart
        lane (~5-6 ft); the wider `bridges()` carried-way deck matches the lane it carries, but a footplank does not.
        USEFULNESS: a plank is placed only where BOTH banks reach ground someone walks to - cultivated field,
        the village, or a dike (via _plank_reaches_useful_ground); a stretch whose far bank opens onto marsh/scrub/off-map
        carries NO plank (GM 2026-07-22, Hikari no Sato: crossings into the reed marsh).
        FORM (269 B21): every crossing this lays takes the settlement's one rolled form - a single log, logs under
        earth, or a planked deck (`FOOTBRIDGE_FORM`, research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html) - declared as `meta.footbridge_form` and on
        each deck's record as `form`. The form changes the glyph only, never where or how wide a crossing is laid.

        Research:
            supply ditches only - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: never the collector, drain or feeder
            no path leads to a plank - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html
            one near the middle, more on a long run - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: one per 320 px of the run wide enough
            short stub stepped over - UNRESEARCHED: under 140 px, no plank
            only water too wide to step across - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: worth_planking, a hard filter at the seat
            square across the ditch - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html
            plank width - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: about 4 ft (`px(4)`), a single-file crossing
            short abutment - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the local width plus PLANK_ABUTMENT
            polder crossings by side - UNRESEARCHED: seg_caps, none on the feeder, far toe or drain
            longer plank at a junction - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the joins of ditches rule a seat out and the span stays about 8 ft; the code widens the deck over a junction
            obliqueness ceiling - UNRESEARCHED: no seat needing over three times the nominal span
            off the homes - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html
            off dry crops and gardens - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: houses, crops and other crossings rule a seat out
            off groves - UNRESEARCHED: a farm's grove rules a seat out
            a seat nearer a drain refused - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: never the collector or drain (`plank_on_supply`)
            assumed ditch width - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a field ditch 2.5 ft at the head tapering toward 1.2 ft; the code assumes 4.2 px where a record has none (`DEFAULT_W`)
            assumed stream and channel widths - UNRESEARCHED: 9 and 2.5 px where a record has none (`DEFAULT_W`)
            not on another deck - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html
            both banks reach useful ground - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html
            one rolled form - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: FOOTBRIDGE_FORM
            slide resolution - NONE: max(8, length/40) px, the check's own
        """
        plank_w = self.px(4.0) if plank_w is None else plank_w  # a footplank about 4 ft wide (research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html)

        from l7r.diagram.waterfields import taper_w, worth_planking  # local: the engine packages are peers, imported lazily

        houses = [_deck_quad(h["x"], h["y"], h["w"], h["h"], h.get("rot", 0)) for h in self.M.get("houses", [])]
        n0 = len(self.M.get("bridges", []))
        form = self.M["meta"]["footbridge_form"] = self.resolve("footbridge_form")
        # THREE MORE THINGS A PLANK SLIDES AWAY FROM (2026-08-11, found by rolling cohorts of
        # scripted hamlets - the shipped maps' ditches happen to run clear of all three):
        #
        #  - a DRY CROP PLOT. The slide already avoids houses; a deck laid across a hem strip is a
        #    board lying on the barley, and it is the same rule (`groves_clear_of_dry_plots` states
        #    it for trees, `structures_clear_of_dry_plots` for buildings). This became checkable at
        #    all only once `draw_comb_field` started registering its hem in `dry_polys`.
        #  - ANOTHER BRIDGE. Two planks drawn on top of each other is a drawing error, and it
        #    happens where two ditches run close and each independently wants a crossing at the
        #    same slot. `features_do_not_overlap` reads it as a ('bridges', 'bridges') pair.
        #  - A CONFLUENCE, where the deck is instead made LONGER. The span is sized from THIS
        #    ditch's nominal width, but where another watercourse joins, the water under the deck is
        #    the WIDER one - so a nominal deck comes up short and its abutment stands in the water
        #    (`bridges_span_their_water`). Skipping such spots was tried first and is too strong: on
        #    a drain whose banks are reed marsh for all but one short stretch, the only point with
        #    useful ground on both banks IS a junction, so the map ended up with a long ditch and no
        #    crossing (`long_ditches_have_a_footbridge`) - two correct rules forbidding between them
        #    a plank that ought to exist. A plank at a junction is simply a longer plank, which is
        #    what a farmer would lay, so the deck is sized to the widest water actually beneath it.
        dry_quads = [list(poly) for poly in self.dry_polys]
        # ...AND A FARM'S WORKED GROUND: its kitchen garden and its own grove (feature 291). Once the farms carried their own
        # groves the frames moved, and on cohort seed 1 a garden stood 5 ft off a field main, where the plank's landing
        # lay on the beds.
        # Each by its recorded box, which is what `features_do_not_overlap` reads (a garden's box stood 0.75 ft wider than its
        # bed outline, and the plank that cleared the outline met the box), a foot wider all round.
        ground_quads = [
            _deck_quad(g["x"], g["y"], g["w"] + 2.0, g["h"] + 2.0, g.get("rot", 0)) for key in ("gardens", "groves") for g in self.M.get(key, []) if all(k in g for k in ("x", "y", "w", "h"))
        ]
        # EACH KEEP-OUT FROM ITS BOX (feature 306, the GM: a check against many things means a box was not drawn). Every
        # deck candidate was tested against every dry plot and every garden and grove - 5,485 `quad_hits_poly` a call on the
        # pool. A deck meets a polygon only inside both their boxes (containment either way, or edges crossing), so the
        # polygons whose box - a pixel wider - meets the deck's box hold every one it can meet, and `quad_hits_poly`
        # decides as before; `any` over them is `any` over all. The homes are boxed the same way for `_quads_overlap`.
        dry_grid, ground_grid, house_grid = (boxed_grid(boxed_polys(q, 1.0)) for q in (dry_quads, ground_quads, houses))
        DEFAULT_W = {"streams": 9.0, "channels": 2.5, "field_ditches": 4.2}
        # ...including the OTHER FIELD DITCHES, which is where the confluences actually are: a comb's
        # branch takes off from a main, and the plank the branch wants at its own head sits over the
        # junction where the water is the main's width, not the branch's. Listing only streams and
        # channels missed every one of them.
        # NOT `drawn_channels`: it holds the filleted twin of every course including the one being
        # planked, and `wl is pts` cannot exclude a twin, so every candidate then reads as sitting at
        # a confluence with itself. Tried 2026-08-11; it made both footbridge checks fail at once.
        other_water = [(rec.get("poly") or rec.get("pts"), float(rec.get("w") or DEFAULT_W[key])) for key in ("streams", "channels", "field_ditches") for rec in self.M.get(key, []) or []]
        _water_segs = water_segment_index(other_water)  # built once for every deck candidate below (feature 278, FR-003)
        for d in self.M.get("field_ditches", []):
            if d.get("role") not in SUPPLY_ROLES:
                continue  # a plank is laid on a supply ditch, never the collector, the drain or the feeder (ways W14, `SUPPLY_ROLES`)
            pts = d["poly"]
            seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
            total = sum(seg)
            if total < min_len:
                continue  # a short stub (e.g. the head-race) is stepped over, no plank
            w = d.get("w", 4.2)
            w_tail = float(d.get("w_tail", w))
            if not worth_planking(w, w_tail, self.ftpx):
                continue  # narrow enough to stride across ANYWHERE - see `worth_planking`; the gate agrees
            # HOW MANY planks, measured over the run that can actually TAKE one. `n` used to come
            # from the ditch's whole LENGTH, which on a tapering ditch asks for crossings along a
            # stretch too narrow to deserve any: on Inashiro one main qualified only at its head,
            # drew n=2, and its second slot fell through the wide-first sort onto 2.42 ft of water -
            # narrower than decks this very rule had just removed, and bunched 120 ft from its
            # neighbor (settlement-review 2026-08-17, which traced it to the slot count rather than
            # to the gate/placer standoff I had assumed). Measuring the QUALIFYING run collapses n to
            # 1 there. `long_ditches_have_a_footbridge` is unaffected - it demands one plank per long
            # ditch, never one per spacing interval - so this cannot re-open the placer/check split.
            _lw = [taper_w(w, w_tail, k2 / 40.0) for k2 in range(41)]
            n = max(1, round(total * sum(1 for v in _lw if worth_planking(v, v, self.ftpx)) / len(_lw) / spacing))
            # SIDE-AWARE crossings (research 2026-07-22): on a polder the ring-canal `seg` tag caps crossings
            # per side - they cluster on the SETTLEMENT (east) toe, sparse on the interior laterals, NONE on
            # the unsettled feeder / far toe / drain (people cross to the fields where they live, then walk the
            # bund network). `seg_caps` maps seg -> max planks (0 = none); an untagged ditch uses the spacing.
            if seg_caps is not None and d.get("seg") in seg_caps:
                cap = seg_caps[d["seg"]]
                if cap <= 0:
                    continue
                n = min(n, cap)
            span = w + PLANK_ABUTMENT  # provisional; re-sized at each seat from the LOCAL width below
            for k in range(n):
                base = (k + 0.5) / n * total  # midway for n=1, evenly spaced otherwise
                # SLIDE along the ditch to a spot that (a) misses every home and (b) lands on
                # useful ground (field/village/dike) on BOTH banks. If no such spot is near this
                # slot - a marsh/scrub toe stretch with nothing to cross to - it carries NO plank.
                # THE SLIDE SAMPLES AT THE CHECK'S RESOLUTION, in arc length, not in fractions.
                #
                # `long_ditches_have_a_footbridge` decides a ditch needs a plank by walking it in
                # steps of max(8, length/40) and asking whether ANY point has useful ground on both
                # banks. The placer used a handful of fractional offsets, which on a long ditch is a
                # far coarser grid - so on a drain whose banks are marsh for all but one short
                # stretch, the check found the one good point and the placer stepped over it, and
                # the map failed for a plank that was legal and simply never tried. Same discipline
                # as reading the same manifest source: placement and its check must also LOOK at the
                # same resolution, or one of them is answering a different question.
                _step = max(8.0, total / 40)
                _cands = [k2 * _step / total for k2 in range(-int(total / 2 / _step), int(total / 2 / _step) + 1)]

                def _wide_enough(fr: float, _base: float = base, _tot: float = total, _w0: float = w, _w1: float = w_tail) -> bool:  # noqa: B008 - bind this ditch's geometry at definition, not at call
                    """Does the water at this seat earn a board (`worth_planking` at the seat's own taper)?"""
                    _a = max(0.0, min(_tot, _base + fr * _tot))
                    _lw = taper_w(_w0, _w1, _a / _tot if _tot else 0.0)
                    return worth_planking(_lw, _lw, self.ftpx)

                # ONLY WATER THAT EARNS A BOARD TAKES ONE (feature 287, ways W15, FR-005). This was a
                # preference - seats whose own taper earns a board sorted first, the narrow ones kept last
                # - because the gate once DEMANDED a plank on every long ditch (`long_ditches_have_a_
                # footbridge`), and a hard filter left cohort seeds 41 and 43 with a ditch the gate
                # required a plank on and the placer would not lay. That demand is retired (no rule asks
                # for a plank per ditch), so the preference only ever laid a plank on water the record
                # says is stepped across: the width is now a hard filter, and a ditch whose every wide
                # seat is taken carries no plank.
                # WHERE THIS LANDS ON A TAPERING BRANCH (accepted, settlement-review 2026-08-26,
                # feature 133 T11): `n` counts the QUALIFYING run but `base` is still the midpoint of
                # the WHOLE ditch, so on a branch whose head 30-50% qualifies, the nearest qualifying
                # seat to mid-ditch is the TAIL of that run - the plank lands 160-250 ft below the
                # head, not at the widest water. Seating from the qualifying run instead would put it
                # at the head, ~120 ft from the canal plank that already stands at the junction, and
                # the review judged mid-field the better crossing. Left as is on purpose; the width
                # under such a seat is `taper_w` (square-root taper), which is the authoritative
                # measurement - a linear read of w -> w_tail understates it by ~0.05 ft.
                for frac in sorted((fr for fr in _cands if _wide_enough(fr)), key=abs):
                    _arc = max(0.0, min(total, base + frac * total))
                    px, py, ang = _at_arc(pts, seg, _arc)
                    deck = ang + 90  # deck runs ACROSS the ditch (perpendicular)
                    quad = _deck_quad(px, py, span, plank_w, deck)
                    # WIDEN the deck to the widest water actually under it, then re-cut the quad:
                    # a plank at a junction spans the junction. Tested as "another course runs UNDER
                    # this deck", not "another course passes within a deck's length" - the looser
                    # form catches a ditch merely running parallel to a neighbor.
                    span_here = self._widen_for_confluence(quad, deck, pts, other_water, span, plank_w, _water_segs)
                    # THE OBLIQUENESS CEILING IS MEASURED AGAINST THE DITCH'S WIDEST SECTION, not
                    # against `span`, which is built from the HEAD width. On a COLLECTOR the head is
                    # the narrow end - a drain starts as a thread and earns its section at the
                    # outfall (`waterfields`, "a collector STARTS as a thread") - so a head-based
                    # ceiling is tiny and `_widen_for_confluence` clears it at every seat. Cohort
                    # seed 5 is the case: a 996 px drain tapering 1.5 -> 5.5 px got NO plank because
                    # all 40-odd seats read as "too oblique", while the gate rightly demanded one.
                    # `max(w, w_tail)` is the same section `worth_planking` uses to decide the ditch
                    # deserves a plank at all, so the two questions are now asked about one width.
                    #
                    # Re-sizing the DECK at each seat was tried first and is wrong: it widened decks
                    # on the downstream half of every collector and cost `features_do_not_overlap`
                    # (48-seed cohort 45 -> 44). The deck's size was never the defect; the ceiling's
                    # basis was.
                    if span_here > 3.0 * (max(w, w_tail) + PLANK_ABUTMENT):
                        continue  # too oblique to plank: widen where a longer deck is reasonable, but a
                        # crossing that needs three times the nominal span is a course running nearly
                        # ALONGSIDE this one, and the answer there is to cross somewhere else. (The fine
                        # arc-length slide above is what makes "somewhere else" reliably available.)
                    quad = _deck_quad(px, py, span_here, plank_w, deck)
                    if any(_quads_overlap(quad, it[0]) for it in boxes_meeting(house_grid, *_quad_box(quad))):
                        continue
                    # ...nor touching it: the overlap matrix reads a deck on a plot's edge as on the plot (Mizuguchi, on main too:
                    # a log plank's corner on a millet plot's corner, zero area) - tested half a foot wider all round
                    _touch = _deck_quad(px, py, span_here + 1.0, plank_w + 1.0, deck)
                    if any(quad_hits_poly(_touch, it[0]) for it in boxes_meeting(dry_grid, *_quad_box(_touch))):
                        continue  # no plank laid across the hem crop
                    if any(quad_hits_poly(quad, it[0]) for it in boxes_meeting(ground_grid, *_quad_box(quad))):
                        continue  # ...nor landing on a garden's beds or in a farm's grove
                    if any(_quads_overlap(quad, _deck_quad(b["x"], b["y"], b.get("span", 8.0), b.get("w", 4.0), b.get("rot", 0.0))) for b in self.M.get("bridges", [])):
                        continue  # ...nor on top of another deck
                    # ...tested on the EXACT numbers that will be recorded. `footbridges_reach_useful_ground`
                    # re-derives the bank points from the span and rot in the manifest, which `bridge()`
                    # rounds to 1 dp, while this used the unrounded values - and a bank sample sitting on
                    # the 55 px village reach flips between the two (a scripted-cohort hamlet, 2026-08-13:
                    # bank at 55.0 from the nearest house; placement said useful, the check said marsh).
                    # A MARGIN IS THE WRONG CURE HERE and was tried first: sampling further out is not
                    # strictly stricter, because past a strip of scrub the sample can land back INSIDE the
                    # field, so the wider test PASSED the very plank the check rejects. Rounding the inputs
                    # the same way the manifest does makes the two sides bit-identical, which is the only
                    # thing that actually settles a knife-edge. Measured on the plank that motivated it:
                    # bank-to-house 54.97 px at placement against 55.02 at the end, threshold 55.0 - and
                    # the 0.05 px came from `bridge()` rounding the deck's recorded POSITION, not its span.
                    if not self._plank_reaches_useful_ground(round(px, 1), round(py, 1), round(deck, 1), round(span_here, 1)):
                        continue
                    if not self._deck_clears_its_water(px, py, deck, span_here, plank_w):
                        continue
                    if not plank_on_supply((px, py), self.M.get("field_ditches")):
                        continue  # ...and a seat nearer a drain or collector than its own ditch (a junction) is refused (ways W14)
                    if not self.admits("bridges", {"x": round(px, 1), "y": round(py, 1), "rot": round(deck, 1), "span": round(span_here, 1), "w": round(plank_w, 1)}):
                        continue  # ...nor a plank the registry of what stands refuses: its ends on a dry plot or a fallow patch (M8)
                    self.bridge(px, py, deck, span_here, plank_w, form)
                    self.M["bridges"][-1]["foot"] = True  # a standalone footplank (checked by footbridges_reach_useful_ground)
                    self.M["bridges"][-1]["form"] = form
                    break
        return len(self.M["bridges"]) - n0

    def _widen_for_confluence(self: Settlement, quad: Any, deck: float, own_pts: Any, other_water: Any, span: float, plank_w: float, segs: PointGrid | None = None) -> float:  # type: ignore[misc]
        """The widest water actually UNDER this deck, expressed as a span - a plank at a junction is
        simply a longer plank, which is what a farmer would lay. Tested as "another course runs
        under this deck", not "another course passes within a deck's length": the looser form
        catches a ditch merely running alongside a neighbor. Returns `span` unchanged where nothing
        else crosses.

        THE SEGMENTS FROM AN INDEX (feature 278, FR-003): every segment of every other watercourse was tested per deck
        candidate - 62,565 of Inashiro's 63,674 `quad_hits_seg` calls. `quad_hits_seg(..., 3.0)` can pass only a segment
        whose box meets the deck's box widened by those 3 px, so the index (`water_segment_index`, built once per
        footbridge pass by the caller) returns every segment the test could pass, and the test decides as before. `under`
        is a maximum, so neither the order of the hits nor a hit met twice changes it.

        Research: longer plank at a junction - UNRESEARCHED: spans the widest water under it, corners 2 ft past it
        """
        _da = math.radians(deck)
        _dux, _duy = math.cos(_da), math.sin(_da)
        under: list[float] = []
        segs = segs if segs is not None else water_segment_index(other_water)
        qx0, qy0 = min(q[0] for q in quad) - 3.0, min(q[1] for q in quad) - 3.0
        qx1, qy1 = max(q[0] for q in quad) + 3.0, max(q[1] for q in quad) + 3.0
        seen: set[tuple[int, int]] = set()
        for wi, i2, bx0, by0, bx1, by1 in segs.near((qx0 + qx1) / 2, (qy0 + qy1) / 2, max(qx1 - qx0, qy1 - qy0) / 2):
            if (wi, i2) in seen or bx1 < qx0 or bx0 > qx1 or by1 < qy0 or by0 > qy1:
                continue
            seen.add((wi, i2))
            wl, ow = other_water[wi]
            if wl is own_pts:
                continue
            if not quad_hits_seg(quad, tuple(wl[i2]), tuple(wl[i2 + 1]), 3.0):
                continue
            _wx, _wy = wl[i2 + 1][0] - wl[i2][0], wl[i2 + 1][1] - wl[i2][1]
            _wl = math.hypot(_wx, _wy) or 1.0
            _sin = abs(_dux * _wy / _wl - _duy * _wx / _wl)  # deck-vs-course crossing angle
            _cos = abs(_dux * _wx / _wl + _duy * _wy / _wl)
            # THE CHECK'S OWN GEOMETRY, not the shorthand in its message. It requires
            # every deck CORNER to stand at least `cw/2 + floor` from the crossed
            # course's centerline (floor = 2 real ft for a footplank), so at a
            # crossing angle t the deck's half-length must exceed that over sin(t) -
            # i.e. the whole span is (cw + 2*floor + deck_w*|cos|) / sin. Deriving it
            # from the message's "(width + deck_w*|cos|)/sin plus a landing" leaves
            # the landing UNDIVIDED by sin and comes up short on a shallow crossing,
            # which is precisely the case this exists for.
            under.append((ow + 2.0 * (2.0 / self.ftpx) + plank_w * _cos) / max(_sin, 0.02) + 1.0)
        return max([span] + under)

    def _deck_clears_its_water(self: Settlement, px: float, py: float, deck: float, span_here: float, plank_w: float) -> bool:  # type: ignore[misc]
        """EVERY DECK CORNER LANDS PAST THE BANK - the exact test `bridges_span_their_water` will
        make, on the same geometry, before the deck is committed rather than after. A deck
        perpendicular to a STRAIGHT ditch clears by construction, which is why this was not needed
        for years; a deck at a BEND does not, because the polyline curves back toward one of its
        corners. (`w`/2 + 2 real ft is the check's own floor for a footplank.)

        Measured against `bridge_crossed_waters`, which is where the CHECK reads its geometry - the
        DRAWN, filleted polyline, not the recorded one `field_channel` was handed. Testing the
        recorded line looked right and rejected nothing, because the fillet is exactly what curves
        back toward the corner.

        Research: every corner past the bank - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: half the width plus 2 ft
        """
        _seat = None
        _cw = 0.0
        for _wp, _ww in bridge_crossed_waters(self.M):
            if min(seg_dist(px, py, _wp[i3], _wp[i3 + 1]) for i3 in range(len(_wp) - 1)) <= _ww / 2 + 2 and _ww > _cw:
                _seat, _cw = _wp, _ww
        if _seat is not None:
            _need = _cw / 2 + 2.0 / self.ftpx
            _dr = math.radians(deck)
            _cux, _cuy = math.cos(_dr), math.sin(_dr)
            if any(
                min(
                    seg_dist(px + su * _cux * span_here / 2 - sv * _cuy * plank_w / 2, py + su * _cuy * span_here / 2 + sv * _cux * plank_w / 2, _seat[i3], _seat[i3 + 1])
                    for i3 in range(len(_seat) - 1)
                )
                < _need
                for su, sv in ((-1, -1), (-1, 1), (1, -1), (1, 1))
            ):
                return False  # pragma: no cover - the corner rejection. It fires on real geometry (a scripted-cohort hamlet's branch ditch, whose gentle curve brought a deck corner back within the water at the ditch's head) but no pool map and no synthetic bed reproduces it: every fixture tried either finds a clear offset first or fails the useful-ground test before reaching here. The guard stays - the case it prevents shipped.
        return True

    def _plank_reaches_useful_ground(self: Settlement, px: float, py: float, deck_deg: float, span: float) -> bool:  # type: ignore[misc]
        """A STANDALONE footplank is worth building only if BOTH banks reach ground someone walks to:
        cultivated field (wet paddy or dry crop), the village (a dwelling within a short reach), or a
        walked polder-dike crest. A crossing whose far bank opens onto reed marsh, scrub commons, forest,
        or off-map serves no one - field-workers cross a ditch to reach the FIELD, not to wade into the
        bog (GM 2026-07-22, Hikari no Sato: drain-toe planks that stepped straight into the reed marsh).
        The deck spans the ditch along `deck_deg`, so its two ends ARE the two banks; each is sampled a
        short reach past its abutment. See the footbridges_reach_useful_ground check in check_village.py.

        Research:
            both banks reach useful ground - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: field, dry plot, dike crest or a dwelling
            bank and village reach - UNRESEARCHED: PLANK_BANK_REACH past the end, PLANK_VILLAGE_REACH to a house
        """
        a = math.radians(deck_deg)
        ux, uy = math.cos(a), math.sin(a)
        reach = span / 2 + PLANK_BANK_REACH
        # read the SAME cultivation source the footbridges_reach_useful_ground check reads (the manifest
        # field outlines + dry plots), so placement and check never disagree - self.field_polys is a
        # separate blocking-only list that some gens leave empty.
        crop = [f["outline"] for f in self.M.get("fields", []) if f.get("outline")]
        crop += [d["poly"] for d in self.M.get("dry_plots", [])]
        dikes = [dk["outline"] for dk in self.M.get("dikes", []) if dk.get("outline")]
        houses = self.M.get("houses", [])
        for sgn in (1.0, -1.0):
            bx, by = px + ux * reach * sgn, py + uy * reach * sgn
            if any(point_in_poly(bx, by, p) for p in crop):
                continue
            if any(point_in_poly(bx, by, p) for p in dikes):
                continue
            if any((bx - h["x"]) ** 2 + (by - h["y"]) ** 2 < PLANK_VILLAGE_REACH**2 for h in houses):
                continue
            return False
        return True


def water_segment_index(water: Any) -> PointGrid:
    """Every segment of every watercourse in `water` - `(polyline, width)` pairs - filed by its box as
    `(course index, segment index, x0, y0, x1, y1)` (feature 278, FR-003)."""
    grid = PointGrid()
    grid.extend(
        (wi, i, min(wl[i][0], wl[i + 1][0]), min(wl[i][1], wl[i + 1][1]), max(wl[i][0], wl[i + 1][0]), max(wl[i][1], wl[i + 1][1]))
        for wi, (wl, _w) in enumerate(water)
        if wl
        for i in range(len(wl) - 1)
    )
    return grid


def way_water_crossings(carried: Any, waters: Any) -> Any:
    """Every place a carried way's segment CROSSES a watercourse's segment (`segments_cross`), as `(ra, rb, rw, wa, wb, ww,
    wpts)` in the order the scan over every pair meets them: way by way, segment by segment, then water by water.

    THE WATER'S SEGMENTS FROM AN INDEX (feature 306, the GM: a check against many things means a box was not drawn).
    `bridges()` tested every way segment against every water segment - 16,190 tests a call on the pool, nearly all of
    them a lane and a brook a canvas apart. Two segments that cross meet inside both their boxes, so the water segments
    whose box meets the way segment's box (a pixel wider, so a rounding at a touching end cannot drop one) hold every
    crossing; `segments_cross` decides as before, and the candidates are taken in (water, segment) order, because
    `bridges()` lays and merges decks as it meets the crossings and the order is part of its answer."""
    grid = water_segment_index(waters)
    for rpts, rw in carried:
        for i in range(len(rpts) - 1):
            ra, rb = tuple(rpts[i]), tuple(rpts[i + 1])
            near = boxes_meeting(grid, min(ra[0], rb[0]) - 1.0, min(ra[1], rb[1]) - 1.0, max(ra[0], rb[0]) + 1.0, max(ra[1], rb[1]) + 1.0)
            for wi, j, *_ in sorted(near, key=lambda it: (it[0], it[1])):
                wpts, ww = waters[wi]
                wa, wb = tuple(wpts[j]), tuple(wpts[j + 1])
                if segments_cross(ra, rb, wa, wb):
                    yield ra, rb, rw, wa, wb, ww, wpts
