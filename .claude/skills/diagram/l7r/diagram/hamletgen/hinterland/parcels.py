"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist

from ..consts import Poly, Pt
from ..plan import SitePlan
from .frame import content_box, title_pocket

CROP_MARGIN = 48.0  # the one crop margin, shared by stage_frame's crop_to_content call and the
# predicted-kept-window math in open_ground_patches - two hardcoded 48s would drift

# How much of a woodland parcel's ROTATED bbox must fall inside the predicted kept window for the
# scan to seat it. Module-level so the attribution census can drive it - a floor buried in a closure
# cannot be measured against, and this one had to be measured twice before it was right.
#
# 0.72 sits 2 points above `woodland_commons_within_the_frame`'s own 0.7, which is all the cushion
# the prediction needs: instrumenting cohort seed 33 showed the window is byte-identical at all 16
# `_crop_boxes` calls of a build AND equal to the final `meta.view`, because everything that sets the
# frame is placed before the woodland scan runs. The neighboring square test's 0.8 exists for drift
# that measurement says does not happen; carrying 0.8 over to the rotated bbox cost seed 33 its
# woodland outright. See future-work/, "the woodland scan vetted a SQUARE".
WOODLAND_BBOX_FLOOR = 0.72

_COMMONS_REACH = 1.49
"""How much further a rotated parcel reaches than the equal-AREA square, worst case.

`open_ground_patches` rolls an aspect up to 2.2:1 while holding area, so the long half-axis grows by
sqrt(2.2) = 1.483 and the short one shrinks to match. Every keep-out test is done at this reach, so
a parcel that rotates cannot end up nearer a crop, a lane or the marsh than the square it replaced -
rotating a footprint must never buy ground the square could not have had."""

_COMMONS_FLOOR_FT = 120.0
"""The smallest square a woodland COMMONS may be drawn as, in feet.

Not a historical minimum - `research/fields.md` is clear that coppice lots were "whatever odd corner
the village spared", and there is no attested floor. This is a LEGIBILITY floor, and it exists
because the size-variance machinery above can compound its way under one: a per-map ladder scale
times a per-parcel band multiplier took Kashikawa to 103 ft. The number is our own recorded
judgment - when the first (shrink-only) size roll produced a 116 ft parcel on Mizuguchi the reading
was "a copse, not a commons", which is what made the roll two-sided - so 120 ft is just above the
size we have already said does not read. A settlement whose ground genuinely cannot hold one draws
FEWER parcels rather than smaller ones."""


def parcel_bbox_ok(x: float, y: float, hw: float, hh: float, bc: float, bs: float, frame: tuple[float, float, float, float]) -> bool:
    """Does a ROTATED parcel keep enough of its own bbox inside the frame? The check's own rule.

    ROTATING A BOX GROWS ITS AXIS-ALIGNED BBOX - by up to sqrt(2), at 45 degrees, even for a square -
    and `woodland_commons_within_the_frame` measures that grown bbox. Testing the unrotated square
    instead let a seat pass the ladder at 0.8 and draw a parcel 0.67 inside the window, which is what
    cohort seed 33 did the moment the cluster change walked it to the edge: a check and the thing it
    checks measuring different quantities.

    `WOODLAND_BBOX_FLOOR` is 0.72, NOT the 0.8 the square test uses, and the difference is measured
    rather than taste. The 0.8 elsewhere buys slack because that window is called a PREDICTION of the
    crop - but instrumenting seed 33 showed the window is byte-identical at all 16 `_crop_boxes` calls
    across the build AND equal to the final `meta.view`, because everything that sets the frame is
    already placed when the woodland scan runs. The prediction does not drift, so paying 10 points of
    slack for drift that does not happen just deletes coppices: at 0.8 on the rotated bbox seed 33 lost
    its woodland outright, a worse map than the 67%-clipped parcel this rule set out to stop. 0.72
    keeps a 2-point cushion over the gate for float ordering.

    Lifted out of `open_ground_patches` so it can be asked with plain numbers (GM 2026-08-28).
    """
    fx0, fy0, fx1, fy1 = frame
    bw, bh = abs(hw * bc) + abs(hh * bs), abs(hw * bs) + abs(hh * bc)
    inside = max(0.0, min(x + bw, fx1) - max(x - bw, fx0)) * max(0.0, min(y + bh, fy1) - max(y - bh, fy0))
    return inside >= WOODLAND_BBOX_FLOOR * (2.0 * bw) * (2.0 * bh)


def fit_square_parcel(half: float, floor_half: float, fits: Any) -> float | None:
    """Shrink a square parcel down the ladder until it fits, or return None.

    SHRINK BEFORE DROPPING - the same principle as the outer aspect ladder, applied to the rotated
    bbox. A seat whose square will not fit the window is usually a seat near the edge that a slightly
    smaller square clears, and a smaller coppice on the sheet beats a larger one the crop cuts off.
    Only when even the floor-sized parcel fails is the seat genuinely unusable.

    The floor is a FLOOR, not a rung: every rung is clamped up to it, so a parcel already at the
    minimum is offered once rather than shrunk below the size at which a commons is still legible.

    Lifted out of `open_ground_patches` (GM 2026-08-28). Feature 147 parked its two lines behind a
    coverage pragma while the floor's verdict on them flickered; feature 149 found the cause - an
    entry's stored coverage outliving the key it was recorded under - and the park came off. This is
    what should have happened instead of the park: the ladder is a decision about numbers, and it can
    be asked about numbers.
    """
    for sh in (0.9, 0.8, 0.7, 0.6):
        cand = max(half * sh, floor_half)
        if fits(cand):
            return cand
    return None


