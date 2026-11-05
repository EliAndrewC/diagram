"""A NUCLEATED CLUSTER SEATED IN RUST (feature 444 T30, the door's first half): what `growth.grow_the_margin` reads, gathered
once the seat region stands, handed to `l7r_phases.seat_households` (`rust/phases/src/homesteads/place.rs` `grow`), and each
household it seats recorded as `Settlement._try_place_bundle` records one - its box placed, its record, its parts and wood
share. Run where `L7R_RUST_SEATING` is set, the Python growth's stand-in while the port is compared; the stage is wired to it,
and the Python growth deleted, once the rest of the stage is ported (`specs/444-work-budget-program/phases/homesteads.port.md`).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT
from l7r.diagram.settlement.rolling.lot import record_parts
from l7r.diagram.settlement.rolling.passage import reserve_way

from ..clearance import margin_of
from ..consts import WEB_HARD_GAP
from .boundary import web_hard_ground

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

#: The cell the free ground is handed over at (ft): half the Rust raster's own, so a point's verdict is its cell center's to 2 ft.
GROUND_CELL_FT = 4.0
"""Research: plumbing - NONE: a raster's grain, under the 9-point rectangle test's spacing"""

#: The registry keys a homestead's parts are filed under (`rolling/lot.py` `BUNDLE_PART_KEYS`, `held_part_records`).
PART_KEYS = ("houses", "threshing_yards", "gardens", "farm_sheds", "byres", "farm_fixtures", "retirement_houses")
"""Research: plumbing - NONE: the registry's own keys"""


def ground_cells(s: Settlement) -> tuple[tuple[float, float], float, int, list[bool]]:
    """The free ground over the canvas at `GROUND_CELL_FT`, row by row: a cell taken where the site's raster surely takes its
    center, or - its center in a cell the raster leaves uncertain - the site's chains or corridors refuse it there (the tests
    `access.site_samples_clear` asks, every uncertain cell at once as `gap_ways.lane_layers` asks them), or a box placed before
    the growth (a shared byre's pocket) covers it. Built in arrays: a canvas is half a million cells.

    Research: plumbing - NONE: the site boundary's own verdicts, read at cell centers"""
    import numpy as np

    from l7r.diagram.settlement._geom.primitives import chain_violated_many

    c = GROUND_CELL_FT
    nx, ny = max(1, math.ceil(float(s.W) / c)), max(1, math.ceil(float(s.H) / c))
    cx, cy = (np.arange(nx) + 0.5) * c, (np.arange(ny) + 0.5) * c
    taken = np.zeros((ny, nx), bool)
    fg = getattr(s, "_free_ground", None)
    gx, gy = np.meshgrid(cx, cy)
    uncertain = np.ones((ny, nx), bool)
    if fg is not None:
        fg.lines_edge_points([])  # its state array, built once
        ki = np.floor((gx - fg.x0) / fg.cell).astype(np.int64)
        kj = np.floor((gy - fg.y0) / fg.cell).astype(np.int64)
        inside = (ki >= 0) & (fg.nx > ki) & (kj >= 0) & (fg.ny > kj)
        state = np.zeros((ny, nx), np.int8)
        state[inside] = fg._state[ki[inside], kj[inside]]
        taken |= state == 1
        uncertain = state == 0
    ja, ia = np.nonzero(uncertain & ~taken)
    chains, corr = getattr(s, "_site_chains", None), getattr(s, "_site_corridors", None)
    if len(ja) and chains:
        bad = chain_violated_many(cx[ia], cy[ja], chains, 0.0)
        taken[ja[bad], ia[bad]] = True
        ja, ia = ja[~bad], ia[~bad]
    if corr is not None:
        for j, i in zip(ja.tolist(), ia.tolist(), strict=True):
            if corr.hit_points([(float(cx[i]), float(cy[j]))]):
                taken[j, i] = True
    for px, py, pw, ph in (tuple(float(v) for v in p[:4]) for p in getattr(s, "placed", None) or ()):
        taken[(np.abs(cy - py) <= ph / 2)[:, None] & (np.abs(cx - px) <= pw / 2)[None, :]] = True
    return (0.0, 0.0), c, nx, taken.ravel().tolist()


def pocket_bars(s: Settlement) -> list[tuple[float, float, float]]:
    """The shared sheds' pockets the seating reserved before any house, each as the wood's keep-out disc `file_byre_pockets` files.

    Research: copse clump kept off a shared byre by its half-diagonal plus the clump radius and 2 px - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html"""
    from l7r.diagram.settlement.homestead_parts.wood_share import BAR_MARGIN_PX
    from l7r.diagram.settlement.shrines_wells.byres import BYRE_FT

    wood = getattr(s, "_wood", None)
    if wood is None:
        return []
    r = 0.5 * math.hypot(s.px(BYRE_FT[0]), s.px(BYRE_FT[1])) + wood.clump / 2.0 + 2.0 + BAR_MARGIN_PX
    return [(float(x), float(y), float(r)) for x, y in getattr(s, "_byre_pockets", None) or ()]


