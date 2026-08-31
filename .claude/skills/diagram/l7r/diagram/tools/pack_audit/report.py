"""Split from tools/pack_audit.py by feature 173 - see this package's CLAUDE.md for the index."""

import sys

from .checks import (
    TUB_MAX_GAP_FT,
    aligned_gaps,
    dark_on_dark_labels,
    fire_water_adrift,
    floating_doors,
    gap_tag,
    notice_board_adrift,
    occluded_foreground,
    orphan_group_labels,
    overlapping_labels,
    passage_blockers,
    structures_on_walls,
    tubs_in_buildings,
    tubs_on_wells,
    wall_openings,
)
from .grids import FTPX, _grids, perimeter_hugging_pct, region_density, top_vacant_rects
from .parse import ParsedPlan, parse_svg


def format_report(plan: ParsedPlan, cell: int = 2) -> str:
    """Human-readable packing report (the CLI prints this; pure so it is testable)."""
    g = _grids(plan, cell)
    inside = built = openc = empty = 0
    for gy in range(g.h):
        for gx in range(g.w):
            if not g.inside[gy][gx]:
                continue
            inside += 1
            if g.building[gy][gx]:
                built += 1
            elif g.occ[gy][gx]:
                openc += 1
            else:
                empty += 1
    minx, miny, maxx, maxy = plan.bounds
    hug = perimeter_hugging_pct(plan, cell=cell)
    lines = [
        f"walled interior: {(maxx - minx) / FTPX:.0f} x {(maxy - miny) / FTPX:.0f} ft = {inside * cell * cell / (FTPX * FTPX):,.0f} sqft",
        f"building coverage: {100 * built / inside:.0f}%  (jin'ya band 37-42%)",
        f"purposeful open (garden/court/glyphs): {100 * openc / inside:.0f}%  (features)",
        f"bare open ground: {100 * empty / inside:.0f}%  (courts are open - not a defect alone)",
        f"perimeter-hugging: {100 * hug:.0f}% of building footprint within 25 ft of a wall  (high = buildings ring the courts)",
        "top vacant rectangles (largest first - CENTRAL=courtyard/feature, PERIMETER=ring gap/slack):",
    ]
    tv = top_vacant_rects(plan, n=4, cell=cell)
    if not tv:
        lines.append("    (none above the floor area)")
    lines += [f"    {v.w_ft:.0f} x {v.h_ft:.0f} ft = {v.area_sqft:,.0f} sqft [{v.orient}, {v.zone}] at svg({v.x:.0f},{v.y:.0f})" for v in tv]
    lines.append("per-region density (a large low-coverage tile = consolidation candidate):")
    lines += [f"    tile[r{t.row}c{t.col}]: {100 * t.coverage_pct:.0f}% built  ({t.interior_sqft:,.0f} sqft interior)" for t in region_density(plan, cell=cell)]
    lines.append("aligned building gaps 5-30 ft (kura fire-gap OK ~10 ft; wooden >8 ft loose):")
    gaps = aligned_gaps(plan)
    if not gaps:
        lines.append("    (none in the 5-30 ft range)")
    lines += [f"    {gp.ft:.1f} ft  {gp.orient}  at svg({gp.mx:.0f},{gp.my:.0f})   {gap_tag(gp)}" for gp in gaps[:12]]
    lines.append(f"fire-water tubs adrift (a gutter-fed tub must sit <={TUB_MAX_GAP_FT:.0f} ft from a building):")
    if not plan.tubs:
        lines.append("    (no fire-water tubs in this plan)")
    else:
        adrift = fire_water_adrift(plan)
        intruding = tubs_in_buildings(plan)
        if not adrift and not intruding:
            lines.append(f"    (all {len(plan.tubs)} tubs sit outside, clear of every building)")
        lines += [f"    tub at svg({t.x:.0f},{t.y:.0f}) is {t.gap_ft:.1f} ft from the nearest building - move it to a wall/eaves" for t in adrift]
        lines += [
            f"    TUB IN BUILDING: a fire-water tub at svg({t.x:.0f},{t.y:.0f}) reaches {t.into_ft:.1f} ft INTO a building - a tensuioke is gutter-fed and bucket-served, so move it OUT clear of the wall"
            for t in intruding
        ]
    lines.append("LAYER/LABEL checks:")
    occ = occluded_foreground(plan)
    if not occ:
        lines.append("    labels/tubs on top: OK (nothing buried under a later feature)")
    lines += [f"    BURIED: {o.kind} {(repr(o.text) + ' ') if o.text else ''}at svg({o.x:.0f},{o.y:.0f}) is under a feature drawn later - move it to the top layer" for o in occ]
    for orp in orphan_group_labels(plan):
        lines.append(f"    ORPHAN LABEL: {orp.text!r} at svg({orp.x:.0f},{orp.y:.0f}) is {orp.gap_ft:.1f} ft from the nearest glyph it names - move it beside one")
    for bd in notice_board_adrift(plan):
        lines.append(f"    NOTICE BOARD: at svg({bd.x:.0f},{bd.y:.0f}) is {bd.gap_ft:.1f} ft from the nearest gate opening - move it to a gate")
    for dk in dark_on_dark_labels(plan):
        fix = f"nudge ({dk.nudge_dx_ft:+.0f},{dk.nudge_dy_ft:+.0f}) ft clears it" if dk.fixable else "no small nudge clears it - relocate"
        lines.append(f"    DARK-ON-DARK: {dk.text!r} at svg({dk.x:.0f},{dk.y:.0f}) - black ink over a dark feature; {fix}")
    for cl in overlapping_labels(plan):
        lines.append(f"    LABEL CLASH: {cl.a!r} and {cl.b!r} overlap at svg({cl.x:.0f},{cl.y:.0f}) - move one apart")
    for dr in floating_doors(plan):
        lines.append(f"    DOOR ADRIFT: a door at svg({dr.x:.0f},{dr.y:.0f}) floats {dr.gap_ft:.1f} ft inside the building - set it on the wall")
    for tw in tubs_on_wells(plan):
        lines.append(f"    TUB ON WELL: a fire-water tub at svg({tw.x:.0f},{tw.y:.0f}) overlaps a well - move it to a different eaves corner")
    lines.append("GATE OPENINGS (compound wall, measured from the INK - a square cap eats 1.5 ft per end):")
    openings = wall_openings(plan)
    if not openings:
        lines.append("    (no openings found in the compound wall)")
    lines += [f"    {o.ft:5.1f} ft  at svg({o.x:.0f},{o.y:.0f})   compare with the width this opening's comment claims" for o in openings]
    blocked = passage_blockers(plan)
    if blocked:
        lines.append("PASSAGE check (a gateway's track stays clear - stones and posts flank it, they never stand in it):")
        lines += [
            f"    IN THE PASSAGE: a {b.w_ft:.1f} x {b.h_ft:.1f} ft object at svg({b.x:.0f},{b.y:.0f}) stands in a {b.opening_ft:.1f} ft opening - "
            "move it clear of the road (a threshold stone flanks the passage, above ground)"
            for b in blocked
        ]
    else:
        lines.append("PASSAGE check: every gateway's track is clear: OK")
    lines.append("STRUCTURE/WALL check (a structure abuts a wall, never stands in it):")
    if not plan.wall_bands:
        lines.append("    (no wall strokes in this plan)")
    else:
        onwall = structures_on_walls(plan)
        if not onwall:
            lines.append(f"    all {len(plan.structures)} structures clear the wall ink: OK")
        lines += [
            f"    ON WALL: a {sw.w_ft:.0f} x {sw.h_ft:.0f} ft structure at svg({sw.x:.0f},{sw.y:.0f}) reaches {sw.into_ft:.1f} ft into the {sw.wall} - "
            "set it against the wall's inner face, or break the wall around it if it IS part of the wall"
            for sw in onwall
        ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python3 -m l7r.diagram.tools.pack_audit <compound.svg> [more.svg ...]", file=sys.stderr)
        return 2
    for path in args:
        with open(path, encoding="utf-8") as fh:
            plan = parse_svg(fh.read())
        print(f"=== {path.split('/')[-1]} ===")
        print(format_report(plan))
        print()
    return 0
