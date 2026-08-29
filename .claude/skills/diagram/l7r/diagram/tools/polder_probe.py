"""THE POLDER BLOCK ALONE, WITH ITS NUMBERS - the geometry loop without a map (feature 149, US1).

WHY THIS EXISTS. Feature 150's T55 - "one of the vegetable grounds overlaps with the irrigated channels"
- took 79.8 minutes for a fix whose final diff is one function, and **19 of those minutes were map rolls**
(29-100 s each, median 47 s) whose only purpose was to produce numbers that need no houses, no hinterland
and no render. Four different algorithms were tried; each attempt cost a minute of wall clock before it
said anything. This prints the same numbers in about a second.

WHAT IT IS NOT. It is not a second implementation of the geometry: it builds the block through
`plan_site` + `fit_polder`, the exact path `stage_polder` takes, so it cannot pass while the map fails.
`tests/tools/test_polder_probe.py` holds that line by checking the probe's numbers against a rolled
manifest's.

WHAT IT REPORTS, and why each number is here rather than another:

- parcels overlapping a channel      the T55 rule itself (`_plots_clear_of_channels`)
- minimum and median berm            the T55 review's finding: the cut edges kept 1.2 px where the
                                     fabric keeps 7.2, so the crop met the waterline
- acreage against target             what a cut costs (the shipped projection 0.29%, the declined
                                     half-plane clip 3.4%)
- vertices and square corners        `polder_parcels_are_organic`'s own two numbers, measured with the
                                     engine's own `_sharp_corners`
- ring point counts                  the densify/thin balance: one cut of T55 bloated every ring from
                                     ~32 points to ~200 and another thinned them to 15
- wall time                          this tool's own bar (SC-001: about a second, at most three)

Exits non-zero when a metric would fail the gate, so it can guard an expensive run.
"""

from __future__ import annotations

import argparse
import math
import statistics
import time
from typing import Any

from l7r.diagram.hamletgen.consts import POLDER_ARCHETYPES, POLDER_FABRIC, POND_LAYOUT_MOSAIC
from l7r.diagram.hamletgen.plan import HamletSpec, plan_site
from l7r.diagram.hamletgen.water import fit_polder
from l7r.diagram.settlement import _sharp_corners
from l7r.diagram.settlement._geom import point_in_poly, seg_dist
from l7r.diagram.sitegen.geom import net_acres

MIN_VERTICES = 12  # `polder_parcels_are_organic`: a ruled quad has 4, a hand-piled outline never nears it
MAX_SQUARE_MEAN = 2.5  # ...and across the fabric, at most this many still-square corners per parcel


def _bands(net: dict[str, Any]) -> list[tuple[list[Any], float]]:
    """Every channel as (polyline, half-width) - the drawn water a parcel must stay out of."""
    out: list[tuple[list[Any], float]] = []
    for c in net.get("channels", []):
        pts = [(float(x), float(y)) for x, y in c.get("pts", [])]
        if len(pts) >= 2:
            out.append((pts, max(float(c.get("w", 0.0)), float(c.get("w_tail", 0.0))) / 2))
    return out


def _clearance(ring: list[Any], bands: list[tuple[list[Any], float]]) -> float:
    """The closest this parcel's outline comes to the EDGE of any channel - the BERM the crop keeps back."""
    best = math.inf
    for pts, hw in bands:
        for i in range(len(pts) - 1):
            for q in ring:
                best = min(best, seg_dist(q[0], q[1], pts[i], pts[i + 1]) - hw)
    return best


def _crosses(ring: list[Any], bands: list[tuple[list[Any], float]], step: float = 3.0) -> bool:
    """Does any channel RUN THROUGH this parcel? Sampled along the run, not read off the parcel's
    vertices: a lateral crosses a parcel with no vertex of either near the other (T55's own trap - the
    first cut of that fix measured vertices and reported a clean block while a ditch ran the parcel's
    whole length). The band's edges are sampled too, so a channel grazing the outline counts."""
    for pts, hw in bands:
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            n = max(1, int(math.dist(a, b) / step))
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            for k in range(n + 1):
                x, y = a[0] + dx * k / n, a[1] + dy * k / n
                for off in (-hw, 0.0, hw):
                    if point_in_poly(x - dy / ln * off, y + dx / ln * off, ring):
                        return True
    return False