def open_ground_patches(s: Settlement, plan: SitePlan, count: int, size: float = 250.0) -> list[Poly]:
    """Find `count` patches of ground still open enough for a managed woodland - by SCANNING.

    Woodland (coppice, bamboo, tung-oil - the "economic forest") is a few discrete patches on the
    higher, farther ground, set back from the sun-needing crops by the scrub between. Ikegami places
    three by hand. The script cannot hand-place, so it scans a coarse lattice over the canvas and
    scores each candidate square on the two things that actually decide the answer:

      - it must be CLEAR of the crops by a real margin, and clear by MORE on the crop's sunny side,
        because a canopy south of a field shades it (this mirrors `woodland_clear_of_crops`, whose
        set-back is bigger to the south for exactly that reason);
      - it must be clear of the settlement, its lanes, its grove and its water.

    Among the candidates that qualify it prefers the ones furthest from the crop and highest up the
    slope, and it keeps them apart from each other so three patches read as three woods rather than
    one ragged mass. This is the stage that most obviously could not be done by pinning coordinates:
    "where is there still room" is a question about the map as it stands at that moment."""
    dx, dy = plan.fall
    keep: list[tuple[float, float, float]] = []  # (x, y, radius) of everything to stay clear of
    for h in s.M.get("houses", []):
        keep.append((h["x"], h["y"], 150.0))
    for wl in s.M.get("wells", []):
        keep.append((wl["x"], wl["y"], 90.0))
    pond = s.M.get("pond")
    if pond:
        keep.append((pond[0], pond[1], max(pond[2], pond[3]) + 120.0))
    lanes: list[tuple[Poly, float]] = [(ln["pts"], 70.0) for ln in s.M.get("lanes", [])]
    # THE COPPICE IS A DISTINCT WOOD from the fengshui grove, and must not merge into it
    # (`woodland_clear_of_grove`, which measures to each grove CLUMP, not to the belt outline - so a
    # patch merely touching the belt's edge already fails). Both groves count: the windbreak belt
    # behind the cluster, and the copse scattered through the gaps among the houses, whose footprint
    # is the house bbox. The margin is generous because a clump's drawn canopy overhangs its
    # recorded radius, and because two woods that nearly touch read as one ragged mass anyway.
    # Kept clear by RECTANGLE, not by a circle around the bounding box. A belt is a long thin band
    # and a cluster is usually longer than it is deep, so a circle sized to the LONG side leaves the
    # short side hugely over-reserved while a circle sized any tighter under-covers the ends - and
    # the ends are exactly where a patch slips in and merges with the grove.
    keep_rects: list[tuple[float, float, float, float]] = [title_pocket(s, plan)]
    if plan.belt:
        keep_rects.append((min(p[0] for p in plan.belt) - 110.0, min(p[1] for p in plan.belt) - 110.0, max(p[0] for p in plan.belt) + 110.0, max(p[1] for p in plan.belt) + 110.0))
    hxs = [h["x"] for h in s.M.get("houses", [])]
    hys = [h["y"] for h in s.M.get("houses", [])]
    if hxs:  # the copse's ground, which is the house cloud
        keep_rects.append((min(hxs) - 110.0, min(hys) - 110.0, max(hxs) + 110.0, max(hys) + 110.0))
    streams: list[tuple[Poly, float]] = [(st["poly"], 60.0) for st in s.M.get("streams", [])]
    # ...AND THE MARSH IS NOT OPEN GROUND (settlement-review x3, 2026-08-16: the kept-window
    # confinement pushed parcels onto the wet toe - Inashiro seated one 100% inside the marsh
    # with zero crowns, Sawada 97%, Mizuguchi ~60%; the crown filter refuses wet ground, so a
    # wet seat renders as a claimed woodland with almost no trees). "Still open" is not "dry":
    # a candidate square must keep every sample point out of every recorded marsh poly.
    # `woodland_commons_on_dry_ground` gates the result.
    marshes: list[Poly] = [[(float(v[0]), float(v[1])) for v in mp.get("poly") or []] for mp in s.M.get("marshes", [])]
    marshes = [mp for mp in marshes if len(mp) >= 3]

    def _wet(x: float, y: float, half_: float) -> bool:
        return any(point_in_poly(x + ddx * half_, y + ddy * half_, mp) for mp in marshes for ddx in (-1.0, 0.0, 1.0) for ddy in (-1.0, 0.0, 1.0))

    crops: list[Poly] = [list(plan.envelope)] + [[(float(v[0]), float(v[1])) for v in d["poly"]] for d in s.M.get("dry_plots", [])]
    _hx = [h["x"] for h in s.M.get("houses", [])] or [plan.W / 2]
    _hy = [h["y"] for h in s.M.get("houses", [])] or [plan.H / 2]
    ccx, ccy = sum(_hx) / len(_hx), sum(_hy) / len(_hy)

    # THE PATCHES MUST NOT STRETCH THE FRAME. `crop_to_content` frames the map to its HARD features,
    # and a woodland patch is one - so a patch parked in a far corner of the working canvas drags the
    # crop out with it, leaving a band of empty scrub on one side and (worse) putting the map edge
    # beyond the reach of the drain brook, which then no longer runs off the frame. That is three
    # gate failures from one badly-sited wood: `crop_not_held_open_by_one_feature`,
    # `stream_runs_off_edge` and `stream_end_anchored`. So the scan is confined to the ground the
    # map already occupies, expanded by a margin - a coppice stands on the settlement's own high
    # ground, not a quarter mile out in nowhere.
    cbx0, cby0, cbx1, cby1 = content_box(s, plan, pad=210.0)
    step = 90.0

    # ...AND CONFINED TO THE PREDICTED KEPT WINDOW (known-open ledger 2026-08-16, Sawada: two of
    # three parcels wholly above the frame, the third half-cropped under the title; Kashikawa and
    # Mizuguchi the same shape). The commons never set the frame (crop_to_content: woods bleed at
    # the edge), so a parcel the keep-outs push past the future crop simply vanishes from the
    # sheet. The decision, over "let the crop admit them": the frame stays tight to the working
    # settlement - the documented reason commons do not set the frame at all - and a coppice is
    # walked-to-daily ground that belongs ON the sheet, so it is the coppice that moves. The
    # window is computed from the SAME source the crop will read (`_crop_boxes` -> hull + the
    # shared CROP_MARGIN), and at this stage it is final except for features that only GROW it -
    # so a parcel held inside it now is inside the kept view later.
    # `woodland_commons_within_the_frame` gates the result.
    _cb = s._crop_boxes(city=False)
    _cx = [v for b in _cb for v in (b[0], b[1])] or [0.0, plan.W]
    _cy = [v for b in _cb for v in (b[2], b[3])] or [0.0, plan.H]
    _fx0, _fy0 = max(0.0, min(_cx) - CROP_MARGIN), max(0.0, min(_cy) - CROP_MARGIN)
    _fx1, _fy1 = min(plan.W, max(_cx) + CROP_MARGIN), min(plan.H, max(_cy) + CROP_MARGIN)

    chosen: list[Poly] = []
    centers: list[tuple[float, float, float]] = []  # (x, y, this parcel's OWN exclusion radius - see the stride roll)
    # THE LADDER ITSELF IS ROLLED PER MAP (settlement-review x2, 2026-08-18). The shrink ladder's
    # rungs were the same four numbers on every map, so every tight composition fell to the SAME
    # bottom rung and produced the same wood: Kashikawa shipped a 121.7 ft stand with 18 crowns and
    # Sawada a 127.2 ft stand with 19 - two different hamlets, effectively one wood, and the
    # per-parcel size roll could not separate them because it only spans +/-15% of a rung they
    # SHARED. Scaling the whole ladder by a per-map factor moves the rungs themselves apart, so two
    # tight maps land on different sizes before the per-parcel roll even runs.
    _ladder = 0.90 + 0.20 * s._hjit(plan.W, plan.H, 76.0)
    # ...AND THE PARCEL SIZES ARE STRATIFIED, one per band, rather than drawn independently. A
    # continuous roll clusters near its own middle, which is exactly the reading being fixed:
    # Mizuguchi's four came out 292 / 294 / 290 / 269 ft - three of them inside 1.4% of each other,
    # perceptually one wood drawn three times, from a roll that was already +/-18% wide. Independent
    # draws will keep doing that (with four samples a near-tie somewhere is the NORMAL outcome, not
    # bad luck), so each accepted parcel instead TAKES a band and removes it from the pool: with
    # four parcels the multipliers are 0.865 / 0.955 / 1.045 / 1.135 and no two woods can land
    # within 9% of each other. Which parcel gets which band is still rolled from its own position,
    # so the sizes are not ordered by seating order.
    _bands = list(range(max(2, count)))
    # SHRINK BEFORE GIVING UP (settlement-review round 2, 2026-08-16): with the kept window and
    # the marsh both closed to it, a tight composition can offer no full-size seat at all - the
    # first dry pass seated ZERO parcels on Kashikawa, the map NAMED for its oaks. A smaller
    # woodlot (200 ft, then 160 ft) is historically ordinary - coppice lots were whatever odd
    # corner the village spared - while an absent one on a name-story map is not. Unfilled slots
    # re-scan at the smaller sizes; a slot no size can seat is honestly dropped.
    # ...AND THE SET-BACK RELAXES BEFORE THE MAP GOES WOODLESS (Kashikawa round 3, 2026-08-16:
    # after the wells realigned, the generous 80/180 px crop set-backs plus the marsh closed the
    # whole kept window at every rung - zero parcels on the map NAMED for its oaks). The scan's
    # defaults are deliberately far above the gate's own floors (`woodland_clear_of_crops`:
    # CLEAR 14 px overhang, SHADE 69 px sunny-side at 1 ft/px), so a second pass at 40/100 px
    # still clears them - and the satoyama mosaic genuinely puts the woodlot on the margin
    # beside the field. ONE trap, found by the 48-seed sweep (Audit-24): `_clear_gap` measures
    # center-to-crop minus HALF, which overstates the true polygon gap by up to 0.414*half when
    # the crop lies diagonal to the square - the generous profile absorbed that slack, the
    # relaxed one shipped a parcel the check called shading. So the relaxed thresholds carry
    # the diagonal slack EXPLICITLY, per parcel size (the measured-gap floor then implies a
    # true-gap floor of 40/100, both above the check's 14/69). The generous profile always runs
    # first, so a roomy composition is byte-identical; only one that would otherwise draw NO
    # woodland tightens.
    for _sb_normal, _sb_sunny in ((80.0, 180.0), (40.0, 100.0)):
        if len(chosen) >= count:
            break
        for size_try in (size * _ladder, size * 0.8 * _ladder, size * 0.64 * _ladder, size * 0.5 * _ladder):
            if len(chosen) >= count:
                break
            # A RUNG UNDER THE LEGIBILITY FLOOR IS NOT OFFERED AT ALL. The first cut clamped each
            # candidate up to the floor and then dropped the parcel when the clamped size did not
            # fit, which needed a fall-through nobody could reach in a test; skipping the rung says
            # the same thing in one line and leaves `half_used = half` unconditionally safe, because
            # every rung that survives to the accept block is already above the floor. Either way a
            # settlement whose ground cannot hold a legible commons draws FEWER, never smaller.
            if size_try < _COMMONS_FLOOR_FT:
                continue
            half = size_try / 2.0
            _sb_pad = 0.415 * half if _sb_normal < 80.0 else 0.0  # the diagonal slack (see above); the generous profile keeps its historical thresholds exactly
            _sb_n, _sb_s = _sb_normal + _sb_pad, _sb_sunny + _sb_pad
            # MIRROR THE CHECK'S WINDOW, NOT JUST ITS FORMULA (2026-08-18). The kept-window
            # confinement above and `woodland_commons_within_the_frame` are meant to be the same
            # rule, and they were not: the check asks for **70% of the parcel's bbox** inside the
            # view and says in as many words that a parcel clipping at the edge "reads as 'more wood
            # that way' and is fine", while the scan demanded the whole square inside the window
            # plus a further 16 px. Being stricter than your own gate sounds safe and is not - it
            # cost two of the four hamlets their woodland outright. Measured before the fix: at
            # EVERY rung of the shrink ladder and BOTH set-back profiles, Kashikawa - the map named
            # 樫川, "oak river" - had ZERO qualifying seats out of a 231-286 point lattice and Sawada
            # exactly one, with the crop clause alone refusing 93-97% and the best achievable
            # clearance NEGATIVE (the square overlapped a paddy). Neither the shrink ladder nor the
            # set-back relaxation, both added FOR Kashikawa, could ever have worked: the binding
            # constraint was never the set-back, it was that a 20-household hamlet's field fills its
            # own frame and the scan would not let a wood touch the edge of it.
            #
            # So the seat is judged the way the check judges it, by AREA. The center may now sit up
            # to 0.6*half outside the kept window and the exact bbox-overlap fraction is tested in
            # `_ok` - which is what makes the both-axes corner case safe, where a per-axis box test
            # would pass two 0.4*half overhangs at 0.64 inside and ship a check failure. The floor
            # is 0.8 rather than the check's 0.7 because this window is a PREDICTION of the crop:
            # the margin absorbs the features that may still grow it.
            sx0, sy0 = max(cbx0 + 16.0, _fx0 - 0.6 * half), max(cby0 + 16.0, _fy0 - 0.6 * half)
            sx1, sy1 = min(cbx1 - 16.0, _fx1 + 0.6 * half), min(cby1 - 16.0, _fy1 + 0.6 * half)

            # THE QUALIFICATION IS ONE PREDICATE, so a seat can be re-asked after it is nudged. It
            # used to be an inline `if` that only the lattice scan could evaluate, which is why the
            # jitter below could not exist: there was no way to check that a moved seat was still
            # legal. Same shape as every other "placement and its check read one source" fix here.
            def _ok(
                x: float,
                y: float,
                half: float = half,
                n: float = _sb_n,
                sn: float = _sb_s,
                sx0: float = sx0,
                sy0: float = sy0,
                sx1: float = sx1,
                sy1: float = sy1,
            ) -> bool:
                # ONE guard clause, deliberately: the window bounds and the kept-window AREA are the
                # same question asked of a seat that may have been MOVED since the scan offered it
                # (the jitter and the size roll both re-ask). Split into two statements the bounds
                # half is unreachable in the corpus - no pool map or cohort seed happens to jitter a
                # seat past the edge - and an untested line in a predicate whose whole job is
                # re-asking is exactly what rots.
                if (
                    not (max(half + 40.0, sx0) <= x <= min(plan.W - half - 40.0, sx1) and max(half + 40.0, sy0) <= y <= min(plan.H - half - 40.0, sy1))
                    or (max(0.0, min(x + half, _fx1) - max(x - half, _fx0)) * max(0.0, min(y + half, _fy1) - max(y - half, _fy0))) < 0.8 * (2.0 * half) ** 2
                ):
                    return False  # off the window, or under the check's own 70%-of-bbox rule (0.8 here, for prediction slack)
                return (
                    _clear_gap((x, y), half, crops, dy, n, sn) is not None
                    and not any(math.hypot(x - kx, y - ky) < kr + half for kx, ky, kr in keep)
                    and not any(rx0 - half < x < rx1 + half and ry0 - half < y < ry1 + half for rx0, ry0, rx1, ry1 in keep_rects)
                    and not any(_near_line((x, y), half, pts, pad) for pts, pad in lanes + streams)
                    and not _wet(x, y, half)
                )

            scored: list[tuple[float, float, float]] = []
            y = max(half + 40.0, sy0)
            while y <= min(plan.H - half - 40.0, sy1):
                x = max(half + 40.0, sx0)
                while x <= min(plan.W - half - 40.0, sx1):
                    if _ok(x, y):
                        # PREFER THE NEAREST QUALIFYING GROUND, leaning upslope. The first version of this
                        # maximized distance from the crop instead, which sounds right and is wrong twice
                        # over: it drove every patch to the canvas's far upslope margin, where the dedupe
                        # radius strung them out along one line at identical height, and then the crop -
                        # which frames to the HARD features and lets commons bleed off-frame - cut three of
                        # the four off the sheet entirely. A settlement's coppice is walked to daily for
                        # fuel and fodder; it stands on the back slope behind the houses, as close as the
                        # crop set-back allows. The keep-outs above are what make it far ENOUGH.
                        upslope = -((x - ccx) * dx + (y - ccy) * dy)
                        scored.append((-math.hypot(x - ccx, y - ccy) + 0.35 * upslope, x, y))
                    x += step
                y += step
            # THE COPPICE IS A HILLSIDE WOOD, SO A DOWN-SLOPE-DOMINANT SEAT LOSES TO A CROSS-SLOPE ONE
            # (settlement-review, Kashikawa 2026-08-18 round 2, and its research pass settled the
            # ruling this ledger item was waiting for). Three project files say woodland goes on the
            # higher, farther ground - `settlements/vegetation.md`, `research/fields.md` and this
            # function's own scorer comment - and Kashikawa drew both its stands downslope, one of them
            # 886 ft down and 75 ft off the reed marsh: a coppice walking onto the wet toe of the fan.
            # The scorer's additive `+0.35 * upslope` never binds, because a 90 px step toward the
            # cluster outbids 257 px of height.
            #
            # THE RULING, and why it is neither of the two options I ledgered. Raising the weight until
            # it binds returns this map to ZERO parcels - the defect closed that morning - and a knob
            # was not available either: the reviewer's research pass found satoyama DEFINED as the
            # foothill border zone with its coppice on the hillsides, and the China-first analog (the
            # fengshui back-hill wood) upslope as well, so a downslope commons is not a co-equal
            # attested form and "correct the prose instead" would mean rewriting doctrine to match a
            # placement artifact. What the record does support is weaker than "uphill of the houses":
            # the wood is ON THE HILLSIDE, i.e. at or above the settlement's own contour. So the test
            # is the along/cross RATIO, not the height. Decomposed on Kashikawa, that refuses the
            # down-dominant parcel (886 ft down against 276 cross) and keeps the cross-dominant one
            # (505 down against 1562 cross, effectively a contour seat) - one parcel, not zero.
            #
            # A PREFERENCE, not a filter, per this scan's standing habit: if no cross-slope seat
            # qualifies at all, the down-slope ones are still offered rather than leaving a map
            # woodless. The GM can reverse this ruling; it is recorded in `future-work/`.
            _cross_seats = [t for t in scored if abs((t[1] - ccx) * -dy + (t[2] - ccy) * dx) >= ((t[1] - ccx) * dx + (t[2] - ccy) * dy)]
            if _cross_seats:
                scored = _cross_seats
            for _, x, y in sorted(scored, reverse=True):
                if len(chosen) >= count:
                    break
                if any(math.hypot(x - cx0, y - cy0) < _ex0 for cx0, cy0, _ex0 in centers):
                    continue
                # OFF THE LATTICE, AND NOT ALL ONE SIZE (settlement-review, Mizuguchi 2026-08-18).
                # The scan samples a uniform 90 px lattice, scores every seat by one monotone
                # function (near the cluster, leaning upslope) and then takes the best remaining seat
                # outside a FIXED separation radius. Those three together do not merely tend to
                # produce an even chain - they produce one by construction, and Mizuguchi shipped the
                # proof: three identical 250 x 250 ft squares at (456,967), (726,697), (996,427),
                # offsets of exactly (+270,-270) and (+270,-270), reading as three stamps of one wood
                # marching up a ruled diagonal. The fourth parcel, seated off the ladder at a
                # different size, reads fine and is the control.
                #
                # So the LATTICE is a sampling artifact and must not survive into the output. The
                # accepted seat is nudged up to half a step off it and the parcel's size rolled down
                # by up to a fifth, both from `_hjit` - positional, so a map is unchanged by
                # regeneration and two maps differ from each other. Every nudge is re-asked through
                # `_ok`, and a nudge that would not qualify is simply not taken: this can only move a
                # legal seat to another legal seat, never widen what the scan admits.
                # VARY THE STRIDE, NOT JUST THE SEAT (settlement-review x2, 2026-08-18 - the FIRST
                # version of this fix did not work and this is why). Jittering the accepted seat off
                # the lattice killed the identical-STAMP reading, and left the CHAIN: Mizuguchi still
                # stepped 379.7 ft then 361.9 ft up one axis with the middle parcel 3.1% off the
                # straight line, and Inashiro independently stepped 366 / 371 / 392 ft. Measured, and
                # the cause is not the lattice at all - it is that a MONOTONE score plus a FIXED
                # `size * 1.5` exclusion radius means each parcel is by construction the nearest
                # qualifying seat just outside the last one's circle, so the stride is pinned at
                # ~375 ft however the seats are dithered. A +/-45 px jitter is +/-12% of that stride:
                # far too small to break a rhythm it does not touch. So each parcel now carries its
                # OWN exclusion radius, rolled 1.15x-2.50x its size from its own position, and the
                # spacing varies because the generative rule varies rather than because the output
                # is dithered.
                jx = x + (s._hjit(x, y, 71.0) - 0.5) * step
                jy = y + (s._hjit(x, y, 72.0) - 0.5) * step
                # ...and the size roll is wider than it was, for the reason recorded at `_ladder`:
                # +/-15% of a shared rung left two maps' stands 1.8% apart. This is a DEGREE on a
                # continuum (calibrated liberty), not a knob - `settlements/vegetation.md` already
                # says coppice lots were "whatever odd corner the village spared", so a narrow roll
                # was narrower than our own doctrine.
                # TRY THE MIRRORED SIZE BEFORE FALLING BACK TO THE RUNG. Widening the roll upward
                # made it WORSE at first, in a way only the artifact showed: a grown parcel often
                # fails `_ok` (it is asking for ground the rung already fitted snugly), the ladder
                # fell straight back to `half`, and Mizuguchi shipped three parcels at 292 / 294 /
                # 290 ft - the exact rung, three times, more identical than before the roll existed.
                # Reflecting the factor about 1.0 gives a distinctly SMALLER parcel to try before
                # surrendering to the rung, so a refused growth becomes variety instead of a twin.
                _bi = min(int(s._hjit(x, y, 73.0) * len(_bands)), len(_bands) - 1) if _bands else 0
                _f = 0.82 + 0.36 * (((_bands[_bi] if _bands else 0) + 0.5) / max(2, count))
                # The band first; then one distinctly SMALLER try, because a grown parcel is asking
                # for ground the rung only just fitted and the plain fallback to `half` is what
                # produced the near-identical trio above.
                # ...BUT NEVER BELOW A COMMONS' OWN FLOOR. The band multipliers compound with the
                # per-map ladder, and at the ladder's bottom rung that took Kashikawa's smaller
                # parcel to 103 ft - under the ~116 ft that THIS change already judged "a copse, not
                # a commons" when it made the size roll two-sided. A floor is the honest guard: a
                # parcel too small to read as a managed wood should not be drawn smaller to satisfy
                # a variance rule. If the floor does not fit, the rung fallback still applies, so
                # this can only ever make a parcel larger or leave it alone.
                half_used = half  # the rung: the scan already tested this seat at REACH, so the rotated parcel fits
                # the reach a rotated parcel needs is its circumscribing half - a 2.2:1 parcel of the
                # same AREA reaches sqrt(2.2) further along its long axis than the square did, so the
                # candidate is tested at that reach and the rotation cannot buy ground.
                for _cand in (max(half * _f, _COMMONS_FLOOR_FT / 2.0), max(half * 0.84, _COMMONS_FLOOR_FT / 2.0)):
                    if _ok(jx, jy, _cand):
                        x, y, half_used = jx, jy, _cand
                        break
                    if _ok(x, y, _cand):
                        half_used = _cand
                        break
                # THE FLOOR WAS NOT A FLOOR (settlement-review, Kashikawa 2026-08-18 round 2). Both
                # candidates are clamped to `_COMMONS_FLOOR_FT`, but when neither fitted, control fell
                # through to `half_used = half` - the UNCLAMPED rung - and Kashikawa shipped a 116.6 ft
                # parcel, under the floor, at the very size this file's own docstring calls "a copse,
                # not a commons". The comment above claimed the clamp "can only ever make a parcel
                # larger or leave it alone" and the fall-through did the one thing it forbade.
                #
                # The rung is now only taken if the rung itself clears the floor; otherwise the parcel
                # is DROPPED, which is what `_COMMONS_FLOOR_FT`'s docstring says should happen - "a
                # settlement whose ground genuinely cannot hold one draws FEWER parcels rather than
                # smaller ones". The band is returned to the pool by not popping it until acceptance,
                # so a dropped parcel does not silently consume a size band the next one could use.
                if _bands:
                    _bands.pop(_bi)
                # ...AND IT IS NOT A SQUARE (settlement-review x2, 2026-08-18 round 2). Every woodland
                # parcel the engine had ever drawn was `rot: 0` with `w == h` - 12 of 12 across the
                # four hamlets - and the reviewers' point was that the size work made this MORE
                # conspicuous, not less: four identical squares read as one repeated stamp, but four
                # differently-sized perfect squares read as a lattice with a size knob bolted on,
                # because the varying dimension proves the constant one was a choice.
                #
                # The record is decisive rather than two-sided, so this is calibrated liberty and not
                # a knob between forms: *iriai* commons boundaries were customary and described by
                # ridge, stream and path (UNSOURCED - read under T46, 2026-08-27: the cited Yamaguni
                # study says nothing about boundaries; see research/vegetation.md), and satoyama
                # coppice sits on the slope break - there is no attested rectilinear woodlot. Aspect and bearing therefore roll per parcel from its
                # own position, AREA HELD (hw*hh is unchanged, so every size rule above still means
                # what it says), and the bearing is taken off the fall line because a hillside wood
                # runs with the contour rather than with the page.
                #
                # The keep-out tests keep using the CIRCUMSCRIBING half, so a rotated parcel clears
                # everything a square of the same reach would have: rotating a footprint must not be
                # able to buy ground the square could not have had.
                # THE ASPECT ADAPTS TO THE ROOM, it does not demand it. Testing every seat at the
                # worst-case circumscribing reach was the first cut and it was far too strict: it
                # left Kashikawa - the oak map - woodless again, undoing the morning's fix, because
                # that map's ground is genuinely tight and a 1.49x reach requirement refuses nearly
                # all of it. So the rolled aspect is a TARGET, stepped down to whatever this seat
                # actually supports, with the square as the floor. A roomy seat gets a long wood, a
                # tight one still gets its square, and no map loses a parcel to the shape roll.
                # The ladder steps DOWN from the rolled target toward the square. The first cut wrote
                # the rungs as literals (target, 1.6, 1.3) and so could step UP - a seat that rolled
                # 1.2 was then offered 1.6, a LONGER parcel than the roll asked for - and it needed a
                # guard clause to stop that, which was itself unreachable. Scaling the rolled excess
                # says what was meant in one expression: at the last rung the excess is 45% of the
                # roll, and if even that will not fit the square always does, because the seat was
                # accepted at exactly this half.
                # THE LADDER MUST VET THE SHAPE THAT GETS DRAWN, NOT A SQUARE STAND-IN FOR IT
                # (2026-08-19). `_ok` tests an axis-aligned square of the LONG half, which sounds
                # conservative and is not: the parcel is drawn as a rotated rectangle, and rotating a
                # box GROWS its axis-aligned bbox - by up to sqrt(2), at 45 degrees, even for a
                # square. `woodland_commons_within_the_frame` measures that bbox. So a seat could
                # pass the ladder at 0.8 of a square and draw a parcel 0.67 inside the window, which
                # is exactly what cohort seed 33 did the moment the cluster change walked it to the
                # edge: a check and the thing it checks measuring different quantities, the same
                # defect as the drawn-vs-band aspect confusion in `CLUSTER_DRAWN_ASPECT`.
                #
                # The bearing is therefore computed BEFORE the ladder (it never depended on the
                # aspect - only on the fall direction and the seat), and each rung is tested on the
                # true rotated bbox. The line this replaced carried the comment "the scan already
                # tested this seat at REACH, so the rotated parcel fits", which was an assumption
                # stated as a fact; it is now the thing being checked.
                _bear = math.radians(math.degrees(math.atan2(dy, dx)) + 90.0 + 40.0 * (s._hjit(x, y, 78.0) - 0.5))
                _bc, _bs = math.cos(_bear), math.sin(_bear)  # not `_cb` - that name is the crop-boxes list above

                def _bbox_ok(hw: float, hh: float, x: float = x, y: float = y, _bc: float = _bc, _bs: float = _bs) -> bool:
                    """This seat's rotated-bbox test - see `parcel_bbox_ok`, which holds the body."""
                    return parcel_bbox_ok(x, y, hw, hh, _bc, _bs, (_fx0, _fy0, _fx1, _fy1))

                _excess = 1.2 * s._hjit(x, y, 77.0)
                _asp = 0.0  # 0.0 means "no rung fitted" - distinct from the square, which is 1.0
                for _step in (1.0, 0.72, 0.45, 0.0):
                    _try = 1.0 + _excess * _step
                    if _ok(x, y, half_used * math.sqrt(_try)) and _bbox_ok(half_used * math.sqrt(_try), half_used / math.sqrt(_try)):
                        _asp = _try
                        break
                if not _asp:
                    # SHRINK BEFORE DROPPING - see `fit_square_parcel`, which holds the ladder and is
                    # unit-tested over plain numbers. Written as one expression rather than an `if`
                    # on purpose: the DECISION is tested in that function, so a separate branch here
                    # is plumbing that only a real site can execute, and pinning a cohort member to
                    # execute it is what made `test_woodland_shrink_147` rot twice (features 147 and
                    # 149) before it was re-aimed a third time.
                    _cand_half = fit_square_parcel(half_used, _COMMONS_FLOOR_FT / 2.0, lambda _h, _x=x, _y=y: _ok(_x, _y, _h) and _bbox_ok(_h, _h))
                    half_used, _asp = (_cand_half, 1.0) if _cand_half is not None else (half_used, _asp)
                if not _asp:
                    # Nothing fits. Drop the parcel rather than draw one the crop will cut off: a
                    # settlement whose ground cannot hold a legible commons draws FEWER, never one
                    # that is half off the sheet.
                    #
                    # The size band popped above is NOT put back. Restoring it would mean pushing
                    # `_bi` - an INDEX into a list that has since been mutated - back as a VALUE,
                    # which silently corrupts the size distribution; and a consumed band costs only a
                    # little size variety on a map that just declined to seat a parcel anyway.
                    continue
                _hw, _hh = half_used * math.sqrt(_asp), half_used / math.sqrt(_asp)
                chosen.append(_parcel_outline(s, x, y, _hw, _hh, _bc, _bs))
                centers.append((x, y, size * (1.15 + 1.35 * s._hjit(x, y, 74.0))))
    return chosen


