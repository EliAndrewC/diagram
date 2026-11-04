"""STAGE 2 - the field, its comb in Rust (feature 444 T16 D1): a thin Python function that gathers the plan's fields, rolls the
stage's own knobs through Rust from their tables (D3), calls `l7r_phases.stage_field`, and writes what it returns - the
manifest's keys with their record shapes (`specs/444-work-budget-program/phases/field.keys.json`), the plan's `acres`,
`envelope`, `net` and `brook`, and the engine's no-build registries (`phases/field.state.json`) - then draws it
(`settlement/fields/ink.py`, D12). The polder forms are Rust's too (`stage_polder`), written and drawn by `_polder`.

Research:
    the field's seam - NONE: the stage's plumbing; each rule's claim is at the Rust that decides it (`rust/phases/src/field/`)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from l7r.diagram.interactive.tags import Split
from l7r.diagram.settlement._knobs import KNOBS, Knob, register_knob
from l7r.diagram.settlement.fields import ink
from l7r.diagram.waterfields.palette import _RICE_GREEN, AZE, FLOODED, RIPE_GOLD, aze_w

from .consts import POLDER_ARCHETYPES, SQ_FT_PER_ACRE
from .consts_water import BROOK_SKIRT, BROOK_SLEW, BROOK_TAP_RUN, BROOK_WANDER, BROOK_WANDER_STEP, OFFTAKE_DEG, WEIR_SKEW_DEG, WEIR_THICK_FT
from .phases_ext import phases
from .water.brook_rules import BROOK_DRAWN_W

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from .plan import SitePlan

BROOK_W = BROOK_DRAWN_W
"""Research: the feed brook's width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: a village creek at roughly three and a half times the 1.5 ft floor, 5.25 ft, narrower than the 6.0 ft head race it feeds (the brook rules' `BROOK_DRAWN_W`, one figure)"""
BROOK_STATION = 20.0
"""Research: the brook's station spacing - CONVENTION: one station every 20 ft, enough that a bend led in over two reads round"""
DITCH_BANK_FT = 4.0
"""Research: a field ditch's no-build bank - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the bank an early Yayoi paddy kept along its canal, 2.6 to 4.9 ft; 4 ft past the ditch's half-width kept off by buildings"""
CELL_SHARE = 31.0
"""Research: a basin's cell - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: about 48 ft across its canal and 26 to 36 ft along it, the cell the row's spacing times the middle, 31 ft"""
ROW_FT_DEFAULT = 48.0
"""Research: the rows' spacing - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: about 48 ft across its canal, a hamlet's basin row"""
ROW_FT = {"small_irregular": 40.0, "large_block": 60.0}
"""Research: the rows' spacing by plot size - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a hamlet basin some 40 to 60 ft across - a small plot's row at its foot, 40 ft, a large block's at its top, 60 ft; Rust maps the same (`lattice::row_ft_for`)"""
INTAKE_PLACE = register_knob(Knob("intake_place", ["shoulder", "center"], default="shoulder"))
"""Research: the intake's place - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the intake stands at the left, the center or the right of the fan's head, chosen at random for each settlement with odds of 1:2:1 (a guess) - a shoulder (the plan's flank, left or right at even odds) or the middle, at even odds"""
INTAKE_SITING = register_knob(Knob("intake_siting", ["bend", "straight"], default="bend"))
"""Research:
    the intake's siting - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html: an offtake in a straight reach, or else on the outside of a bend - the two forms rolled per settlement
    the siting's odds - GUESS: the record silent on how often each was chosen; even odds"""
