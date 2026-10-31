"""THE POLDER ARCHETYPES - the reclaimed block, its dike, its flanks and the reed fringe outside them.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.

Research: polder geometry - NONE: grid search, flank letters, binning and intersection plumbing
"""

from __future__ import annotations

from collections.abc import Sequence

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.land.dikes import DIKE_GAP_HW

from ..consts import (
    POLDER_ARCHETYPES,
    WATERWARD_DEPTH,
    Poly,
    Pt,
)
from ..plan import SitePlan
from ..pondstock import reserve_sty_seat

# ---- the polder's flanks (feature 150) --------------------------------------------------------------


def _compass(v: Pt) -> str:
    """The compass letter a screen-space vector points to (screen y grows DOWN, so +y is S)."""
    return ("E" if v[0] > 0 else "W") if abs(v[0]) >= abs(v[1]) else ("S" if v[1] > 0 else "N")


def polder_flanks(plan: SitePlan) -> dict[str, str]:
    """The four flanks of a polder block as compass letters, in the roles the composition uses.

    `head` is where the water comes in (uphill), `foot` where it leaves, `plus` the +cross side -
    the one `build_polder` names the settlement side and gives the `e_toe` collector - and `minus`
    the other; `cluster` is the flank the seated village actually stands on (from `plan.seat`,
    empty before `stage_seat`). Polders are laid to cardinal falls, so every letter is exact."""
    dx, dy = plan.fall
    out = plan.seat.get("out") if plan.seat else None
    return {
        "head": _compass((-dx, -dy)),
        "foot": _compass((dx, dy)),
        "plus": _compass((dy, -dx)),
        "minus": _compass((-dy, dx)),
        "cluster": _compass((float(out[0]), float(out[1]))) if out else "",
    }


def waterward_flanks(plan: SitePlan) -> list[str]:
    """Which flanks of the dike face the fluctuating water it was reclaimed from.

    research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.html: outside the dike is the lake, creek, reed marsh or
    mudflat the block was dug out of - EXCEPT on the landward flank where the polder abuts the
    natural shore, which is where the village stands (nobody lives on a flood-fighting earthwork
    when dry ground is a few steps away), and the head flank, where the header reservoir already
    stands as the wild water. So: the foot (the outfall side, already wet) and the cross flank(s)
    the cluster does not occupy. This is the hand-authored Kuwabata's and Enokida's `["W", "S"]`
    derived rather than declared.

    Research: waterward flanks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the foot and the cross flanks the village does not stand on, not the head where the reservoir stands
    """
    f = polder_flanks(plan)
    return [q for q in (f["minus"], f["plus"], f["foot"]) if q != f["cluster"]]


