#!/usr/bin/env python3
"""Every drawn thing on a Mode A plan, in feet, for `size-audit` (feature 251, FR-006).

WHY. `size-audit` checks whether the things drawn on a compound plan are the size such things actually
were. Its first step was to parse the SVG and convert every rect, gap and stroke from px to feet - which
is arithmetic, done by a model turn by turn with the whole sheet in context. This does that step exactly
and hands the table over; the agent starts from it, checks it against the sheet, adds what it missed,
and keeps the part that is judgment: what the real thing measured, and what the ratios and the ordering
mean.

SCALE: 3 px = 1 ft, the Mode A constant (`size-audit.md`, Inputs).

WHAT IT LISTS.
- every `<rect>` outside `<defs>`/`<pattern>`/`<symbol>`/`<clipPath>`, with the `translate(...)` of its
  ancestors applied; any other transform (a rotation, a scale) is NOT applied and the row says so,
  because a wrong number stated plainly is worse than a flagged one;
- every distinct stroke width on a line, path, polyline, polygon or rect (a wall's thickness is a stroke);
- the GAPS between consecutive collinear axis-aligned `<line>` segments of the same stroke - a gate or a
  door is drawn as the gap between two wall segments.
Each rect is labeled with the nearest `<text>` by center distance, and the distance is printed: a label
60 ft away is a guess and reads as one.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

# THE PAIRING IS THE PACKAGE'S (feature 254, D7): `pack_audit.labels.nearest_label` is the one rule that
# says which label a footprint carries, shared with the band check, so the two cannot drift apart.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "skills", "diagram"))
from l7r.diagram.tools.pack_audit.labels import nearest_label  # noqa: E402

PX_PER_FT = 3.0
SKIP = {"defs", "pattern", "symbol", "clipPath", "mask", "marker"}
ALIGN = 1.0  # px: two wall segments share an axis when their fixed coordinate agrees within this


def tag(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def num(value: str | None) -> float:
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)", value or "")
    return float(m.group(1)) if m else 0.0


def shift_of(transform: str | None) -> tuple[float, float, bool]:
    """(dx, dy, whether something other than translate was present) for one `transform` attribute."""
    if not transform:
        return 0.0, 0.0, False
    dx = dy = 0.0
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", transform):
        if name == "translate":
            vals = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", args)] + [0.0, 0.0]
            dx, dy = dx + vals[0], dy + vals[1]
    other = any(name != "translate" for name, _ in re.findall(r"(\w+)\s*\(([^)]*)\)", transform))
    return dx, dy, other


def walk(root: ET.Element) -> list[tuple[ET.Element, float, float, bool]]:
    """(element, dx, dy, untransformed?) for every drawn element, skipping definitions.

    `stroke` and `stroke-width` are INHERITED in SVG - a wall's thickness is usually set once on the group
    its segments sit in - so each element is given its ancestors' values where it states none of its own.
    """
    out: list[tuple[ET.Element, float, float, bool]] = []

    def visit(el: ET.Element, dx: float, dy: float, other: bool, stroke: str, width: str) -> None:
        if tag(el) in SKIP:
            return
        ex, ey, eo = shift_of(el.get("transform"))
        dx, dy, other = dx + ex, dy + ey, other or eo
        stroke, width = el.get("stroke") or stroke, el.get("stroke-width") or width
        if stroke and not el.get("stroke"):
            el.set("stroke", stroke)
        if width and not el.get("stroke-width"):
            el.set("stroke-width", width)
        out.append((el, dx, dy, other))
        for child in el:
            visit(child, dx, dy, other, stroke, width)

    visit(root, 0.0, 0.0, False, "", "")
    return out


def ft(px: float) -> float:
    return round(px / PX_PER_FT, 1)


def table(svg_text: str) -> dict:
    root = ET.fromstring(svg_text)
    items = walk(root)
    labels = [(num(el.get("x")) + dx, num(el.get("y")) + dy, " ".join("".join(el.itertext()).split())) for el, dx, dy, _ in items if tag(el) == "text" and "".join(el.itertext()).strip()]
    rects, strokes, lines = [], {}, []
    for el, dx, dy, other in items:
        kind = tag(el)
        width = el.get("stroke-width")
        if width and kind in ("line", "path", "polyline", "polygon", "rect"):
            key = ft(num(width))
            strokes[key] = strokes.get(key, 0) + 1
        if kind == "rect":
            x, y, w, h = num(el.get("x")) + dx, num(el.get("y")) + dy, num(el.get("width")), num(el.get("height"))
            if w <= 0 or h <= 0:
                continue
            cx, cy = x + w / 2, y + h / 2
            near = nearest_label(cx, cy, labels)
            rects.append(
                {
                    "x_px": round(x, 1),
                    "y_px": round(y, 1),
                    "w_ft": ft(w),
                    "h_ft": ft(h),
                    "area_sqft": round(ft(w) * ft(h)),
                    "label": near[0] if near else "",
                    "label_ft_away": ft(near[1]) if near else None,
                    "note": "transform not applied" if other else "",
                }
            )
        elif kind == "line" and not other:
            x1, y1, x2, y2 = num(el.get("x1")) + dx, num(el.get("y1")) + dy, num(el.get("x2")) + dx, num(el.get("y2")) + dy
            lines.append((x1, y1, x2, y2, el.get("stroke") or "", num(width)))
    rects.sort(key=lambda r: -r["area_sqft"])
    return {"rects": rects, "strokes_ft": dict(sorted(strokes.items())), "gaps": gaps(lines)}


def gaps(lines: list[tuple[float, float, float, float, str, float]]) -> list[dict]:
    """The openings between consecutive collinear axis-aligned segments of one stroke."""
    runs: dict[tuple[str, int, str, float], list[tuple[float, float]]] = {}
    for x1, y1, x2, y2, stroke, width in lines:
        if abs(y1 - y2) <= ALIGN and abs(x1 - x2) > ALIGN:
            runs.setdefault(("h", round((y1 + y2) / 2 / ALIGN), stroke, width), []).append((min(x1, x2), max(x1, x2)))
        elif abs(x1 - x2) <= ALIGN and abs(y1 - y2) > ALIGN:
            runs.setdefault(("v", round((x1 + x2) / 2 / ALIGN), stroke, width), []).append((min(y1, y2), max(y1, y2)))
    out: list[dict] = []
    for (axis, fixed, _stroke, width), spans in sorted(runs.items()):
        spans.sort()
        for (_, end), (start, _) in zip(spans, spans[1:]):
            if start - end > ALIGN:
                out.append({"axis": axis, "at_px": fixed * ALIGN, "from_px": round(end, 1), "gap_ft": ft(start - end), "wall_ft": ft(width)})
    return out


def render(name: str, data: dict) -> str:
    lines = [f"size-table: {name} - 3 px = 1 ft; {len(data['rects'])} rects, {len(data['gaps'])} wall gaps"]
    lines.append(f"{'w ft':>7}{'h ft':>7}{'sq ft':>8}  {'at px':<14}{'label (ft away)':<44}note")
    for r in data["rects"]:
        label = f"{r['label'][:34]} ({r['label_ft_away']})" if r["label"] else "-"
        lines.append(f"{r['w_ft']:>7}{r['h_ft']:>7}{r['area_sqft']:>8}  {str(r['x_px']) + ',' + str(r['y_px']):<14}{label:<44}{r['note']}")
    lines.append("wall gaps (openings between collinear segments): " + ("; ".join(f"{g['gap_ft']} ft {g['axis']}@{g['at_px']:g} from {g['from_px']:g} (wall {g['wall_ft']} ft)" for g in data["gaps"]) or "none found - check gates drawn another way"))
    lines.append("stroke widths in ft (count): " + ", ".join(f"{k} ({v})" for k, v in data["strokes_ft"].items()))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("plan", help="the plan's SVG")
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    path = pathlib.Path(args.plan)
    if not path.is_file():
        print(f"size-table: no such plan - {path}", file=sys.stderr)
        return 2
    data = table(path.read_text(encoding="utf-8"))
    print(render(path.name, data))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
