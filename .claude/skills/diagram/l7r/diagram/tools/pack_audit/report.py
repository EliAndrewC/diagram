"""Split from tools/pack_audit.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import os
import re
import sys

from ...buildings.types import BuildingType, by_tier, tiers
from .checks import TUB_MAX_GAP_FT, aligned_gaps, fire_water_adrift, gap_tag, tubs_in_buildings, wall_openings
from .grids import FTPX, _grids, perimeter_hugging_pct, region_density, top_vacant_rects
from .parse import ParsedPlan, parse_svg
from .registry import Context, run_checks


def format_report(plan: ParsedPlan, cell: int = 2, text: str = "", tier: str | None = None, btype: BuildingType | None = None, form: str | None = None) -> str:
    """Human-readable packing report (the CLI prints this; pure so it is testable).

    `text` is the sheet's source (the crop check reads it), `tier` the sheet's declared type (None: the
    shared layer only), `btype` and `form` what the program checks read (feature 254)."""
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
        f"building coverage: {100 * built / inside:.0f}%  (a jin'ya runs ~33-42% built: Takayama's floor to the record's band)",
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
    lines.append("GATE OPENINGS (compound wall, measured from the INK - a square cap eats 1.5 ft per end):")
    openings = wall_openings(plan)
    if not openings:
        lines.append("    (no openings found in the compound wall)")
    lines += [f"    {o.ft:5.1f} ft  at svg({o.x:.0f},{o.y:.0f})   compare with the width this opening's comment claims" for o in openings]
    lines += check_lines(Context(plan, text, btype, form), tier)
    return "\n".join(lines)


_FORM_RE = re.compile(r"^\*\*Form\*\*:\s*([^\n]+?)\s*$", re.M)


def read_form(svg_path: str) -> str | None:
    """The `**Form**: ...` line of the sheet's notes file (`<stem>.notes.md` beside it), or None."""
    notes = svg_path[: -len(".svg")] + ".notes.md" if svg_path.endswith(".svg") else ""
    if not notes or not os.path.isfile(notes):
        return None
    with open(notes, encoding="utf-8") as fh:
        m = _FORM_RE.search(fh.read())
    return m.group(1).strip() if m else None


def check_lines(ctx: Context, tier: str | None) -> list[str]:
    """The REGISTERED checks (feature 254): each applicable check in registry order, its findings or OK.

    The report used to compose these by hand, one block per check, which is how the tub check gained
    a fill list its docstring contradicted (2026-07-25). Now the registry is the one list: a check
    the sweep runs is a check the report prints, with the same fix sentence."""
    lines = [f"CHECKS ({'shared layer only' if tier is None else 'shared layer + ' + tier}):"]
    for ch, found in run_checks(ctx, tier):
        if not found:
            lines.append(f"    {ch.name}: OK")
            continue
        lines += [f"    {ch.name.upper()}: {f} - {ch.fix}" for f in found]
    return lines


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python3 -m l7r.diagram.tools.pack_audit <compound.svg> [more.svg ...]", file=sys.stderr)
        return 2
    for path in args:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        plan = parse_svg(text)
        # the sheet's type is its pool tier when the folder above its own is a declared one (feature 254)
        tier = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(path))))
        tier = tier if tier in tiers() else None
        print(f"=== {path.split('/')[-1]} ===")
        print(format_report(plan, text=text, tier=tier, btype=by_tier(tier) if tier else None, form=read_form(path)))
        print()
    return 0