def dike_face(pts: Sequence[Pt], flank: str, lo: float, hi: float, bins: int = 32, cut: float = 0.0, cuts: Sequence[Pt] = (), cut_hw: float = DIKE_GAP_HW) -> Poly:
    """The dike's OUTER FACE along one flank, as a polyline spanning [lo, hi] (feature 150 T54).

    The waterward reed strip has to end exactly where the embankment starts: on the mound is the GM's
    defect, short of it is a dry apron in front of the water. A rectangle can do neither, because the
    ring wanders - Kuwabata's west face stands up to 40 px inside its own outermost point. So the face
    is read off the dike's drawn outline: bin the outline's points along the flank's axis and take the
    OUTERMOST one in each bin (`min` on the W/N sides, `max` on the E/S). Outermost, not average, is
    what keeps the strip off the band - within a bin the face can only be at or outside the value
    taken. A bin the ring does not reach (the strip runs a little past the dike's extent, and the ring
    is CUT by its crossing gaps) keeps its neighbor's face, so the polyline stays continuous to the
    frame. Only the ring's own half counts, split at its center: measured, a gap in the west face let
    the east face win those bins and the west strip came out 2,422 px wide - the whole map wet.

    `cut` is how far the face steps INWARD at a NOTCH - a sluice cut or a crossing, where the
    earthwork is cut through and the water passes - and `cuts` are the notch centers the dike itself
    records (`M['dikes'][*]['gaps']`), already assigned to this flank by the caller. Holding the
    neighbor's face across one left a ~50 ft dry pocket in front of the south outfall
    (settlement-review 2026-08-28), which is backwards: an outfall notch is the wettest ground on the
    flank. The step is keyed on the RECORD and applies UNCONDITIONALLY to the bins the notch covers -
    the first cut made it an `elif` on an empty bucket, on the assumption that a cut empties its bin,
    and the next review measured 14 outline points in the notch bin and 0 steps on all four flanks:
    the ring's cut ENDS fill it. A rule that cannot fire looks exactly like a rule that passes, so the
    step now reads the record alone (bins beyond the ring's own span still keep the extreme - the
    strip runs a little past the dike's ends, and there is no cut there).

    Research: strip at the dike's outer face - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); the reeds stop at the outermost face, stepping in through a notch
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N1, 2026-10-25) - 32 (how many bins sample the dike's outer face)
    """
    horiz = flank in ("W", "E")
    ai, fi = (1, 0) if horiz else (0, 1)  # bin ALONG `ai`; the face is the extreme on `fi`
    outward_min = flank in ("W", "N")
    fs = [p[fi] for p in pts]
    mid = (min(fs) + max(fs)) / 2  # the ring's center on the face axis: only its own half counts
    step = (hi - lo) / bins
    buckets: list[list[float]] = [[] for _ in range(bins)]
    for p in pts:
        k = int((p[ai] - lo) / step)
        if 0 <= k < bins and ((p[fi] <= mid) if outward_min else (p[fi] >= mid)):
            buckets[k].append(p[fi])
    filled = [k for k in range(bins) if buckets[k]]
    first, final = (filled[0], filled[-1]) if filled else (bins, -1)
    last = min(fs) if outward_min else max(fs)  # the extreme, for the bins beyond the ring's own extent
    vals: list[float] = []
    for k in range(bins):
        if buckets[k]:
            last = min(buckets[k]) if outward_min else max(buckets[k])
        v = last
        c = lo + (k + 0.5) * step
        if first <= k <= final and any(abs(g[ai] - c) <= cut_hw + step / 2 for g in cuts):
            v = last + (cut if outward_min else -cut)  # a NOTCH on this flank: the water passes through the cut
        vals.append(v)
    # THINNED, BUT IN SQUARE STEPS. Every point of this polyline is paid for again by `marsh()`'s
    # per-scatter-point `point_in_poly` - 64 bins turned a 4-point rectangle into a 66-point ring in the
    # hottest test on the map - so a run of bins at one face value emits its FIRST and LAST point only.
    # Keeping just the first was tried and is wrong: the run then slants to the next value across its
    # whole length, and a slant cuts back INSIDE the band it was measured to stay outside of (5.5 px on
    # the unit fixture). The step is square; only the one bin where the face actually changes slants.
    out: Poly = []
    for k, v in enumerate(vals):
        if k in (0, bins - 1) or v != vals[k - 1] or v != vals[k + 1]:
            c = lo + (k + 0.5) * step
            out.append((round(v, 1), round(c, 1)) if horiz else (round(c, 1), round(v, 1)))
    return out


