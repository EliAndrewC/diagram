"""The channel widths the field's drawing reads - the taper law, the ditch widths in pixels, when a ditch takes a plank - and the
segment helpers the banks use (the Python field engine this was the frame of was deleted by feature 444 T16).

Research: frame geometry - NONE: segment predicates and a ring's signed area
"""

import math

from l7r.diagram.work_counts import OPS

Pt = tuple[float, float]  # an (x, y) point in map pixels
Poly = list[Pt]  # a polyline / polygon as a list of points

GAP = 26.0  # threads never pinch closer than this - a plot must fit between them
"""Research: least spacing between ditch threads - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: the maps set no least width for a basin, the hamlet basin about 48 ft across its canal - a 26 px floor between threads sets a least column width, a departure the code keeps until feature 417 T34; 26 px"""
# A FIX THAT FAILED (feature 328 wave 85, 2026-10-09): 0005's basin is some 40 to 60 ft across its ditch, so the floor was
# derived from it - `plot_across` (48 px) and 40/48 of it - and passed into `_comb_march`. Every comb hamlet moved and the
# 48-seed cohort went 48 -> 45 and 48 -> 44 (Kashikawa refused by its lane web at the 40 ft floor). Reverted; the row is E3,
# its work the seeds that broke (m:wave85-thread-floor-reverted; the patch is in the spec's audit/reverted/).

DRAIN_FT = (1.2, 5.5)  # the akusui, mirrored: a thread at its head, full at the outfall. Drainage
# EXCEEDS supply at the outfall (it passes drawdown plus storm, not just the irrigation duty), which
# is why the drain's tail is wider than the head-race that fed the same ground.
"""Research: drain width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html, research/questions/0060-field-drains-akusuiro.drawing.html: 1.2 ft at its head gathering to 5.5 at the outfall"""


# THE VISIBILITY FLOOR, and the one place map SCALE enters the ladder. True widths are honest at
# hamlet/village resolution (1-2 ft/px) and vanish above it: at a provincial city's 3 ft/px the
# terminal tier is 0.4 px, i.e. not a line at all. So a stroke is drawn at its true width or this
# floor, whichever is larger - the coarser the sheet, the more of the ladder collapses onto it,
# which is the honest form of the "minimum-visibility floor" the stroke convention in
# `../../../research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html` already sanctions.
#
# 1.5, AND 1.2 WAS TRIED AND REVERTED (2026-08-17) - the number is load-bearing on the carve, not
# just on legibility. `settlement-review` noted that 1.5 COLLIDES with `aze_w`, which at hamlet grain
# is also exactly 1.5 px: the finest water tier is drawn at precisely the paddy bund's stroke width
# and separated from the brown lattice it runs among only by hue. 1.2 fixes that and is also truer
# (1.2 ft IS the field-ditch tier, ~0.3-0.37 m, so at hamlet scale the floor would bind on nothing).
#
# But the floor feeds `supply_bank_clearance`, so lowering it moves every bund that hems a supply
# stroke, and `close_seams` then welds a different set of scraps. Measured on the 24-seed cohort,
# with the change isolated by reverting this line alone: **1.2 costs seeds 19 and 22 to
# `paddy_plot_seams_shared` (22/24 -> 20/24); at 1.5 they pass.** A cosmetic ambiguity is not worth
# two broken maps, so the collision stands as recorded-and-accepted rather than fixed.
#
# IF IT IS EVER WORTH CLOSING, the lever is the OTHER side: `AZE_FT` is 1.5 by its own research
# (a plain aze ran ~1-2 ft), so there is room to take the BUND to 1.3 and leave the water alone -
# which changes only a stroke width and touches no clearance. That was not attempted here.
MIN_CHANNEL_PX = 1.5
"""Research: visibility floor - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: no stroke drawn under 1.5 px, 1.5 ft on a hamlet map"""