def seat_inputs(s: Settlement, plan: SitePlan, byre_share: float, quota: dict[str, float]) -> dict[str, Any]:
    """What the Rust growth reads (`l7r_phases.seat_households`), gathered where `grow_the_margin` would run: the free ground, the
    way out's anchor, the field's envelope, the streams, the margin's bearing, the lots (`byre_share`, `quota` as the stage dealt
    them), the fixture forms, and what the rules read past the raster - the paddy's facing chords, the running water, the web's
    hard ground and the extents the registry forbids each part.

    Research: plumbing - NONE: the seating's inputs, each read where the Python reads it"""
    pt = lambda q: (float(q[0]), float(q[1]))  # noqa: E731
    ring = lambda r: [pt(q) for q in r]  # noqa: E731
    anchor = [pt(q) for q in getattr(s, "_way_out_anchor", None) or ()]
    seeds = [
        (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for a, b in zip(anchor, anchor[1:], strict=False) for n in [max(1, int(math.dist(a, b) / GROUND_CELL_FT))] for k in range(n + 1)
    ]
    streams = [(pt(a), pt(b)) for f in s.M.get("streams") or [] for a, b in zip(f.get("poly") or [], (f.get("poly") or [])[1:], strict=False)]
    ax, ay = plan.seat["along"]
    forms = s._fixture_forms
    chains = s._field_chains()[0]
    st = getattr(s.M, "standing", None)
    return {
        "ground": ground_cells(s),
        "seeds": seeds,
        "field": ring(plan.envelope),
        "streams": streams,
        "canvas": (float(s.W), float(s.H)),
        "bearing": (math.degrees(math.atan2(ay, ax)), float(s._house_bearing)),
        "lots": (int(plan.spec.seed), int(plan.spec.households), float(byre_share)),
        "shares": [(k, float(v)) for k, v in quota.items()],
        "byre": getattr(s, "_byre_form", None),
        "forms": (
            [(k, float(w)) for k, w in forms.privy_weights],
            float(forms.bath_stable_share),
            float(forms.persimmon_front),
            forms.manure_form == "pit",
            tuple(float(v) for v in forms.retirement_ft),
            [float(v) for v in forms.retirement_gaps],
        ),
        "shade": float(CANOPY_SHADE_FT),
        "chains": [[(pt(a), pt(b), pt(n)) for a, b, n in chain] for chain in chains],
        "waters": [(ring(poly), float(hw)) for poly, hw, _b in s._water_obstacles()],
        "hard": [(ring(p), float(margin_of(p, WEB_HARD_GAP))) for p in web_hard_ground(s, plan) if len(p) >= 3],
        "forbidding": [(k, [ring(e[1]) for e in st.forbidding(k)] if st is not None else []) for k in PART_KEYS],
        "sun": bool(getattr(s, "_sun_corridor_ft", 0.0)),
        "bars": pocket_bars(s),
        "center": (float(plan.seat["cx"]), float(plan.seat["cy"])),
        "want": int(plan.spec.households),
    }


def homestead_geom(h: dict[str, Any]) -> dict[str, Any]:
    """A household the Rust seated, as the geometry `_bundle_geom` lays: its parts, their true sizes and turn, each part's box as
    drawn, the box round them, the fixtures' laid sizes and the bath room's wall, and the wood seats it reserved.

    Research: plumbing - NONE: the Rust's homestead in the record's own form"""
    boxes = [tuple(b) for b in h["boxes"]]
    gardens = [tuple(g) for g in h["gardens"]]
    n = 2 + len(gardens)
    shed = tuple(h["shed"]) if h["shed"] is not None else None
    byre = tuple(h["byre"][0]) if h["byre"] is not None else None
    shed_box = boxes[n] if shed is not None else None
    byre_box = boxes[n + (shed is not None)] if byre is not None else None
    first = n + (shed is not None) + (byre is not None)
    fixtures = {k: tuple(r) for k, r in h["fixtures"]}
    notes: dict[str, Any] = {"ft": {k: [r[2], r[3]] for k, r in fixtures.items()}}
    if h["bath"] is not None:
        notes["bath_seat"] = h["bath"]
    return {
        "house": tuple(h["house"]),
        "yard": tuple(h["yard"]),
        "garden": gardens[0] if gardens else None,
        "gardens": gardens,
        "shed": shed,
        "byre": byre,
        "fixtures": fixtures,
        "fixture_notes": notes,
        "turn": float(h["turn"]),
        "boxes": {
            "house": boxes[0],
            "yard": boxes[1],
            "gardens": boxes[2:n],
            "shed": shed_box,
            "byre": byre_box,
            "well": None,
            "fixtures": {k: boxes[first + i] for i, k in enumerate(fixtures)},
        },
        "bbox": tuple(h["bbox"]),
        "opens": True,
        "wood": [tuple(p) for p in h["wood"]],
    }


def rust_grow(s: Settlement, plan: SitePlan, placed: int, byre_share: float, quota: dict[str, float]) -> int:
    """Seat the cluster's households in Rust and record each as `_try_place_bundle` does: its box placed, its record, its way's
    reservation, its parts and wood share. Returns how many stand.

    Research: the growth in Rust - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household seated where its yard opens onto lane ground, its rules asked at the Rust that seats it"""
    from ..phases_ext import phases

    got = phases().seat_households(seat_inputs(s, plan, byre_share, quota))
    form = getattr(s, "_byre_form", None)
    for h in got["seated"]:
        geom = homestead_geom(h)
        cx, cy = geom["house"][0], geom["house"][1]
        s.placed.append(geom["bbox"])
        rec = {
            "x": cx,
            "y": cy,
            "w": geom["house"][2],
            "h": geom["house"][3],
            "kind": "plain",
            "rot": geom["turn"],
            "role": None,
            "shed": geom["shed"] is not None,
            "shed_side": "N",
            "wealth": 1.0,
            "geom": geom,
        }
        reserve_way(s, rec, geom, (cx, cy))
        record_parts(s, rec, geom, form if geom["byre"] is not None else None)
        s.M["houses"].append(rec)
        s._pending_farmsteads.append(rec)
    offered, positions, rects, layouts = got["search"]
    s._seat_search.update({"grow_offered": offered, "grow_took": len(got["seated"]), "positions": positions, "rects": rects, "layouts": layouts, "rust_counts": sum(got["counts"].values())})
    return placed + len(got["seated"])
