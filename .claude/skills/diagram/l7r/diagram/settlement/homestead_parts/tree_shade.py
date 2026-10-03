"""Does a tree stand in a threshing yard's or a garden bed's sun? (GM 2026-10-02: "no canopy trees should be exempt".)

One predicate and one reach for every canopy tree on a scripted map (feature 310): the persimmon's seat
(`fixture_seats._persimmon`), the placer's test between neighbors (`fit._persimmon_sun_conflict`), every crown placer's
keep-out (`KeepoutsMixin._sun_keepouts`, read by `_crown_covers`), the woodland commons, the scrub's pines and the planted
dikes' trees, and the finished map's check (`trees_shading_plots`, run by the gate and the cohort audit). The sun crosses a
plot from the southeast at nine to the southwest at three, so a tree throws its shadow on the plot from anywhere within the
reach to its east, its west or its south, from the plot's north edge down; a tree north of that line throws its shadow away
from it. Measured as a rectangle, the record's knowing simplification of the wedge the moving sun sweeps
(research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html). Bamboo is not held (the GM's "maybe bamboo"), nor the
coppiced mulberry and the clipped tea hedge, which are not canopy (spec 310's Decisions).

Research: plumbing - NONE
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

#: THE REACH, for every canopy tree (GM 2026-10-02, feature 310; first the persimmon's alone). The windbreak's (`WEST_SUN_FT`):
#: a 10 m (~33 ft) tree, the least height the record draws a tree at, throws about 50 ft of its 3 pm shadow east, and the
#: 9 am shadow mirrors it west - held as the windbreak's lane is, a rectangle from the plot's north edge to 50 ft below its
#: south edge, on both sides and below. A GUESS for the height (the record's least; taller trees would reach further).
CANOPY_SHADE_FT = 50.0
"""Research: canopy shade reach - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: 50 ft east, west and south of a plot"""

Box = Sequence[float]  # (center x, center y, width, height), +y south


def crown_shades(cx: float, cy: float, r: float, plot: Box, reach: float) -> bool:
    """Does a crown of radius `r` at (`cx`, `cy`) meet `plot`'s sun ground - the plot widened by `reach` east and west and
    deepened by `reach` to the south, from its north edge?"""
    return crown_in_ground(cx, cy, r, sun_ground(plot, reach))


def sun_ground(plot: Box, reach: float) -> tuple[float, float, float, float]:
    """`plot`'s sun ground as `(x0, x1, y0, y1)`: the plot widened by `reach` east and west and deepened by `reach` to the south,
    from its north edge. Taken once per plot by a caller asking many crowns of the same plots (feature 314: the persimmon's
    seat asked it of every plot at every rake for every pace, a tenth of the homesteads stage).

    Research:
        sun ground as a rectangle - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: from the plot's
            north edge, widened east and west and deepened south by the reach
    """
    px, py, pw, ph = (float(v) for v in plot[:4])
    return px - pw / 2 - reach, px + pw / 2 + reach, py - ph / 2, py + ph / 2 + reach


def crown_in_ground(cx: float, cy: float, r: float, ground: tuple[float, float, float, float]) -> bool:
    """Does a crown of radius `r` at (`cx`, `cy`) meet the sun ground `(x0, x1, y0, y1)` (`sun_ground`)?"""
    x0, x1, y0, y1 = ground
    dx = cx - min(max(cx, x0), x1)
    dy = cy - min(max(cy, y0), y1)
    return dx * dx + dy * dy < r * r


def sun_box(plot: Box, reach: float) -> tuple[float, float, float, float]:
    """`plot`'s sun ground as a (center x, center y, half-width, half-height) box - the keep-out form `_crown_covers` reads,
    against which a crown's disc meets it exactly when `crown_shades` says so."""
    x0, x1, y0, y1 = sun_ground(plot, reach)
    return ((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2)


def plot_box(o: Mapping[str, Any]) -> tuple[float, float, float, float] | None:
    """A yard's or bed's box as drawn: its quad's extent where it records one (the plot turned with its house), else its
    recorded box."""
    poly = o.get("poly")
    if poly:
        xs, ys = [float(p[0]) for p in poly], [float(p[1]) for p in poly]
        return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys))
    if all(k in o for k in ("x", "y", "w", "h")):
        return (float(o["x"]), float(o["y"]), float(o["w"]), float(o["h"]))
    return None


def map_trees(M: Mapping[str, Any]) -> list[tuple[str, float, float, float]]:
    """Every canopy tree the map records, as (kind, x, y, r): the crowns (`tree_crowns`, the persimmon's among them), the
    scrub's pines (`scrub_pines`) and the planted dikes' trees (`planted_trees`, each run's kept trees).

    Research:
        which trees are canopy - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: crowns, scrub pines
            and dike trees; bamboo, mulberry and tea not held
    """
    tc = M.get("tree_crowns") or []
    out = [("crown", float(tc[i]), float(tc[i + 1]), float(tc[i + 2])) for i in range(0, len(tc) - 2, 3)]
    out += [("pine", float(t[0]), float(t[1]), float(t[2])) for t in M.get("scrub_pines") or ()]
    out += [(str(run.get("kind", "planted")), float(t[0]), float(t[1]), float(t[2])) for run in M.get("planted_trees") or () for t in run.get("trees") or ()]
    return out


def trees_shading_plots(M: Mapping[str, Any], reach_ft: float) -> list[tuple[str, str, tuple[float, float], tuple[float, float]]]:
    """Each (plot kind, tree kind, tree center, plot center) where a recorded canopy tree stands in a threshing yard's or a
    garden bed's sun ground, `reach_ft` feet (drawn at the map's `ftpx`, feet per pixel)."""
    meta = M.get("meta") or {}
    reach = reach_ft / float(meta.get("ftpx", 1.0) or 1.0)
    plots = [(kind, b) for kind in ("threshing_yards", "gardens") for o in M.get(kind) or () if (b := plot_box(o)) is not None]
    out = []
    for tk, x, y, r in map_trees(M):
        for kind, b in plots:
            if crown_shades(x, y, r, b, reach):
                out.append((kind, tk, (x, y), (b[0], b[1])))
    return out
