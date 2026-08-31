"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, seg_intersect
from l7r.diagram.sitegen.geom import crosses_disc, crosses_poly, unit

from ..clearance import pairs_within
from ..consts import (
    LANE_JOIN_FT,
    WEB_REACH_FT,
    Poly,
    Pt,
)


def stream_segs(s: Settlement) -> list[tuple[Pt, Pt]]:
    """Just the STREAMS - the water a way needs a real deck to cross, as opposed to a plank.

    SPLIT OUT FROM `drawn_water_segs` BECAUSE THE DISTINCTION IS LOAD-BEARING, and it was measured
    the hard way. A peer session wired a blanket `shallow_crossing` veto into the link pass against
    the undifferentiated list (`plan.watercourses` plus every drawn channel) and the cohort went
    **41/48 -> 26/48, with 21 seeds failing `farmhouses_reach_a_way`**. The cause was the LIST, not
    the placement: a link joining two halves of a hamlet crosses field ditches constantly and often
    obliquely, and an aze ditch is a stride across - demanding a square crossing of every one strands
    the very components the pass exists to join. A far bigger defect than the oblique stream crossing
    the veto was written for.

    So the rule a way must respect is not "never cross water at a slant", it is "never cross water
    that needs a DECK at a slant", and this is that subset. `drawn_water_segs` still returns
    everything, for callers that want to avoid or bridge any water at all.

    Consumer note: `_join_orphan_ways` is the pass that needs this - it deliberately passes an EMPTY
    water list today ("a link may go the long way round, and may be planked"), which is exactly why
    it is the pass that can lay a way down the length of a brook (cohort seed 47).
    `_bridge_collinear_breaks` does NOT: it hands its water to `_route`, which already refuses to
    cross a watercourse at any angle, so a veto there would be unreachable code."""
    return [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for st in s.M.get("streams", []) if st.get("poly") for a, b in zip(st["poly"], st["poly"][1:], strict=False)]


def drawn_water_segs(s: Settlement) -> list[tuple[Pt, Pt]]:
    """Every DRAWN watercourse on the map, as segments - channels AND streams.

    THE STREAMS WERE MISSING FROM EVERY WAY-VS-WATER TEST, and that is the whole reason this helper
    exists rather than the inline `drawn_channels` comprehension it replaces. `drawn_channels` holds
    the irrigation net; `M["streams"]` holds the feed brook and any natural course, and nothing in
    this module ever looked at it. So `shallow_crossing` - which exists, is correct, and is wired
    into `path_violations` - simply never saw the brook: on cohort seed 47 a connector crossed a
    7 px stream at 17 degrees, and `bridges_span_their_water` failed the deck it produced, with the
    guard that was written for exactly that case sitting one list away.

    Same family as this engine's recurring defect - a guard keyed on the wrong input measures
    something other than what it protects. `trades.py` already reads both records together; this is
    that pattern, applied where the ways are laid."""
    segs = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    return segs + stream_segs(s)  # ONE definition of what a stream is, shared with the deck-needing subset


def path_violations(path: Poly, avoid: Sequence[Poly], pond: tuple[float, float, float, float] | None, brook: Sequence[tuple[Pt, Pt]], waters: Sequence[tuple[Pt, Pt]] = ()) -> int:
    """How many segments of a drawn way foul the crop, the pond or the drain brook (0 = clear).

    A COUNT rather than a boolean, so a caller with no clean option can still take the least-bad one.

    The pond and the brook are avoided outright rather than bridged: a way meeting water at a
    shallow angle needs a far longer deck than a square crossing, and `bridges_span_their_water`
    measures the deck the engine actually drew. Going around removes the crossing entirely, which
    is also what a real track does - you ford a ditch where it is narrow and square."""
    bad = 0
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        if (
            (pond is not None and crosses_disc(a, b, (pond[0], pond[1]), max(pond[2], pond[3]) + 80.0))
            or any(seg_intersect(a, b, p, q) is not None for p, q in brook)
            or any(crosses_poly(a, b, poly) for poly in avoid)
            or any(shallow_crossing(a, b, p, q) for p, q in waters)
            or any(crossing_lands_on_crop(a, b, p, q, avoid) for p, q in waters)
        ):
            bad += 1
    # ...and a way may not bridge TWICE within a deck's length. `s.bridges()` decks every crossing
    # it finds, so a way cutting two ditches a few tens of px apart gets two decks drawn on top of
    # each other - which `features_do_not_overlap` reads as a ('bridges', 'bridges') pair, and which
    # is a drawing error rather than a siting one. Crossing further along, where the ditches have
    # separated, is what a track does anyway.
    hits = [x for i in range(len(path) - 1) for p, q in waters if (x := seg_intersect(path[i], path[i + 1], p, q)) is not None]
    bad += pairs_within(hits, 46.0)  # the same pairs the every-pair form counted (170 million `hypot` on a polder - feature 138), by a sweep
    return bad


def crossing_lands_on_crop(a: Pt, b: Pt, p: Pt, q: Pt, crops: Sequence[Poly], pad: float = 14.0) -> bool:
    """Does the way a->b meet the watercourse p->q at a point standing on cropland?

    A crossing gets a DECK, and a deck laid on a hem plot is a bridge across the barley
    (`features_do_not_overlap` reports it as a dry_plots/bridges pair). The way is free to cross the
    same ditch a little further along where the crop stops - which is where the bund is anyway."""
    hit = seg_intersect(a, b, p, q)
    if hit is None:
        return False
    return any(point_in_poly(hit[0], hit[1], list(c)) or min(seg_dist(hit[0], hit[1], c[i], c[(i + 1) % len(c)]) for i in range(len(c))) < pad for c in crops)


