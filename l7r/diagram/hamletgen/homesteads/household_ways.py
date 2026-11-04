"""THE TRACK OUT, CHOSEN ONCE THE LAST HOUSE STANDS, AND THE HOUSEHOLDS' WAYS LAID TO IT (feature 320, plan D2, FR-008).

The GM, 2026-10-04, of the exit strip and the field's corridor the seating used to reserve before any house: *"we should
eliminate both ... because the space we've already allocated can serve the same function"*. So nothing of a way is laid or
reserved while the farmhouses are seated - the lane's room between neighbors (feature 318) is what keeps a way possible.

Once the last house stands, the track out's whole course is chosen ONCE (`track.choose_track_out`), the GM: *"collapsing the
multiple decisions into a single decision regarding the lane"* - a first leg decided on the seating's bearing apart from the
track's own route met a household's way in a nub. No farmstead is drawn yet (the overlap registry would refuse a way on a
drawn yard), so the homesteads as seated stand in for them (`seated_parts`, read by `fabric._homestead_polys`), with every
household's wood seats. Each household's way is then laid in the gaps to the track's stretch about the cluster
(`near_the_cluster`, `gap_ways.lay_the_ways`), and `stage_track` draws the track as chosen.

Research: houses before lanes - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every farmhouse seated before any way is laid; the track out leaves from the cluster's edge and each household's way joins it
"""

from __future__ import annotations

import math
import os
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.settlement.homestead_parts.groves import crown_lift
from l7r.diagram.settlement.homestead_parts.stands import crown_reach
from l7r.diagram.settlement.homestead_parts.wood_share import COPSE_CLUMP_BS

from ..consts import Poly, Pt
from .region import _clip

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan


def box_poly(b: Sequence[float]) -> Poly:
    """A box `(cx, cy, w, h)` as its four corners.

    Research: plumbing - NONE: a box's corners"""
    x0, y0, x1, y1 = b[0] - b[2] / 2, b[1] - b[3] / 2, b[0] + b[2] / 2, b[1] + b[3] / 2
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def seat_walls(s: Settlement) -> tuple[list[Pt], float]:
    """Every household's reserved wood seats and the reach a lane keeps off each: the buffer the registry reserves them with
    (`stages.reserve_the_seating`) and half the track's tread.

    Research: the track off the wood seats - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a lane kept off a household's copse seat by the crown's reach (or 0.45 of the clump and 4 ft) and 4 ft more; no page read shows a lane between a farmhouse and its own grove, and none gives how far a way kept off one"""
    clump = COPSE_CLUMP_BS * s.bscale
    reach = max(clump * 0.45 + 4, crown_reach(clump, 0.0, lift=crown_lift(s.bscale))) + 4.0
    seats = [(float(p[0]), float(p[1])) for h in s.M.get("houses") or [] for p in (h.get("wood_share") or {}).get("seats") or ()]
    return seats, reach


TRUNK_FT = 4.0
"""A persimmon's trunk box, the part of it a way keeps off (`access.fixtures_clear` holds it the same).

Research: a persimmon by its trunk alone - GUESS: held off by a 4 ft trunk box, the crown free to overhang the path"""


