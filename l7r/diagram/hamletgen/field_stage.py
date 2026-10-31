"""STAGE 2 - the field, its comb in Rust (feature 444 T16 D1): a thin Python function that gathers the plan's fields, rolls the
stage's own knobs through Rust from their tables (D3), calls `l7r_phases.stage_field`, and writes what it returns - the
manifest's keys with their record shapes (`specs/444-work-budget-program/phases/field.keys.json`), the plan's `acres`,
`envelope`, `net` and `brook`, and the engine's no-build registries (`phases/field.state.json`) - then draws it
(`settlement/fields/ink.py`, D12). The polder forms take the old Python until their port (D11: the comb first).

Research:
    the field's seam - NONE: the stage's plumbing; each rule's claim is at the Rust that decides it (`rust/phases/src/field/`)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from l7r.diagram.interactive.tags import Split
from l7r.diagram.settlement._knobs import KNOBS
from l7r.diagram.settlement.fields import ink
from l7r.diagram.waterfields.palette import _RICE_GREEN, AZE, FLOODED, RIPE_GOLD, aze_w

from .consts import POLDER_ARCHETYPES, SQ_FT_PER_ACRE
from .consts_water import BROOK_SKIRT, BROOK_SLEW, BROOK_TAP_RUN, BROOK_WANDER, BROOK_WANDER_STEP, OFFTAKE_DEG, WEIR_HALF_FT, WEIR_SKEW_DEG, WEIR_THICK_FT
from .phases_ext import phases

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from .plan import SitePlan

BROOK_W = 7.0
"""Research: the feed brook's width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: a village creek at roughly three and a half times the 1.5 ft floor"""
BROOK_STATION = 20.0
"""Research: the brook's station spacing - CONVENTION: one station every 20 ft, enough that a bend led in over two reads round"""
DITCH_BANK_FT = 4.0
"""Research: a field ditch's no-build bank - GUESS: the record gives a ditch's width, not the ground kept off it; 4 ft past its
half-width, as a farm's own channel keeps (`homesteads/farm_water.py`)"""
CELL_SHARE = 31.0
"""Research: a basin's cell - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: about 48 ft across its canal and 26 to 36 ft along it, the cell the row's spacing times the middle, 31 ft"""
ROW_FT = {"small_irregular": 34.0, "large_block": 70.0}
"""Research: the rows' spacing by plot size - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: 48 ft, the plan's small (34) and large block (70) departures - the cell's row; Rust maps the same (`lattice::row_ft_for`)"""
STAGE_KNOBS = ("town_nearness", "winter_crop", "fan_middle", "paddy_rest", "plot_regularity", "weir_form", "grave_form")
"""Research: the stage's own knobs, in the order each typing rule reads the last - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: the nearness of a town sets the winter crop's odds"""
FILL = {"green": _RICE_GREEN, "wet": FLOODED, "flooded": FLOODED, "gold": RIPE_GOLD, "rest": _RICE_GREEN}
"""Research: the plots' paint - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: the wet paddy tinted blue-green; research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: one in sixteen flooded, one in twenty gold"""


def _knob_tables(s: Settlement, plan: SitePlan) -> list[tuple[str, list[str], list[float], str | None]]:
    """Each of the stage's knobs drawn in Rust from its table against the running context (`roll_knob`), recorded on the
    settlement as `resolve` records it, and handed to the stage as a pin so the stage reads the value drawn."""
    ext = phases()
    out: list[tuple[str, list[str], list[float], str | None]] = []
    for name in STAGE_KNOBS:
        knob = KNOBS.get(name)
        if knob is None:
            continue
        pin = s.knob_pins.get(name, plan.spec.pins.get(name))
        if pin is None:
            ctx = s.knob_context()
            forms = knob.allowed(ctx)
            weights = knob.weights_for(ctx)
            w = [weights.get(v, 0.0) for v in forms] if weights is not None else []
            pin = forms[ext.roll_knob(s.seed, name, len(forms), w)]
        s._resolved_knobs[name] = pin
        out.append((name, [str(pin)], [], str(pin)))
    out.append(("intake", [plan.intake], [], plan.intake))
    return out


