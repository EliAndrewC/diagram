"""The checks feature 254 added: three for every Mode A sheet, three for the magistracy alone.

The GM's own example of a shared check was "whether different shapes end up overlapping with each
other"; the spec (254 FR-002) adds the scale bar and the viewBox crop to the shared layer, and names
the coverage band, perimeter hugging and two-court zoning as the magistracy's (FR-003). Each one here
is a pure function of a `ParsedPlan` returning finding strings; `registry.py` gives each its types,
its red fixture and its fix sentence.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

from .checks import WALL_OVERLAP_MIN_PX, wall_openings
from .grids import FTPX, coverage, perimeter_hugging_pct
from .parse import COURT_FLOORS, WALL_STROKE, ParsedPlan, Rect
from .tagged import marks

# A structure may CONTAIN another (an engawa strip on a residence, a door, a room) and two blocks of
# one building may join by a corridor that laps a few px into each - those are compositions, not
# accidents. An accident is a substantial lap: more than this share of the smaller footprint, with
# neither rect inside the other. Tuned on the five pool sheets (2026-09-19): the largest legitimate
# lap on them is a joining corridor's end.
OVERLAP_SHARE: float = 0.30
"""Research: building overlap share - NONE: an overlap over 0.30 of the smaller footprint is an accident, a tolerance tuned on the pool sheets."""
# The coverage band: the record's "~37-42%" (research/contents.json#compounds, the packing entry) is the page's
# own measurement of jin'ya plans with no readable source, and the same entry gives Takayama at ~33%
# built (1,000 of 3,000 tsubo) as a figure that rests on no page read. Both are the page's own; the
# FLOOR was that 33 (30 since feature 372 wave 105, below) and the ceiling the page's 42 with two points for a rule written with a tilde. Hayakawa ships at 35% with every building at its
# size-audited footprint (the audit of 2026-07 shrank four laundered sizes AFTER the entry called it
# 37-38%): inside the attested spread, so the exact 37 was the check's defect, not the sheet's
# (feature 254 T06/T08, plan D9); the entry's stale sentence is corrected in the same work.
# FEATURE 372 WAVE 105: the floor follows 0116's drawing page as corrected on 2026-10-01 - about 30-42%, the bottom the one
# office measured (Takayama's floors ~31% of its site); the 33 above was read off the entry before that correction.
COVERAGE_FLOOR: float = 0.30
"""Research: building coverage floor - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: a compound's buildings cover about 30-42% of its walled ground; the bottom, 30%, is near Takayama's ~31% of floor against site."""
COVERAGE_CEILING: float = 0.42
"""Research: building coverage ceiling - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the top of the 30-42% coverage range, 42%, is the project's estimate from plans, which the page records as a guess."""
COVERAGE_TOL: float = 0.02
"""Research: coverage tolerance - GUESS: two points either side of the band, for the page's "about" 30-42%; no page gives the slack."""
# The hugging floor is DERIVED, not typed from a source: the five pool sheets measure 51-58% of
# building footprint within 25 ft of a wall (m:hugging-floor, feature 254), and one building pulled
# into the center of a court costs about six points, so the floor sits one such building under the
# lowest shipped value. Nothing read gives a historical figure for it; the ring is the composition
# rule (docs/buildings.md, "Composition"), and this is its measurable form.
HUGGING_FLOOR: float = 0.45
"""Research: wall-hugging floor - GUESS: at least 0.45 of building footprint stands within 25 ft of a wall; derived from the pool sheets (51-58%) and no source gives a historical figure."""
CROP_MAX_MARGIN_PX: float = 25.0  # the checklist's "~15-25 px border" on each side of the viewBox
"""Research: sheet crop margin - CONVENTION: a drawn sheet keeps at most a 25 px border on each side of the viewBox, the checklist's 15-25 px."""
CROP_TOL_PX: float = 5.0
"""Research: crop tolerance - NONE: 5 px of slack on the crop margin, an audit pixel tolerance."""
GATE_MIN_FT: float = 5.0  # narrower is not a passage anyone drives or walks through
"""Research: narrowest gate - GUESS: a wall opening under 5 ft is not a passage anyone drives or walks through; the record's gates run 6 to 12 ft (0093) and no page gives the audit's floor."""
GATE_MAX_FT: float = 16.0  # wider is a structure's width, not a passage's (the gate lesson of 2026-07), unless a structure spans it
"""Research: widest gate - GUESS: a wall opening over 16 ft is a structure's width, not a passage's; no page sets a widest gate; the record's Japanese gates run 6 to 12 ft (0093) and a yamen's 18-24 ft is a guess there."""

_VIEWBOX_RE = re.compile(r'viewBox="\s*([\-\d.]+)\s+([\-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*"')
_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
_SCALE_LABEL_RE = re.compile(r"^\d+\s*ft$")
_SCALE_NOTE_RE = re.compile(r"3\s*px\s*=\s*1\s*ft")


def _lap(a: Rect, b: Rect) -> tuple[float, float]:
    return min(a.x2, b.x2) - max(a.x, b.x), min(a.y2, b.y2) - max(a.y, b.y)


def _contains(outer: Rect, inner: Rect) -> bool:
    tol = WALL_OVERLAP_MIN_PX
    return outer.x - tol <= inner.x and outer.y - tol <= inner.y and inner.x2 <= outer.x2 + tol and inner.y2 <= outer.y2 + tol


