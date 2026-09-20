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
from .parse import WALL_STROKE, ParsedPlan, Rect

# A structure may CONTAIN another (an engawa strip on a residence, a door, a room) and two blocks of
# one building may join by a corridor that laps a few px into each - those are compositions, not
# accidents. An accident is a substantial lap: more than this share of the smaller footprint, with
# neither rect inside the other. Tuned on the five pool sheets (2026-09-19): the largest legitimate
# lap on them is a joining corridor's end.
OVERLAP_SHARE: float = 0.30
# The coverage band: the record's "~37-42%" (research/buildings.html, the packing entry) is the page's
# own measurement of jin'ya plans with no readable source, and the same entry gives Takayama at ~33%
# built (1,000 of 3,000 tsubo) as a figure that rests on no page read. Both are the page's own; the
# FLOOR is that 33 and the ceiling the page's 42 with two points for a rule written with a tilde. Hayakawa ships at 35% with every building at its
# size-audited footprint (the audit of 2026-07 shrank four laundered sizes AFTER the entry called it
# 37-38%): inside the attested spread, so the exact 37 was the check's defect, not the sheet's
# (feature 254 T06/T08, plan D9); the entry's stale sentence is corrected in the same work.
COVERAGE_FLOOR: float = 0.33
COVERAGE_CEILING: float = 0.42
COVERAGE_TOL: float = 0.02
# The hugging floor is DERIVED, not typed from a source: the five pool sheets measure 51-58% of
# building footprint within 25 ft of a wall (m:hugging-floor, feature 254), and one building pulled
# into the center of a court costs about six points, so the floor sits one such building under the
# lowest shipped value. Nothing read gives a historical figure for it; the ring is the composition
# rule (buildings.md, "Composition"), and this is its measurable form.
HUGGING_FLOOR: float = 0.45
CROP_MAX_MARGIN_PX: float = 25.0  # the checklist's "~15-25 px border" on each side of the viewBox
CROP_TOL_PX: float = 5.0
GATE_MIN_FT: float = 5.0  # narrower is not a passage anyone drives or walks through
GATE_MAX_FT: float = 16.0  # wider is a structure's width, not a passage's (the gate lesson of 2026-07), unless a structure spans it

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
    skipped rather than read as ink at negative x, which is what a plain number scan did."""
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
    parchment background, not ink. The same walk as `scripts/_size_table.py`'s, for the same reason: a glyph
    authored in local coordinates inside a translated group is ink where the group puts it, not at the origin."""
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
            xs += [_num(el.get("x1")) + dx, _num(el.get("x2")) + dx]
            ys += [_num(el.get("y1")) + dy, _num(el.get("y2")) + dy]
        elif kind in ("circle", "ellipse"):
            rx = _num(el.get("r") or el.get("rx"))
            ry = _num(el.get("r") or el.get("ry"))
            cx, cy = _num(el.get("cx")) + dx, _num(el.get("cy")) + dy
            xs += [cx - rx, cx + rx]
            ys += [cy - ry, cy + ry]
        elif kind == "text":
            content = " ".join("".join(el.itertext()).split())
            if content:
                fs = _num(el.get("font-size")) or 10.0
                w = 0.55 * fs * len(content)
                x, y = _num(el.get("x")) + dx, _num(el.get("y")) + dy
                anchor = el.get("text-anchor", "start")
                left = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
                xs += [left, left + w]
                ys += [y - fs, y]
        elif kind == "path":
            px, py = _path_points(el.get("d") or "")
            xs += [v + dx for v in px]
            ys += [v + dy for v in py]
        for child in el:
            visit(child, dx, dy)

    visit(root, 0.0, 0.0)
    if not xs or not ys:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def viewbox_cropped(text: str, plan: ParsedPlan, max_margin_px: float = CROP_MAX_MARGIN_PX, tol_px: float = CROP_TOL_PX) -> list[str]:
    """The viewBox is cropped to the ink: no side leaves more than the checklist's border of empty parchment."""
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


def coverage_band(plan: ParsedPlan, floor: float = COVERAGE_FLOOR, ceiling: float = COVERAGE_CEILING, tol: float = COVERAGE_TOL) -> list[str]:
    """Building coverage of the precinct between Takayama's ~33% floor and the record's ~42% ceiling (two points over it)."""
    cov = coverage(plan)
    if floor <= cov <= ceiling + tol:
        return []
    return [f"building coverage is {100 * cov:.0f}% - a jin'ya runs ~{100 * floor:.0f}-{100 * ceiling:.0f}% built (consolidate or add a program building below it; never shrink the envelope)"]


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