def stage_waterward(s: Settlement, plan: SitePlan) -> None:
    """The reed fringe along every water-facing flank of a polder dike, and its declaration.

    Its own stage since feature 150 - `STAGES` position 5, after the seat and BEFORE the houses and the
    track, because the strip RESERVES wet ground both must avoid (laid in the hinterland it was drawn
    over a connector already routed through it; `driver.py` records the move). The hinterland's own toe
    marsh and scrub come later and keep out of it. Each strip hugs the dike's outer face (reeds auto-skip the band and the ponds via the
    keep-outs) and runs off the frame - it is wild ground continuing, not a feature with an edge,
    so the crop ignores it. `meta.waterward` declares the water-facing flanks, and the frame holds each
    strip to the view's edge (`to_the_strips`, `waterward_to_the_frame`).

    THE STRIP STOPS AT THE MOUND (feature 150 T54, GM 2026-08-28: "the marshland overlaps with the
    earthen mounds ... In some cases, it seems to even extend past them"). Each strip used to lap 60 px
    INWARD from the dike's outer extreme - past a band 11-38 px wide, so the reeds and their wet tint
    were drawn over the mound and out the other side, and the recorded polygon claimed the mound as wet
    ground (which since T50 is no-build ground too). The lap is gone: the strip's inner edge FOLLOWS the
    dike's outer face (`dike_face`), so record and ink both stop where the embankment starts and neither
    leaves a dry apron in front of it - clipping the rectangle to the dike's extreme instead was tried
    and showed one up to 40 px wide wherever the ring wanders inward from its outermost point. `marsh()`
    keeps its reed tile off the band itself and off every pond bank in the same change: the strip is the
    REGION, the keep-out is the guarantee - the two halves of one rule.

    Steps:
        l7r.diagram.hamletgen.water.polder.waterward_flanks
        l7r.diagram.hamletgen.water.polder.dike_face
        l7r.diagram.settlement.Settlement.marsh
        l7r.diagram.hamletgen.pondstock.reserve_sty_seat

    Research:
        reed fringe on the waterward flanks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a marsh strip off each water-facing flank
        strip depth - CONVENTION: WATERWARD_DEPTH outlasts any crop, the strip running off the frame
        its reed strip's run - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 30 (how far the reed strip runs past the dike's ends, across the other axis); 20 (the same, at the other end)
    """
    if plan.field_archetype not in POLDER_ARCHETYPES or not s.M.get("dikes"):
        return
    pts = [p for dk in s.M["dikes"] for p in dk.get("outline", [])]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    W, H = float(s.W), float(s.H)
    ylo, yhi = y0 - 30.0, y1 + 20.0
    xlo, xhi = x0 - 30.0, x1 + 20.0
    cut = max(float(dk.get("w_max", 0.0)) for dk in s.M["dikes"])  # a notch is cut through the whole band
    # EACH NOTCH BELONGS TO ONE FLANK - the one whose face it stands nearest. A cut near a corner is
    # otherwise stepped into on both, which bites the strip's edge where the band is whole.
    by_flank: dict[str, list[Pt]] = {"W": [], "E": [], "N": [], "S": []}
    for dk in s.M["dikes"]:
        for g in dk.get("gaps") or []:
            gx, gy = float(g[0]), float(g[1])
            by_flank[min((("W", gx - x0), ("E", x1 - gx), ("N", gy - y0), ("S", y1 - gy)), key=lambda t: t[1])[0]].append((gx, gy))
    # THE STRIP IS A BAND, NOT A HALF-CANVAS (feature 150 T55). It used to run from the dike's face to the
    # edge of the canvas, and the crop then threw nearly all of it away - on Kuwabata the view keeps ~74 px
    # of open water west of the dike out of the 1,880 px drawn. Every one of those reeds and tint circles
    # was scattered, tested against every keep-out and discarded: `stage_waterward` cost 18-24 s of a 40 s
    # gen. `WATERWARD_DEPTH` outlasts any crop this tier produces while cutting the scatter ~4x; the strip
    # still runs off the frame, so it is still wild ground continuing rather than a feature with an edge.
    d = WATERWARD_DEPTH
    strips: dict[str, Poly] = {
        "W": [(max(-20.0, x0 - d), ylo), *dike_face(pts, "W", ylo, yhi, cut=cut, cuts=by_flank["W"]), (max(-20.0, x0 - d), yhi)],
        "E": [(min(W + 20.0, x1 + d), ylo), *dike_face(pts, "E", ylo, yhi, cut=cut, cuts=by_flank["E"]), (min(W + 20.0, x1 + d), yhi)],
        "N": [(xlo, max(-20.0, y0 - d)), *dike_face(pts, "N", xlo, xhi, cut=cut, cuts=by_flank["N"]), (xhi, max(-20.0, y0 - d))],
        "S": [(xlo, min(H + 20.0, y1 + d)), *dike_face(pts, "S", xlo, xhi, cut=cut, cuts=by_flank["S"]), (xhi, min(H + 20.0, y1 + d))],
    }
    flanks = waterward_flanks(plan)
    for q in flanks:
        s.marsh(strips[q], role="waterside")
    s.meta(waterward=flanks)
    # ...AND THE STY'S SEAT, the other ground a dike-pond hamlet decides once the flank is known and before the houses stand
    # (feature 287, water W50). A re-seat by `seat_every_household` keeps to this flank (`margin_ladder`), so neither the
    # strips, their declaration nor this reservation has to be redrawn for it (`waterward_flanks` reads the flank alone).
    reserve_sty_seat(s, plan)