def structures_overlap(plan: ParsedPlan, share: float = OVERLAP_SHARE) -> list[str]:
    """Two built footprints lapping each other by more than `share` of the smaller, neither inside the other.

    A sorted-edge sweep: rects ordered by x, each compared only with those whose x-span reaches it -
    O(n log n) over a few dozen rects, which is the whole population of a Mode A sheet."""
    out: list[str] = []
    rects = sorted(plan.structures, key=lambda r: r.x)
    for i, a in enumerate(rects):
        for b in rects[i + 1 :]:
            if b.x >= a.x2 - WALL_OVERLAP_MIN_PX:
                break
            lx, ly = _lap(a, b)
            if lx <= WALL_OVERLAP_MIN_PX or ly <= WALL_OVERLAP_MIN_PX or _contains(a, b) or _contains(b, a):
                continue
            smaller = min(a.area_px, b.area_px)
            if smaller > 0 and lx * ly / smaller > share:
                out.append(
                    f"a {a.w / FTPX:.0f} x {a.h / FTPX:.0f} ft footprint at svg({a.x:.0f},{a.y:.0f}) and a {b.w / FTPX:.0f} x {b.h / FTPX:.0f} ft one at "
                    f"svg({b.x:.0f},{b.y:.0f}) overlap by {lx / FTPX:.1f} x {ly / FTPX:.1f} ft ({100 * lx * ly / smaller:.0f}% of the smaller)"
                )
    return out


def scale_bar_present(plan: ParsedPlan) -> list[str]:
    """The scale bar's two labels - a length in ft and the `(3 px = 1 ft)` note - are on the sheet."""
    texts = [lb.text.strip() for lb in plan.labels]
    missing = []
    if not any(_SCALE_LABEL_RE.match(t) for t in texts):
        missing.append("no scale-bar length label (e.g. `30 ft`)")
    if not any(_SCALE_NOTE_RE.search(t) for t in texts):
        missing.append("no `(3 px = 1 ft)` note")
    return missing


_PATH_CMD_RE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)")


def _path_points(d: str) -> tuple[list[float], list[float]]:
    """The ABSOLUTE points a path visits - the coordinates after an upper-case command. A relative
    command's offsets (a lower-case `q 3 -8 -2 -14` on a steam plume) are not coordinates and are
    skipped rather than read as ink at negative x, which is what a plain number scan did.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 7 (SVG arc arguments); 6 (SVG arc arguments)
    """
    xs: list[float] = []
    ys: list[float] = []
    for cmd, body in _PATH_CMD_RE.findall(d):
        nums = [float(n) for n in _NUM_RE.findall(body)]
        if cmd == "H":
            xs += nums
        elif cmd == "V":
            ys += nums
        elif cmd in "MLTCSQ":
            xs += nums[0::2]
            ys += nums[1::2]
        elif cmd == "A":
            for k in range(0, len(nums) - 6, 7):
                xs.append(nums[k + 5])
                ys.append(nums[k + 6])
    return xs, ys


PARCHMENT_SHARE: float = 0.9  # a rect covering this much of the viewBox is the background, not ink
"""Research: background rect share - NONE: a rect covering 0.9 of the viewBox is the parchment background, not ink, a parser classification."""
_SKIP_TAGS = {"defs", "pattern", "symbol", "clipPath", "mask", "marker"}
_TRANSLATE_RE = re.compile(r"translate\(\s*(-?[\d.]+)[\s,]*(-?[\d.]+)?\s*\)")


def _tag(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _num(value: str | None) -> float:
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)", value or "")
    return float(m.group(1)) if m else 0.0