def two_court_zoning(plan: ParsedPlan) -> list[str]:
    """A divider wall splits the compound, and the sanded hearing court lies on the gate's side of it."""
    if not plan.dividers:
        return ["no court divider - a magistracy is an outer (public) court at the gate and an inner (private) court behind a divider"]
    sand = [r for r in plan.open_features if r.fill == "url(#oshirasu-sand)"]
    if not sand:
        return ["no sanded hearing court (oshirasu) - the bench overlooks it from the office hall's dais"]
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
EDGE_TOL_FT: float = 2.0  # the arch stands AT the precinct edge: within this of it
FENCE_ID = "fence"
_FENCE_RE = re.compile(r'<g\b[^>]*\bid="fence"')


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


def fence_not_wall(text: str, plan: ParsedPlan) -> list[str]:
    """The precinct is bounded by a fence or hedge (a group marked id=\"fence\"), never by a compound wall."""
    out: list[str] = []
    if not _FENCE_RE.search(text):
        out.append('no fence or hedge bounds the precinct (a `<g id="fence">` of fence strokes)')
    minx, miny, maxx, maxy = plan.bounds
    tol = EDGE_TOL_FT * FTPX
    for band in plan.wall_bands:
        if band.fill != WALL_STROKE:
            continue
        cx, cy = _center(band)
        if min(abs(cx - minx), abs(cx - maxx), abs(cy - miny), abs(cy - maxy)) <= tol + max(band.w, band.h):
            out.append(f"a compound wall stroke at svg({band.x:.0f},{band.y:.0f}) bounds the precinct - a shrine is fenced, a compound is walled")
            break
    return out


# A TREE STANDS ON OPEN GROUND AND ON NOTHING ELSE (feature 257; the GM, 2026-09-20: "an automated check
# to prevent trees from overlapping with other things"). The ground - the precinct's gravel, a court, a
# garden bed - is what a canopy grows from; a building, a fence, a well, a label or another canopy under it
# reads as a mistake, which is what the GM saw on the Hoshigaoka sheet. Two canopies may touch and no
# more; the touching tolerance is the one the built-footprint overlap check owns, not a second number.
def _canopy_depth(cx: float, cy: float, r: float, rect: Rect) -> float:
    """How far a canopy of radius `r` at (cx, cy) reaches into `rect` (px); zero or less = clear of it."""
    dx = max(rect.x - cx, 0.0, cx - rect.x2)
    dy = max(rect.y - cy, 0.0, cy - rect.y2)
    return r - math.hypot(dx, dy)


def _things_under_a_tree(plan: ParsedPlan) -> list[tuple[str, Rect]]:
    """Everything a canopy may not cover, named: built footprints, furniture, walls, the fence, glyphs, tubs, labels.
    Open ground (the precinct, a court, a garden bed - any pattern-filled or open-feature rect) is left out."""
    ground = set(plan.interior) | set(plan.open_features)
    out: list[tuple[str, Rect]] = [("a building", r) for r in plan.structures]
    out += [("furniture", r) for r in plan.furniture if r not in ground and not r.fill.startswith("url(") and r not in plan.structures]
    out += [("a wall", r) for r in plan.wall_bands] + [("a divider", r) for r in plan.dividers] + [("the fence", r) for r in plan.fence_segs]
    out += [("a glyph", r) for r in plan.glyphs] + [("a fire-water tub", r) for r in plan.tubs]
    out += [(f"the label {lb.text!r}", Rect(lb.x, lb.y, lb.w, lb.h)) for lb in plan.labels]
    return out


def trees_overlap(plan: ParsedPlan, tol: float = WALL_OVERLAP_MIN_PX) -> list[str]:
    """Every canopy that covers something that is not open ground, and every pair of canopies that overlap."""
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
            lap = ar + br - math.hypot(ax - bx, ay - by)
            if lap > tol:
                out.append(f"two trees at svg({ax:.0f},{ay:.0f}) and svg({bx:.0f},{by:.0f}) overlap by {lap / FTPX:.1f} ft")
    return out