def seated_parts(s: Settlement) -> list[tuple[Poly, Pt | None, str]]:
    """The homesteads as seated, before any is drawn, as `fabric._homestead_polys` reads the drawn ones - (polygon, owner,
    kind): each household's house, threshing yard, beds, well, shed, byre and fixtures from its seated geometry (a persimmon
    by its trunk), and its wood seats as octagons of the reach a lane keeps off them (`seat_walls`).

    Research:
        nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the track out keeps off every homestead's house, yard, beds, well, sheds and fixtures as they will be drawn
        the track off the wood seats - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: each seat an octagon of the reach a lane keeps off it (`seat_walls`); no page read shows a lane between a farmhouse and its own grove
        a persimmon by its trunk alone - GUESS: held off by `TRUNK_FT`, the crown free to overhang the track
        its salts, guards and sentinels - NONE: they decide nothing about the place - 8 (octagon standing in for a circle)
    """
    out: list[tuple[Poly, Pt | None, str]] = []
    for h in s.M.get("houses") or []:
        boxes = (h.get("geom") or {}).get("boxes") or {}
        own = (float(h["x"]), float(h["y"]))
        for key, kind in (("house", "houses"), ("yard", "threshing_yards"), ("well", "wells"), ("shed", "sheds"), ("byre", "sheds")):
            if boxes.get(key) is not None:
                out.append((box_poly(boxes[key]), own, kind))
        out += [(box_poly(b), own, "gardens") for b in boxes.get("gardens") or ()]
        for name, b in (boxes.get("fixtures") or {}).items():
            out.append((box_poly(b if name != "persimmon" else (b[0], b[1], s.px(TRUNK_FT), s.px(TRUNK_FT))), own, "fixtures"))
    seats, reach = seat_walls(s)
    ring = [(math.cos(k * math.pi / 4.0), math.sin(k * math.pi / 4.0)) for k in range(8)]
    out += [([(p[0] + c * reach, p[1] + d * reach) for c, d in ring], None, "wood seats") for p in seats]
    return out


def near_the_cluster(s: Settlement, track: Poly, margin: float) -> list[tuple[Pt, Pt]]:
    """The legs of `track` within `margin` of the seated homesteads' extent and the track's start, each clipped to it (`region._clip`): the stretch the
    households' ways are laid to. The stages ask it at the gap pass's farther join reach (`gap_ways.JOIN_FAR_FT`): at the
    raster's 160 ft margin a household's way joined the track 26 ft past the cropped frame, two paths leaving the map side by
    side (Inashiro's glyph check, feature 320) - the frame is cropped later, about the homesteads' own extent.

    Research: plumbing - NONE: the search's window on the track"""
    boxes = list(getattr(s, "placed", None) or [])
    if not boxes:
        return list(zip(track, track[1:], strict=False))
    # ...AND THE TRACK'S START, its gateway off the cluster's edge: Kuwabata's stood 51 ft off its homesteads and ran on along
    # them, so a window of the homesteads alone held none of the track and no way could be laid
    g = track[0] if track else (boxes[0][0], boxes[0][1])
    box = (
        min(g[0], *(b[0] - b[2] / 2 for b in boxes)) - margin,
        min(g[1], *(b[1] - b[3] / 2 for b in boxes)) - margin,
        max(g[0], *(b[0] + b[2] / 2 for b in boxes)) + margin,
        max(g[1], *(b[1] + b[3] / 2 for b in boxes)) + margin,
    )
    out = []
    for a, b in zip(track, track[1:], strict=False):
        span = _clip(a, b, box)
        if span is not None and span[1] > span[0]:
            out.append(((a[0] + (b[0] - a[0]) * span[0], a[1] + (b[1] - a[1]) * span[0]), (a[0] + (b[0] - a[0]) * span[1], a[1] + (b[1] - a[1]) * span[1])))
    return out