def _parcel_outline(s: Settlement, x: float, y: float, hw: float, hh: float, bc: float, bs: float, n: int = 12) -> Poly:
    """A coppice parcel's outline: an IRREGULAR ring inside the rolled ellipse, never a rectangle.

    THE RESEARCHED RULING WAS ONLY HALF DRAWN (GM 2026-08-27, feature 133 T36: *"those coppice
    Patches. basically it looked like little squares ... I want to make sure that that is intentional
    and based on research rather than just happenstance"*). It was happenstance. The 2026-08-18
    review pass had already found the record decisive - *iriai* commons boundaries were customary and
    "described by ridge, stream and path", satoyama coppice sits on the slope break, and there is no
    attested rectilinear woodlot - and implemented it as a ROTATED RECTANGLE with the plain square as
    the fallback for a tight seat. A rotated rectangle is still rectilinear, and on Inashiro all three
    parcels took the fallback: `rot 0`, `w == h`, twelve of twelve across the pool before that. So the
    outline is now what the ruling says: a ring that follows no page axis, its radius wandering the
    way a boundary that runs "by ridge, stream and path" does.

    Built INSIDE the tested reach, on purpose. Every keep-out test in `open_ground_patches` was made
    at the ellipse's circumscribing half, so a vertex that never leaves the ellipse can never buy
    ground the square could not have had. The radius runs 0.80-1.00 of the ellipse's, on two low
    harmonics seeded from the parcel's own position (`_hjit`), so the ring is smooth rather than
    spiky - a wood's edge wanders, it does not serrate - and the AREA comes out at ~85% of the
    ellipse's: the size rules above still bound it, from above. Recorded in research/vegetation.md
    "How is a coppice lot bounded?", with the one form deliberately NOT drawn here: the strip
    holdings of a shinden dry-upland village, which are a settlement form, not a woodlot knob."""
    p1, p2 = 2 * math.pi * s._hjit(x, y, 79.0), 2 * math.pi * s._hjit(x, y, 80.0)
    ring: Poly = []
    for i in range(n):
        t = 2 * math.pi * (i + 0.35 * (s._hjit(x + i, y, 81.0) - 0.5)) / n
        re = hw * hh / math.hypot(hh * math.cos(t), hw * math.sin(t))
        f = 0.80 + 0.20 * (0.5 + 0.25 * math.sin(2 * t + p1) + 0.25 * math.sin(3 * t + p2))
        lx, ly = re * f * math.cos(t), re * f * math.sin(t)
        ring.append((x + lx * bc - ly * bs, y + lx * bs + ly * bc))
    return ring


