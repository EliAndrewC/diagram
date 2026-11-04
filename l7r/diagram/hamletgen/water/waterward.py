"""THE POLDER ARCHETYPES - the reclaimed block, its dike, its flanks and the reed fringe outside them.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.

Research: polder geometry - NONE: grid search, flank letters, binning and intersection plumbing
"""

from __future__ import annotations

from ..consts import Pt
from ..plan import SitePlan

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
    """Which flanks of the dike face the fluctuating water it was reclaimed from - the Rust's own derivation
    (`rust/phases/src/waterward.rs` `flanks`, feature 444 T29), the one the fringe is drawn on, asked here for the stages that read
    the flanks too, never derived a second time.

    Research: waterward flanks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: every flank but the landward one holds water back; a reed fringe along the low foot where the outfall drains and along the cross flank off the shore, the wild pond that feeds the polder at its head - its water drawn there as the pond, so no reed strip is laid off the head
    """
    from ..phases_ext import phases

    out = plan.seat.get("out") if plan.seat else None
    return list(phases().water_flanks(plan.fall, (float(out[0]), float(out[1])) if out else None))


def polder_crossing_caps(plan: SitePlan) -> dict[str, int]:
    """Where plank crossings go on a polder's ring canal (a reading of 2026-07-22, a GUESS): people cross to the fields where they LIVE and then walk the bund network,
    so crossings CLUSTER on the collector the village abuts, and every other supply collector, whose both ends reach the
    fields, keeps one. On a FLANK: three on the settlement-side toe, one on each interior lateral, the feeder and the far
    toe, none on the drain (the interior laterals are the Rust polder's `column` ditches). At the HEAD: three on the feeder, one on each toe. At the FOOT: two on each toe, one on the
    feeder and none on the drain. `build_polder` names the +cross collector `e_toe` and the other
    `w_toe`; which is the settlement side is read off the seat, not assumed. (A valley hamlet such as the reference has
    no polder: this and the dike gates draw nothing there.)

    Research:
        no plank on the drain - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: none over the drain at the field's foot
        crossings wherever both ends are useful - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a crossing stands wherever both ends reach useful ground, a walked dike included, and a long ditch takes a crossing near its middle, a very long one several - every supply collector counted by its length (`channel_footbridges`' spacing), the drain capped at none
        at most three where the village lives - GUESS: research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html silent on crossings clustering by the village; the village's own collector capped at three (two a toe at the foot), so its planks stand near the houses rather than strung along it
    """
    f = polder_flanks(plan)
    if f["cluster"] == f["plus"]:
        return {"drain": 0, "e_toe": 3}
    if f["cluster"] == f["minus"]:
        return {"drain": 0, "w_toe": 3}
    # The village at the HEAD or the FOOT: its own collector is the one it abuts - the feeder at the
    # head, the drain at the foot - and THAT carries the crossings, with one plank on each toe. The
    # first cut here gave both toes two and the feeder none, which satisfied
    # `long_ditches_have_a_footbridge` and put every plank 350-1,100 ft from the houses while the
    # canal directly behind the north dike had none (settlement-review, Kuwabata 2026-08-28: "the
    # crossings are where the CHECK wanted them, not where the feet are"). The research the rule
    # rests on - people cross where they LIVE - applies to whichever collector that is.
    if f["cluster"] == f["head"]:
        return {"feeder": 3, "drain": 0}
    # ...EXCEPT THAT A DRAIN TAKES NO PLANK (feature 287, ways W14 and the WAYS law's `plank_on_supply`: a footplank stands on
    # a supply ditch - research 0084, archetypes/110). The village at the FOOT abuts the drain, which the law refuses a
    # plank, so its crossings go on the supply ditches that reach it - the two toe collectors (role `lateral`) run down to
    # the foot, two a side - and none is asked of the drain that `channel_footbridges` would refuse.
    return {"drain": 0, "e_toe": 2, "w_toe": 2}