def polder_crossing_caps(plan: SitePlan) -> dict[str, int]:
    """Where plank crossings go on a polder's ring canal (research 2026-07-22, research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.html): people cross to the fields where they LIVE and then walk the bund network,
    so crossings CLUSTER on the collector the village abuts. On a FLANK: three on the settlement-side toe, one on each
    interior lateral, NONE on the feeder, the far toe or the drain. At the HEAD: three on the feeder, one on each toe.
    At the FOOT: two on each toe and none on the drain. `build_polder` names the +cross collector `e_toe` and the other
    `w_toe`; which is the settlement side is read off the seat, not assumed. (A valley hamlet such as the reference has
    no polder: this and the dike gates draw nothing there.)

    Research:
        no plank on the drain - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: none over the drain at the field's foot
        crossings where the village lives - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a crossing stands wherever both ends reach useful ground, a walked dike included - the far toe and the feeder are capped at none on the flank seats, a departure the code keeps until feature 417 T34; at a flank seat three on the collector the village abuts, one per lateral, none on the feeder or far toe; at the head the feeder 3 and the toes 1, at the foot the toes 2 each
    """
    f = polder_flanks(plan)
    if f["cluster"] == f["plus"]:
        return {"feeder": 0, "w_toe": 0, "drain": 0, "e_toe": 3, "lateral": 1}
    if f["cluster"] == f["minus"]:
        return {"feeder": 0, "e_toe": 0, "drain": 0, "w_toe": 3, "lateral": 1}
    # The village at the HEAD or the FOOT: its own collector is the one it abuts - the feeder at the
    # head, the drain at the foot - and THAT carries the crossings, with one plank on each toe. The
    # first cut here gave both toes two and the feeder none, which satisfied
    # `long_ditches_have_a_footbridge` and put every plank 350-1,100 ft from the houses while the
    # canal directly behind the north dike had none (settlement-review, Kuwabata 2026-08-28: "the
    # crossings are where the CHECK wanted them, not where the feet are"). The research the rule
    # rests on - people cross where they LIVE - applies to whichever collector that is.
    if f["cluster"] == f["head"]:
        return {"feeder": 3, "drain": 0, "e_toe": 1, "w_toe": 1, "lateral": 1}
    # ...EXCEPT THAT A DRAIN TAKES NO PLANK (feature 287, ways W14 and the WAYS law's `plank_on_supply`: a footplank stands on
    # a supply ditch - research 0084, archetypes/110). The village at the FOOT abuts the drain, which the law refuses a
    # plank, so its crossings go on the supply ditches that reach it - the two toe collectors (role `lateral`) run down to
    # the foot, two a side - and none is asked of the drain that `channel_footbridges` would refuse.
    return {"feeder": 0, "drain": 0, "e_toe": 2, "w_toe": 2, "lateral": 1}