WEIR_KEY_FT = 1.0
"""Research: the weir keyed into the banks - GUESS: research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html silent on how far a weir runs into each bank, drawing it across the whole brook; a foot either side"""
WEIR_HALF = BROOK_W / 2.0 / math.cos(math.radians(WEIR_SKEW_DEG)) + WEIR_KEY_FT
"""Research: the weir's half-length - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a weir is drawn across the whole brook, diagonally upstream - half the drawn brook's width across at the weir's skew, and `WEIR_KEY_FT` into the bank"""
STAGE_KNOBS = ("town_nearness", "winter_crop", "fan_middle", "paddy_rest", "plot_regularity", "weir_form", "grave_form", "intake_place", "intake_siting")
"""Research: the stage's own knobs, in the order each typing rule reads the last - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: the nearness of a town sets the winter crop's odds"""
FILL = {"green": _RICE_GREEN, "wet": FLOODED, "flooded": ink.POND_WATER, "gold": RIPE_GOLD, "rest": _RICE_GREEN}
"""Research:
    the plots' paint - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: the wet paddy tinted blue-green, the tint marking the ground, not the season
    the freshly flooded plot - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: one in sixteen drawn still flooded and the flooded basin a flat color - the open water's own ink (`ink.POND_WATER`), so it reads apart from the wet ground's tint
    the ripening plot - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: one in twenty gold, ripening early
    the resting plot's fill - NONE: its record's; a resting basin's ink is `rest_basin`'s (research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html)"""
GRAVE_KEEP_FT = 6.5
"""Research: a field grave's keep-out - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on a grave's size; the disc of the drawn mound's half-length, 6.5 ft (`ink.grave`)"""
WEIR_THICK_FALLBACK_FT = 1.5
"""Research: a weir's thickness, its form unknown - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: four forms 1.5 to 5 ft thick; a form missing from the table takes the thinnest, the fence's"""
POND_FEEDER_FT = 3.0
"""Research: the polder's pond feeder - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: a pond feeder at roughly twice the 1.5 ft floor"""
OUTFALL_FT = 5.5
"""Research: the polder's outfall - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the drain's 5.5 ft at its tail, carried on past the outfall"""


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


def _ring_stats(ring: list[tuple[float, float]]) -> tuple[list[float], tuple[float, float], float]:
    """A plot's box, middle and area in ONE walk of its ring (the work-budget audit at T16's landing: the writer walked each
    ring three times), each as `_bbox`, `_center` and `_area` give it."""
    x0 = y0 = math.inf
    x1 = y1 = -math.inf
    sx = sy = cross = 0.0
    n = len(ring)
    for i, (x, y) in enumerate(ring):
        x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
        sx += x
        sy += y
        nx, ny = ring[(i + 1) % n]
        cross += x * ny - nx * y
    return [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)], (sx / n, sy / n), abs(cross) / 2.0


def _water_source(place: str | None, brook_side: int) -> str:
    """Where the water comes in, in the names the manifest has always used: the head's middle, or the shoulder the brook comes
    down past (the brook's flank, +1 the fan's right looking downhill).

    Research: the intake's place - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: at the left, the center or the right of the fan's head"""
    if place == "center":
        return "head_center"
    return "head_right" if brook_side > 0 else "head_left"


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
    row = ROW_FT.get(plan.plot_size, ROW_FT_DEFAULT)
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
        (WEIR_HALF, WEIR_SKEW_DEG, dict(WEIR_THICK_FT)),
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
        water_source=(place := _water_source(rolled.get("intake_place"), plan.brook_side)),
        water_source_position=place,
        plot_size=plan.plot_size,
        grain_drift=plan.grain_drift,
        coarse_grain_dry_acres=round(drawn, 2),
        coarse_grain_dry_need_acres=round(need, 2),
        coarse_grain_room_acres=round(room, 2),
    )
    acres = 0.0
    for k, f in enumerate(out["fields"]):
        acres += _write_field(s, plan, f, f"{plan.spec.name.lower()}-paddies" + (f"-{k + 1}" if k else ""), rolled)
    # the hem's inputs, the first field's, for the hem stage after the seat (T28), with its outline and its name
    first = out["fields"][0]
    plan.hem_in = {**first["hem"], "ring": first["ring"], "field": f"{plan.spec.name.lower()}-paddies"} if first.get("hem") else None
    plan.acres = acres


