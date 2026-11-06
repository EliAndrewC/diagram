"""A DISPERSED farm's own water as a CHANNEL led into its grounds (feature 291 amendment 5, plan D18; FR-018).

homesteads/200, the Tonami dispersed-village museum (translated): "because in former times on the fan plain the water
table was deep and wells were hard to dig, in many areas a small channel was led into the house's grounds and used for
cooking, washing and drinking water" - ACCURATE. The `farm_water` knob (`FARM_WATERS`) rolls it against a well of the
farm's own (drawn at its well pocket, `wells.grove_water`), the other areas as the record reads them, a GUESS.

Each channel runs from the nearest point of the irrigation water - a drawn supply ditch (a main or a branch, never the
drain), or the brook where that is nearer (the nearest a map drawing convention; the brook standing for the water the
ditches are fed from, a GUESS) - to the farm's dooryard, a step off the edge of its threshing yard nearest the water
(where in the dooryard no page read says: a GUESS). It ends there: where it left the lot again no page read says, so the
return is not drawn (a deliberate deviation). The routing is the Rust's since feature 444 T33 (`rust/phases/src/appurtenances/
farm_water.rs`, its search constants with it). It is routed round every building, yard and garden, every OTHER farm's
grove, the crop, the lanes and all other water, and may cross the farm's own grove band - it is led INTO the
grounds, through the wood that surrounds them. A later farm's channel may be led off one already drawn (amendment 6, a GUESS).

Research: channel routing - NONE: candidate points, lattices, crossings and search budgets; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, rot_rect
from l7r.diagram.settlement.water_ways.water import SUPPLY_HUE
from l7r.diagram.sitegen.geom import crop_polys

from ..consts import Poly, Pt

FARM_CHANNEL = "farm channel"
"""The class the channel is drawn under (`interactive/classes/water_and_ways.FarmChannel`)."""

FARM_CHANNEL_W_FT = 2.5
"""The channel's drawn bed: the field channel's legibility floor (`Settlement.channel`'s 2.5 ft) - a map drawing
convention; no page read gives the width of a channel into a farm's grounds.

Research: channel width - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: drawn at the field channel's 2.5 ft bed
"""


def supply_courses(M: Mapping[str, Any]) -> list[list[Pt]]:
    """The irrigation water a channel may be led off: every supply ditch (`field_ditches` whose role is not the drain) and
    every brook (`streams`).

    Research: led off the irrigation water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a main or branch ditch or the brook, never the drain
    """
    out = [[(float(x), float(y)) for x, y in d["poly"]] for d in M.get("field_ditches") or [] if d.get("role") != "drain" and len(d.get("poly") or ()) >= 2]
    out += [[(float(x), float(y)) for x, y in r["poly"]] for r in M.get("streams") or [] if len(r.get("poly") or ()) >= 2]
    return out


def _obstacles(s: Settlement) -> tuple[list[Poly], list[Poly], dict[tuple[float, float], list[Poly]]]:
    """(hard, walls, each farm's own) for the farms' channels: the crop and the paddy plots are hard; every building, yard and
    garden and every lane are walls; and each farm's grove bands and well pocket, keyed by its house, are walls to every OTHER
    farm's channel - its own runs into its grounds through its grove, and its arrival releases its pocket (`wells.grove_water`).

    Research:
        routed round the farm - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: round buildings, yards, gardens and other groves; through its own grove
        walled off lanes, wells and crop - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); every lane, other farms' well pockets and the crop and paddy plots walled
        its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N3, 2026-10-25) - 6 (well pocket = well-house + 3 ft a side, walled from channels)
    """
    from ..ways.geom import steading_footprints, stroke_quad  # local: the ways are a later stage

    walls: list[Poly] = list(steading_footprints(s.M))
    own: dict[tuple[float, float], list[Poly]] = {}
    for g in s.M.get("groves") or []:
        of = g.get("of")
        if of and all(k in g for k in ("x", "y", "w", "h")):
            own.setdefault((round(float(of[0]), 1), round(float(of[1]), 1)), []).append(rot_rect(float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"]), float(g.get("rot", 0.0))))
    # ...and each farm's WELL POCKET (feature 287's seating laid one in each grove farm's dooryard): a farm the channels leave dry
    # draws its well there, so no other farm's channel may run across one
    vr = 2.0 * float(s._well_vr()) + s.px(6.0)
    for q in s.M.get("houses") or []:
        if q.get("well_pocket"):
            own.setdefault((round(float(q["x"]), 1), round(float(q["y"]), 1)), []).append(rot_rect(float(q["well_pocket"][0]), float(q["well_pocket"][1]), vr, vr, 0.0))
    # NOT the other farms' FRAMES: a frame holds the lane's room between two groves, which is exactly where a channel to a
    # farm behind them runs (Audit-905: with the frames walled, six of sixteen farms were cut off their water)
    for ln in s.M.get("lanes") or []:
        p = [(float(x), float(y)) for x, y in ln.get("pts") or []]
        half = float(ln.get("w") or 3) / 2.0
        walls += [stroke_quad(a, b, half) for a, b in zip(p, p[1:], strict=False)]
    paddies = [[(float(a), float(b)) for a, b in r] for f in s.M.get("fields") or [] for r in f.get("plot_rings") or [] if len(r) >= 3]
    return [*crop_polys(s), *paddies], walls, own


def farm_channels(s: Settlement, houses: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """A channel into each grove farm's grounds, routed in Rust (feature 444 T33 D7b, `l7r_phases.farm_channels`: the farms nearest
    the water first, each from the nearest points of the irrigation water to a step off its threshing yard, round everything but its
    own grove and pocket, crossing no other water, a later channel led off an earlier one) and drawn here; returns the farms no
    course reached, which the caller gives a well of their own - never left dry, and reported by `row_rules.water_rules`.

    Research:
        a channel into the grounds - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the shortest route found from the nearest sources
        a farm no channel reaches - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: returned for a well of its own
        channel corridor - GUESS: searched, the record silent (feature 417 T29 pass C, 2026-10-25); a 4 ft no-build corridor along each channel
        washing places - research/questions/0065-washing-places-at-the-waters-edge.drawing.html: a farm's channel is one of the
            waters a washing place stands on, and the one-at-each-house form a step at its end (drawn by `hamletgen/washing.py`)
    """
    from l7r.diagram.work_counts import OPS

    from ..phases_ext import phases
    from ..ways.checks import drawn_water_segs  # local: the ways are a later stage

    courses = supply_courses(s.M)
    if not courses:
        return list(houses)
    hard, walls, own = _obstacles(s)
    pt = lambda q: (float(q[0]), float(q[1]))  # noqa: E731
    farms = []
    for h in houses:
        hx, hy = float(h["x"]), float(h["y"])
        yard = next((y for y in s.M.get("threshing_yards") or [] if y.get("of") and math.dist((float(y["of"][0]), float(y["of"][1])), (hx, hy)) < 0.5), None)
        ring = (yard or {}).get("poly") or (yard or {}).get("outline") or []
        farms.append(((hx, hy), [pt(q) for q in ring], own.get((round(hx, 1), round(hy, 1)), [])))
    got = phases().farm_channels(
        {
            "farms": farms,
            "hard": [[pt(q) for q in r] for r in hard],
            "walls": [[pt(q) for q in r] for r in walls],
            "courses": courses,
            "water": [(pt(a), pt(b)) for a, b in drawn_water_segs(s)],
        }
    )
    for k, n in got["counts"].items():  # the Rust's counted work on the stage's (feature 444 D5)
        OPS[k] += n
    dry: list[Mapping[str, Any]] = []
    for h, path in zip(houses, got["paths"], strict=True):
        if len(path) < 2:
            dry.append(h)
            continue
        hx, hy = float(h["x"]), float(h["y"])
        path = [pt(q) for q in path]
        s.field_channel(path, SUPPLY_HUE, s.px(FARM_CHANNEL_W_FT), s.px(FARM_CHANNEL_W_FT), cls=FARM_CHANNEL)
        s.M["drawn_channels"][-1]["farm"] = [hx, hy]
        s.M.setdefault("farm_channels", []).append({"of": [hx, hy], "pts": [[round(x, 1), round(y, 1)] for x, y in path], "w": s.px(FARM_CHANNEL_W_FT)})
        s.corridors.append((path, s.px(4.0)))
    return dry
