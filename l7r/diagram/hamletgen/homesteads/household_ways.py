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
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram import work_counts
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


def ways_inputs(s: Settlement) -> dict[str, object]:
    """What the Rust households' ways read (`l7r_phases.households_ways`, feature 444 T30), gathered where `gap_ways.lay_the_ways`
    and the seating's lane law (`tree.seating_law`) read it, before any way is laid.

    Research: plumbing - NONE: the households' ways' inputs, each read where the Python reads it"""
    from l7r.diagram.settlement._knobs import bridge_crossed_waters
    from l7r.diagram.settlement.city.bridges import flooded_ground

    from ..ways import law
    from ..ways.corridors import open_ground_rings
    from ..ways.geom import memo_ground, steading_footprints, worked_ground
    from ..ways.law_water import water_courses
    from ..ways.settle import square_waters
    from ..ways.tree import seating_law
    from .rust_seating import site_cells

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
    cells = site_cells(s, (x0, y0), 5.0, (nx, ny)).ravel().tolist()  # the site's verdict at each cell's center, every cell at once
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


def chose_the_track(s: Settlement, plan: SitePlan) -> Poly:
    """The track out chosen once the last house stands, in Rust (`l7r_phases.track_out`, feature 444 T30), with the homesteads as
    seated standing in for the farmsteads not yet drawn (`seated_parts`); the wood seats it gave up released along it by name
    (`meta.wood_seats_to_the_connector`). `NoDryExit` where no way leaves the frame - the stage's own refusal.

    Research: the track out decided once - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way joins the track out"""
    from ..phases_ext import phases
    from ..ways.track import CONNECTOR_WIDTH, NoDryExit  # the ways' layer sits above the homesteads; asked here once the houses stand

    s._seated_parts = seated_parts(s)  # type: ignore[attr-defined]
    try:
        got = phases().track_out(track_inputs(s, plan))
    finally:
        s._seated_parts = None  # type: ignore[attr-defined]
    if got is None:
        raise NoDryExit("no dry way out of the frame from a gateway on any bearing off the cluster")
    s._seat_search["track_counts"] = sum(got["counts"].values())
    for k, n in got["counts"].items():  # the Rust's counted work on the stage's (feature 444 D5)
        work_counts.OPS[k] += n
    track = [(float(q[0]), float(q[1])) for q in got["track"]]
    st = getattr(s.M, "standing", None)
    if got["seats_taken"] and st is not None:  # ...over a reserved seat, which the way out takes: given up by name
        gone = st.reserved.release_seats_along(track, CONNECTOR_WIDTH)
        if gone:
            s.M["meta"]["wood_seats_to_the_connector"] = [[round(x, 1), round(y, 1)] for x, y in gone]
    return track


def laid_order(tree: Sequence[tuple[Pt, Pt]], houses: Sequence[dict[str, Any]], drawn: Sequence[Any]) -> list[tuple[dict[str, Any], tuple[Pt, ...]]]:
    """Each household's drawn way with its record, in an order it could have been laid: a way after the run its end joins - the
    tree or a way before it - as the gap pass lays them, nearest the way out first, so a record read back in order finds every
    way's end on the track or an earlier way (SC-007). The Rust returns them by household; a way whose end joins nothing goes
    last, in household order.

    Research: households' ways in the order laid - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way joins the track out or a way laid before it"""
    left = [(rec, tuple((float(q[0]), float(q[1])) for q in way)) for rec, way in zip(houses, drawn, strict=True) if way is not None]
    segs: list[tuple[Pt, Pt]] = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in tree]
    out: list[tuple[dict[str, Any], tuple[Pt, ...]]] = []

    def on(p: Pt) -> bool:
        return any(_seg_gap(p, a, b) <= 1.0 for a, b in segs)

    while left:
        k = next((i for i, (_rec, run) in enumerate(left) if on(run[-1])), 0)
        rec, run = left.pop(k)
        out.append((rec, run))
        segs.extend(zip(run, run[1:], strict=False))
    return out


def _seg_gap(p: Pt, a: Pt, b: Pt) -> float:
    """The distance from `p` to the segment a-b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = 0.0 if dx == dy == 0.0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def lay_the_ways(s: Settlement) -> tuple[int, int]:
    """Every household's way laid in the gaps once the last house stands, in Rust (`l7r_phases.households_ways`, feature 444 T30),
    and recorded as `gap_ways.lay_the_ways` records one: its corridor reserved on the tree and the manifest, its way on its record,
    a passage it makes unnecessary ended; a household no way reaches pinched across the neighbor's yard the Rust names. Returns
    (passages ended, pinches); nothing where no access tree stands.

    Research: each household's way in Rust - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the homesteads built first and the lanes after, each household's way run along the gaps to the track out or a way before it, one no way reaches reached across a neighbor's yard"""
    from l7r.diagram.settlement.rolling.access import reserve
    from l7r.diagram.settlement.rolling.gap_ways import pinch

    from ..phases_ext import phases

    houses = [h for h in (s.M.get("houses") or []) if h.get("geom") and h["geom"].get("bbox") is not None]
    if getattr(s, "_access", None) is None or not houses:
        return 0, 0
    got = phases().households_ways(ways_inputs(s))
    s._seat_search["ways_counts"] = sum(got["counts"].values())
    for k, n in got["counts"].items():  # the Rust's counted work on the stage's (feature 444 D5)
        work_counts.OPS[k] += n
    ended = pinched = 0
    for rec, run in laid_order(s._access.segs, houses, got["drawn"]):
        reserve(s, run, (float(rec["x"]), float(rec["y"])))
        rec["geom"]["access"] = run
        if rec.pop("reached_across", None) is not None:  # ...a passage the finished map makes unnecessary, ended where it stands
            rec.pop("passage_depth", None)
            rec.pop("passage", None)
            ended += 1
    for rec, near in zip(houses, got["pinched"], strict=True):
        if near is not None and not rec.get("reached_across"):
            pinched += pinch(rec, [houses[near]])
    return ended, pinched