# A FARMER STEPS OVER A DITCH THIS NARROW RATHER THAN DECKING IT (settlement-review 2026-08-17).
# The footplank rule used to be about LENGTH only - any ditch over ~140 px got a plank about midway -
# which was harmless while the net was 5-6x oversize and absurd the moment it went to true size:
# eight of Inashiro's fifteen planks were decking water 1.7-2.3 ft wide, with 3-4 ft abutments each
# side. A plank bridge is a real object a household builds and maintains; nobody builds one over
# something they can stride across.
#
# WHERE THE LINE SITS: 2.0 ft = 2 shaku (~60 cm), the attested width of the traditional farm-level
# ditch (GM ruling 2026-08-26, feature 133 T11). It first stood at 3.0 ft - "about a stride", a
# session's own judgment - which landed in the gap the measured pool leaves (deliveries 1.8-2.5 ft,
# supply canals 3.0-4.5) and so decked the canals only. The GM, looking at the reference hamlet,
# asked why the delivery ditches had no planks; the research pass found the traditional 小用水路 at
# 2 shaku and the record SILENT on whether a ditch of that width was planked or stepped, so the GM
# ruled on the map: they are not too narrow. At 2.0 the standard farm ditch earns a board and only
# the ~1.2-1.5 ft tails are stepped over. Full record: research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html.
FOOTPLANK_MIN_FT = 2.0
"""Research: water worth a plank - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: 2 ft or more"""


def worth_planking(w_px: float, w_tail_px: float, ftpx: float) -> bool:
    """Is this ditch wide enough anywhere to be worth a plank rather than a stride?

    ONE predicate, called by the placer (`channel_footbridges`) and by the gate
    (`long_ditches_have_a_footbridge`), because a ditch the placer declines to deck and the check
    still demands a deck on is the classic disagreement this engine keeps rediscovering.

    TWO SCOPES, and both are needed. Pass the ditch's HEAD and TAIL and this answers "is this ditch
    worth a crossing ANYWHERE" - which is the question the gate asks, since it demands one plank per
    long ditch. Pass the same value twice and it answers "is the water wide enough HERE", which is
    what the placer must ask at each candidate seat: a tapering run can qualify on its head and still
    put a board over 2.4 ft if the seat is chosen by arc fraction alone, which is what shipped and
    what a review caught (2026-08-17). The placer now tests both - the ditch to decide whether to
    look at all, then each seat as it slides - so the board lands where the water earns it.

    Research: planked only over water too wide to step - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the widest drawn width at least FOOTPLANK_MIN_FT
    """
    return max(w_px, w_tail_px) * ftpx >= FOOTPLANK_MIN_FT


def chan_px(ft: float, grain: float) -> float:
    """A channel's DRAWN width in pixels, from its true width in feet.

    `grain` is defined as `2 / ftpx` (see `carve_comb`'s docstring and `hamletgen.consts.GRAIN`), so
    `ft * grain / 2` is `ft / ftpx` - the true width in pixels at this map's scale. Written through
    grain rather than taking `ftpx` directly because grain is what every caller already threads
    down, and inventing a second scale parameter is how the two drift apart.

    The floor is applied to each END of a taper independently, because it is a floor on the DRAWN
    stroke, not on the taper: a run whose true head clears the floor and whose true tail does not
    should still narrow, just less far than the truth would take it.

    Research: true width or the floor - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: feet at the map's scale, floored at MIN_CHANNEL_PX
    """
    return max(MIN_CHANNEL_PX, ft * grain / 2.0)


