"""Does a single tree's crown shade a threshing yard or a garden bed? (GM 2026-10-02, `PERSIMMON_SHADE_FT`.)

One predicate for the three places that ask it: the persimmon's seat in its own household (`fixture_seats._persimmon`),
the placer's test between neighbors (`fit._persimmon_sun_conflict`) and the finished map's check
(`persimmons_shading_plots`, run by the gate and the cohort audit). The sun crosses a plot from the southeast at nine to
the southwest at three, so a tree throws its shadow on the plot from anywhere within the reach to its east, its west or
its south, from the plot's north edge down; a tree north of that line throws its shadow away from it. Measured as a
rectangle, the record's knowing simplification of the wedge the moving sun sweeps
(research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

Box = Sequence[float]  # (center x, center y, width, height), +y south


def crown_shades(cx: float, cy: float, r: float, plot: Box, reach: float) -> bool:
    """Does a crown of radius `r` at (`cx`, `cy`) meet `plot`'s sun ground - the plot widened by `reach` east and west and
    deepened by `reach` to the south, from its north edge?"""
    px, py, pw, ph = (float(v) for v in plot[:4])
    x0, x1, y0, y1 = px - pw / 2 - reach, px + pw / 2 + reach, py - ph / 2, py + ph / 2 + reach
    dx = cx - min(max(cx, x0), x1)
    dy = cy - min(max(cy, y0), y1)
    return dx * dx + dy * dy < r * r


def _plot_box(o: Mapping[str, Any]) -> tuple[float, float, float, float] | None:
    """A yard's or bed's box as drawn: its quad's extent where it records one (the plot turned with its house), else its
    recorded box."""
    poly = o.get("poly")
    if poly:
        xs, ys = [float(p[0]) for p in poly], [float(p[1]) for p in poly]
        return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys))
    if all(k in o for k in ("x", "y", "w", "h")):
        return (float(o["x"]), float(o["y"]), float(o["w"]), float(o["h"]))
    return None


def persimmons_shading_plots(M: Mapping[str, Any], reach_ft: float) -> list[tuple[str, tuple[float, float], tuple[float, float]]]:
    """Each (plot kind, persimmon center, plot center) where a drawn persimmon's crown stands in a threshing yard's or a
    garden bed's sun ground, `reach_ft` feet (drawn at the map's `ftpx`, feet per pixel)."""
    meta = M.get("meta") or {}
    reach = reach_ft / float(meta.get("ftpx", 1.0) or 1.0)
    out = []
    for kind in ("threshing_yards", "gardens"):
        for o in M.get(kind) or ():
            box = _plot_box(o)
            if box is None:
                continue
            for t in M.get("persimmons") or ():
                if crown_shades(float(t["x"]), float(t["y"]), float(t["r"]), box, reach):
                    out.append((kind, (float(t["x"]), float(t["y"])), (box[0], box[1])))
    return out