def track_inputs(s: Settlement, plan: SitePlan) -> dict[str, object]:
    """What the Rust track out reads (`l7r_phases.track_out`, feature 444 T30), gathered as `track.choose_track_out` reads it, with
    the homesteads as seated standing in for the farmsteads (`seated_parts`, installed by the caller).

    Research: plumbing - NONE: the track out's inputs, each read where `choose_track_out` reads it"""
    from l7r.diagram.settlement import skeleton_layout
    from l7r.diagram.settlement.land.wet import marsh_ground
    from l7r.diagram.sitegen.geom import crop_polys

    from ..ways import law
    from ..ways.checks import drawn_water_segs
    from ..ways.fabric import _homestead_polys
    from ..ways.route import _CROSSING
    from ..ways.settle import square_waters

    seat = plan.seat
    ax, ay = seat["along"]
    ox, oy = seat["out"]
    layout = skeleton_layout(plan.lane_skeleton, 0.0, 0.0, seat["lat"], seat["dep"])
    gx, gy = float(layout["gateway"][0]), float(layout["gateway"][1])
    polys = _homestead_polys(s)
    toe = s.toe_band()
    st = getattr(s.M, "standing", None)
    forbid = st.forbidding("lanes") if st is not None else []
    channels = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    pt = lambda q: (float(q[0]), float(q[1]))  # noqa: E731
    ring = lambda r: [pt(q) for q in r]  # noqa: E731
    return {
        "canvas": (float(plan.W), float(plan.H)),
        "out": (float(ox), float(oy)),
        "fall": pt(plan.fall),
        "seat": (float(seat["cx"]), float(seat["cy"])),
        "along": (float(ax), float(ay)),
        "fallback": (seat["cx"] + ax * gx + ox * gy, seat["cy"] + ay * gx + oy * gy),
        "houses": [(float(h["x"]), float(h["y"])) for h in s.M.get("houses") or []],
        "envelope": ring(plan.envelope),
        "crops": [ring(c) for c in crop_polys(s)],
        "wet": [ring(w) for w in ([toe] if toe else []) + marsh_ground(s.M)],
        "paddy": [ring(f["outline"]) for f in s.M.get("fields") or [] if f.get("outline")],
        "steadings": [(ring(poly), kind == "groves") for poly, _owner, kind in polys],
        "solid": [tuple(float(v) for v in b) for b in law.solid_boxes(s.M)],
        "pond": tuple(float(v) for v in plan.sink_pond) if plan.sink_pond else None,
        "sink_brook": ring(plan.sink_brook or []),
        "watercourses": [(pt(a), pt(b)) for a, b in plan.watercourses],
        "drawn": drawn_water_segs(s),
        "thread_lines": [*((pt(a), pt(b)) for a, b in plan.watercourses), *channels],
        "course": ring(getattr(plan, "brook", None) or []),
        "forbidding": [ring(e[1]) for e in forbid if e[0] != "wood seat"],
        "seats": [ring(e[1]) for e in forbid if e[0] == "wood seat"],
        "brooks": [ring(b) for b in law._brooks(s.M)],
        "square_waters": [(ring(c), float(h)) for c, h in square_waters(s.M)],
        "crossing": (ring(plan.brook), float(_CROSSING["radius"]), float(_CROSSING["cost"])) if float(_CROSSING["cost"]) and getattr(plan, "brook", None) else None,  # type: ignore[arg-type]
    }