def comb_net(f: dict[str, Any], name: str, cell: float, down_deg: float, fan_middle: str | None) -> dict[str, Any]:
    """The `net` of one comb the Rust stage returned: its plots (a grave's host replaced by the rings it leaves), channels, dry
    plots, pocket ponds and graves, in the shapes the free readers and the ink read (`plan.net`; the test fixtures build theirs
    with it too).

    Research:
        the comb's net - NONE: the Rust's records in the readers' shapes; the one figure it adds is claimed where it stands (`GRAVE_KEEP_FT`)"""
    graves = f["grave"]
    host = graves[2] if graves else None
    plots: list[dict[str, Any]] = []
    for i, p in enumerate(f["plots"]):
        rings = graves[3] if i == host else [p["ring"]]
        for ring in rings:
            # the Rust's own walk of the ring (`stats`: box, middle, area), a grave's rings walked here (`_write_field`)
            stats = p.get("stats") if i != host else None
            plots.append({"poly": ring, "fill": FILL[p["state"]], "low": p["state"] == "wet", "rest": p["state"] == "rest", "state": p["state"], "drain_side": p["drain_side"], "stats": stats})
    chans = [{"role": r, "pts": pts, "w": w, "w_tail": wt} for r, pts, w, wt in f["channels"]]
    dry = dry_records(f.get("dry") or [], name)  # the hem is laid after the seat (`hem_stage`, T28): none here
    ponds = [{"x": x, "y": y, "rx": rx, "ry": ry} for _, x, y, rx, ry in [f["pond"]]] if f["pond"] else []
    grave_recs = [{"x": graves[0][0], "y": graves[0][1], "form": graves[1], "ground": f["plots"][host]["ring"]}] if graves else []
    beans = [pt for run in f["beans"] for pt in run]
    outline = f["ring"]
    net: dict[str, Any] = {
        "down_deg": down_deg,
        "fork": f["fork"],
        "cell": cell,
        "channels": chans,
        "plots": plots,
        "drain": next((c["pts"] for c in chans if c["role"] == "drain"), []),
        "brook": [],
        "envelope": outline,
        "dry_plots": dry,
        "dry_acres": sum(_area(d["poly"]) for d in dry) / SQ_FT_PER_ACRE,
        "bund_bean_runs": f["beans"],
        "bund_beans": beans,
        "fan_middle": fan_middle,
        "grave_discs": [(g["x"], g["y"], GRAVE_KEEP_FT) for g in grave_recs],
        "bead_ponds": [(p["x"], p["y"], p["rx"], p["ry"]) for p in ponds],
        "grave_records": grave_recs,
        "pocket_ponds": ponds,
        "plots_box": f.get("plots_box"),
    }
    return net


def dry_records(dry: Any, name: str) -> list[dict[str, Any]]:
    """The dry plots the Rust laid, in the shapes the readers and the ink read: each plot's ring, crop, rows' direction and its
    tract named for its field.

    Research:
        the dry plots' records - NONE: the Rust's in the readers' shapes"""
    return [{"poly": poly, "crop": crop, "theta": theta, "tract": f"{name}:{tract}", "fill": ink.CROP_FILL[crop], "furrow": ink.CROP_FURROW[crop]} for poly, crop, theta, tract in dry]


