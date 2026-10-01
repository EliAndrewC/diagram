"""STAGE 8: the crossings, the notice board, the map frame - and the LABEL PHASE that closes every roll.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement

from .consts import POLDER_ARCHETYPES
from .hinterland import title_pocket
from .hinterland.frame import frame_for
from .plan import SitePlan
from .water import polder_crossing_caps

# ---- STAGE 8: crossings, the board, and the frame ------------------------------------------------


def stage_crossings(s: Settlement, plan: SitePlan) -> None:
    """Planks and decks.

    Every way that crosses water gets its deck HERE, which is why the earlier way stages are free to cross a
    ditch: the crossing is legal because this stage will deck it.

    Bridges where a way crosses water, and plank footbridges over the long irrigation ditches.

    After every way and every watercourse, because a crossing added later leaves an unbridged one -
    the engine's own `bridges()` docstring says so and the `roads_bridge_water` check enforces it.

    Steps:
        l7r.diagram.settlement.Settlement.bridges
        l7r.diagram.settlement.Settlement.channel_footbridges
        l7r.diagram.settlement.Settlement.dike_gates
        l7r.diagram.hamletgen.water.polder_crossing_caps
    """
    # THE LANES ARE ALREADY SQUARE (feature 287, M4c): every way crosses the brook and every drawn channel square, and so
    # does its deck (features 261, research 0084) - squared as the first step of `settle_the_web`, the web's last pass
    # (`ways/settle.py:square_every_crossing`), so every rule of the lane law is judged on the squared lane and no stage
    # after the web rewrites one. This stage only decks what the web drew. (The brook is round since `stage_sink`, M2.)
    s.bridges()
    if s.M.get("field_ditches"):
        if plan.field_archetype in POLDER_ARCHETYPES:
            # A POLDER'S RING CANAL is crossed where the village is (feature 150; the rule the
            # hand-authored polders carried, `polder_crossing_caps`): planks cluster on the
            # settlement-side toe collector, one per interior lateral, none on the feeder, the far
            # toe or the drain. Spacing as the hand-authored maps had it.
            s.channel_footbridges(spacing=320, seg_caps=polder_crossing_caps(plan))
            s.dike_gates()  # a sluice gate at every cut of the perimeter dike, snapped to the recorded water (feature 150 A7)
        else:
            s.channel_footbridges(spacing=300)


def stage_notice(s: Settlement, plan: SitePlan) -> None:
    """The notice board - the last FEATURE placed.

    The notice board (a `kosatsuba`, which is the word the engine's own identifiers use) is deliberately the
    last map feature, after even the crop and the title - only the label phase
    follows it, and that phase places captions, not features - and the reason is about the settlement rather
    than about the drawing (GM 2026-08-29): "where you put the notice board on the map does depend on what other
    features already exist ... the real humans that live in the society that decide where the notice board will
    go will look around at the things which already exist and then decide where to put the notice board. They
    may even decide to move a notice board which has already been placed." Every other stage either reserves
    ground or grows into it; the board does neither. It is a 12 x 5 ft plank a village drives in beside a way
    once the village is there, so it is the one feature that should see the whole map before it chooses. It
    stands ON a way - on the verge, a few feet off the tread (feature 133 T13), because a kosatsu is read where
    people pass - and WHICH way, and where along it, is a per-settlement knob rolled from the map's own seed
    over the placements the record attests and the map can site (feature 154). Placing it last also fixed a
    defect by construction: sited among the trees it used to claim a ~55 ft cleared disc, and an entrance seat
    on a windward fringe punched a 40 ft hole in the shelter belt that nothing replanted. No feature is placed
    after the board now, so it displaces nothing - and the GM's ruling is that it never should have: "humans
    would not need to clear any amount of space in order to put up a notice board at the side of a path." It may
    stand under a canopy at the wood's edge.

    The official notice board, on a lane verge at the busiest node.

    EVERY settlement tier posts the state's standing law, hamlets included - the ofuregaki circulars
    reached the peasantry through this board, read out by the one required-literate person (a
    hamlet's senior farmer, answering to the village headman). `place_kosatsuba` sites it itself,
    deterministically, from the same route records the validator reads.

    IT RUNS LAST - stage 17 of 17, after the woods, the ground cover, the crop and the title (GM
    2026-08-29). This docstring used to say the opposite, and the reason it gave was real at the time:
    sited after the cover it "silently found nowhere to go on one cohort map in six". What made that
    true was the board AVOIDING the woods - it needed a clear verge, and by then there was none. The
    board no longer avoids anything: its `village_grove` keep-out is retired and it may stand under a
    canopy at the wood's edge, so the ground it needs is a verge, which the woods never took.

    The GM's reasoning is about the settlement rather than the drawing: "the real humans that live in
    the society that decide where the notice board will go will look around at the things which
    already exist and then decide where to put the notice board. They may even decide to move a notice
    board which has already been placed." Every other stage reserves ground or grows into it; a plank
    driven in beside a way does neither, so it is the one feature that should see the whole map first -
    and nothing is placed after it for it to displace.

    ONE SITER (feature 287, labels L2): `place_kosatsuba` applies every board rule once - inside the view, off the title
    placard, beside its way and facing it, where every way out passes an `entrance` board, and only where the one placer
    seats its caption clean - and hands the caption's proved seat to the label phase. The re-seat that stood here, a
    second siter restating those rules because the first sampled seats outside the view, is deleted with its `loose`
    fallback: its own comments recorded four drifts from the siter (features 154, 227, 230, 261).

    Steps:
        l7r.diagram.settlement.structures.fixtures._helpers.kosatsuba_anchor
        l7r.diagram.settlement.Settlement.fixture_clear_of_water
        l7r.diagram.settlement.Settlement.place_kosatsuba
        l7r.diagram.settlement.Settlement.kosatsuba
    """
    s.place_kosatsuba()


def stage_frame(s: Settlement, plan: SitePlan) -> None:
    """Crop, title, scalebar.

    The canvas is deliberately generous and is cropped to content only now. Erring large is cheap - unused
    canvas is thrown away - while erring small silently mis-shapes the field.

    The crop, then the title.

    In that order: the title searches the FRAMED window for blank space to sit in, so the frame has
    to exist first.

    THE VIEW WAS DECIDED EARLIER, at the end of `stage_hinterland`'s seating (feature 287, M6): the crop takes exactly
    `plan.view`, so every rule that reads the picture - the bare ground, the woodland in the view, the belt's record against
    its ink, the scatter's frame - was placed against the page it is judged on. Should anything placed since have moved
    the frame the crop would take, the difference is recorded as `meta.view_drift` (left, top, right, bottom) and the
    view is still the decided one; the pool test holds that no map records one.

    Steps:
        l7r.diagram.hamletgen.hinterland.frame.title_pocket
        l7r.diagram.settlement.Settlement.crop_to_view
        l7r.diagram.settlement.Settlement.title
        l7r.diagram.hamletgen.frame.waterward_to_the_frame
    """
    # The margin leaves the TITLE somewhere to stand: `title()` scans the framed window for a box
    # that clears every feature and falls back to a corner overlap when the map is too full, which
    # `title_clear_of_features` then fails. But it is bounded above as well as below - `crop_hugs_
    # content` allows at most 56 px of view past the frame-setting content, because a band whose
    # only extra is open ground is wasted image. 64 was tried and fails all twelve. 48 is the most
    # air the frame will give the title.
    _pocket = title_pocket(s, plan)  # the pocket the belt was dented around (feature 150) - reserved once, see hinterland.title_pocket
    # The extras the frame reserves as content - an outside pocket, the confluence with its trunk, the brook beside the
    # field - are `frame_extras`, and the view carrying them was decided in `stage_hinterland` (`frame_for`). Predicting
    # the confluence back in `stage_sink` was tried twice and cannot work; reserving it where the view is decided can.
    assert plan.view is not None, "stage_frame runs after stage_hinterland, which decides the view"
    _now = frame_for(s, plan)
    if _now != plan.view:
        _v, _n = plan.view, _now
        s.M["meta"]["view_drift"] = [_v[0] - _n[0], _v[1] - _n[1], (_n[0] + _n[2]) - (_v[0] + _v[2]), (_n[1] + _n[3]) - (_v[1] + _v[3])]
    s.crop_to_view(plan.view)
    s.M["meta"]["title_pocket"] = [round(v, 1) for v in _pocket]  # recorded so a placard that fell back can be read against the reservation
    s.title(plan.spec.name, prefer=_pocket)
    waterward_to_the_frame(s)  # after the title: a sheet with no room for its name grows a band on the north, and the strip reads the final view


def strip_reaches_view(strip: Sequence[Sequence[float]], view: Sequence[float], faces: Sequence[str]) -> bool:
    """Does a waterward reed strip reach the view's edge on one of the water-facing `faces` - the bunds test's `reach`,
    lifted (feature 287, water:W43)."""
    vx0, vy0, vw, vh = (float(v) for v in view)
    xs, ys = [float(q[0]) for q in strip], [float(q[1]) for q in strip]
    reach = {"W": min(xs) <= vx0, "E": max(xs) >= vx0 + vw, "N": min(ys) <= vy0, "S": max(ys) >= vy0 + vh}
    return any(reach[f] for f in faces if f in reach)


def strip_face(strip: Sequence[Sequence[float]], dikes: tuple[float, float, float, float]) -> str:
    """Which flank of the dike's (x0, y0, x1, y1) box a waterward strip lies off - the side its center stands furthest
    outside."""
    xs, ys = [float(q[0]) for q in strip], [float(q[1]) for q in strip]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return max((("W", dikes[0] - cx), ("E", cx - dikes[2]), ("N", dikes[1] - cy), ("S", cy - dikes[3])), key=lambda t: t[1])[0]


def band_to_edge(strip: Sequence[Sequence[float]], face: str, view: Sequence[float], past: float = 20.0) -> list[tuple[float, float]]:
    """The wild ground between a strip's outer edge on `face` and the view's edge there, `past` beyond it, over the strip's
    own extent along the flank - lapping the strip by two feet so the two are one ground."""
    vx0, vy0, vw, vh = (float(v) for v in view)
    xs, ys = [float(q[0]) for q in strip], [float(q[1]) for q in strip]
    if face in ("W", "E"):
        a, b = (vx0 - past, min(xs) + 2.0) if face == "W" else (max(xs) - 2.0, vx0 + vw + past)
        return [(a, min(ys)), (b, min(ys)), (b, max(ys)), (a, max(ys))]
    a, b = (vy0 - past, min(ys) + 2.0) if face == "N" else (max(ys) - 2.0, vy0 + vh + past)
    return [(min(xs), a), (max(xs), a), (max(xs), b), (min(xs), b)]


def waterward_to_the_frame(s: Settlement) -> None:
    """A WATERWARD REED STRIP RUNS OFF THE FRAME (feature 287, water:W43; GM 2026-08-28, feature 150 T55): where the view
    reaches past the strip's `WATERWARD_DEPTH` on a water-facing flank, the wild ground between the strip and the view's
    edge is scattered too (`marsh`, with every keep-out it honors) and joined to the strip's record, so the reed fringe
    runs off the picture rather than stopping in it - a lake with a ruled edge. Here, because the strip is laid at the
    seat and the view is not final until the title has grown its band; the band depth stays as feature 150 T55 set it,
    and only the ground a view actually shows is added. A strip already reaching the edge is untouched; the extension is
    one ground with its strip (`unary_union`), or its own record where the two cannot join."""
    from shapely.geometry import Polygon  # noqa: PLC0415 - bound on first use
    from shapely.ops import unary_union  # noqa: PLC0415

    meta = s.M.get("meta") or {}
    faces, view = meta.get("waterward") or [], meta.get("view")
    pts = [p for dk in s.M.get("dikes") or [] for p in dk.get("outline") or []]
    if not faces or not view or not pts:
        return
    box = (min(float(p[0]) for p in pts), min(float(p[1]) for p in pts), max(float(p[0]) for p in pts), max(float(p[1]) for p in pts))
    for rec in [m for m in s.M.get("marshes") or [] if m.get("role") == "waterside" and m.get("poly")]:
        face = strip_face(rec["poly"], box)
        if strip_reaches_view(rec["poly"], view, faces) or face not in faces:
            continue
        n = len(s.M["marshes"])
        s.marsh(band_to_edge(rec["poly"], face, view), role="waterside")
        if len(s.M["marshes"]) == n:
            continue  # nothing open to scatter on: the wild ground there is all keep-out
        # ...AND THE STRIP IS ONE RECORD WITH ITS EXTENSION, always (feature 287, homes wave 5): the two grounds as one ring -
        # a hole keyholed, a keep-out between them (a lane) bridged by a zero-width seam - so the record is exactly the ground
        # the reeds are drawn on and the strip it names runs to the view's edge. The extension used to stay its own record
        # where the two could not join, which left the strip's record stopping inside the frame.
        joined = unary_union([Polygon(rec["poly"]).buffer(0), Polygon(s.M["marshes"][-1]["poly"]).buffer(0)])
        s.M["marshes"].pop()
        ring = [[round(float(x), 1), round(float(y), 1)] for x, y in one_ring(joined)]
        xs, ys = [q[0] for q in ring], [q[1] for q in ring]
        rec.update(poly=ring, x=round((min(xs) + max(xs)) / 2, 1), y=round((min(ys) + max(ys)) / 2, 1), w=round(max(xs) - min(xs), 1), h=round(max(ys) - min(ys), 1))


def one_ring(g: Any) -> list[tuple[float, float]]:
    """A polygon or a multipolygon as ONE ring whose inside is exactly its ground: each hole keyholed (`wet._keyholed`) and
    each further piece spliced in along a zero-width seam from the ring's nearest vertex, walked the same way round - so an
    even-odd reader counts the seam twice and the ground between the pieces stays outside."""
    from l7r.diagram.settlement.land.wet import _keyholed, _signed_area  # noqa: PLC0415

    pieces = sorted((p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and not p.is_empty), key=lambda p: -p.area)
    ring: list[tuple[float, float]] = list(_keyholed(pieces[0]))
    for p in pieces[1:]:
        loop: list[tuple[float, float]] = list(_keyholed(p))
        i, j = min(((a, b) for a in range(len(ring)) for b in range(len(loop))), key=lambda ab: math.dist(ring[ab[0]], loop[ab[1]]))
        loop = loop[j:] + loop[:j]
        if _signed_area(loop) * _signed_area(ring) < 0:
            loop = [loop[0], *reversed(loop[1:])]  # ...the same way round as the ring, so the piece adds
        ring = ring[: i + 1] + loop + [loop[0], ring[i]] + ring[i + 1 :]
    return ring


def stage_labels(s: Settlement, plan: SitePlan) -> None:
    """The labels - the final phase, after the last feature.

    Every caption on the map is placed here, against the finished sheet, and nothing comes after it (feature
    157, GM 2026-08-29): "add a phase at the very end of every settlement creation process, which is putting
    down the labels for things. Thus, after the final map feature is added, which on a hamlet is the notice
    board, there is a final phase in which we add labels for whatever map features get labels. This is because
    how we place labels will always depend on what else is on the map." No feature draws its own caption any
    more: a stage that wants one queues it (`label()`), and this stage drains the queue
    (`Settlement.place_labels`) once every feature a caption might have to avoid exists. It draws no feature and
    reserves no ground, so it can only ever be last - the same argument that put the notice board after the
    frame, taken one step further. The plate is the previous one with its captions on, which on a hamlet is
    exactly what the stage is.

    THE LABEL PHASE - the last stage of a hamlet, after every map feature is on the sheet.

    GM 2026-08-29 (feature 157): *"add a phase at the very end of every settlement creation process,
    which is putting down the labels for things. Thus, after the final map feature is added, which on
    a hamlet is the notice board, there is a final phase in which we add labels for whatever map
    features get labels. This is because how we place labels will always depend on what else is on
    the map."*

    It draws no feature and reserves no ground, so nothing can be placed after it and nothing it
    places can displace anything - the same argument that put `stage_notice` last, one step further.
    The work itself is `Settlement.place_labels`, which every tier shares: a hand-authored village,
    town or city script has no stage pipeline, so `finish()` runs the identical phase as the last
    thing it does. Whichever runs first drains the queue; the other is a no-op.

    `plan` is unused, and stays in the signature because `STAGES` is a list of `(s, plan)` callables -
    the pipeline's contract, not this stage's need.

    Steps:
        l7r.diagram.settlement.Settlement.place_labels
    """
    s.place_labels()
