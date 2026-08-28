"""Town and city policy helpers - fire features, the theater stage, ward interiors, the ring road (feature 145: moved out of common_02 so the hamlet path, which never calls them, never executes the module that holds them; the module-level floor then means what the GM said)."""

import math
from collections.abc import Sequence
from typing import Any

from .common_01_geometry import (
    Manifest,
    Poly,
    Pt,
    _struct_rect,
    point_in_poly,
    poly_area,
    rect_corners,
    seg_dist,
    sweep_hi,
)
from .common_02_overlap_policy import in_ellipse
from .common_03_capacity import DWELLING_KINDS, RESERVE_CAP_FRAC, RHO_CANONICAL


def _ward_interior(fence: Any, wall: Any) -> Any:
    """Close a samurai-ward FENCE polyline against the city wall ring: the ward's interior polygon.

    The fence's ends abut the rampart (city_ward_fence_meets_wall holds that), so the fence plus
    the wall arc between its ends encloses the ward. Two arcs qualify; the ward is the SMALLER
    enclosed region - a ward is a quarter carved off the city, never the larger half (all three
    pool cities measure 21-25% of the walled area). None when there is nothing to close (no wall
    ring / a degenerate fence) - the caller skips rather than guesses. Deliberately independent of
    settlement.ward_interior: the check must not trust the arithmetic of the engine it grades."""
    if not wall or len(wall) < 3 or not fence or len(fence) < 2:
        return None
    # ARC-LENGTH closure, not nearest-VERTEX closure: a fence end abuts the rampart mid-EDGE, so
    # walking vertex indices from "the nearest vertex" can skip (or wrongly include) the vertex on
    # the far side of the junction, and the resulting polygon self-intersects - a bowtie, whose
    # shoelace area under-measures by cancellation and steals the smaller-area vote (caught by the
    # square-wall unit test). Projecting each end onto the ring and collecting the vertices whose
    # arc position lies strictly between the two junctions, in traversal order, yields a SIMPLE
    # polygon for both candidate closures, so the smaller-area rule is sound.
    ring = list(wall) + [wall[0]]
    arcs = [0.0]
    for i in range(len(ring) - 1):
        arcs.append(arcs[-1] + math.hypot(ring[i + 1][0] - ring[i][0], ring[i + 1][1] - ring[i][1]))
    perim = arcs[-1]
    if perim <= 0:
        return None

    def project(p: Any) -> float:
        best: tuple[float, float] | None = None
        for i in range(len(ring) - 1):
            ax, ay = ring[i]
            bx, by = ring[i + 1]
            dx, dy = bx - ax, by - ay
            length2 = dx * dx + dy * dy
            t = 0.0 if length2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / length2))
            qx, qy = ax + t * dx, ay + t * dy
            d = (p[0] - qx) ** 2 + (p[1] - qy) ** 2
            if best is None or d < best[0]:
                best = (d, arcs[i] + t * math.sqrt(length2))
        return 0.0 if best is None else best[1]

    def area(poly: Any) -> float:
        a = 0.0
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            a += x1 * y2 - x2 * y1
        return abs(a) / 2

    t0, t1 = project(fence[-1]), project(fence[0])
    fwd_span = (t1 - t0) % perim
    fwd = sorted(((arcs[i] - t0) % perim, wall[i]) for i in range(len(wall)))
    arc_fwd = [v for o, v in fwd if 1e-6 < o < fwd_span - 1e-6]
    back = sorted(((t0 - arcs[i]) % perim, wall[i]) for i in range(len(wall)))
    arc_back = [v for o, v in back if 1e-6 < o < (perim - fwd_span) - 1e-6]
    pa = list(fence) + arc_fwd
    pb = list(fence) + arc_back
    return pa if area(pa) <= area(pb) else pb