def ink_bounds(text: str, plan: ParsedPlan, canvas_area: float = 0.0) -> tuple[float, float, float, float] | None:
    """The bounding box of everything DRAWN: rects, text, lines, circles, ellipses and the absolute points of
    every path, each shifted by the `translate(...)` of its ancestors; definitions (patterns, symbols,
    markers) draw nothing where they stand and are skipped, and a rect covering most of the canvas is the
    parchment background, not ink. The same walk as `scripts/reviews/size_table.py`'s, for the same reason: a glyph
    authored in local coordinates inside a translated group is ink where the group puts it, not at the origin.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.55 (character width figure)
    """
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None
    xs: list[float] = []
    ys: list[float] = []

    def visit(el: ET.Element, dx: float, dy: float) -> None:
        nonlocal xs, ys
        kind = _tag(el)
        if kind in _SKIP_TAGS:
            return
        m = _TRANSLATE_RE.search(el.get("transform") or "")
        if m:
            dx, dy = dx + float(m.group(1)), dy + float(m.group(2) or 0.0)
        if kind == "rect":
            w, h = _num(el.get("width")), _num(el.get("height"))
            if not (canvas_area and w * h >= PARCHMENT_SHARE * canvas_area):
                x, y = _num(el.get("x")) + dx, _num(el.get("y")) + dy
                xs += [x, x + w]
                ys += [y, y + h]
        elif kind == "line":
            # A STROKE IS INK HALF ITS WIDTH EITHER SIDE of the centerline (feature 372 wave 103: a 90 px road read at its
            # centerline left 45 px of its own ink counted as an empty margin)
            hw = _num(el.get("stroke-width")) / 2
            xs += [min(_num(el.get("x1")), _num(el.get("x2"))) + dx - hw, max(_num(el.get("x1")), _num(el.get("x2"))) + dx + hw]
            ys += [min(_num(el.get("y1")), _num(el.get("y2"))) + dy - hw, max(_num(el.get("y1")), _num(el.get("y2"))) + dy + hw]
        elif kind in ("circle", "ellipse"):
            rx = _num(el.get("r") or el.get("rx"))
            ry = _num(el.get("r") or el.get("ry"))
            cx, cy = _num(el.get("cx")) + dx, _num(el.get("cy")) + dy
            xs += [cx - rx, cx + rx]
            ys += [cy - ry, cy + ry]
        elif kind == "text":
            content = " ".join("".join(el.itertext()).split())
            # A caption DECLARED without `x` stands nowhere until the render pipeline places it (feature 286), and the
            # placer seats it inside the view (`labels.placer.place`'s frame), so it holds no edge the crop is judged by:
            # the crop is the drawing's. Read at x=0 it would be ink at the origin, hiding a slack left or top margin.
            if content and el.get("x") is not None:
                fs = _num(el.get("font-size")) or 10.0
                w = 0.55 * fs * len(content)
                x, y = _num(el.get("x")) + dx, _num(el.get("y")) + dy
                anchor = el.get("text-anchor", "start")
                left = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
                xs += [left, left + w]
                ys += [y - fs, y]
        elif kind == "path":
            px, py = _path_points(el.get("d") or "")
            hw = _num(el.get("stroke-width")) / 2 if (el.get("stroke") or "none") != "none" else 0.0
            xs += [v + dx + e for v in px for e in ((-hw, hw) if hw else (0.0,))]
            ys += [v + dy + e for v in py for e in ((-hw, hw) if hw else (0.0,))]
        for child in el:
            visit(child, dx, dy)

    visit(root, 0.0, 0.0)
    if not xs or not ys:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def viewbox_cropped(text: str, plan: ParsedPlan, max_margin_px: float = CROP_MAX_MARGIN_PX, tol_px: float = CROP_TOL_PX) -> list[str]:
    """The viewBox is cropped to the ink: no side leaves more than the checklist's border of empty parchment.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 5 (regex group range)
    """
    m = _VIEWBOX_RE.search(text)
    if not m:
        return ["no viewBox on the sheet"]
    vx, vy, vw, vh = (float(m.group(i)) for i in range(1, 5))
    ink = ink_bounds(text, plan, vw * vh)
    if ink is None:
        return ["nothing drawn to crop to"]
    ix1, iy1, ix2, iy2 = ink
    margins = {"left": ix1 - vx, "top": iy1 - vy, "right": (vx + vw) - ix2, "bottom": (vy + vh) - iy2}
    return [f"{side} margin is {px:.0f} px of empty parchment - crop the viewBox to ~{max_margin_px:.0f} px" for side, px in margins.items() if px > max_margin_px + tol_px]


#: the fix the coverage check names (feature 433 D3, the GM 2026-10-26: "whatever other changes need to be made should be made
#: in order to make the whole thing correspond to our research"): a smaller wall never hides slack, but when the research sizes a
#: magistracy's house - Hayakawa's cut from ~145 to ~65 tsubo left it at 26% - a wall moved in to bring it into the band is a
#: DEVIATION recorded on 0116's drawing page with its reason and who chose it. The check is the magistracy's alone (registry.py), so the amendment reaches no other sheet type.
COVERAGE_FIX = (
    "consolidate loose slack or add a program building below it; never shrink the envelope to hide slack - only when the "
    "research sizes the house does the envelope follow it into the band, a DEVIATION recorded on 0116's drawing page (feature 433)"
)


def coverage_band(plan: ParsedPlan, floor: float = COVERAGE_FLOOR, ceiling: float = COVERAGE_CEILING, tol: float = COVERAGE_TOL) -> list[str]:
    """Building coverage of the precinct between Takayama's ~33% floor and the record's ~42% ceiling (two points over it)."""
    cov = coverage(plan)
    if floor <= cov <= ceiling + tol:
        return []
    return [f"building coverage is {100 * cov:.0f}% - a jin'ya runs ~{100 * floor:.0f}-{100 * ceiling:.0f}% built ({COVERAGE_FIX})"]


def perimeter_hugging(plan: ParsedPlan, floor: float = HUGGING_FLOOR) -> list[str]:
    """Most building footprint rings the courts: at least `floor` of it within 25 ft of a wall or divider."""
    hug = perimeter_hugging_pct(plan)
    if hug >= floor:
        return []
    return [f"only {100 * hug:.0f}% of building footprint lies within 25 ft of a wall (floor {100 * floor:.0f}%) - buildings ring the courts, the center stays open"]