def compare_rust_track(s: Settlement, plan: SitePlan, track: Poly, path: str) -> None:
    """Run the Rust track out on the state `track` was chosen from and append both, with the Rust's counted work, to the JSON
    lines at `path` - the comparison of feature 444 T30 before the stage is wired; the map is not touched.

    Research: plumbing - NONE: a comparison's record, deciding nothing about the place"""
    import json

    from ..phases_ext import phases

    got = phases().track_out(track_inputs(s, plan))
    rec = {
        "name": plan.spec.name,
        "seed": plan.spec.seed,
        "households": plan.spec.households,
        "python": [[round(q[0], 1), round(q[1], 1)] for q in track],
        "rust": None if got is None else [[round(q[0], 1), round(q[1], 1)] for q in got["track"]],
        "rust_counts": None if got is None else sum(got["counts"].values()),
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def ways_inputs(s: Settlement) -> dict[str, object]:
    """What the Rust households' ways read (`l7r_phases.households_ways`, feature 444 T30), gathered where `gap_ways.lay_the_ways`
    and the seating's lane law (`tree.seating_law`) read it, before any way is laid.

    Research: plumbing - NONE: the households' ways' inputs, each read where the Python reads it"""
    from l7r.diagram.settlement._knobs import bridge_crossed_waters
    from l7r.diagram.settlement.city.bridges import flooded_ground
    from l7r.diagram.settlement.rolling.access import on_site_ground

    from ..ways import law
    from ..ways.corridors import open_ground_rings
    from ..ways.geom import memo_ground, steading_footprints, worked_ground
    from ..ways.law_water import water_courses
    from ..ways.settle import square_waters
    from ..ways.tree import seating_law

    pt = lambda q: (float(q[0]), float(q[1]))  # noqa: E731
    ring = lambda r: [pt(q) for q in r]  # noqa: E731
    box = lambda b: tuple(float(v) for v in b)  # noqa: E731
    houses = [h for h in (s.M.get("houses") or []) if h.get("geom") and h["geom"].get("bbox") is not None]
    rows = []
    for rec in houses:
        geom = rec["geom"]
        bx = geom.get("boxes") or {}
        fixtures = [(name == "persimmon", box(b)) for name, b in (bx.get("fixtures") or {}).items()]
        sheds = [box(bx[k]) for k in ("shed", "byre") if bx.get(k) is not None]
        beds = [box(b) for b in [bx.get("well"), *(bx.get("gardens") or ())] if b is not None]
        yard = bx.get("yard") or geom.get("yard") or geom["house"]
        well = geom.get("well")
        head = None if well is None else (float(well[0]), float(well[1]), 2.0 * float(s._well_vr()), 2.0 * float(s._well_vr()))
        rows.append(
            (
                box(bx.get("house") or geom["house"]),
                box(yard),
                beds,
                sheds,
                fixtures,
                box(geom["house"]),
                box(geom.get("yard") or yard),
                float(geom.get("turn") or 0.0),
                box(geom["bbox"]),
                (float(rec["x"]), float(rec["y"])),
                head,
            )
        )
    segs = [(pt(a), pt(b)) for a, b in s._access.segs]  # type: ignore[attr-defined]
    placed = [box(b) for b in getattr(s, "placed", []) or []]
    xs = [b[0] - b[2] / 2 for b in placed] + [q[0] for ab in segs for q in ab]
    ys = [b[1] - b[3] / 2 for b in placed] + [q[1] for ab in segs for q in ab]
    xe = [b[0] + b[2] / 2 for b in placed] + [q[0] for ab in segs for q in ab]
    ye = [b[1] + b[3] / 2 for b in placed] + [q[1] for ab in segs for q in ab]
    # the site at the lane raster's own 5 ft cells, as `gap_ways.lane_layers` asks it (its origin, 160 ft past every placed box -
    # the households' and what else stands, or the cells are not the raster's), and 40 ft further each way for the lines the
    # standing ground samples
    lx0, ly0 = max(0.0, min(xs) - 160.0), max(0.0, min(ys) - 160.0)
    x0, y0 = lx0 - 8 * 5.0, ly0 - 8 * 5.0
    x1, y1 = min(float(s.W), max(xe) + 160.0) + 40.0, min(float(s.H), max(ye) + 160.0) + 40.0
    nx, ny = max(1, math.ceil((x1 - x0) / 5.0)), max(1, math.ceil((y1 - y0) / 5.0))
    cells = [not on_site_ground(s, c, c) for j in range(ny) for i in range(nx) for c in [(x0 + (i + 0.5) * 5.0, y0 + (j + 0.5) * 5.0)]]
    wood = getattr(s, "_wood", None)
    seats = [(float(q[0]), float(q[1])) for bucket in (wood.seats.buckets.values() if wood is not None else ()) for q in bucket]
    lawful = seating_law(s)
    st = getattr(s.M, "standing", None)
    lanes = st.forbidding("lanes") if st is not None else []
    decks = st.forbidding("bridges") if st is not None else []
    edge = memo_ground(s, "worked", worked_ground).edge
    edge_segs = [] if edge is None else [(pt(a), pt(b)) for g in getattr(edge, "geoms", [edge]) for a, b in zip(g.coords, list(g.coords)[1:], strict=False)]
    turned = lambda h: (float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"]), float(h.get("rot", 0.0)))  # noqa: E731
    own = lambda h, r: r.get("of") and math.dist(pt(r["of"]), (float(h["x"]), float(h["y"]))) <= 0.5  # noqa: E731
    parts_of = lambda h: [ring(r["poly"]) for key in ("byres", "farm_sheds", "threshing_yards", "gardens") for r in s.M.get(key) or [] if own(h, r) and r.get("poly")]  # noqa: E731
    return {
        "households": rows,
        "extra": [box(b) for b in getattr(s, "placed", []) or [] if not any(b is h["geom"]["bbox"] for h in houses)],
        "segs": segs,
        "ground": ((x0, y0), 5.0, nx, cells),
        "seats": seats,
        "lane_gap": float(wood.lane_gap) if wood is not None else 0.0,
        "canvas": (float(s.W), float(s.H)),
        "square_waters": [(ring(c), float(h)) for c, h in square_waters(s.M)],
        "brooks": [ring(b) for b in law._brooks(s.M)],
        "destinations": ([(float(h["x"]), float(h["y"])) for h in s.M.get("houses") or []] + law.way_targets(s.M), edge_segs, [ring(p) for p in steading_footprints(s.M)]),
        "root": ring(s.M.get("way_out_track") or []),
        "steadings": [(turned(h), parts_of(h)) for h in s.M.get("houses") or [] if all(k in h for k in ("x", "y", "w", "h"))],
        "houses": [turned(h) for h in lawful.houses if all(k in h for k in ("x", "y", "w", "h"))],
        "yards": [(ring(p), None if o is None else pt(o)) for p, o in lawful.yards if len(p) >= 3],
        "solid": [box(b) for b in lawful.solid],
        "fixtures": [ring(q) for q in lawful.fixtures],
        "buildings": [ring(q) for q in lawful.buildings],
        "open_rings": [ring(r) for r in open_ground_rings(s.M)],
        "forbidding": [ring(e[1]) for e in lanes],
        "channels": [ring(c) for c in water_courses(s.M, "channel")],
        "crossed": [(ring(w), float(ww)) for w, ww in bridge_crossed_waters(s.M)],
        "fords": [pt(f) for f in (s.M.get("meta") or {}).get("brook_fords") or []],
        "flooded": flooded_ground(s.M),
        "deck_forbidding": [ring(e[1]) for e in decks if e[0] != "bridges"],
    }


def watch_verdicts(path: str) -> Any:
    """Record every verdict Python's lane law gives a household's way while `lay_the_ways` runs - the run, the house, the first
    rule `Lawful.fault` names - to the JSON lines at `path`, for bisecting a way the Rust admits and Python refuses; returns the
    undo.

    Research: plumbing - NONE: a comparison's record, deciding nothing about the place"""
    import json

    from ..ways import tree as tree_mod
    from ..ways.settle.lawful import Lawful

    fh = open(path, "a", encoding="utf-8")  # noqa: SIM115 - closed by the undo
    faults: list[Any] = []
    orig_fault, orig_admits = Lawful.fault, tree_mod.admits

    def fault(self: Any, run: Any, width: float, skip: Any = None) -> Any:
        why = orig_fault(self, run, width, skip)
        faults.append(why)
        return why

    def admits(base: Any, M: Any, run: Any, role: Any = "access", house: Any = None, yard: Any = None) -> bool:
        faults.clear()
        ok = orig_admits(base, M, run, role, house, yard)
        rec = {
            "house": None if house is None else [round(float(house["x"]), 1), round(float(house["y"]), 1)],
            "run": [[round(q[0], 1), round(q[1], 1)] for q in run],
            "ok": ok,
            "faults": [f for f in faults if f],
        }
        fh.write(json.dumps(rec) + "\n")
        return ok

    from l7r.diagram.settlement.rolling import access as acc
    from l7r.diagram.settlement.rolling import gap_ways as gw

    orig_first, orig_taut = gw._first_admitted, gw.taut
    legs: list[Any] = []

    def first(s_: Any, runs: Any, leg_ok: Any, geom: Any, memo: Any) -> Any:
        def logged(a: Any, b: Any) -> bool:
            ok = leg_ok(a, b)
            if not ok:
                why = [
                    n
                    for n, f in (
                        ("house", lambda: acc.house_clear(a, b, geom, acc.house_gap(s_))),
                        ("fixtures", lambda: acc.fixtures_clear(s_, a, b, geom)),
                        ("parts", lambda: acc.parts_clear(s_, a, b, geom)),
                        ("standing", lambda: acc.standing_ground(s_, a, b, memo)),
                    )
                    if not f()
                ]
                legs.append([[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)], why])
            return ok

        for q in runs:
            legs.clear()
            run = orig_taut(q, logged, acc.doubles_back, gw.GAP_LEGS)
            drawn = acc.admitted(s_, run, geom, memo) if run is not None else None
            fh.write(
                json.dumps(
                    {
                        "house": [round(float(geom["house"][0]), 1), round(float(geom["house"][1]), 1)],
                        "cand": [[round(p[0], 1), round(p[1], 1)] for p in q],
                        "taut": None if run is None else [[round(p[0], 1), round(p[1], 1)] for p in run],
                        "drawn": drawn is not None,
                        "refused_legs": legs[:6],
                    }
                )
                + "\n"
            )
            if drawn is not None:
                return drawn
        return None

    Lawful.fault, tree_mod.admits = fault, admits  # type: ignore[method-assign]
    gw._first_admitted = first

    def undo() -> None:
        Lawful.fault, tree_mod.admits = orig_fault, orig_admits  # type: ignore[method-assign]
        gw._first_admitted = orig_first
        fh.close()

    return undo


def compare_rust_ways(s: Settlement, inputs: dict[str, object], path: str) -> None:
    """Run the Rust households' ways on the state `inputs` was gathered from and append each household's way beside Python's -
    which `lay_the_ways` has laid since - to the JSON lines at `path`; the map is not touched.

    Research: plumbing - NONE: a comparison's record, deciding nothing about the place"""
    import json

    from ..phases_ext import phases

    got = phases().households_ways(inputs)
    houses = [h for h in (s.M.get("houses") or []) if h.get("geom") and h["geom"].get("bbox") is not None]
    python = [None if h["geom"].get("access") is None else [[round(q[0], 1), round(q[1], 1)] for q in h["geom"]["access"]] for h in houses]
    rust = [None if w is None else [[round(q[0], 1), round(q[1], 1)] for q in w] for w in got["drawn"]]
    rec = {
        "centers": [[round(float(h["x"]), 1), round(float(h["y"]), 1)] for h in houses],
        "households": len(houses),
        "placed": len(getattr(s, "placed", []) or []),
        "python": python,
        "rust": rust,
        "rust_counts": sum(got["counts"].values()),
        "rust_verdicts": [[[[round(q[0], 1), round(q[1], 1)] for q in w], k, ok] for w, k, ok in got["verdicts"]],
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def chose_the_track(s: Settlement, plan: SitePlan) -> Poly:
    """The track out chosen once the last house stands (`track.choose_track_out`), with the homesteads as seated standing in
    for the farmsteads not yet drawn (`seated_parts`).

    Research: the track out decided once - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way joins the track out"""
    from ..ways.track import choose_track_out  # the ways' layer sits above the homesteads; asked here once the houses stand

    s._seated_parts = seated_parts(s)  # type: ignore[attr-defined]
    try:
        track = choose_track_out(s, plan)
        compare = os.environ.get("L7R_RUST_COMPARE")
        if compare:  # feature 444 T30: the Rust track out run beside it on the same state, logged, the map untouched
            compare_rust_track(s, plan, track, compare)
        return track
    finally:
        s._seated_parts = None  # type: ignore[attr-defined]