def _write_field(s: Settlement, plan: SitePlan, f: dict[str, Any], name: str, rolled: dict[str, str]) -> float:
    """One field's records, registries and ink; returns its paddy acres.

    Research:
        the comb's records - NONE: written from the Rust's; the figures it adds are claimed where they stand (`ROW_FT_DEFAULT`, `WEIR_THICK_FALLBACK_FT`, `DITCH_BANK_FT`, `BROOK_W`)"""
    M = s.M
    cell = ROW_FT.get(plan.plot_size, ROW_FT_DEFAULT) * CELL_SHARE
    net = comb_net(f, name, cell, plan.down_deg, rolled.get("fan_middle"))
    plots, chans, dry, ponds, grave_recs = net["plots"], net["channels"], net["dry_plots"], net["pocket_ponds"], net["grave_records"]
    beans, outline = net["bund_beans"], net["envelope"]
    # ONE pass over the plots writes each one's record and ring entry, and its drain hem, wet or flooded middle where it has one
    # (the work-budget audit at T16's landing: five passes)
    plot_recs, rings, hem, wet, flooded, acres, walked = [], [], [], [], [], 0.0, 0
    for p in plots:
        if p.get("stats"):
            (x0, y0, x1, y1), c, a = p["stats"]
            b = [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)]
        else:
            b, c, a = _ring_stats(p["poly"])
            walked += len(p["poly"])
        acres += a
        plot_recs.append([round(b[2] - b[0], 1), round(b[3] - b[1], 1), round(c[0], 1), round(c[1], 1), len(p["poly"]), 0])
        rings.append(p["poly"])
        if p["drain_side"]:
            hem.append(p["drain_side"])
        if p["low"]:
            wet.append(list(c))
        if p["state"] == "flooded":
            flooded.append(list(c))
    acres /= SQ_FT_PER_ACRE
    # the writer's own walks, counted where they happen (S5; the work-budget audit at T16's landing): a grave's rings (every other
    # plot's figures are the Rust's), a dry plot's ring for its area, the outline and every channel point for the field's boxes,
    # the beans flattened, and the record built for each plot, dry plot and channel in `comb_net`
    if __debug__:
        from l7r.diagram import work_counts

        work_counts.OPS["pt_test@write_field"] += walked + sum(len(d["poly"]) for d in dry) + 2 * len(outline) + sum(len(c["pts"]) for c in chans)
        work_counts.OPS["write@comb_net"] += len(plots) + len(dry) + len(chans) + len(beans)
        # ...and the one pass's writes: each plot's record and ring entry, and the drain hem, wet and flooded entries
        work_counts.OPS["write@plot_pass"] += 2 * len(plots) + len(hem) + len(wet) + len(flooded)
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
    # the widths in pixels at the map's scale, as every channel record holds them (`bridges.channel_footbridges` reads them so)
    M.setdefault("field_ditches", []).extend({"field": name, "poly": c["pts"], "role": c["role"], "w": s.px(c["w"]), "w_tail": s.px(c["w_tail"])} for c in chans[1:])
    M.setdefault("channels", []).append({"poly": chans[0]["pts"], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": name}, "w": s.px(chans[0]["w"]), "field": name})
    if f["weir"]:
        ring, deg, form = f["weir"]
        M.setdefault("weirs", []).append(
            {"x": f["intake"][0], "y": f["intake"][1], "len": round(2 * WEIR_HALF, 2), "w": WEIR_THICK_FT.get(form, WEIR_THICK_FALLBACK_FT), "deg": round(deg, 1), "form": form, "poly": ring}
        )
    M.setdefault("dry_plots", []).extend({k: d[k] for k in ("poly", "crop", "theta", "tract")} for d in dry)
    M.setdefault("wet_plots", []).extend(wet)
    M.setdefault("flooded_plots", []).extend(flooded)
    if ponds:
        M.setdefault("field_ponds", []).extend(ponds)
    if grave_recs:
        M.setdefault("field_graves", []).extend({"x": g["x"], "y": g["y"]} for g in grave_recs)
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
    # on its drawn course, its bends rounded where it is laid (T26 D2), its stations the course the ways keep routing against
    s.stream(f["brook_drawn"], frm={"kind": "offmap"}, to={"kind": "offmap"}, width=BROOK_W, stations=f["brook"])
    if f["weir"]:
        ink.weir(s, M["weirs"][-1])
    ink.draw(s, net, name, plan.field_archetype)
    return acres


def _area(ring: list[tuple[float, float]]) -> float:
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:] + ring[:1], strict=True))) / 2.0


def _roll(s: Settlement, plan: SitePlan, name: str) -> Any:
    """One registered knob drawn in Rust from its table (`roll_knob`) against the running context - the spec's pin taken - and
    recorded as `resolve` records it."""
    knob = KNOBS[name]
    pin = s.knob_pins.get(name, plan.spec.pins.get(name))
    if pin is None:
        ctx = s.knob_context()
        forms = knob.allowed(ctx)
        weights = knob.weights_for(ctx)
        w = [weights.get(v, 0.0) for v in forms] if weights is not None else []
        pin = forms[phases().roll_knob(s.seed, name, len(forms), w)]
    s._resolved_knobs[name] = pin
    return pin