def _bbox(pts: list[tuple[float, float]]) -> list[float]:
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]


def _center(ring: list[tuple[float, float]]) -> tuple[float, float]:
    return (sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring))


def stage_field(s: Settlement, plan: SitePlan) -> None:
    """The field: a comb or a polder, placed in Rust (`rust/phases/src/field/`), written and drawn here (D1, D12).

    Steps:
        l7r.diagram.hamletgen.field_stage._knob_tables
        l7r.diagram.hamletgen.field_stage._write_field
        l7r.diagram.hamletgen.field_stage._polder
        l7r.diagram.settlement.fields.ink.draw

    Research:
        the comb - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: the fan of paddies, its basins and bunds"""
    if plan.field_archetype in POLDER_ARCHETYPES:
        _polder(s, plan)
        return
    ftpx = plan.ftpx
    knobs = _knob_tables(s, plan)
    brook = (plan.head_lead * ftpx, OFFTAKE_DEG, BROOK_TAP_RUN, BROOK_SLEW, BROOK_SKIRT, BROOK_WANDER, BROOK_STATION, BROOK_W)
    _ = BROOK_WANDER_STEP  # the plan's walk step: the Rust walk steps a slew a station (brook.rs)
    row = ROW_FT.get(plan.plot_size, 48.0)
    out = phases().stage_field(
        plan.spec.seed,
        plan.spec.households,
        float(plan.down_deg),
        float(plan.fan_aspect),
        (plan.W * ftpx / 2.0, plan.H * ftpx / 2.0),
        (plan.W * ftpx, plan.H * ftpx),
        float(plan.brook_side),
        brook,
        (list(plan.offtakes_a), list(plan.offtakes_b)),
        (WEIR_HALF_FT, WEIR_SKEW_DEG, dict(WEIR_THICK_FT)),
        plan.plot_size,
        row * CELL_SHARE,
        knobs,
    )
    for k, n in out["counts"].items():
        if __debug__:
            from l7r.diagram import work_counts

            work_counts.OPS[k] += n
    rolled = out["knobs"]
    drawn, need, room = out["grain"]
    s.meta(
        field_archetype=plan.field_archetype,
        winter_crop=rolled.get("winter_crop"),
        town_nearness=rolled.get("town_nearness"),
        fan_middle=rolled.get("fan_middle"),
        paddy_rest=rolled.get("paddy_rest"),
        plot_regularity=rolled.get("plot_regularity"),
        weir_form=rolled.get("weir_form") if plan.intake == "weir" else None,
        grave_form=None,
        dry_furrows_vary=True,
        water_source="head_center",
        water_source_position="head_center",
        plot_size=plan.plot_size,
        grain_drift=plan.grain_drift,
        coarse_grain_dry_acres=round(drawn, 2),
        coarse_grain_dry_need_acres=round(need, 2),
        coarse_grain_room_acres=round(room, 2),
    )
    acres = 0.0
    for k, f in enumerate(out["fields"]):
        acres += _write_field(s, plan, f, f"{plan.spec.name.lower()}-paddies" + (f"-{k + 1}" if k else ""), rolled)
    plan.acres = acres