def measure(net: dict[str, Any], target_acres: float, ftpx: float = 1.0) -> dict[str, Any]:
    """Every metric this tool reports, from a built block. Pure - the tests drive it directly."""
    bands = _bands(net)
    rings = [[(float(x), float(y)) for x, y in p["poly"]] for p in net.get("plots", [])]
    clears = [_clearance(r, bands) for r in rings] if bands else []
    offenders = [(i, r) for i, r in enumerate(rings) if bands and _crosses(r, bands)]
    verts = [len(r) for r in rings]
    squares = [_sharp_corners(r) for r in rings]
    return {
        "parcels": len(rings),
        "overlaps": [(i, (round(sum(q[0] for q in r) / len(r)), round(sum(q[1] for q in r) / len(r)))) for i, r in offenders],
        "berm_min": round(min(clears), 2) if clears else None,
        "berm_median": round(statistics.median(clears), 2) if clears else None,
        "acres": round(net_acres(net, ftpx), 2),  # the map's own conversion (`stage_polder`), not the block's raw figure - they differ by ftpx and the probe must not invent a second answer
        "acres_target": round(target_acres, 2),
        "vertices_min": min(verts) if verts else 0,
        "vertices_thin": [i for i, v in enumerate(verts) if v < MIN_VERTICES],
        "squares_mean": round(sum(squares) / len(squares), 2) if squares else 0.0,
        "ring_points": (min(verts), int(statistics.median(verts)), max(verts)) if verts else (0, 0, 0),
    }


def verdict(m: dict[str, Any]) -> list[str]:
    """The metrics that would fail the gate, named. Empty means the block is clean."""
    bad = []
    if m["overlaps"]:
        bad.append(f"{len(m['overlaps'])} parcel(s) overlap a channel at {[c for _i, c in m['overlaps']][:3]}")
    if m["vertices_thin"]:
        bad.append(f"{len(m['vertices_thin'])} parcel(s) under {MIN_VERTICES} vertices (polder_parcels_are_organic)")
    if m["squares_mean"] > MAX_SQUARE_MEAN:
        bad.append(f"square-corner mean {m['squares_mean']} over {MAX_SQUARE_MEAN} (polder_parcels_are_organic)")
    return bad


def probe(seed: int, archetype: str = "mulberry_dike_fishpond", households: int = 16, pond_layout: str | None = "mosaic") -> tuple[dict[str, Any], float]:
    """Build one block the way the map does, and measure it. Returns (metrics, seconds)."""
    if archetype not in POLDER_ARCHETYPES:
        raise SystemExit(f"polder-probe: {archetype!r} is not a polder archetype; expected one of {POLDER_ARCHETYPES}")
    t0 = time.time()
    plan = plan_site(HamletSpec(name=f"Probe-{seed:02d}", seed=seed, households=households, field_archetype=archetype, pond_layout=pond_layout))
    net = fit_polder(plan, seed, fabric=POLDER_FABRIC[archetype], mosaic=POND_LAYOUT_MOSAIC if plan.pond_layout == "mosaic" else 0.0)
    return measure(net, plan.target_acres, plan.ftpx), time.time() - t0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="the polder block alone, with its geometry metrics (feature 149)")
    ap.add_argument("--seed", type=int, default=21, help="the block's seed (the reference dike-pond is 21)")
    ap.add_argument("--seeds", default=None, help="comma-separated seeds, for one table over several blocks")
    ap.add_argument("--archetype", default="mulberry_dike_fishpond", choices=POLDER_ARCHETYPES)
    ap.add_argument("--households", type=int, default=16, help="the household count the acreage is fitted to")
    ap.add_argument("--layout", default="mosaic", choices=("grid", "mosaic"), help="a dike-pond's arrangement")
    a = ap.parse_args(argv)
    seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else [a.seed]
    failed = False
    for seed in seeds:
        m, secs = probe(seed, a.archetype, a.households, a.layout)
        bad = verdict(m)
        failed = failed or bool(bad)
        print(f"\033[1mseed {seed}\033[0m  {a.archetype}/{a.layout}  {m['parcels']} parcels  {secs:.2f}s")
        print(f"  overlap        {len(m['overlaps'])} parcel(s) across a channel {[c for _i, c in m['overlaps']][:3]}")
        print(f"  berm           min {m['berm_min']} px, median {m['berm_median']} px  (the fabric's own is what a cut edge must match)")
        print(f"  acreage        {m['acres']} of {m['acres_target']} target")
        print(f"  organic        vertices min {m['vertices_min']} (want >= {MIN_VERTICES}), square-corner mean {m['squares_mean']} (want <= {MAX_SQUARE_MEAN})")
        print(f"  ring points    {m['ring_points'][0]} / {m['ring_points'][1]} / {m['ring_points'][2]}  (min/median/max)")
        for line in bad:
            print(f"  \033[1;31mFAIL\033[0m           {line}")
    return 1 if failed else 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.tools.polder_probe")
    raise SystemExit(main())