def gate_widths(plan: ParsedPlan, lo_ft: float = GATE_MIN_FT, hi_ft: float = GATE_MAX_FT) -> list[str]:
    """Every opening in the compound wall is a passable gate, or a break a structure stands in."""
    out: list[str] = []
    for o in wall_openings(plan):
        if o.ft < lo_ft:
            out.append(f"a {o.ft:.1f} ft opening at svg({o.x:.0f},{o.y:.0f}) is too narrow for a passage - pull the flanking endpoints back by half a stroke, or close it")
        elif o.ft > hi_ft:
            x1, y1, x2, y2 = (o.span1, o.across1, o.span2, o.across2) if o.horiz else (o.across1, o.span1, o.across2, o.span2)
            spanned = (
                any(s.x <= x1 + WALL_OVERLAP_MIN_PX and s.x2 >= x2 - WALL_OVERLAP_MIN_PX and s.y <= y1 + WALL_OVERLAP_MIN_PX and s.y2 >= y2 - WALL_OVERLAP_MIN_PX for s in plan.structures)
                if o.horiz
                else any(s.y <= y1 + WALL_OVERLAP_MIN_PX and s.y2 >= y2 - WALL_OVERLAP_MIN_PX and s.x <= x1 + WALL_OVERLAP_MIN_PX and s.x2 >= x2 - WALL_OVERLAP_MIN_PX for s in plan.structures)
            )
            if not spanned:
                out.append(
                    f"a {o.ft:.1f} ft opening at svg({o.x:.0f},{o.y:.0f}) is a structure's width, not a passage's - a gate is drawn at passage width (~13 ft), or a structure stands in the break"
                )
    return out


def divider_gates_ft(plan: ParsedPlan) -> list[float]:
    """The openings in the court divider, in feet: the gaps between consecutive runs of one divider line (its runs share
    an axis and a line, within a pixel)."""
    lines: dict[tuple[bool, int], list[tuple[float, float]]] = {}
    for d in plan.dividers:
        horiz = d.w >= d.h
        key = (horiz, round(d.y + d.h / 2) if horiz else round(d.x + d.w / 2))
        lines.setdefault(key, []).append((d.x, d.x2) if horiz else (d.y, d.y2))
    out: list[float] = []
    for runs in lines.values():
        runs.sort()
        out += [(b[0] - a[1]) / FTPX for a, b in zip(runs, runs[1:], strict=False)]
    return out


def two_court_zoning(plan: ParsedPlan) -> list[str]:
    """A divider wall splits the compound, the divider has its own gate, and the sanded hearing court lies on the gate's
    side of it."""
    if not plan.dividers:
        return ["no court divider - a magistracy is an outer (public) court at the gate and an inner (private) court behind a divider"]
    # THE DIVIDER HAS A GATE (feature 267 pass 3, the building-review's catch on the placer's draft, which drew the
    # divider unbroken): the household's middle gate, the nakamon (docs/building-programs.md "Two-court zoning") - a
    # divider with no opening seals the house from the office. A passage is at least GATE_MIN_FT, like a wall's.
    if not any(g >= GATE_MIN_FT for g in divider_gates_ft(plan)):
        return ["the court divider has no gate - the household's middle gate (nakamon, ~6-8 ft, narrower than the main gate) joins the courts"]
    sand = [r for r in plan.open_features if r.fill in COURT_FLOORS]
    if not sand:
        return ["no hearing court (oshirasu) - the bench overlooks it from the office hall's dais"]
    gates = [o for o in wall_openings(plan) if o.ft <= GATE_MAX_FT]
    if not gates:
        return ["no gate opening in the compound wall"]
    main = max(gates, key=lambda o: o.ft)
    horiz = [d for d in plan.dividers if d.w >= d.h]
    if not horiz:
        return []  # a vertical divider: the sides are east/west; the sheet's own composition rule, not checked here
    dy = sum(d.y + d.h / 2 for d in horiz) / len(horiz)
    court = sand[0]
    if ((court.y + court.h / 2) > dy) != (main.y > dy):
        return [f"the hearing court at svg({court.x:.0f},{court.y:.0f}) lies on the far side of the divider from the main gate - the public court is at the gate, the private court behind"]
    return []


# --- the country shrine's own checks (feature 254, D8) - each reads a DECLARED feature by id ---

AXIS_TOL_FT: float = 3.0  # the sanctuary's center may stray this far from the approach axis
"""Research: shrine axis tolerance - GUESS: no page says how exactly a sanctuary sat on its approach's axis; its center may stray 3 ft from it."""
EDGE_TOL_FT: float = 2.0  # the arch stands AT the precinct edge: within this of it
"""Research: arch edge tolerance - GUESS: no page gives it; the arch stands within 2 ft of the precinct edge."""


def _one(plan: ParsedPlan, ident: str) -> Rect | None:
    found = plan.by_id(ident)
    return found[0] if found else None


def _center(r: Rect) -> tuple[float, float]:
    return r.x + r.w / 2, r.y + r.h / 2


def sanctuary_on_axis(plan: ParsedPlan, tol_ft: float = AXIS_TOL_FT) -> list[str]:
    """The sanctuary stands on the approach's axis, BEHIND the hall (farther from the arch than the hall)."""
    hall, sanctuary, approach, arch = (_one(plan, k) for k in ("hall", "sanctuary", "approach", "arch"))
    missing = [k for k, v in (("hall", hall), ("sanctuary", sanctuary), ("approach", approach), ("arch", arch)) if v is None]
    if missing:
        return [f"the sheet declares no {' / '.join(missing)} (mark the rect id=\"<name>\")"]
    assert hall and sanctuary and approach and arch
    vertical = approach.h >= approach.w
    ax, ay = _center(approach)
    sx, sy = _center(sanctuary)
    hx, hy = _center(hall)
    gx, gy = _center(arch)
    off = abs(sx - ax) if vertical else abs(sy - ay)
    out: list[str] = []
    if off > tol_ft * FTPX:
        out.append(f"the sanctuary's center is {off / FTPX:.1f} ft off the approach axis")
    along = (lambda y: abs(y - gy)) if vertical else (lambda x: abs(x - gx))
    if along(sy if vertical else sx) <= along(hy if vertical else hx):
        out.append("the sanctuary stands nearer the arch than the hall - it belongs BEHIND the hall on the axis")
    return out


