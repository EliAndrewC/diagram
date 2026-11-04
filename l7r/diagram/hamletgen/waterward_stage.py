"""STAGE 4c - the waterward fringe, in Rust (feature 444 T29): a thin Python function that hands the Rust a polder's dike rings and
notches, the fall and the seat's back, calls `l7r_phases.stage_waterward`, and draws the reed strip it returns on each water-facing
flank, declares the flanks, and reserves the sty's seat - before the houses and the track, so both treat the strip as wet ground.

Research:
    the fringe's seam - NONE: the stage's plumbing; each rule's claim is at the Rust that decides it (`rust/phases/src/waterward.rs`)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from l7r.diagram import work_counts
from l7r.diagram.settlement.land.dikes import DIKE_GAP_HW

from .consts import POLDER_ARCHETYPES, WATERWARD_DEPTH
from .phases_ext import phases
from .pondstock import reserve_sty_seat

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from .plan import SitePlan


def stage_waterward(s: Settlement, plan: SitePlan) -> None:
    """The reed fringe along every water-facing flank of a polder dike, and its declaration - laid in Rust, drawn here; nothing on
    a valley hamlet.

    Steps:
        l7r.diagram.settlement.Settlement.marsh
        l7r.diagram.hamletgen.pondstock.reserve_sty_seat

    Research:
        the strip drawn - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a marsh strip off each water-facing flank, drawn as the waterside marsh
        strip depth - CONVENTION: WATERWARD_DEPTH outlasts any crop, the strip running off the frame
        a notch through the whole band - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the band cut where a channel crosses, the strip stepping in by the band's widest"""
    if plan.field_archetype not in POLDER_ARCHETYPES or not s.M.get("dikes"):
        return
    dikes = [([(float(p[0]), float(p[1])) for p in dk.get("outline") or []], [(float(g[0]), float(g[1])) for g in dk.get("gaps") or []]) for dk in s.M["dikes"]]
    cut = max(float(dk.get("w_max", 0.0)) for dk in s.M["dikes"])
    out = plan.seat.get("out") if plan.seat else None
    got = phases().stage_waterward(dikes, cut, DIKE_GAP_HW, WATERWARD_DEPTH, (float(s.W), float(s.H)), plan.fall, (float(out[0]), float(out[1])) if out else None)
    for k, n in (got.get("counts") or {}).items():
        work_counts.OPS[k] += n
    for strip in got["strips"]:
        s.marsh([(float(x), float(y)) for x, y in strip], role="waterside")
    s.meta(waterward=list(got["flanks"]))
    # ...AND THE STY'S SEAT, the other ground a dike-pond hamlet decides once the flank is known and before the houses stand
    # (feature 287, water W50): a re-seat by `seat_every_household` keeps to this flank, so nothing here is redrawn for it
    reserve_sty_seat(s, plan)
