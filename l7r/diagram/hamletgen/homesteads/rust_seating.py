"""THE HOMESTEADS SEATED IN RUST (feature 444 T30, the door): what each seating form reads, gathered once the seat region stands,
handed to `l7r_phases` - a nucleated cluster to `seat_households` (`rust/phases/src/homesteads/place.rs` `grow`), a scattered
hamlet to `seat_scattered` (`grove_rounds.rs`), a row village to `seat_rows` (`row_seat.rs`) - and each household it seats
recorded as `Settlement._try_place_bundle` records one: its box placed, its record, its parts and wood share.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from l7r.diagram import work_counts
from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT
from l7r.diagram.settlement.rolling.lot import record_parts
from l7r.diagram.settlement.rolling.passage import reserve_way

from ..clearance import margin_of
from ..consts import WEB_HARD_GAP, Pt
from .boundary import seating_window, web_hard_ground

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

#: The cell the free ground is handed over at (ft): half the Rust raster's own, so a point's verdict is its cell center's to 2 ft.
GROUND_CELL_FT = 4.0
"""Research: plumbing - NONE: a raster's grain, under the 9-point rectangle test's spacing"""

#: The registry keys a homestead's parts are filed under (`rolling/lot.py` `held_part_records`), a grove farm's well pocket among them
#: (`wells`: unasked, a pocket stood on a drawn channel and the registry refused it - the Rust stage gate's seed 375337).
PART_KEYS = ("houses", "threshing_yards", "gardens", "farm_sheds", "byres", "farm_fixtures", "retirement_houses", "wells")
"""Research: plumbing - NONE: the registry's own keys"""