def arch_on_approach(plan: ParsedPlan, edge_tol_ft: float = EDGE_TOL_FT) -> list[str]:
    """The arch straddles the approach where the way enters the precinct."""
    approach, arch = _one(plan, "approach"), _one(plan, "arch")
    if approach is None or arch is None:
        return ["the sheet declares no approach / arch (mark the rects id=\"approach\", id=\"arch\")"]
    lx, ly = _lap(approach, arch)
    out: list[str] = []
    if lx <= 0 or ly <= 0:
        out.append("the arch does not straddle the approach - a gateway stands over the way")
    minx, miny, maxx, maxy = plan.bounds
    gx, gy = _center(arch)
    tol = edge_tol_ft * FTPX
    at_edge = min(abs(gx - minx), abs(gx - maxx), abs(gy - miny), abs(gy - maxy)) <= tol + max(arch.w, arch.h) / 2
    if not at_edge:
        out.append("the arch stands inside the precinct rather than at its edge, where the way enters")
    return out


def well_clear_of_arch(plan: ParsedPlan) -> list[str]:
    """The well stands beside the approach, never on it and never under the arch."""
    approach, arch = _one(plan, "approach"), _one(plan, "arch")
    wells = plan.by_id("well") or plan.wells
    if not wells:
        return ["no well on the sheet (a shrine needs its purification well or basin)"]
    if approach is None or arch is None:
        return ["the sheet declares no approach / arch (mark the rects id=\"approach\", id=\"arch\")"]
    out: list[str] = []
    for w in wells:
        for name, r in (("approach", approach), ("arch", arch)):
            lx, ly = _lap(w, r)
            if lx > WALL_OVERLAP_MIN_PX and ly > WALL_OVERLAP_MIN_PX:
                out.append(f"the well at svg({w.x:.0f},{w.y:.0f}) stands on the {name}")
    return out


def no_precinct_enclosure(text: str, plan: ParsedPlan) -> list[str]:
    """A village shrine's precinct is NOT enclosed (feature 268; research/questions/0223-shrine-woods-and-fences-chinju-no-mori-tamagaki.html): its ground is marked by its arch and its wood. Every dated fence
    the research found rings the sanctuary alone (a Taisho/Showa donation) or lines the approach, and a
    wall is a temple's rank mark. So a fence group whose extent takes in the hall - a precinct fence - is
    reported, as is a compound wall stroke at the sheet's edge; a fence around the sanctuary alone (a
    richer shrine's donation, on the wealth knob) passes. `text` is kept for the registry's signature."""
    del text
    out: list[str] = []
    hall = plan.by_id("hall")
    if plan.fence_segs and hall:
        fx0 = min(r.x for r in plan.fence_segs)
        fy0 = min(r.y for r in plan.fence_segs)
        fx1 = max(r.x + r.w for r in plan.fence_segs)
        fy1 = max(r.y + r.h for r in plan.fence_segs)
        h = hall[0]
        if fx0 <= h.x and fy0 <= h.y and fx1 >= h.x + h.w and fy1 >= h.y + h.h:
            out.append(
                "a fence rings the precinct (its extent takes in the hall) - a village shrine's ground is marked by its arch and its wood; a fence rings the sanctuary alone, and only as a richer shrine's donation"
            )
    minx, miny, maxx, maxy = plan.bounds
    tol = EDGE_TOL_FT * FTPX
    for band in plan.wall_bands:
        if band.fill != WALL_STROKE:
            continue
        cx, cy = _center(band)
        if min(abs(cx - minx), abs(cx - maxx), abs(cy - miny), abs(cy - maxy)) <= tol + max(band.w, band.h):
            out.append(f"a compound wall stroke at svg({band.x:.0f},{band.y:.0f}) bounds the precinct - a village shrine is neither walled nor fenced")
            break
    return out


def one_compound_shrine(text: str) -> list[str]:
    """A compound draws ONE modest shrine, however many a real office kept (0218's drawing page, a deliberate deviation:
    research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html). A second kami is enshrined in that hall, or
    keeps a shrine of its own inside the precinct where the sheet's roll of its form says so - that shrine's group declares
    `data-form="own shrine"` and is not counted (feature 374 wave 123: Hayakawa's river kami, which rolls one hall, had a
    shrine of its own). A shrine is a group tagged `compound shrine`; its arch, tagged a part of it, is not one."""
    groups = re.findall(r'<g data-kind="compound shrine"([^>]*)>', text)
    main = [g for g in groups if 'data-form="own shrine"' not in g]
    return (
        [f"{len(main)} compound shrines drawn - a compound draws one modest shrine; enshrine a second god in its hall, or declare its rolled own shrine data-form=\"own shrine\""]
        if len(main) > 1
        else []
    )


STALL_FT: tuple[float, float] = (4.5, 7.5)  # one ken (~6 ft) a stall, with a drawing's play either side
"""Research: stall width band - research/questions/0108-stables-umaya.drawing.html: a stall is one ken (~6 ft) wide, as the page draws it, with 4.5 to 7.5 ft allowed for a drawing's play."""