def taper_w(w0: float, w1: float, t: float) -> float:
    """The drawn width of a tapering channel a fraction `t` along its run (0 = head, 1 = tail).

    THE WIDTH SQUARED IS WHAT RUNS LINEARLY, not the width - because a channel's width goes as the
    SQUARE ROOT of the discharge it carries, and the discharge is what changes linearly along one of
    these runs. (why: `../../../research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.html`)

    Both halves of that are load-bearing, so neither is a free choice:

      - *Width goes as sqrt(Q).* This is the regime relation the water-width ladder in
        `../../../research/contents.json#water` has always asserted ("channel width scales with the square-root of
        the command-area flow it carries"), and it is Lacey's canal result, P = 4.75 * sqrt(Q) - the
        standard design equation for exactly this kind of unlined earthen channel.
      - *Q runs linearly.* A delivery ditch sheds its water through a `mizuguchi` per plot into a row
        of near-equal paddies, so it loses roughly the same flow per unit length; a collector gathers
        its tail-water the same way. Uniform shedding over the run IS Q linear in `t`.

    Interpolating the WIDTH linearly - which is what every one of these call sites used to do -
    quietly asserts Q proportional to w, a different and wrong law, and it looks wrong in the way the
    GM caught (2026-08-17): the stroke thins almost imperceptibly for its whole length and then stops
    dead at a still-substantial width. Under the true law a delivery ditch holds most of its working
    width while it still has most of its water to deliver, then dwindles hard over the last stretch -
    which is what "the water is leaving it" is supposed to look like.

    THAT PROFILE IS DATA, NOT A VISIBLE GRADIENT, and saying so is part of the rule. Since the net
    went to true size a delivery ditch sheds one pixel over five hundred (0.20 px per 100 px, against
    0.93 before), so the shape below is correct and unreadable at once. The GM asked directly, was
    given x1.5 and x2 legibility multipliers with the gradients priced, and chose true size
    (2026-08-17). Do NOT widen these strokes to make the taper show - the numbers and the reasoning
    are in `../../../research/questions/0069-how-our-maps-draw-a-channel-narrowing-along-its-run.drawing.html`.

    **THE WORKED EXAMPLE LIVES IN A TEST, NOT HERE** -
    `test_the_delivery_taper_holds_then_dwindles` asserts the SHAPE this paragraph promises (wider
    than a straight line at every interior point; more of the drop in the back half than the front;
    the floor reached only at the tail) against the shipped tier constants. That is deliberate and
    it is the third attempt at this paragraph. Twice it carried magnitudes in prose and twice they
    went false without anything failing: first the formula's numbers while `field_channel` was still
    sampling by vertex index, so the real ink was 4.6 px at mid-run; then a re-measured set that the
    true-size ladder invalidated the same day, leaving this docstring describing 8.0 -> 3.0 ft
    ditches on a map whose ditches are 2.5 -> 1.2. **A number in a docstring is not falsifiable by
    any gate; a number in a test is.** So state the shape here, assert it there, and if you need a
    magnitude, measure the SVG - never compute it from the rule this docstring is describing.

    `taper_pieces` in `banks.py` carries the arc-parameterization half of the story, and the bound
    between its piecewise ink and the continuous law the bank clearances evaluate.

    NOT a taper to nothing: `w1` is a real tier, not zero. See the same research anchor for why the
    finest channel we DRAW stops at the terminal-lateral width instead of vanishing to a point.

    ONE helper, called by every site that needs a local width - the drawn stroke, the two bank
    clearances the gate shares, the seam buffer, the carve's burial filter, and the channel keep-out
    corridor. A taper law re-derived per call site is the "one measurement, not several" trap in the
    diagram CLAUDE.md: the bunds are laid against the bank this returns and the checks read the same
    number, so two formulas here means a bund drawn inside the water.

    Research: square-root taper - research/questions/0069-how-our-maps-draw-a-channel-narrowing-along-its-run.drawing.html: the width squared runs linearly along the run
    """
    return math.sqrt(max(0.0, w0 * w0 + (w1 * w1 - w0 * w0) * t))


def _seg_x(a: Pt, b: Pt, c: Pt, d: Pt) -> Pt | None:
    r = (b[0] - a[0], b[1] - a[1])
    s = (d[0] - c[0], d[1] - c[1])
    den = r[0] * s[1] - r[1] * s[0]
    if abs(den) < 1e-9:
        return None
    t = ((c[0] - a[0]) * s[1] - (c[1] - a[1]) * s[0]) / den
    u = ((c[0] - a[0]) * r[1] - (c[1] - a[1]) * r[0]) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (a[0] + t * r[0], a[1] + t * r[1])
    return None


BANK_MARGIN = 0.75  # half a drawn bund stroke (aze_w is ~1.5 real ft), so bund and ditch ABUT rather than overlap
"""Research: bund and ditch abut - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: half a bund's width past the stroke's edge"""


def _seg_d(px: float, py: float, a: Pt, b: Pt) -> float:
    """Distance from a point to a segment (the same arithmetic several passes nest as a local
    `sd`; module-level here because _bund_beans' burial filter needs it too)."""
    if __debug__:
        OPS["dist@_seg_d"] += 1  # the counted work (feature 443): dropped under `python -O`
    vx, vy = b[0] - a[0], b[1] - a[1]
    ll = vx * vx + vy * vy or 1.0
    t = max(0.0, min(1.0, ((px - a[0]) * vx + (py - a[1]) * vy) / ll))
    return math.hypot(px - a[0] - t * vx, py - a[1] - t * vy)


def _signed_area(poly: Poly) -> float:
    """Shoelace WITH its sign - the sign is the diagnosis. Every basin the carve lays comes out
    positively wound; one that comes back negative has had its two boundaries cross, so what is
    drawn is a bowtie, not a field. See the inverted-toe drop in `carve_comb`."""
    s = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        s += x0 * y1 - x1 * y0
    return s / 2