def ground_cells(s: Settlement) -> tuple[tuple[float, float], float, int, list[bool]]:
    """The free ground over the canvas at `GROUND_CELL_FT`, row by row: a cell taken where the site's raster surely takes its
    center, or - its center in a cell the raster leaves uncertain - the site's chains or corridors refuse it there (the tests
    `access.site_samples_clear` asks, every uncertain cell at once as `gap_ways.lane_layers` asks them). Built in arrays: a canvas
    is half a million cells. (The boxes placed before the growth go as boxes, `placed`, which the placer moves a seat off.)

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
        # ...over the seating's window, as the seat region rasterized it (a cost window, never an answer: `boundary.seating_window`)
        "window": (lambda w: ((w[0], w[1]), (w[2], w[3])))(seating_window(s, (float(plan.seat["cx"]), float(plan.seat["cy"])), plan.spec.households)) if getattr(s, "_nucleated", False) else None,
        "field": ring(plan.envelope),
        "streams": streams,
        "canvas": (float(s.W), float(s.H)),
        "bearing": (math.degrees(math.atan2(ay, ax)), float(s._house_bearing or 0.0)),
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
        "placed": [tuple(float(v) for v in b[:4]) for b in getattr(s, "placed", None) or ()],
        "lane_gap": float(s._wood.lane_gap) if getattr(s, "_wood", None) is not None else 0.0,
        "passage_left": int(getattr(s, "_passage_left", 0) or 0),
        "site_chains": [[(pt(a), pt(b), pt(n)) for a, b, n in chain] for chain in getattr(s, "_site_chains", None) or ()],
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
    out: dict[str, Any] = {
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
    grove = grove_parts(h)
    if "well_box" in grove:
        out["boxes"]["well"] = grove.pop("well_box")
    out.update(grove)
    return out


def grove_parts(h: dict[str, Any]) -> dict[str, Any]:
    """A grove farm's own parts on its geometry, as `dispersed_layout` lays them: its bands and their faces (as turned), and its well
    pocket and the pocket's box as drawn; nothing for a clustered household.

    Research: plumbing - NONE: the Rust's grove in the record's own form"""
    if not h.get("groves"):
        return {}
    out: dict[str, Any] = {"groves": [tuple(r) for r, _f, _d in h["groves"]], "grove_faces": [(tuple(f), "deep" if d else "thin") for _r, f, d in h["groves"]]}
    if h.get("well") is not None:
        w = tuple(h["well"])
        th = math.radians(float(h["turn"]))
        c, sn = abs(math.cos(th)), abs(math.sin(th))
        out["well"] = w
        out["well_box"] = (w[0], w[1], w[2] * c + w[3] * sn, w[2] * sn + w[3] * c)
    return out


def rust_grow(s: Settlement, plan: SitePlan, placed: int, byre_share: float, quota: dict[str, float]) -> int:
    """Seat the cluster's households in Rust and record each as `_try_place_bundle` does: its box placed, its record, its way's
    reservation, its parts and wood share. Returns how many stand.

    Research: the growth in Rust - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household seated where its yard opens onto lane ground, its rules asked at the Rust that seats it"""
    from ..phases_ext import phases

    got = phases().seat_households(seat_inputs(s, plan, byre_share, quota))
    return placed + record_seated(s, got)


def record_seated(s: Settlement, got: dict[str, Any]) -> int:
    """Record each household the Rust seated as `_try_place_bundle` does: its box placed, its record, its way's reservation, its
    parts and wood share; the search's counts on the seating's. How many it recorded.

    Research: plumbing - NONE: the Rust's households in the record's own form"""
    form = getattr(s, "_byre_form", None)
    recs: list[dict[str, Any]] = []
    for h in got["seated"]:
        geom = homestead_geom(h)
        cx, cy = geom["house"][0], geom["house"][1]
        if h["passage"] is not None:  # ...reached across a neighbor's yard: its walk, whom, and the chain's depth (`passage_of`)
            walk, of, depth = h["passage"]
            geom.pop("opens", None)
            geom["passage"] = {"walk": [tuple(q) for q in walk], "of": (float(recs[of]["x"]), float(recs[of]["y"])), "depth": int(depth)}
        s.placed.append(geom["bbox"])
        rec = {
            "x": cx,
            "y": cy,
            "w": geom["house"][2],
            "h": geom["house"][3],
            "kind": "plain",
            "rot": geom["turn"],
            "role": None,
            "shed": bool(h["kura"]),  # the lot's kura: a grove farm's drawn on its north wall, its bundle reserving none (as Python did)
            "shed_side": "N",
            "wealth": 1.0,
            "geom": geom,
        }
        reserve_way(s, rec, geom, (cx, cy))
        record_parts(s, rec, geom, form if geom["byre"] is not None else None)
        s.M["houses"].append(rec)
        s._pending_farmsteads.append(rec)
        recs.append(rec)
    offered, positions, rects, layouts = got["search"]
    s._seat_search.update({"grow_offered": offered, "grow_took": len(got["seated"]), "positions": positions, "rects": rects, "layouts": layouts, "rust_counts": sum(got["counts"].values())})
    for k, n in got["counts"].items():  # the Rust's counted work on the stage's (feature 444 D5, as `sink_stage` hands its on)
        work_counts.OPS[k] += n
    return len(got["seated"])


def grove_inputs(s: Settlement, plan: SitePlan, single_file: bool, house_max: tuple[float, float], bound: float, band: tuple[float, float], quota: dict[str, float]) -> dict[str, Any]:
    """What a grove farm's seating hands the Rust (`l7r_phases.seat_scattered`, `seat_rows`): the seating's site, the grove, the other
    ground and the water, the seat band and its axes, the chains, the largest house, the shape, the lanes' form, the seed, the band's
    reach and whether its farms stand in single file.

    Research: plumbing - NONE: Python's gathered state in the Rust's own form"""
    from l7r.diagram.settlement.homestead_parts.grove_sides import windward_pair

    pt = lambda q: (float(q[0]), float(q[1]))  # noqa: E731
    ring = lambda r: [pt(q) for q in r]  # noqa: E731
    inputs = seat_inputs(s, plan, 0.0, quota)
    sun = s.px(CANOPY_SHADE_FT) + s.px(s.CANOPY_R_FT) * 1.7 * 1.15 if getattr(s, "_sun_corridor_ft", 0.0) else 0.0
    corr = getattr(s, "_site_corridors", None)
    seat = plan.seat
    chains = s._seat_ring_chains if single_file else s._site_chains
    inputs.update(
        {
            "grove": (int(s._grove_sides()), windward_pair(s._windward(), s._grove_flank()), bool(sun), float(2.0 * s._well_vr() + s.px(6.0)), float(sun or 22.0)),
            "corridors": ([ring(r) for r in corr.ring_pts], [ring(h.ring) for h in corr.holes], [(pt(a), pt(b), float(c)) for a, b, c in corr.water]) if corr is not None else ([], [], []),
            "axes": (pt((seat["cx"], seat["cy"])), pt(seat["along"]), pt(seat["out"]), pt(seat["anchor"]), float(seat["lat"])),
            "paddies": [ring(p) for p in s.field_polys if len(p) >= 3],
            "row_chains": [[(pt(a), pt(b), pt(n)) for a, b, n in chain] for chain in chains or ()],
            "house_max": (float(house_max[0]), float(house_max[1])),
            "shape": plan.cluster_shape or "crescent",
            "alleys": plan.lane_web == "alleys",
            "seed": int(plan.spec.seed),
            "band": (float(band[0]), float(band[1])),
            "bound": float(bound),
            "single_file": bool(single_file),
        }
    )
    return inputs


def rust_scatter(s: Settlement, plan: SitePlan, single_file: bool, house_max: tuple[float, float], bound: float, band: tuple[float, float], quota: dict[str, float]) -> int:
    """Seat a scattered hamlet's grove farms in Rust (`l7r_phases.seat_scattered`): its front row, then - off the single file - its ranks,
    the rescue and the exhaustive pass, from the site boundary installed for this seating (`install_site_boundary`), and record each as
    `_try_place_bundle` does. How many stand.

    Research: a scattered hamlet's seating in Rust - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a front row along the paddy's chords, ranks behind, a rescue cloud, the exhaustive pass; its rules asked at the Rust that seats it"""
    from ..phases_ext import phases

    return record_seated(s, phases().seat_scattered(grove_inputs(s, plan, single_file, house_max, bound, band, quota)))


def rust_rows(s: Settlement, plan: SitePlan, house_max: tuple[float, float], bound: float, band: tuple[float, float], quota: dict[str, float]) -> int:
    """Seat a row village's grove farms along its streets in Rust (`l7r_phases.seat_rows`), from the hard ground `rows.seat_rows`
    gathers, and record what that writes: each farm as `_try_place_bundle` does, its sheltered mark, the holdings reserved (drawn
    later, kept off by the next placers and the woods), and the streets that seated a farm, for the web. How many stand.

    Research: a row village's seating in Rust - research/questions/0033-row-villages-resson.drawing.html: farms in rows along their streets, each further street parallel past the far row's holdings; its rules asked at the Rust that seats it"""
    from l7r.diagram.settlement.homestead_parts.grove_sides import grove_faces

    from ..consts import WIND_VECTORS
    from ..phases_ext import phases

    pt = lambda q: (float(q[0]), float(q[1]))  # noqa: E731
    corr = getattr(s, "_site_corridors", None)
    # ...AND THE WET GROUND the ways refuse, as `rows.seat_rows` gathers it: the toe marsh and every marsh drawn so far
    wet = [[pt(q) for q in (s.toe_band() or [])]] + [[pt(q) for q in m["poly"]] for m in s.M.get("marshes", []) if m.get("poly")]
    field = [pt(q) for q in (plan.envelope or [])]
    polys = [r for r in [field, *[[pt(q) for q in r] for r in (getattr(corr, "ring_pts", ()) or ())], *wet] if len(r) >= 3]
    strips = [(pt(a), pt(b), max(float(c), 0.5)) for a, b, c in (getattr(corr, "water", ()) or ()) if tuple(a) != tuple(b)]
    inputs = grove_inputs(s, plan, False, house_max, bound, band, quota)
    inputs["rows"] = (
        plan.row_sides == "both",
        plan.row_line,
        plan.row_shelter == "sheltered",
        pt(WIND_VECTORS.get(plan.windward, WIND_VECTORS["NW"])),
        pt(grove_faces(plan.windward, plan.grove_sides, plan.grove_flank)[2]),
        (float(s.W), float(s.H)),
        (float(plan.seat["cx"]), float(plan.seat["cy"])),
        polys,
        strips,
    )
    got = phases().seat_rows(inputs)
    placed = record_seated(s, got)
    recs = s._pending_farmsteads[len(s._pending_farmsteads) - placed :]
    for rec, mark in zip(recs, got["sheltered"], strict=True):
        if mark:  # the leeward row: its grove drawn one tree deep, its bamboo along its south side
            rec["sheltered"] = True
            s.M["meta"]["sheltered_farms"] = int(s.M["meta"].get("sheltered_farms", 0)) + 1
    holdings: list[tuple[list[Pt], Pt, Pt, float]] = []
    for ring, t, nrm, depth, lot in got["holdings"]:
        hold = [pt(q) for q in ring]
        holdings.append((hold, pt(t), pt(nrm), float(depth)))
        s.M.setdefault("row_holdings", []).append({"id": len(holdings) - 1, "of": [float(recs[lot]["x"]), float(recs[lot]["y"])], "poly": [[round(x, 1), round(y, 1)] for x, y in hold]})
        s.block_polys.append(hold)  # the next placers and the woods keep off it (plan D16)
        s.hard_polys.append(hold)
    streets = [[pt(q) for q in line] for line, _farms in got["streets"]]
    s._row_holdings = holdings  # type: ignore[attr-defined]
    s._row_streets = streets  # type: ignore[attr-defined]
    s._row_street_farms = [[pt(q) for q in farms] for _line, farms in got["streets"]]  # type: ignore[attr-defined]
    s.M["meta"]["row_streets"] = len(streets)
    s.M["row_street_plans"] = [[[round(x, 1), round(y, 1)] for x, y in line[:: max(1, len(line) // 60)] + line[-1:]] for line in streets]
    return placed