def city_capacity(M: Manifest, step: float = 8, grid_step: float | None = None) -> dict[str, Any] | None:
    """SPACE-BUDGET ANALYSIS: is the city wall sized to hold its target population?

    Guessing a wall size and then grinding placements is backwards - the honest process is to
    MEASURE. This grid-samples the walled interior (every `step` px), classes each cell as
    dwelling / civic-overhead / water / trunk-circulation / residential-street / field / OPEN,
    reads the density the built residential quarters actually achieve, and projects whether
    filling the OPEN ground would reach the target. Returns a dict with a verdict
    ('enlarge' | 'shrink' | 'densify' | 'sized_and_packed'), the space budget, and a suggested wall SCALE so
    the wall can be resized ONCE to the right size rather than by trial and error. A city WITH
    an agricultural district commits its slack to fields (canon), so field cells are excluded
    from both the residential ground and the wasted-open ground."""
    meta = M.get("meta", {})
    wall = M.get("wall")
    pop = meta.get("population")
    if not wall or not pop:
        return None
    T = pop / 5.0
    bound = M.get("ring_road") or (list(wall) + [wall[0]])
    xs = [p[0] for p in bound]
    ys = [p[1] for p in bound]
    # bound the sweep span so a malformed coordinate (a wall/ring vertex millions of px off) cannot
    # blow the cell + ASCII grid sweeps up to billions of cells and hang the validator (both sweeps
    # below run over x0..x1 / y0..y1); a real map's span is far under sweep_hi's cap.
    x0, x1, y0, y1 = min(xs), sweep_hi(min(xs), max(xs), step), min(ys), sweep_hi(min(ys), max(ys), step)

    def _rects(items: Sequence[dict[str, Any]], vscale: float = 1.0) -> list[list[tuple[float, float]]]:
        out: list[list[tuple[float, float]]] = []
        for it in items:
            if "w" not in it:
                continue
            out.append(rect_corners({"x": it["x"], "y": it["y"], "w": it["w"], "h": it["h"] * vscale, "rot": it.get("rot", 0)}))
        return out

    dwell_r = _rects([b for b in M.get("buildings", []) if b.get("kind") in DWELLING_KINDS])
    dwell_r += [rect_corners(_struct_rect(h)) for h in M.get("houses", []) if point_in_poly(h["x"], h["y"], wall)]
    civic = (
        M.get("ministries", [])
        + M.get("religious", [])
        + M.get("flophouses", [])
        + M.get("storehouses", [])
        + M.get("cemeteries", [])
        + M.get("mausoleums", [])
        + M.get("merchant_estates", [])
        + M.get("inspection_stations", [])
        + [b for b in M.get("buildings", []) if b.get("kind") in ("shop", "inn", "stables")]
        + ([M["governor_mansion"]] if M.get("governor_mansion") else [])
        + M.get("docks", [])
    )
    civic_r = _rects(civic)
    ts9_raw = M.get("theater_stage")
    for ts9 in ts9_raw if isinstance(ts9_raw, list) else ([ts9_raw] if ts9_raw else []):
        civic_r.append(rect_corners({"x": ts9["x"], "y": ts9["y"], "w": ts9["w"], "h": ts9["h"] * 1.3, "rot": ts9.get("rot", 0)}))
    field_polys = [f["outline"] for f in M.get("fields", []) if point_in_poly((f["bbox"][0] + f["bbox"][2]) / 2, (f["bbox"][1] + f["bbox"][3]) / 2, wall)]
    field_polys += [dp["poly"] for dp in M.get("dry_plots", []) if point_in_poly(dp["poly"][0][0], dp["poly"][0][1], wall)]
    water = ([(M["moat"], M.get("moat_width", 22) / 2)] if M.get("moat") else []) + [(cc["poly"], cc.get("w", 12) / 2) for cc in M.get("canals", [])]
    trunk = [(M["road"], M.get("road_width", 30) / 2)] if M.get("road") else []
    trunk += [(r["pts"], r["w"] / 2) for r in M.get("roads", [])]
    if M.get("ring_road"):
        trunk.append((M["ring_road"], M.get("ring_road_width", 15) / 2 + 24))
    res_st = [(s["pts"], s.get("w", 12) / 2) for s in M.get("town_streets", [])] + [(a["pts"], a.get("w", 8) / 2) for a in M.get("alleys", [])]

    # PERFORMANCE: the sweeps below sample ~40k grid points on a provincial city, and the naive
    # form probed every dwelling/civic rect, field poly, and street segment from every point -
    # ~23M point_in_poly/seg_dist calls, ~13s per gate run (profiled on Tango, 2026-07-20), paid
    # on every in-session map iteration and every city regression fixture. The features are tiny
    # relative to the walled span, so index them into coarse spatial bins and test each sample
    # point only against the features whose bounding box overlaps its bin. The classification is
    # IDENTICAL to the naive sweep: same sample points, same predicates in the same priority
    # order, and the bin prefilter is conservative (a poly lies inside its bbox; a "within hw of
    # segment" capsule lies inside the segment bbox inflated by hw), so no true hit is skipped.
    BIN = step * 8

    def _bucket_polys(polys: Sequence[Poly]) -> dict[tuple[int, int], list[Poly]]:
        out: dict[tuple[int, int], list[Poly]] = {}
        for p in polys:
            pxs = [q[0] for q in p]
            pys = [q[1] for q in p]
            for bx in range(int(min(pxs) // BIN), int(max(pxs) // BIN) + 1):
                for by in range(int(min(pys) // BIN), int(max(pys) // BIN) + 1):
                    out.setdefault((bx, by), []).append(p)
        return out

    def _bucket_lines(lines: Sequence[tuple[Poly, float]]) -> dict[tuple[int, int], list[tuple[Pt, Pt, float]]]:
        out: dict[tuple[int, int], list[tuple[Pt, Pt, float]]] = {}
        for pts, hw in lines:
            for k in range(len(pts) - 1):
                a, b = pts[k], pts[k + 1]
                for bx in range(int((min(a[0], b[0]) - hw) // BIN), int((max(a[0], b[0]) + hw) // BIN) + 1):
                    for by in range(int((min(a[1], b[1]) - hw) // BIN), int((max(a[1], b[1]) + hw) // BIN) + 1):
                        out.setdefault((bx, by), []).append((a, b, hw))
        return out

    dwell_bk, civic_bk, field_bk = _bucket_polys(dwell_r), _bucket_polys(civic_r), _bucket_polys(field_polys)
    water_bk, trunk_bk, res_bk = _bucket_lines(water), _bucket_lines(trunk), _bucket_lines(res_st)
    pond = M.get("pond")

    def _classify(gx: float, gy: float) -> str:
        """Class one sample point: 'outside' the wall, else the first matching ground category
        in the fixed priority order. Shared by the count sweep and the ASCII-map sweep so the
        two can never disagree."""
        b = (int(gx // BIN), int(gy // BIN))
        if not point_in_poly(gx, gy, wall):
            return "outside"
        if any(point_in_poly(gx, gy, r) for r in dwell_bk.get(b, [])):
            return "dwell"
        if any(point_in_poly(gx, gy, r) for r in civic_bk.get(b, [])):
            return "civic"
        if (pond and in_ellipse(gx, gy, pond)) or any(seg_dist(gx, gy, a, bb) < hw for a, bb, hw in water_bk.get(b, [])):
            return "water"
        if any(point_in_poly(gx, gy, p) for p in field_bk.get(b, [])):
            return "field"
        if any(seg_dist(gx, gy, a, bb) < hw for a, bb, hw in trunk_bk.get(b, [])):
            return "trunk"
        if any(seg_dist(gx, gy, a, bb) < hw for a, bb, hw in res_bk.get(b, [])):
            return "res_st"
        return "open"

    c = {"dwell": 0, "civic": 0, "water": 0, "trunk": 0, "res_st": 0, "field": 0, "open": 0}
    gx = x0
    while gx <= x1:
        gy = y0
        while gy <= y1:
            kind = _classify(gx, gy)
            if kind != "outside":
                c[kind] += 1
            gy += step
        gx += step
    cell = step * step
    A = {k: v * cell for k, v in c.items()}
    ring_area = sum(A.values()) or 1
    # OPTIONAL coarse ASCII map of the interior classification, so the report shows WHERE the
    # open ground is (not just how much) - the operator can then aim new quarters at it rather
    # than guess. Reuses the rects/lines already built above; a second coarse sweep is cheap.
    grid_rows = None
    if grid_step:
        _sym = {"outside": " ", "dwell": "D", "civic": "C", "water": "~", "trunk": "#", "res_st": "+", "field": "F", "open": "."}
        grid_rows = []
        gy = y0
        while gy <= y1:
            row = []
            gx = x0
            while gx <= x1:
                row.append(_sym[_classify(gx, gy)])
                gx += grid_step
            grid_rows.append("".join(row))
            gy += grid_step
    # PLACED dwellings: for a walled city only those INSIDE the wall count (feature 006 - the
    # extramural spill must not inflate the figure); in-wall farmhouses count too.
    D = len([b for b in M.get("buildings", []) if b.get("kind") in DWELLING_KINDS and point_in_poly(b["x"], b["y"], wall)]) + sum(1 for h in M.get("houses", []) if point_in_poly(h["x"], h["y"], wall))
    # residential-CAPABLE ground = the interior minus the fixed overhead (government + temples +
    # wharf/dock/gates/shops, water, trunk roads + ring road + wall berm, committed field ground) -
    # the per-cell classification already excludes civic buildings, water, trunk, and fields (an
    # agricultural-district reserve draws as fields, so it is already out). A drill-ground / garden
    # reserve draws as OPEN, so subtract those declared reserves explicitly (feature 006): they are
    # committed to non-housing and must not count toward what the wall can house.
    quarters = M.get("quarters", [])
    civic_q = sum(poly_area(q["poly"]) for q in quarters if q.get("zone") == "civic")
    reserve_q = sum(poly_area(q["poly"]) for q in quarters if q.get("zone") == "reserve")
    # ALL reserve ground is committed to non-housing and must not count toward what the wall can
    # house. An agricultural district draws mostly as FIELDS - those cells are already classed out -
    # so deduct only its non-field remainder (farmhouse yards, groves, margins between combs).
    # (Feature 009: the earlier deduction skipped agricultural reserves entirely, leaving ~72k px^2
    # of Tango's reserve slack inside res_capable and diluting RHO_CANONICAL - see its comment.)
    reserve_deduct = max(reserve_q - A["field"], 0.0)
    reserve_frac = reserve_q / ring_area
    overhead = A["civic"] + A["water"] + A["trunk"] + A["field"]
    res_capable = max(A["dwell"] + A["res_st"] + A["open"] - reserve_deduct, 1)  # everything that could be residential
    inherent_cap = res_capable * RHO_CANONICAL  # dwellings the wall CAN hold, well-packed
    open_frac = A["open"] / ring_area
    # size the wall so its residential-capable ground holds T at the canonical density (+5% slack).
    need_res = (T / RHO_CANONICAL) * 1.05
    scale = math.sqrt((ring_area - res_capable + need_res) / ring_area)
    # per-quarter density (residential + mixed), measured over non-civic ground - the report the
    # operator reads to see WHICH quarter is under-built, not just the city-wide total.
    per_quarter = []
    if quarters:
        civ_rects = [
            _struct_rect(cc)
            for cc in (
                M.get("ministries", [])
                + M.get("religious", [])
                + M.get("cemeteries", [])
                + M.get("mausoleums", [])
                + M.get("storehouses", [])
                + ([M["governor_mansion"]] if M.get("governor_mansion") else [])
            )
            if "w" in cc
        ]
        dpts = [(b["x"], b["y"]) for b in M.get("buildings", []) if b.get("kind") in DWELLING_KINDS and point_in_poly(b["x"], b["y"], wall)]
        for q in quarters:
            if q.get("zone") not in ("residential", "mixed"):
                continue
            qa = poly_area(q["poly"])
            cf = sum(r["w"] * r["h"] for r in civ_rects if point_in_poly(r["x"], r["y"], q["poly"]))
            nq = sum(1 for x, y in dpts if point_in_poly(x, y, q["poly"]))
            per_quarter.append({"name": q.get("name"), "zone": q["zone"], "dwellings": nq, "density": round(nq / max(qa - cf, 1), 5)})
    # VERDICT -> one clear ACTION (feature 006 rename of the earlier too_small/too_big/underpacked/
    # about_right). The densify boundary tracks population_tol so the capacity verdict and the
    # population check never disagree; a wall fillable only by OVER-CAP reserve reads as shrink
    # (emptiness cannot be laundered as reserve).
    pop_tol = meta.get("population_tol", 0.07)
    if inherent_cap < 0.9 * T:
        verdict = "enlarge"  # even well-packed the wall cannot hold T
    elif inherent_cap > 1.4 * T or reserve_frac > RESERVE_CAP_FRAC:
        verdict = "shrink"  # far more room than T needs (or only fillable via over-cap reserve)
    elif (1 - pop_tol) * T > D:
        verdict = "densify"  # the WALL is right; the placement is too sparse
    else:
        verdict = "sized_and_packed"
    return {
        "verdict": verdict,
        "target_dwellings": round(T),
        "placed": D,
        "inherent_capacity": round(inherent_cap),
        "ring_area": round(ring_area),
        "res_capable_area": round(res_capable),
        "overhead_area": round(overhead),
        "civic_area": round(civic_q),
        "reserve_area": round(reserve_q),
        "reserve_frac": round(reserve_frac, 3),
        "open_frac": round(open_frac, 3),
        "suggested_wall_scale": round(scale, 3),
        "areas": {k: round(v) for k, v in A.items()},
        "per_quarter": per_quarter,
        "grid": grid_rows,
        "grid_origin": (round(x0), round(y0)),
        "grid_step": grid_step,
    }