def shallow_crossing(a: Pt, b: Pt, p: Pt, q: Pt, limit_deg: float = 42.0) -> bool:
    """Does the way a->b cross the watercourse p->q at a SHALLOW angle?

    A way is allowed to cross an irrigation ditch - that is what a plank or a small timber bridge is
    for, and forbidding it outright would cut the field spur off from the field. What it may not do
    is cross at a slant: an oblique crossing needs a deck of (width + deck_w x |cos|) / sin plus a
    landing each side, so `bridges_span_their_water` fails it with an abutment standing in the
    water. Steering the way to meet the ditch square is the fix a farmer would recognize."""
    if seg_intersect(a, b, p, q) is None:
        return False
    ux, uy = unit(b[0] - a[0], b[1] - a[1])
    vx, vy = unit(q[0] - p[0], q[1] - p[1])
    return abs(math.degrees(math.asin(max(-1.0, min(1.0, ux * vy - uy * vx))))) < limit_deg


# ---- WHICH HOUSES THE LANE NETWORK ACTUALLY SERVES (feature 166) --------------------------------
# Lifted out of the retired `farmhouses_reach_a_way` gate check, whose body this is. The generator's
# re-roll ladder used to obtain this by running the whole battery and PARSING its printed output; it
# now asks here.
#
# LIFTED, NOT RE-DERIVED, and that distinction is the whole reason this code looks like the check
# rather than like its neighbors. `driver.py` records what happened the last time someone wrote a
# reach measure from scratch: it "was wrong on five of six seeds... it over-counted and never read
# zero", so anything steered by it was steered by noise.
#
# AND IT DOES NOT REUSE `_components`, WHICH IS THE NEAR-MISS THAT WOULD HAVE MOVED MAPS.
# `_components` joins two ways when an END of one comes within tolerance of the other's tread.
# This rule joins them when ANY VERTEX does. The stricter predicate yields a smaller network, so
# more houses read as unserved, so the ladder re-rolls maps it used to keep. Two connectivity
# helpers that look interchangeable and are not - the exact shape `dev/gate.md` collects under
# "MEASURE WHAT THE RULE MEASURES".


def lanes_share_tread(p: Poly, q: Poly, join: float = LANE_JOIN_FT) -> bool:
    """Do two drawn treads come within `join` anywhere - by ANY vertex of either against the other's run?

    Lifted from the check's own inner `_fw_touch` so it can be tested with two lists of tuples instead
    of a settlement (the project's standing rule on closures that are hard to reach)."""
    return any(seg_dist(v[0], v[1], a, b) <= join for v in p for a, b in zip(q, q[1:], strict=False)) or any(seg_dist(v[0], v[1], a, b) <= join for v in q for a, b in zip(p, p[1:], strict=False))


def served_network(lanes: Sequence[Mapping[str, Any]], join: float = LANE_JOIN_FT) -> list[tuple[Pt, Pt]]:
    """The segments of the CONNECTED network - the component containing the settlement's link to the world.

    THE NETWORK, NOT ANY LINE ON THE GROUND. The rule this serves is that every house in a nucleated
    cluster is reached by the INTERCONNECTED system of lanes, so a house served only by an isolated stub
    is not served. The component is grown from the connector if one is drawn, else from the longest lane;
    a check satisfiable by an island rewards drawing an island."""
    ways = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in lanes]
    seed = next((i for i, ln in enumerate(lanes) if ln.get("connector")), None)
    if seed is None and ways:
        seed = max(range(len(ways)), key=lambda i: sum(math.dist(a, b) for a, b in zip(ways[i], ways[i][1:], strict=False)))
    main = set() if seed is None else {seed}
    grew = True
    while grew:
        grew = False
        for i, p in enumerate(ways):
            if i in main or len(p) < 2:
                continue
            if any(lanes_share_tread(p, ways[j], join) for j in main if len(ways[j]) >= 2):
                main.add(i)
                grew = True
    return [(a, b) for i in sorted(main) for a, b in zip(ways[i], ways[i][1:], strict=False)]


def unreached_houses(M: Mapping[str, Any], reach: float = WEB_REACH_FT) -> list[tuple[int, int, int]]:
    """(x, y, distance) for every farmhouse the connected lane network does not reach. [] when the rule
    does not apply to this map.

    FORM-CONDITIONAL, NOT WAIVED, and the condition is carried verbatim from the check. The rule's own
    justification is about ONE form - every house in the NUCLEATED village is reached by the lane network -
    and a DISPERSED hamlet has no internal network by definition, so the rule is not about it. A waiver
    would have been the wrong tool: a waiver says "this map breaks a rule that is true of it"; a dispersed
    hamlet does not break this rule, the rule does not apply. Defaults to nucleated so a map that declares
    no form keeps its old treatment."""
    meta = M.get("meta") or {}
    if not meta.get("generated_by") or meta.get("settlement_form", "nucleated") == "dispersed":
        return []
    segs = served_network(M.get("lanes") or [])
    if not segs:
        return []
    far: list[tuple[int, int, int]] = []
    for h in M.get("houses") or []:
        cx, cy = float(h["x"]), float(h["y"])  # x, y ARE the center here - the manifest's convention
        d = min(seg_dist(cx, cy, a, b) for a, b in segs)
        if d > reach:
            far.append((round(cx), round(cy), round(d)))
    return far