def _polder(s: Settlement, plan: SitePlan) -> None:
    """The polder: every placement from Rust (`stage_polder`, D8; the plan's seam, re-decided after its review) - the block, the
    dike and its trees, the outfall, the resting plots and on a dike-pond its conversion - written and drawn here; `marsh` only
    fills the fringe ring the Rust returns round its wild pond.

    Research:
        the polder's records - NONE: written and drawn from `stage_polder`'s, whose placement is claimed at the Rust (`field/polder.rs`, `field/dike.rs`, `field/landuse.rs`); the figures it adds are claimed where they stand (`POND_FEEDER_FT`, `OUTFALL_FT`, `DITCH_BANK_FT`)
        every low plot tinted - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: a polder or terraced field tints every low plot - each low plot in the wet tint (`states::polder_states` returns `wet` for every low plot before any other roll, so its `FILL` is the wet one); none rests (`polder::rest` never picks a low plot), so none is drawn untinted through `rest_basin`
        the polder's plots drawn apart - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: on some maps about one rice plot in sixteen drawn still flooded and one in twenty gold - each plot drawn in the state the Rust rolled (`states::polder_states`), the flooded ones recorded as the comb's are
        the banks kept - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the bank kept along a canal, 2.6 to 4.9 ft - a no-build bank (`DITCH_BANK_FT` past the half-width) along every channel the polder draws, its feeder and its outfall too
        no dry plots inside a polder - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: enclosed by its dike all the way round, from outside in the dike, the ring canal, the field ditches and the paddies, its dry landward shore beyond
        no beans on a polder's bunds - GUESS: research/questions/0014-bunds-between-the-paddies-aze.drawing.html silent on a polder's bunds; the polder drawn without the comb's bean runs
        a rice polder's pocket pond - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a polder may have a pond on a low plot - the Rust's roll (`stage_polder`'s `pocket_pond`), recorded and drawn here as the comb's is
        its water source - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the wild pond that feeds the polder stands at its head, by the inlet - recorded at the high corner under `reservoir`, the manifest's one name for a pond a field draws its water from, which its readers take for any feeding pond"""
    from l7r.diagram.settlement.water_ways.water import ditch_style

    ftpx = plan.ftpx
    dikepond = plan.field_archetype == "mulberry_dike_fishpond"
    name = f"{plan.spec.name.lower()}-polder"
    rest_form = _roll(s, plan, "paddy_rest")
    split = float(_roll(s, plan, "dikepond_split")) if dikepond else 0.5
    out = phases().stage_polder(
        plan.spec.seed,
        plan.spec.households,
        dikepond,
        plan.pond_layout,
        float(plan.down_deg),
        (plan.W * ftpx / 2.0, plan.H * ftpx / 2.0),
        float(plan.fan_aspect),
        (plan.W * ftpx, plan.H * ftpx),
        rest_form == "unsettled",
        (split, plan.leftover, plan.fry_form, plan.dike_crop),
    )
    if __debug__:
        from l7r.diagram import work_counts

        for k, n in out["counts"].items():
            work_counts.OPS[k] += n
    s.meta(field_archetype=plan.field_archetype, pond_layout=plan.pond_layout, water_source="reservoir", water_source_position="corner_high", dry_furrows_vary=False, paddy_rest=rest_form)
    px, py, rx, ry = out["pond"]
    s.pond(px, py, rx, ry)
    s.marsh([tuple(q) for q in out["fringe"]], role="pond_fringe")
    plots = [{"poly": p["ring"], "fill": FILL[p["state"]], "low": p["low"], "rest": p["rest"], "state": p["state"], "drain_side": None} for p in out["plots"]]
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
        "bead_ponds": [tuple(pocket[1:])] if (pocket := out["pocket_pond"]) else [],
        "brook": [],
        "drain": next(c["pts"] for c in chans if c["seg"] == "drain"),
        "sluice": tuple(out["sluices"][0]),
        "dike_sluices": [tuple(g) for g in out["sluices"]],
        "ftpx": ftpx,
    }
    rings = [p["poly"] for p in plots]
    # the writer's own walks of the rings, counted where they happen (S5, the work-budget audit at T16's landing): each plot's
    # box and middle for its record, its middle again for the wet or flooded record, its area for the acres
    if __debug__:
        from l7r.diagram import work_counts

        work_counts.OPS["pt_test@write_polder"] += sum(4 * len(r) for r in rings)
        work_counts.OPS["write@polder_net"] += len(plots) + len(chans)
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
    # the widths in pixels at the map's scale, as every channel record holds them
    M.setdefault("field_ditches", []).extend({"field": name, "poly": c["pts"], "role": c["role"], "seg": c["seg"], "w": s.px(c["w"]), "w_tail": s.px(c["w_tail"])} for c in chans)
    M.setdefault("channels", []).append({"poly": out["feeder"], "frm": {"kind": "pond"}, "to": {"kind": "field", "name": name}, "w": s.px(POND_FEEDER_FT), "field": name})
    M.setdefault("wet_plots", []).extend(list(_center(p["poly"])) for p in plots if p["low"])
    M.setdefault("flooded_plots", []).extend(list(_center(p["poly"])) for p in plots if p["state"] == "flooded")
    dk = out["dike"]
    band = dk["outer"] + list(reversed(dk["inner"]))
    M.setdefault("dikes", []).append(
        {
            "outline": band,
            "crest": dk["crest"],
            "gaps": dk["gaps"],
            "keepout": dk["outer"],
            "keepout_chords": len(dk["gaps"]),
            "label": "",
            "w_min": round(dk["widths"][0], 1),
            "w_max": round(dk["widths"][1], 1),
        }
    )
    M.setdefault("planted_trees", []).extend({"kind": kind, "trees": [list(c) for c in crowns]} for kind, crowns in dk["trees"])
    s.comb_base_fill(net, name)
    ink.dike(s, dk)
    if dikepond:
        _dikeponds(s, plan, out, split)
    bund = aze_w(ftpx)
    for p in plots:
        if dikepond:
            continue  # every parcel of a dike-pond block is a pond's, its bank or its rice drawn by `_dikeponds`
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
    if pocket:
        pond = {"x": pocket[1], "y": pocket[2], "rx": pocket[3], "ry": pocket[4]}
        M.setdefault("field_ponds", []).append(pond)
        ink.pocket_pond(s, pond)
    s.field_channel(out["feeder"], ditch_style("main", plan.field_archetype)[0], POND_FEEDER_FT, POND_FEEDER_FT, late=True)
    s.corridors.append((out["feeder"], s.px(POND_FEEDER_FT / 2 + DITCH_BANK_FT)))
    run = out["outfall"]
    M["channels"].append({"poly": run, "frm": {"kind": "drain"}, "to": {"kind": "offmap"}, "w": s.px(OUTFALL_FT)})
    col, cls = ditch_style("drain", plan.field_archetype)
    s.field_channel(run, col, OUTFALL_FT, OUTFALL_FT, late=True, cls=cls)
    s.corridors.append((run, s.px(OUTFALL_FT / 2 + DITCH_BANK_FT)))
    s.field_polys.append(outline)
    plan.net = net
    plan.envelope = outline
    plan.acres = sum(_area(r) for r in rings) / SQ_FT_PER_ACRE
    net["acres"] = plan.acres


