"""STAGE 4b - the dry hem, in Rust (feature 444 T28): a thin Python function that hands the Rust what the field left for the hem and
the settlement's ground the seat chose, calls `l7r_phases.stage_hem`, and writes the dry plots it returns - their records, the
no-build registries, the plan's net and their ink - after the seat, so the houses stand between the paddy's canal and the dry
fields where the settlement stands on the paddy's high edge (0006; the round arbiter on ask:444-T27-seat-hem).

Research:
    the hem's seam - NONE: the stage's plumbing; each rule's claim is at the Rust that decides it (`rust/phases/src/hem.rs`, `field/dry.rs`)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from l7r.diagram import work_counts
from l7r.diagram.settlement.fields import ink

from .consts import SQ_FT_PER_ACRE, Pt
from .field_stage import _area, dry_records
from .phases_ext import phases

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from .plan import SitePlan

BELT_FAR_FT = 146.0
"""How far behind the band's far edge the settlement's ground reaches (feet): the shelter belt's far edge - its near face 36 ft behind
the cluster's fringe and its 110 ft depth, as the seat asks its room (`rust/phases/src/seat/margins.rs` `BELT_BAND`).

Research:
    belt's depth - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: a back wood drawn 80 to 120 ft deep, a convention; 110 ft
    belt's distance behind the fringe - GUESS: no page gives it; the near face 36 ft behind the cluster's fringe"""

STANDOFF_FT = 12.0
"""The band's standoff out from the field's margin (feet), as the seat sets it.

Research: seat standoff from the field - GUESS research/questions/0029-farmhouses-minka.drawing.html: our maps draw farmhouses 10 to 13 ft from the paddy, a figure the page builds from guesses; 12 ft"""


def settlement_ground(seat: dict[str, Any]) -> list[Pt]:
    """The ground the seat chose for the settlement and its belt: from the field's margin out past the band and the belt behind it,
    the band's length along the margin - the ground the dry hem keeps off.

    Research:
        the settlement's ground - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the houses between the canal and the dry fields where the settlement stands, the dry fields behind it
        the belt's ground kept - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a clustered village shelters behind one belt at its windward edge, so the belt's ground is the settlement's too and the hem stands behind it; 0006 says nothing of a belt between the houses and the dry fields"""
    (ax, ay), (ox, oy), (lx, ly) = seat["anchor"], seat["out"], seat["along"]
    lat, deep = float(seat["lat"]), STANDOFF_FT + 2.0 * float(seat["dep"]) + BELT_FAR_FT
    return [(ax - lx * lat, ay - ly * lat), (ax + lx * lat, ay + ly * lat), (ax + lx * lat + ox * deep, ay + ly * lat + oy * deep), (ax - lx * lat + ox * deep, ay - ly * lat + oy * deep)]


def stage_hem(s: Settlement, plan: SitePlan) -> None:
    """The dry hem laid behind the settlement and along the canal elsewhere, in Rust, and written here: its records, the no-build
    registries (`dry_polys`, `block_polys`), the plan's net and the grain figures on the title card, and its ink. A field with no hem
    (the polder) lays none.

    Steps:
        l7r.diagram.settlement.fields.ink.dry_plots

    Research:
        the dry plots' records - NONE: written from the Rust's, as the field wrote them before T28
        the coarse grain - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: the grain drawn and the room left, beside the need the field set"""
    h = plan.hem_in
    if not h:
        return
    keep = [settlement_ground(plan.seat)] if plan.seat else []
    out = phases().stage_hem(
        [(float(x), float(y)) for x, y in h["line"]],
        tuple(h["out"]),
        tuple(h["down"]),
        tuple(h["bounds"]),
        int(h["seed"]),
        [(float(x), float(y)) for x, y in h["ring"]],
        [((float(a[0]), float(a[1])), (float(b[0]), float(b[1])), float(w)) for a, b, w in h["water"]],
        keep,
    )
    for k, n in (out.get("counts") or {}).items():
        work_counts.OPS[k] += n
    dry = dry_records(out["dry"], h["field"])
    s.M.setdefault("dry_plots", []).extend({k: d[k] for k in ("poly", "crop", "theta", "tract")} for d in dry)
    for d in dry:
        s.dry_polys.append(d["poly"])
        s.block_polys.append(d["poly"])
    plan.net.setdefault("dry_plots", []).extend(dry)
    plan.net["dry_acres"] = sum(_area(d["poly"]) for d in plan.net["dry_plots"]) / SQ_FT_PER_ACRE
    drawn, room = out["grain"]
    s.M["meta"]["coarse_grain_dry_acres"] = round(drawn, 2)
    s.M["meta"]["coarse_grain_room_acres"] = round(room, 2)
    if __debug__:
        work_counts.OPS["write@hem_ink"] += sum(len(d["poly"]) for d in dry)
    ink.dry_plots(s, {"dry_plots": dry})