def stall_width(text: str) -> list[str]:
    """A warrior's stall was one bay wide - our maps take a bay as one ken, ~6 ft (0108's drawing page:
    research/questions/0108-stables-umaya.drawing.html; feature 374 wave 126: the sheets drew three stalls 9.3-9.7 ft wide).
    In each stable, the partitions drawn across one of its axes part it into spans; along one axis at least two must be a
    stall's width (the stalls stand three bays long, the passage and the grooms' room in its depth). A stable with no
    partition draws no stalls at all."""
    found = marks(text)
    out = []
    # the stable's body is its outlined rect; a floor drawn inside it (the passage's earth) carries no stroke
    for body in (m for m in found if m.tag == "rect" and m.kind == "stables" and m.lineage[-1:] == ("stables",) and m.paint.get("stroke", "none") != "none"):
        inside = [m for m in found if m.tag == "line" and m.kind == "stables" and body.x <= m.x and m.x2 <= body.x2 and body.y <= m.y and m.y2 <= body.y2]
        best: list[float] = []
        for along_x in (True, False):
            lo, hi = (body.x, body.x2) if along_x else (body.y, body.y2)
            cuts = sorted({(m.x if along_x else m.y) for m in inside if (m.w < 1 if along_x else m.h < 1) and lo < (m.x if along_x else m.y) < hi})
            spans = [b - a for a, b in zip([lo, *cuts], [*cuts, hi], strict=True)]
            if len([w for w in spans if STALL_FT[0] * FTPX <= w <= STALL_FT[1] * FTPX]) >= 2:
                break
            best = best or spans
        else:
            widths = ", ".join(f"{w / FTPX:.1f}" for w in best)
            out.append(f"the stable at svg({body.x:.0f},{body.y:.0f}) parts its length into {widths} ft - draw its stalls one ken (~6 ft) wide")
    return out


HALL_MIN_SPAN_FT: float = 6.0  # an open stretch of the building shorter than this is a partition's gap, not the hall
"""Research: hall span floor - GUESS: no page gives it; an open stretch of a building under 6 ft (one ken) is a partition's gap, not the hall."""


def _dwelling_spans(text: str, hall: Rect, along_x: bool) -> list[tuple[float, float]]:
    """The spans, along the building's long axis, of every mark drawn as a part of its dwelling end (a group tagged
    `data-part-of="hall and dwelling"`: the kitchen, the monk's rooms, their entry), clipped to the building."""
    lo, hi = (hall.x, hall.x + hall.w) if along_x else (hall.y, hall.y + hall.h)
    spans = []
    for m in marks(text):
        if len(m.lineage) < 2 or m.lineage[0] != "hall and dwelling" or m.kind == "hall and dwelling":
            continue
        a, b = (m.x, m.x2) if along_x else (m.y, m.y2)
        if min(b, hi) > max(a, lo):
            spans.append((max(a, lo), min(b, hi)))
    return sorted(spans)


def hall_at_an_end(text: str, plan: ParsedPlan) -> list[str]:
    """Under one roof the villagers' hall is one END of the building and the monk's dwelling the other (0221's drawing page:
    "the monk's dwelling is one end of the worship hall's own building"; research/questions/0221-the-country-monk-who-keeps-a-
    village-shrine-and-their-dwelling-kuri.drawing.html). The hall is the longest stretch of the building no dwelling part
    covers; the dwelling's parts on BOTH sides of it put the hall in the middle. A sheet drawing the two-buildings form
    tags no part of the hall's building, and passes."""
    hall = _one(plan, "hall")
    if hall is None:
        return []  # sanctuary_on_axis names a sheet that declares no hall
    along_x = hall.w >= hall.h
    spans = _dwelling_spans(text, hall, along_x)
    if not spans:
        return []
    lo, hi = (hall.x, hall.x + hall.w) if along_x else (hall.y, hall.y + hall.h)
    gaps, edge = [], lo
    for a, b in spans:
        if a > edge:
            gaps.append((edge, a))
        edge = max(edge, b)
    if hi > edge:
        gaps.append((edge, hi))
    gaps = [g for g in gaps if g[1] - g[0] >= HALL_MIN_SPAN_FT * FTPX]
    if not gaps:
        return []
    h0, h1 = max(gaps, key=lambda g: g[1] - g[0])
    if any(b <= h0 for _, b in spans) and any(a >= h1 for a, _ in spans):
        return [f"the hall stands between the dwelling's rooms (svg {h0:.0f}-{h1:.0f} of {lo:.0f}-{hi:.0f}) - under one roof it is one end of the building, the dwelling the other"]
    return []


# A TREE STANDS ON OPEN GROUND AND ON NOTHING ELSE (feature 257; the GM, 2026-09-20: "an automated check
# to prevent trees from overlapping with other things"). The ground - the precinct's gravel, a court, a
# garden bed - is what a canopy grows from; a building, a fence or a well under it reads as a mistake, which is
# what the GM saw on the Hoshigaoka sheet. Crowns may overlap each other (feature 270, the GM 2026-09-27); a tree
# drawn on top of another may not. The reach tolerance is the built-footprint check's. A caption is not among the
# things checked (feature 286): the placer seats it clear of the canopies, and its unit tests hold that.
def _canopy_depth(cx: float, cy: float, r: float, rect: Rect) -> float:
    """How far a canopy of radius `r` at (cx, cy) reaches into `rect` (px); zero or less = clear of it."""
    dx = max(rect.x - cx, 0.0, cx - rect.x2)
    dy = max(rect.y - cy, 0.0, cy - rect.y2)
    return r - math.hypot(dx, dy)