def _dikeponds(s: Settlement, plan: SitePlan, out: dict[str, Any], split: float) -> None:
    """The dike-pond block's conversion as the Rust placed it: its records (`dikeponds`, `land_use`, the meta and the inset the pig
    sties read), and its ink."""
    M = s.M
    ponds = []
    for kind, parcel, bank, water in out["dikeponds"]:
        ponds.append({"kind": kind, "parcel": parcel, "water": water[1] if water else [], "bank": bank[1] if bank else []})
    M.setdefault("dikeponds", []).extend(p for p in ponds if p["kind"] != "rice")
    M.setdefault("land_use", []).append(
        {
            "overlay": "mulberry_fishpond",
            "count": sum(1 for p in ponds if p["kind"] != "rice"),
            "eligible": "all",
            "plots": [list(_center(p["parcel"])) for p in ponds if p["kind"] != "rice"],
            "leftover_plots": [list(_center(p["parcel"])) for p in ponds if p["kind"] == "rice"],
        }
    )
    # ...read by the pig sties (`pondstock`) through getattr with its default, as the old overlay left it; written through the
    # instance's dict because the settlement declares no such attribute, and declaring one would put core.py in this landing
    # (the round arbiter's ruling on ask:444-T16-fr021-scope: T16 touches only the port's files)
    vars(s)["dikepond_inset"] = float(out["inset"])
    s.meta(dike_crop=plan.dike_crop, dikepond_inset=round(float(out["inset"]), 1), dikepond_split=split, fry_form=plan.fry_form, land_use_overlay="mulberry_fishpond", leftover=plan.leftover)
    ink.dikeponds(s, out["dikeponds"], out["crops"], aze_w(plan.ftpx))