def comb_net(f: dict[str, Any], name: str, cell: float, down_deg: float, fan_middle: str | None) -> dict[str, Any]:
    """The `net` of one comb the Rust stage returned: its plots (a grave's host replaced by the rings it leaves), channels, dry
    plots, pocket ponds and graves, in the shapes the free readers and the ink read (`plan.net`; the test fixtures build theirs
    with it too)."""
    graves = f["grave"]
    host = graves[2] if graves else None
    plots: list[dict[str, Any]] = []
    for i, p in enumerate(f["plots"]):
        rings = graves[3] if i == host else [p["ring"]]
        for ring in rings:
            plots.append({"poly": ring, "fill": FILL[p["state"]], "low": p["state"] == "wet", "rest": p["state"] == "rest", "state": p["state"], "drain_side": p["drain_side"]})
    chans = [{"role": r, "pts": pts, "w": w, "w_tail": wt} for r, pts, w, wt in f["channels"]]
    dry = [{"poly": poly, "crop": crop, "theta": theta, "tract": f"{name}:{tract}", "fill": ink.CROP_FILL[crop], "furrow": ink.CROP_FURROW[crop]} for poly, crop, theta, tract in f["dry"]]
    ponds = [{"x": x, "y": y, "rx": rx, "ry": ry} for _, x, y, rx, ry in [f["pond"]]] if f["pond"] else []
    grave_recs = [{"x": graves[0][0], "y": graves[0][1], "form": graves[1]}] if graves else []
    beans = [pt for run in f["beans"] for pt in run]
    outline = f["ring"]
    net: dict[str, Any] = {
        "down_deg": down_deg,
        "fork": f["fork"],
        "cell": cell,
        "supply_banks": True,
        "channels": chans,
        "plots": plots,
        "threads": [],
        "drain": next((c["pts"] for c in chans if c["role"] == "drain"), []),
        "brook": [],
        "envelope": outline,
        "dry_plots": dry,
        "dry_acres": sum(_area(d["poly"]) for d in dry) / SQ_FT_PER_ACRE,
        "dry_reserve": [],
        "bund_bean_runs": f["beans"],
        "bund_beans": beans,
        "furrows_vary": True,
        "fan_middle": fan_middle,
        "grave_discs": [(g["x"], g["y"], 6.5) for g in grave_recs],
        "bead_ponds": [(p["x"], p["y"], p["rx"], p["ry"]) for p in ponds],
        "grave_records": grave_recs,
        "pocket_ponds": ponds,
    }
    return net


def _write_field(s: Settlement, plan: SitePlan, f: dict[str, Any], name: str, rolled: dict[str, str]) -> float:
    """One field's records, registries and ink; returns its paddy acres."""
    M = s.M
    cell = ROW_FT.get(plan.plot_size, 48.0) * CELL_SHARE
    net = comb_net(f, name, cell, plan.down_deg, rolled.get("fan_middle"))
    plots, chans, dry, ponds, grave_recs = net["plots"], net["channels"], net["dry_plots"], net["pocket_ponds"], net["grave_records"]
    beans, outline = net["bund_beans"], net["envelope"]
    rings = [p["poly"] for p in plots]
    plot_recs = []
    for p in plots:
        b = _bbox(p["poly"])
        c = _center(p["poly"])
        plot_recs.append([round(b[2] - b[0], 1), round(b[3] - b[1], 1), round(c[0], 1), round(c[1], 1), len(p["poly"]), 0])
    hem = [p["drain_side"] for p in plots if p["drain_side"]]
    if grave_recs:
        s.meta(grave_form=grave_recs[0]["form"])
    M["fields"].append(
        {
            "name": name,
            "kind": "paddy",
            "outline": outline,
            "bbox": _bbox(outline + [f["fork"]]),
            "vis_bbox": _bbox(outline + [pt for c in chans for pt in c["pts"]]),
            "plots": plot_recs,
            "drain_hem": hem,
            "plot_rings": rings,
            "bund_beans": beans,
            "cell": cell,
            "down_deg": plan.down_deg,
            "fork": f["fork"],
        }
    )
    M.setdefault("field_ditches", []).extend({"field": name, "poly": c["pts"], "role": c["role"], "w": c["w"], "w_tail": c["w_tail"]} for c in chans[1:])
    M.setdefault("channels", []).append({"poly": chans[0]["pts"], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": name}, "w": chans[0]["w"], "field": name})
    if f["weir"]:
        ring, deg, form = f["weir"]
        M.setdefault("weirs", []).append({"x": f["intake"][0], "y": f["intake"][1], "len": 2 * WEIR_HALF_FT, "w": WEIR_THICK_FT.get(form, 1.5), "deg": round(deg, 1), "form": form, "poly": ring})
    M.setdefault("dry_plots", []).extend({k: d[k] for k in ("poly", "crop", "theta", "tract")} for d in dry)
    M.setdefault("wet_plots", []).extend(list(_center(p["poly"])) for p in plots if p["low"])
    M.setdefault("flooded_plots", []).extend(list(_center(p["poly"])) for p in plots if p["fill"] == FLOODED)
    if ponds:
        M.setdefault("field_ponds", []).extend(ponds)
    if grave_recs:
        M.setdefault("field_graves", []).extend({"x": g["x"], "y": g["y"]} for g in grave_recs)
    acres = sum(_area(r) for r in rings if r) / SQ_FT_PER_ACRE
    net["acres"] = acres
    plan.net = net
    plan.envelope = outline
    plan.brook = f["brook"]
    # the no-build registries the stages after read (`phases/field.state.json`)
    s.field_polys.append(outline)
    for d in dry:
        s.dry_polys.append(d["poly"])
        s.block_polys.append(d["poly"])
    for c in chans:
        s.corridors.append((c["pts"], s.px(max(c["w"], c["w_tail"]) / 2 + DITCH_BANK_FT)))
    s.stream(f["brook"], frm={"kind": "offmap"}, to={"kind": "offmap"}, width=BROOK_W)
    if f["weir"]:
        ink.weir(s, M["weirs"][-1])
    ink.draw(s, net, name, plan.field_archetype)
    return acres


def _area(ring: list[tuple[float, float]]) -> float:
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:] + ring[:1], strict=True))) / 2.0