def _things_under_a_tree(plan: ParsedPlan) -> list[tuple[str, Rect]]:
    """Everything a canopy may not cover, named: built footprints, furniture, walls, the fence, glyphs, tubs.
    Open ground (the precinct, a court, a garden bed - any pattern-filled or open-feature rect) is left out."""
    ground = set(plan.interior) | set(plan.open_features)
    out: list[tuple[str, Rect]] = [("a building", r) for r in plan.structures]
    out += [("furniture", r) for r in plan.furniture if r not in ground and not r.fill.startswith("url(") and r not in plan.structures]
    out += [("a wall", r) for r in plan.wall_bands] + [("a divider", r) for r in plan.dividers] + [("the fence", r) for r in plan.fence_segs]
    out += [("a glyph", r) for r in plan.glyphs] + [("a fire-water tub", r) for r in plan.tubs]
    return out


DUPLICATE_TREE_FRACTION: float = 1 / 3  # trunks closer than this share of the smaller crown's radius are one tree drawn twice (a guess, spec 270 R2)


def trees_overlap(plan: ParsedPlan, tol: float = WALL_OVERLAP_MIN_PX) -> list[str]:
    """Every canopy that covers something that is not open ground, and every tree drawn on top of another.

    Crowns may overlap each other (feature 270, the GM 2026-09-27: "tree crowns may overlap, I never said they
    couldn't"): a kept wood's canopy is closed. What is still reported is a DUPLICATED tree - two trunks within a
    third of the smaller crown's radius, one tree drawn on another (feature 257's "two lie on top of each other").
    The third is a GUESS (spec 270 research R2): no source read gives how close two trees grow, and a third of a
    crown's radius is well inside any spacing a wood's trees stand at."""
    out: list[str] = []
    things = _things_under_a_tree(plan)
    trees = [(t.x + t.w / 2, t.y + t.h / 2, t.w / 2) for t in plan.trees]
    for cx, cy, r in trees:
        for kind, rect in things:
            depth = _canopy_depth(cx, cy, r, rect)
            if depth > tol:
                out.append(f"a tree at svg({cx:.0f},{cy:.0f}) ({2 * r / FTPX:.0f} ft canopy) reaches {depth / FTPX:.1f} ft into {kind} at svg({rect.x:.0f},{rect.y:.0f})")
    for i, (ax, ay, ar) in enumerate(trees):
        for bx, by, br in trees[i + 1 :]:
            gap = math.hypot(ax - bx, ay - by)
            if gap < min(ar, br) * DUPLICATE_TREE_FRACTION:
                out.append(f"a tree at svg({bx:.0f},{by:.0f}) is drawn on top of the tree at svg({ax:.0f},{ay:.0f}) - their trunks stand {gap / FTPX:.1f} ft apart")
    return out


# A POSTERN'S APPROACH (feature 374 batch 4, plan R4-2): the county draft's south postern was sealed - the cell and the
# barracks both ran to the wall across its whole opening - while `passage_blockers` (furniture only, by design) and
# `gate_feeds_its_road` (the road outside) both passed. A gateway is a way through: on each face of its wall a strip as
# wide as the opening and APPROACH_FT deep keeps a clear run of at least CLEAR_FT, room for a carrier and a handcart.
# A building STRADDLING the wall's ink is not counted - that is the wall-broken-around-a-structure idiom (Ubame's parley
# room), not a sealed gate. Both lengths are a GUESS: a person walks a 3 ft way, and 6 ft is one ken before the wall.
APPROACH_FT: float = 6.0
"""Research: gateway approach depth - GUESS: a wall opening keeps a clear strip 6 ft deep, one ken before the wall, on each face; no page gives it."""
CLEAR_FT: float = 3.0
"""Research: gateway clear run - GUESS: the gateway approach keeps a clear run of 3 ft, room for a carrier and a handcart; no page gives it."""


def postern_approach(plan: ParsedPlan) -> list[str]:
    """Each wall opening whose approach on one face has no clear run of CLEAR_FT within APPROACH_FT of the wall."""
    out: list[str] = []
    for o in wall_openings(plan):
        depth = APPROACH_FT * FTPX
        for a1, a2 in ((o.across1 - depth, o.across1), (o.across2, o.across2 + depth)):
            spans: list[tuple[float, float]] = []
            for r in plan.structures:
                s1, s2, t1, t2 = (r.x, r.x2, r.y, r.y2) if o.horiz else (r.y, r.y2, r.x, r.x2)
                if t1 <= o.across1 and t2 >= o.across2:  # straddles the wall's ink: the gap-fill idiom
                    continue
                if min(t2, a2) - max(t1, a1) > 0 and min(s2, o.span2) - max(s1, o.span1) > 0:
                    spans.append((max(s1, o.span1), min(s2, o.span2)))
            free, at = 0.0, o.span1
            for s1, s2 in sorted(spans):
                free, at = max(free, s1 - at), max(at, s2)
            free = max(free, o.span2 - at)
            if free < CLEAR_FT * FTPX:
                out.append(f"the {o.ft:.1f} ft opening at svg({o.x:.0f},{o.y:.0f}) has {free / FTPX:.1f} ft clear on one face (under {CLEAR_FT:.0f} ft) - a building seals the way through")
                break
    return out


