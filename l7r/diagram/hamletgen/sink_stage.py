"""STAGE 3 - where the runoff goes, in Rust (feature 444 T26 D1): a thin Python function that gathers what the sink reads, calls
`l7r_phases.stage_sink`, and writes what it returns - the drain's run as a drainage ditch, the pond, its reeds and its no-build
box, the plan's `water_sink`, `sink_pond`, `sink_brook` and `confluence` - with every rule asked in Rust before anything is
written (`rust/phases/src/sink/`).

Research:
    the sink's seam - NONE: the stage's plumbing; each rule's claim is at the Rust that decides it (`rust/phases/src/sink/`)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from l7r.diagram import work_counts
from l7r.diagram.settlement.water_ways.water import DRAIN_HUE, DRAINAGE_DITCH
from l7r.diagram.waterfields import DRAIN_FT, chan_px

from .consts import GRAIN
from .phases_ext import phases
from .water.brook_rules import BROOK_DRAWN_W

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from .plan import SitePlan


class SinkRefused(RuntimeError):
    """The drain has no route the rules allow (feature 287, FR-005: refused by name, never drawn in breach)."""


SINK_FRINGE = 44.0
"""The tail pond's reed fringe, out from its shore; the bank's trees stand beyond it (`pondbank`).

Research: reed fringe width - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); a 44 ft ring"""

BROOK_JOIN_TRUNK = 150.0
"""Research: brook below a confluence - CONVENTION: 150 ft on the canvas, so the junction reads"""

NO_BUILD_FT = 10.0
"""Research: no building on the water - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); 10 ft round the pond's box"""

RUN_RECORD_W = 2.5
"""The run's TOPOLOGY record width: `M["channels"]` is the connectivity graph the anchor checks walk, its widths held at a
hairline so a natural watercourse out-measures a field ditch by a wide margin; the drawn width lives in `M["drawn_channels"]`,
which `field_channel` records at the collector's outfall width (writing the drawn width here fired two checks on 14 cohort maps).

Research: the run's topology record - CONVENTION: a hairline 2.5 in the connectivity record, the drawn 5.5 ft in `drawn_channels` (research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the drain at 5.5 ft at its outfall)"""


def stage_sink(s: Settlement, plan: SitePlan) -> None:
    """Where the runoff goes: the drain's run to its pond, to the passing brook or off the map, laid in Rust and written here.

    The pond is a HARD feature - houses, lanes and trees all keep off it - so it is laid with the water, before any of them.

    Steps:
        l7r.diagram.settlement.Settlement.field_channel
        l7r.diagram.settlement.Settlement.pond
        l7r.diagram.settlement.Settlement.pond_reeds

    Research:
        a collector beside a dike - NONE: a diked field (the polder) drains by its own outfall and lays no collector, so the two together are a defect upstream, refused by name
        where the runoff goes - research/questions/0060-field-drains-akusuiro.drawing.html: a pond at the foot, the passing brook, or off the map
        the drain's run drawn - research/questions/0060-field-drains-akusuiro.drawing.html: the drainage-ditch class whichever way it runs, at the collector's own outfall width
        no no-build corridor on a hamlet - research/questions/0058-ground-too-wet-to-build-on.drawing.html: the 33 ft strip is the town and city maps' rule
    """
    M = s.M
    name = f"{plan.spec.name.lower()}-paddies"
    drain = next((d["poly"] for d in M.get("field_ditches") or [] if d.get("role") == "drain" and d.get("field") == name), None)
    if drain is not None and M.get("dikes"):
        # a diked field drains by its own outfall and has no collector (the polder): a dike beside a collector is a defect upstream
        raise SinkRefused(f"{plan.spec.name}: a collector beside a dike - the sink's runs are asked of no dike")
    out = None
    if drain is not None:
        # the brook as the map draws it - the field's stream record, its bends rounded where it was laid (T26 D2)
        drawn = next((rec["poly"] for rec in M.get("streams") or [] if rec.get("stations")), [])
        resting = [[(float(x), float(y)) for x, y in r["outline"]] for r in M.get("fallow_patches") or []]
        try:
            out = phases().stage_sink(
                plan.water_sink == "pond",
                (float(plan.W), float(plan.H)),
                plan.fall,
                float(plan.water_flow),
                plan.envelope,
                drain,
                drawn,
                BROOK_DRAWN_W,
                chan_px(DRAIN_FT[1], GRAIN),
                resting,
                SINK_FRINGE,
                BROOK_JOIN_TRUNK,
            )
        except ValueError as e:
            raise SinkRefused(f"{plan.spec.name}: {e}") from e
    if out is not None:
        _write(s, plan, out, name)
    M["meta"]["water_sink"] = plan.water_sink  # the sink as DRAWN, on the title card (feature 319 plan D10)


def _write(s: Settlement, plan: SitePlan, out: dict, field: str) -> None:  # type: ignore[type-arg]
    """The records the Rust sink returned, written to the manifest and drawn: the run's record names its `field`, whose
    collector it continues - a sibling of that field's own plots, as the collector is (the overlap matrix's parents).

    Research:
        the drain's run drawn - research/questions/0060-field-drains-akusuiro.drawing.html: the drainage-ditch class, at the collector's own outfall width
        no building on the water - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); `NO_BUILD_FT` round the pond's box"""
    for k, n in (out.get("counts") or {}).items():
        work_counts.OPS[k] += n
    if out["pond"] is not None:
        (cx, cy), rx, ry = out["pond"]
        s.pond(cx, cy, rx, ry)
        plan.sink_pond = (cx, cy, rx, ry)
        s.M["meta"]["pond_role"] = "drainage"
        s.pond_reeds([(float(x), float(y)) for x, y in out["reeds"]])  # the reeds kept off what the registry holds beside the pond, not the whole map
        pad = NO_BUILD_FT
        s.block_polys.append([(cx - rx - pad, cy - ry - pad), (cx + rx + pad, cy - ry - pad), (cx + rx + pad, cy + ry + pad), (cx - rx - pad, cy + ry + pad)])
    run = [(float(x), float(y)) for x, y in out["run"]]
    plan.water_sink = out["form"]
    w = chan_px(DRAIN_FT[1], GRAIN)  # the collector's own outfall width: its last strides carry all it carries
    s.field_channel(run, DRAIN_HUE, w, w, cls=DRAINAGE_DITCH)
    s.M["channels"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in run], "frm": {"kind": "drain"}, "to": {"kind": out["to"]}, "w": RUN_RECORD_W, "field": field})
    plan.sink_brook = run
    if out["confluence"] is not None:
        plan.confluence = tuple(out["confluence"])  # `stage_frame` reserves it: the junction is a feature, and the crop must show it