POND_FRINGE_FT = 40.0
"""Research: the wild pond's reed fringe - research/questions/0061-reservoir-ponds-tameike.drawing.html: reeds round the shore at the caller's margin, the comb source pond's 40"""


def _polder(s: Settlement, plan: SitePlan) -> None:
    """The polder: its placement from Rust (`stage_polder`, D8), then the free helpers the old stage called - the wild pond and
    its fringe, the perimeter dike and its trees gapped at the sluices, the resting plots, the ditches, the outfall run, and on a
    dike-pond the land-use overlay that makes its ponds (`phases/field.md`, "The polder's seam").

    Research:
        the polder - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: from outside in, the wild water, the dike, the ring canal, the field ditches and the paddies"""
    from l7r.diagram.settlement.fields.outfall import outfall_run
    from l7r.diagram.settlement.land.wet import pond_fringe_ring
    from l7r.diagram.settlement.water_ways.water import ditch_style

    ftpx = plan.ftpx
    dikepond = plan.field_archetype == "mulberry_dike_fishpond"
    name = f"{plan.spec.name.lower()}-polder"
    out = phases().stage_polder(plan.spec.seed, plan.spec.households, dikepond, plan.pond_layout, float(plan.down_deg), (plan.W * ftpx / 2.0, plan.H * ftpx / 2.0), float(plan.fan_aspect))
    if __debug__:
        from l7r.diagram import work_counts

        for k, n in out["counts"].items():
            work_counts.OPS[k] += n
    s.meta(field_archetype=plan.field_archetype, pond_layout=plan.pond_layout, water_source="reservoir", water_source_position="corner_high", dry_furrows_vary=False)
    px, py, rx, ry = out["pond"]
    s.pond(px, py, rx, ry)
    s.marsh(pond_fringe_ring(px, py, rx, ry, POND_FRINGE_FT), role="pond_fringe")
    rows = max(p["row"] for p in out["plots"]) + 1
    cands = [(p["ring"], (p["row"] + 0.5) / rows) for p in out["plots"]]
    rest = s.resting_plots(name, cands)
    plots = [
        {"poly": p["ring"], "fill": FLOODED if p["low"] else _RICE_GREEN, "low": p["low"], "rest": i in rest, "state": "wet" if p["low"] else "green", "drain_side": None}
        for i, p in enumerate(out["plots"])
    ]
    chans = [{"role": r, "seg": seg, "pts": pts, "w": w, "w_tail": wt} for r, seg, pts, w, wt in out["ditches"]]
    outline = out["outline"]
    net: dict[str, Any] = {
        "plots": plots,
        "channels": chans,
        "envelope": outline,
        "floor": outline,
        "dry_plots": [],
        "dry_acres": 0.0,
        "bund_beans": [],
        "bund_bean_runs": [],
        "furrows_vary": False,
        "bead_ponds": [],
        "brook": [],
        "drain": next(c["pts"] for c in chans if c["seg"] == "drain"),
        "sluice": tuple(out["sluices"][0]),
        "dike_sluices": [tuple(g) for g in out["sluices"]],
        "ftpx": ftpx,
        "threads": [],
    }
    rings = [p["poly"] for p in plots]
    M = s.M
    M["fields"].append(
        {
            "name": name,
            "kind": "paddy",
            "outline": outline,
            "bbox": _bbox(out["inner_env"]),
            "vis_bbox": _bbox(outline),
            "plots": [[*(lambda b: [round(b[2] - b[0], 1), round(b[3] - b[1], 1)])(_bbox(r)), *(round(v, 1) for v in _center(r)), len(r), p["col"]] for r, p in zip(rings, out["plots"], strict=True)],
            "drain_hem": [],
            "plot_rings": rings,
            "bund_beans": [],
        }
    )
    M.setdefault("field_ditches", []).extend({"field": name, "poly": c["pts"], "role": c["role"], "seg": c["seg"], "w": c["w"], "w_tail": c["w_tail"]} for c in chans)
    M.setdefault("channels", []).append({"poly": out["feeder"], "frm": {"kind": "pond"}, "to": {"kind": "field", "name": name}, "w": 1.5, "field": name})
    M.setdefault("wet_plots", []).extend(list(_center(p["poly"])) for p in plots if p["low"])
    M.setdefault("flooded_plots", []).extend(list(_center(p["poly"])) for p in plots if p["low"])
    s.perimeter_dike(out["inner_env"], seed=plan.spec.seed, gaps=[tuple(g) for g in out["sluices"]])
    s.comb_base_fill(net, name)
    bund = aze_w(ftpx)
    for p in plots:
        if p["rest"]:
            s.rest_basin(p["poly"], bund, name)
        else:
            s.add_paddy(
                f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in p["poly"])}" fill="{p["fill"]}" stroke="{AZE}" stroke-width="{bund:.2f}" stroke-linejoin="round"/>',
                cls=Split("wet paddy" if p["low"] else "paddy", "bund"),
            )
    for c in chans:
        col, cls = ditch_style(c["role"], plan.field_archetype)
        s.field_channel(c["pts"], col, c["w"], c["w_tail"], late=True, cls=cls)
        s.corridors.append((c["pts"], s.px(max(c["w"], c["w_tail"]) / 2 + DITCH_BANK_FT)))
    s.field_channel(out["feeder"], ditch_style("main", plan.field_archetype)[0], 1.5, 1.5, late=True)
    tail = out["sluices"][1]
    inner = next(c["pts"] for c in chans if c["seg"] == "drain")
    mid = ((inner[0][0] + inner[-1][0]) / 2.0, (inner[0][1] + inner[-1][1]) / 2.0)
    run = outfall_run(mid, tail, plan.fall)
    M["channels"].append({"poly": run, "frm": {"kind": "drain"}, "to": {"kind": "offmap"}, "w": 5.5})
    s.field_channel(run, *ditch_style("drain", plan.field_archetype)[:1], 5.5, 5.5, late=True, cls=ditch_style("drain", plan.field_archetype)[1])
    if dikepond:
        from l7r.diagram.settlement._knobs import knob_rng

        s.apply_land_use(net, "mulberry_fishpond", knob_rng(plan.spec.seed, "land_use"), fraction=1.0, eligible="all", dike_crop=plan.dike_crop, leftover=plan.leftover, fry_form=plan.fry_form)
    s.field_polys.append(outline)
    plan.net = net
    plan.envelope = outline
    plan.acres = sum(_area(r) for r in rings) / SQ_FT_PER_ACRE
    net["acres"] = plan.acres