# THE SHRINE'S TREE (feature 374 wave 130): a household kept its god in a corner of its lot, "by building a small shrine or
# by taking an old tree, a stone or the like as its yorishiro" (kotobank-yashikigami), and our maps set the compound's
# shrine there and "give it the tree as well" (research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html).
# The tree is a crown tagged `sacred tree`, a part of the compound shrine, its trunk within SHRINE_TREE_FT of the hall's
# walls. The 15 ft is a GUESS: no source gives how near the tree stood; it lets a ~20 ft crown clear the hall it stands by.
SHRINE_TREE_FT: float = 15.0
"""Research: shrine tree reach - GUESS: the compound shrine's tree trunk stands within 15 ft of the hall's walls; no source gives how near the tree stood."""


def shrine_tree(text: str) -> list[str]:
    """The compound shrine stands beside its tree: a `sacred tree` crown that is a part of the `compound shrine`, its trunk
    within SHRINE_TREE_FT of the hall (the shrine's largest rect)."""
    found = marks(text)
    halls = [m for m in found if m.tag == "rect" and m.kind == "compound shrine" and "sacred tree" not in m.lineage]
    if not halls:
        return []
    hall = max(halls, key=lambda m: m.w * m.h)
    crowns = [m for m in found if m.tag == "circle" and m.kind == "sacred tree" and "compound shrine" in m.lineage]
    for c in crowns:
        cx, cy = c.x + c.w / 2, c.y + c.h / 2
        dx, dy = max(hall.x - cx, 0.0, cx - hall.x - hall.w), max(hall.y - cy, 0.0, cy - hall.y - hall.h)
        if math.hypot(dx, dy) <= SHRINE_TREE_FT * FTPX:
            return []
    where = f"svg({hall.x:.0f},{hall.y:.0f})"
    return [f"the compound shrine at {where} has no tree beside it"]


# A WELL'S LIFTING GEAR (feature 374 wave 135): research/questions/0196-communal-wells-ido.drawing.html draws every well with
# "a well-sweep or a pulley frame over it"; a sheet's well carries its gear as a group tagged a part of the well, its
# `data-gear` the form rolled (`l7r/diagram/well_gear.py`) and its `data-at` the curb's center. An open-air well's gear and
# roof are the page's; an indoor well (its curb inside a building) takes a pulley hung from the building's beams and no roof
# of its own (plan W135-2, the batch 6 reviews: a sweep cannot work under a roof).
_GEAR_RE = re.compile(r'<g data-kind="well" data-gear="(sweep|pulley frame|beam pulley)" data-at="([\d.]+),([\d.]+)"')
_ROOF_RE = re.compile(r'<g data-kind="well" data-roof="1" data-at="([\d.]+),([\d.]+)">(.*?)</g>', re.S)


def _indoor(cx: float, cy: float, text: str) -> bool:
    """The point stands inside a building: a rect of a structure's fill, not a part of a well, holding it."""
    from .parse import STRUCTURE_FILLS

    return any(m.tag == "rect" and m.kind != "well" and m.paint.get("fill") in STRUCTURE_FILLS and m.x < cx < m.x2 and m.y < cy < m.y2 for m in marks(text))


def well_gear(text: str) -> list[str]:
    """Every well's curb - a rect of the curb's stone, tagged a `well`, a curb marker's size - carries its lifting gear: a
    `data-gear` group whose `data-at` is the curb's center (within 2 px). A basin or a lantern sharing the stone's color is
    not a well. An indoor well's gear is the beam pulley and it has no roof; an open-air well's is never the beam pulley; a
    roof is an unfilled outline standing on its four posts, drawn over the curb (a filled square under it reads as the
    page's paved apron - glyph-check, batch 6).

    Research:
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 15 (smallest curb marker read as a well (px))
    """
    from .parse import WELL_FILL

    gears = [(m[1], float(m[2]), float(m[3])) for m in _GEAR_RE.finditer(text)]
    roofs = [(float(m[1]), float(m[2]), m[3]) for m in _ROOF_RE.finditer(text)]
    out = []
    for m in marks(text):
        if m.tag != "rect" or m.kind != "well" or m.paint.get("fill") != WELL_FILL or min(m.w, m.h) < 15.0:
            continue
        cx, cy = m.x + m.w / 2, m.y + m.h / 2
        at = f"svg({cx:.0f},{cy:.0f})"
        gear = next((g for g, gx, gy in gears if abs(gx - cx) <= 2.0 and abs(gy - cy) <= 2.0), None)
        roof = next((body for rx, ry, body in roofs if abs(rx - cx) <= 2.0 and abs(ry - cy) <= 2.0), None)
        indoor = _indoor(cx, cy, text)
        if gear is None:
            out.append(f"the well at {at} carries no lifting gear")
        elif indoor and gear != "beam pulley":
            out.append(f"the well at {at} stands indoors but draws a {gear} - an indoor well hangs its pulley from the beams")
        elif not indoor and gear == "beam pulley":
            out.append(f"the well at {at} stands in the open but draws a beam pulley - its gear is a sweep or a pulley frame")
        if roof is not None and indoor:
            out.append(f"the well at {at} stands indoors under its building's roof but draws a roof of its own")
        elif roof is not None and (roof.count("<circle") != 4 or not re.search(r'<(?:rect|path)[^>]*fill="none"', roof)):
            out.append(f"the roof over the well at {at} is not an outline on four posts - a filled square reads as a paved apron")
    return out