def _clear_gap(center: Pt, half: float, crops: Sequence[Poly], fall_y: float, normal: float = 80.0, sunny: float = 180.0) -> float | None:
    """Distance from a candidate square to the nearest crop, or None if it is too close.

    The set-back is 80 px normally and 180 px when the square sits on the crop's SUNNY side (south,
    in screen terms) - the shading case. `woodland_clear_of_crops` uses 1 : 2.5-ish set-backs for the
    same reason; this is deliberately a little more generous than the check, so a patch that passes
    here passes there with room to spare rather than sitting on the line."""
    cx, cy = center
    best = 1e9
    for crop in crops:
        d = min(seg_dist(cx, cy, crop[i], crop[(i + 1) % len(crop)]) for i in range(len(crop))) - half
        if point_in_poly(cx, cy, list(crop)):
            return None
        south_of = cy - half > max(p[1] for p in crop) - 40 and min(p[0] for p in crop) - half < cx < max(p[0] for p in crop) + half
        if d < (sunny if south_of else normal):
            return None
        best = min(best, d)
    return None if best >= 1e9 else best


def _near_line(center: Pt, half: float, pts: Sequence[Pt], pad: float) -> bool:
    cx, cy = center
    return any(seg_dist(cx, cy, pts[i], pts[i + 1]) < half + pad for i in range(len(pts) - 1))
