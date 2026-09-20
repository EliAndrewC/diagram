#!/usr/bin/env python3
"""Where a map's ground-cover scatter actually stands: the base points, parsed from its SVG (feature 256, FR-009).

WHY. The manifest does not record scatter - each tuft is draw-time ink - so the rendered SVG is the only source of
truth, and `settlement-review` is told not to hand-build the parse (the 2026-08-16 cut-bank review spent ~21 tool
uses on it). The parse lives in the engine, `l7r.diagram.tools.scatter_audit.parse_bases`, but nothing wrapped it:
the make-only guard refuses a bare interpreter reaching an engine module, so the contract named something the
agent could not run. This is the wrapper `make scatter-bases` calls.

It MEASURES and never judges (feature 193's ruling: the adjudicating half of the old audit was removed because the
author's allowance is precisely what a review is there to question): per family - blade, dot, pine, crown, reed -
the count of bases, and with `--box x0,y0,x1,y1` the bases inside that world-coordinate window, listed.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

SKILL = pathlib.Path(__file__).resolve().parents[1] / ".claude" / "skills" / "diagram"


def locate(subject: str) -> pathlib.Path:
    """A pool map's SVG from its folder, its stem, or the file itself."""
    path = pathlib.Path(subject)
    if path.is_dir():
        return path / f"{path.name}.svg"
    return path if path.suffix == ".svg" else path.with_name(path.name + ".svg")


def in_box(point: tuple[float, float], box: tuple[float, float, float, float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def render(name: str, bases: dict[str, list[tuple[float, float]]], box: tuple[float, float, float, float] | None, limit: int) -> str:
    lines = [f"scatter-bases: {name} - base points per family, world coordinates; a measurement, never a verdict"]
    for family, points in bases.items():
        lines.append(f"  {family:6s} {len(points):>7,}")
    if box is not None:
        lines.append(f"inside the box {box}:")
        for family, points in bases.items():
            inside = [p for p in points if in_box(p, box)]
            lines.append(f"  {family:6s} {len(inside):>7,}" + ("  " + " ".join(f"({x:.1f},{y:.1f})" for x, y in inside[:limit]) + (" ..." if len(inside) > limit else "") if inside else ""))
    return "\n".join(lines)


def main(argv: list[str] | None = None, parse=None) -> int:  # noqa: ANN001
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("map", help="a pool map: its folder, its stem, or its .svg")
    ap.add_argument("--box", default="", help="x0,y0,x1,y1 in world coordinates: also list the bases inside it")
    ap.add_argument("--limit", type=int, default=40, help="how many points of a family to list inside the box")
    args = ap.parse_args(argv)
    svg = locate(args.map)
    if not svg.is_file():
        print(f"scatter-bases: no render at {svg} - a clone carries none until the map is regenerated", file=sys.stderr)
        return 2
    box = None
    if args.box:
        parts = [float(v) for v in args.box.split(",")]
        if len(parts) != 4:
            print("scatter-bases: --box takes x0,y0,x1,y1", file=sys.stderr)
            return 2
        box = (min(parts[0], parts[2]), min(parts[1], parts[3]), max(parts[0], parts[2]), max(parts[1], parts[3]))
    if parse is None:
        sys.path.insert(0, str(SKILL))
        from l7r.diagram.tools.scatter_audit import parse_bases as parse  # noqa: PLC0415 - the engine's own parse, never a copy
    print(render(svg.stem, parse(svg.read_text(encoding="utf-8")), box, args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
