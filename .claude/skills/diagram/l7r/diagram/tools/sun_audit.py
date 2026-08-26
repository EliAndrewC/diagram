"""Measure a map's SUN and its windbreak's PAGE PRESENCE from the recorded manifest: `make sun-audit`.

WHY THIS EXISTS (GM 2026-08-26, feature 133 T10). In one sitting this script was written by hand
three times by the session and twice more by the reviewer, and the two disagreed about the
numbers until they were measuring the same thing. Worse, records were written with numbers that
had not been measured on the artifact ("~30-45 px of canopy shows") and the reviewer's measurement
(0-40, median 15) then cost a correction round. So: MEASURE WITH THIS, THEN WRITE. It reads the
manifest (0.2 s), never re-runs the generator, and prints exactly the figures the sun rules and
the frame rule are judged by:

  - every threshing yard and garden bed: the nearest FARMHOUSE wall to its south with any lateral
    overlap, in feet (rule: >= 39, `yards_unshaded_by_neighbors` / `gardens_unshaded_by_neighbors`);
  - every plot: the nearest WINDBREAK clump west/southwest, in feet (rule: >= 50,
    `village_trees_unshade_from_west`);
  - the belt: visible canopy depth per 25 px band along its length, measured from the view edge
    on the belt's side (the face rule), the median, the blank bands, and clumps whose recorded
    crown lies wholly off the page.

Usage:  make sun-audit [M=pool/hamlets/inashiro.json]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from l7r.diagram.settlement._knobs import windbreak_face

SUN_FT = 39.0
WEST_FT = 50.0


def _rect(o: Any) -> tuple[float, float, float, float]:
    return (o["x"] - o["w"] / 2, o["x"] + o["w"] / 2, o["y"] - o["h"] / 2, o["y"] + o["h"] / 2)


def south_gaps(plots: list[Any], houses: list[Any], ftpx: float) -> list[tuple[float, float, float | None]]:
    """(x, y, gap_ft or None) per plot: the nearest house wall south of it with lateral overlap."""
    out = []
    for p in plots:
        px0, px1, _py0, py1 = _rect(p)
        par = p.get("of")
        gaps = []
        for h in houses:
            if par and abs(h["x"] - par[0]) < 1 and abs(h["y"] - par[1]) < 1:
                continue
            hx0, hx1, hy0, _hy1 = _rect(h)
            if min(px1, hx1) - max(px0, hx0) <= 0:
                continue
            gap = (hy0 - py1) * ftpx
            if gap > -5:
                gaps.append(gap)
        out.append((p["x"], p["y"], min(gaps) if gaps else None))
    return out


def west_gaps(plots: list[Any], belts: list[Any], ftpx: float) -> list[tuple[float, float, float | None]]:
    """(x, y, gap_ft or None) per plot: the nearest windbreak clump in the west/southwest lane."""
    out = []
    for p in plots:
        px0, _px1, py0, py1 = _rect(p)
        gaps = []
        for b in belts:
            r = float(b.get("r") or 0.0)
            for cx, cy in b.get("clumps") or []:
                if cx < px0 + r and py0 - r < cy < py1 + WEST_FT / ftpx + r:
                    gaps.append((px0 - cx - r) * ftpx)
        out.append((p["x"], p["y"], min(gaps) if gaps else None))
    return out


def belt_presence(belt: Any, houses: list[Any], view: list[float]) -> dict[str, Any] | None:
    """Visible canopy depth per 25 px band from the view edge on the belt's side."""
    clumps = belt.get("clumps") or []
    r = float(belt.get("r") or 0.0)
    face = windbreak_face(clumps, r, houses)
    if face is None:
        return None
    axis, sign, _inner = face
    edge = (view[axis] if sign > 0 else view[axis] + view[axis + 2]) if view else 0.0
    along = 1 - axis
    bands: dict[int, float] = {}
    for c in clumps:
        depth = sign * (c[axis] - edge) + r
        band = int(c[along] // 25)
        bands[band] = max(bands.get(band, -1e9), depth)
    depths = [round(v) for _k, v in sorted(bands.items())]
    return {
        "axis": "x" if axis == 0 else "y",
        "edge": edge,
        "depths": depths,
        "median": statistics.median(depths) if depths else 0,
        "blank": sum(1 for d in depths if d <= 0),
        "off_page": sum(1 for c in clumps if sign * (c[axis] - edge) + r <= 0),
        "clumps": len(clumps),
    }


def report(M: dict[str, Any]) -> str:
    meta = M.get("meta", {})
    ftpx = float(meta.get("ftpx") or 1)
    houses = M.get("houses", [])
    yards, gardens = M.get("threshing_yards", []), M.get("gardens", [])
    belts = [g for g in M.get("village_groves", []) if g.get("role") == "windbreak"]
    lines = [f"sun-audit  ftpx={ftpx:g}  houses={len(houses)} yards={len(yards)} beds={len(gardens)} windbreaks={len(belts)}"]
    for label, plots in (("yard", yards), ("bed", gardens)):
        sg = south_gaps(plots, houses, ftpx)
        vals = sorted(round(g) for _x, _y, g in sg if g is not None)
        bad = [(round(x), round(y), round(g)) for x, y, g in sg if g is not None and g < SUN_FT]
        lines.append(f"  {label}s: south gap to nearest house ft {vals} (none: {sum(1 for _x, _y, g in sg if g is None)})  under {SUN_FT:.0f}: {bad or 'none'}")
        wg = west_gaps(plots, belts, ftpx)
        wv = sorted(round(g) for _x, _y, g in wg if g is not None)
        wbad = [(round(x), round(y), round(g)) for x, y, g in wg if g is not None and g < WEST_FT]
        lines.append(f"  {label}s: W/SW gap to nearest belt clump ft {wv[:8]}{'...' if len(wv) > 8 else ''}  under {WEST_FT:.0f}: {wbad or 'none'}")
    for b in belts:
        pres = belt_presence(b, houses, meta.get("view") or [])
        if pres is None:
            lines.append("  belt: no clumps or no houses - no face")
            continue
        lines.append(
            f"  belt: {pres['clumps']} clumps, face on {pres['axis']} at view edge {pres['edge']:.0f}; visible depth per 25 px band "
            f"median {pres['median']:.0f} px, blank bands {pres['blank']}, crowns wholly off-page {pres['off_page']}"
        )
        lines.append(f"        bands: {pres['depths']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("manifest", nargs="?", default="pool/hamlets/inashiro.json")
    a = ap.parse_args(argv)
    print(report(json.loads(Path(a.manifest).read_text())))
    return 0


if __name__ == "__main__":  # pragma: no cover - the make target's entry
    sys.exit(main())
