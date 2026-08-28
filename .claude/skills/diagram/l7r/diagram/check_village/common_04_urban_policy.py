"""Town and city policy helpers - fire features, the theater stage, ward interiors, the ring road (feature 145: moved out of common_02 so the hamlet path, which never calls them, never executes the module that holds them; the module-level floor then means what the GM said)."""

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import sat_overlap

from .common_01_geometry import (
    _OVERLAP_STRUCTS,
    Check,
    Manifest,
    Poly,
    Pt,
    _struct_rect,
    point_in_poly,
    poly_area,
    rect_corners,
    seg_closest,
    seg_dist,
    segments_cross,
    solid_structs,
    sweep_hi,
)
from .common_02_overlap_policy import footprint_on_line, in_ellipse
from .common_03_capacity import DWELLING_KINDS, RESERVE_CAP_FRAC, RHO_CANONICAL


def check_ring_road_clear(M: Mapping[str, Any], check: Any) -> None:
    """THE RING ROAD IS A CLEAR PATROL ROAD - it must run clear of EVERY solid footprint and of
    fields. The gate guard houses / inspection stations / towers DO sit along it (wall furniture -
    `gate_structs` and `wall_towers` are overlap TARGETS and EXEMPT respectively, so the registry
    leaves them out), and a ward fence may cross it only at a gated kido. Overlap = the ring's BED
    passes through a footprint. Reads the REGISTRY, never a hand list (GM 2026-07-25).

    FACTORED OUT of the scale=="city" block (GM 2026-08-09, 'estates should not overlap with the
    ring-road'): a CAPITAL has a ring road too, and this check living only under scale=="city"
    meant four lineage estates could stand on the capital's patrol road with a green gate - the
    check never RAN there, which looks exactly like passing. Two gaps stacked: the scope, and the
    victim list - `manors` and `religious` are overlap TARGETS (protected FROM structs by the
    matrix), but nothing about being a target keeps a compound off the patrol road, so both ride
    along here explicitly."""
    ring_rd = M.get("ring_road")
    if not ring_rd:
        return
    rbed = (M.get("ring_road_width", 15) - 6) / 2

    def _rfoot(it: dict[str, Any]) -> list[tuple[float, float]]:
        if "rot" in it:
            return rect_corners(it)
        rhw, rhh = it["w"] / 2, it["h"] / 2
        return [(it["x"] - rhw, it["y"] - rhh), (it["x"] + rhw, it["y"] - rhh), (it["x"] + rhw, it["y"] + rhh), (it["x"] - rhw, it["y"] + rhh)]

    # ...except an official NOTICE BOARD inside a GATE PRECINCT. A kosatsuba is street furniture,
    # not a compound: a ~12x5 ft post-and-roof board that must stand within ~60 real ft of a road
    # where people pass (kosatsuba_by_the_road), which at a gate means the same crowded verge the
    # guard house, inspection station and towers already line. Scoped to the precinct on purpose -
    # a board out on an open stretch of patrol lane is still a defect.
    rr_gates = [g for g in (M.get("gates") or [])] + ([M["gate"]] if M.get("gate") else [])

    def _rr_exempt(it: dict[str, Any]) -> bool:
        return it.get("label") in (None, "notice board") and "vw" in it and any(math.hypot(it["x"] - g[0], it["y"] - g[1]) < 130 for g in rr_gates)

    on_ring = [
        it.get("name") or it.get("label") or it.get("kind") or "compound" for it in solid_structs(M, "religious", "manors") if footprint_on_line(_rfoot(it), ring_rd, rbed) and not _rr_exempt(it)
    ]
    on_ring += ["field:" + f["name"] for f in M.get("fields", []) if footprint_on_line(f["outline"], ring_rd, rbed)]
    check(
        "ring_road_kept_clear",
        not on_ring,
        f"the ring road must run CLEAR of buildings/civic compounds/fields (only the gate guard houses, inspection stations, towers and gated ward fences may sit on it): {sorted(set(on_ring))}",
    )


def check_theater_stage(M: Manifest, check: Check) -> None:
    """The theater stage's siting. It BELONGS to a temple/monastery precinct (a temple OPERA STAGE / shrine
    NOH stage), the audience gathering in the open ground between stage and hall, the stage FACING the hall:
    (1) `theater_stage_clear` - the stage + its viewing ground sit in CLEAR ground, overlapping NOTHING (no
        wall, moat, road, street/alley, watercourse, building, compound, grave, field, or pond). Unlike a
        packed dwelling it is not auto-checked by the generic overlap pass, so this is its dedicated guard.
    (2) `theater_stage_by_temple` - ADJACENT to a religious hall (center within ~260px of the nearest one).
    (3) `theater_stage_faces_temple` - its viewing ground OPENS TOWARD that hall (the stage faces it). The
        glyph's open side is local +y, so after `rot` it points (-sin, cos); that aligns with the hall."""
    ts_raw = M.get("theater_stage")
    # LIST since 2026-08-10 (the singleton write clobbered a second stage); old manifests carry a dict
    ts_all = ts_raw if isinstance(ts_raw, list) else ([ts_raw] if ts_raw else [])
    if not ts_all:
        return
    ts_hits: list[str] = []
    ts_far: list[str] = []
    ts_back: list[str] = []
    for ts in ts_all:
        _theater_one_stage(M, ts, ts_hits, ts_far, ts_back)
    check(
        "theater_stage_clear",
        not ts_hits,
        f"theater stage footprint(s) overlap {sorted(set(ts_hits))[:6]} - the stage and its viewing ground "
        f"must sit in CLEAR ground, touching nothing (no wall, moat, road, street/alley, watercourse, "
        f"building, compound, grave, field, or pond)",
    )
    if M.get("religious"):
        check(
            "theater_stage_by_temple",
            not ts_far,
            f"monzen theater stage(s) far from every temple/monastery: {ts_far[:3]} (want <= 260px) - a temple/shrine "
            f"performance stage sits ADJACENT to a religious hall with the viewing ground between them "
            f"(a commercial quarter theater takes kind='machi' and owes no hall)",
        )
        check(
            "theater_stage_faces_temple",
            not ts_back,
            f"monzen theater stage(s) whose viewing ground does not OPEN toward the temple: {ts_back[:3]} (alignment "
            f"want >= 0.5) - the stage faces the hall with the audience between; set `rot` so the ground opens "
            f"toward the temple (the stage's back is the side AWAY from the audience)",
        )


def _theater_one_stage(M: Manifest, ts: dict[str, Any], ts_hits: list[str], ts_far: list[str], ts_back: list[str]) -> None:
    """One stage's share of check_theater_stage: clear-ground hits for every stage; the temple
    adjacency/facing verdicts only for a MONZEN (temple) stage - kind='machi' is the commercial
    quarter theater and sits in the fabric, not at a hall."""
    # (1) CLEAR: build the full footprint (the viewing ground PLUS the roofed stage straddling its north edge)
    w, h = ts["w"], ts["h"]
    sh = h * 0.26
    cyl, fh = -sh * 0.25, h + sh * 0.5
    thr = math.radians(ts.get("rot", 0))
    ca, sa = math.cos(thr), math.sin(thr)
    sc = [(ts["x"] + dx * ca - dy * sa, ts["y"] + dx * sa + dy * ca) for dx, dy in ((-w / 2, cyl - fh / 2), (w / 2, cyl - fh / 2), (w / 2, cyl + fh / 2), (-w / 2, cyl + fh / 2))]
    hits = []
    lines = []  # linear barriers (name, polyline, half-width)
    if M.get("wall"):
        lines.append(("the wall", M["wall"], 9))
    if M.get("moat"):
        lines.append(("the moat", M["moat"], M.get("moat_width", 26) / 2 + 4))
    if M.get("road"):
        lines.append(("a road", M["road"], M.get("road_width", 30) / 2))
    if M.get("ring_road"):
        lines.append(("the ring road", M["ring_road"], M.get("ring_road_width", 15) / 2))
    lines += [("a street", st["pts"], st.get("w", 18) / 2) for st in M.get("town_streets", [])]
    lines += [("an alley", a["pts"], a.get("w", 10) / 2) for a in M.get("alleys", [])]
    lines += [("a stream", s["poly"], s.get("w", 9) / 2) for s in M.get("streams", [])]
    lines += [("a channel", c["poly"], c.get("w", 2.5) / 2 + 2) for c in M.get("channels", [])]
    lines += [("the canal", c["poly"], c.get("w", 12) / 2 + 2) for c in M.get("canals", [])]
    for nm, pts, hw in lines:
        if len(pts) >= 2 and footprint_on_line(sc, pts, hw):
            hits.append(nm)
    granary = M.get("granary")  # solid features (buildings, compounds, graves)
    solids = (
        [s for k in _OVERLAP_STRUCTS if k != "theater_stage" for s in M.get(k, [])]  # a stage is not its own obstacle; stage-vs-stage is the generic matrix's business now
        + M.get("manors", [])
        + M.get("religious", [])
        + M.get("shrines", [])
        + M.get("gate_structs", [])
        + M.get("storehouses", [])
        + M.get("merchant_estates", [])
        + M.get("threshing_yards", [])
        + M.get("gardens", [])
        + M.get("inspection_stations", [])
        + (granary["stores"] if granary else [])
    )
    if M.get("governor_mansion"):
        solids.append(M["governor_mansion"])
    for r in solids:
        if abs(r["x"] - ts["x"]) + abs(r["y"] - ts["y"]) <= 440 and sat_overlap(sc, rect_corners(_struct_rect(r))):
            hits.append(f"a {r.get('kind', 'building')}")
    for fkey in ("fields", "fallow_patches", "flower_fields"):  # areas: paddies/fields and the pond
        for fld in M.get(fkey, []):
            ol = fld["outline"]
            if any(point_in_poly(px, py, ol) for px, py in sc) or any(point_in_poly(vx, vy, sc) for vx, vy in ol):
                hits.append("a field")
                break
    pond = M.get("pond")
    if pond and (
        point_in_poly(pond[0], pond[1], sc)  # pond engulfed by the stage, OR a stage corner in the pond
        or any(((px - pond[0]) / (pond[2] + 6)) ** 2 + ((py - pond[1]) / (pond[3] + 6)) ** 2 <= 1.0 for px, py in sc)
    ):
        hits.append("the pond")
    ts_hits += hits
    halls = M.get("religious", [])
    if not halls:
        return
    # EVERY stage faces a temple (GM 2026-08-10). A `machi` kind was briefly exempted here on
    # the research finding that a capital's entertainment district is commercial - but the
    # SETTING rule is older and governs: a Rokugani stage belongs to a hall and opens toward it,
    # whoever pays for the troupe. The kind still records which doctrine sited the stage; it no
    # longer excuses the facing.
    nearest = min(halls, key=lambda h: math.hypot(ts["x"] - h["x"], ts["y"] - h["y"]))
    near = math.hypot(ts["x"] - nearest["x"], ts["y"] - nearest["y"])
    if near > 260:
        ts_far.append(f"({round(ts['x'])},{round(ts['y'])}) {round(near)}px out")
    th = math.radians(ts.get("rot", 0))
    ox, oy = -math.sin(th), math.cos(th)  # the viewing ground's open direction (toward the audience/temple)
    dx, dy = nearest["x"] - ts["x"], nearest["y"] - ts["y"]
    d = math.hypot(dx, dy) or 1.0
    facing = (ox * dx + oy * dy) / d
    if facing < 0.5:
        ts_back.append(f"({round(ts['x'])},{round(ts['y'])}) alignment {facing:.2f}")


def check_fire_features(M: Manifest, check: Check) -> None:
    """Geometry of the fire-watch towers (hinomi-yagura) a walled town or a city draws. Scale-agnostic:
    the PRESENCE/count checks live in the scale blocks; this validates whatever is drawn, so it is a
    no-op for a settlement that has none. WHY (a dense, enclosed wooden core needs a fire-watch over
    its rooftops, manned by the magistrate's watch): settlements.md 'Fire towers'."""
    towers = M.get("fire_towers", [])
    # A tower's WATCH RADIUS: the visual neighborhood of rooftops one hinomi-yagura usefully covers.
    # Both clauses below share it - a tower more than one radius from any dwelling watches nothing,
    # and two towers within one radius of EACH OTHER watch the same rooftops twice.
    WATCH = 230
    COMMON = {"laborer", "laborer_large", "servant", "merchant", "merchant_house", "merchant_large", "shop"}
    SAM = {"samurai", "samurai_large"}
    dwell = [(b["x"], b["y"], b.get("kind")) for b in M.get("buildings", []) if b.get("kind") in COMMON | SAM]
    if towers and dwell:
        misplaced = []
        for t in towers:
            near = sorted(dwell, key=lambda d: math.hypot(d[0] - t["x"], d[1] - t["y"]))[:3]
            nearest = math.hypot(near[0][0] - t["x"], near[0][1] - t["y"])
            sam = sum(1 for d in near if d[2] in SAM)
            if nearest > WATCH or sam * 2 > len(near):  # isolated, or sitting in the samurai quarter
                misplaced.append((round(t["x"]), round(t["y"])))
        check("fire_tower_in_commoner_quarter", not misplaced, f"fire tower(s) {misplaced} sit isolated or in the samurai quarter - a hinomi-yagura watches the dense COMMONER rooftops")
    # a fire tower stands in the dense built-up core, never ON cultivated ground: a hinomi-yagura on a
    # paddy (or the in-wall chrysanthemum field / a fallow patch) is nonsense, and an in-wall agricultural
    # district puts a real field right where a tower might land. (There is no blanket no_structure_on_field
    # - farmhouses legitimately ring the fields - so the towers carry their own field-clearance check.)
    fields = [f["outline"] for f in M.get("fields", [])] + [f["outline"] for f in M.get("fallow_patches", [])] + [f["outline"] for f in M.get("flower_fields", [])]
    if towers and fields:
        on_field = []
        for t in towers:
            rc = rect_corners(_struct_rect(t))
            for ol in fields:
                n = len(ol)
                if any(point_in_poly(cx, cy, ol) for cx, cy in rc) or any(segments_cross(rc[i], rc[(i + 1) % 4], ol[e], ol[(e + 1) % n]) for i in range(4) for e in range(n)):
                    on_field.append((round(t["x"]), round(t["y"])))
                    break
        check("fire_tower_clear_of_fields", not on_field, f"fire tower(s) {on_field} sit on a field - a hinomi-yagura stands in the dense urban core, never on a paddy or planting")
    # MULTIPLE TOWERS DISPERSE. A settlement dense/populous enough to warrant a second tower gets it
    # to watch a DIFFERENT quarter's rooftops: historically the fire-watch was parcelled out per
    # neighborhood (in Edo each machi block-group kept its own hinomi-yagura, and the shogunate's
    # official watch stations were likewise distributed one to a district), so towers were spread
    # across the city, never bunched. Two towers inside one watch radius of each other duplicate
    # coverage while some other dense quarter goes unwatched - the second tower accomplishes nothing.
    # WHY: settlements.md "Fire towers".
    if len(towers) >= 2:
        bunched = [((round(a["x"]), round(a["y"])), (round(b["x"]), round(b["y"]))) for i, a in enumerate(towers) for b in towers[i + 1 :] if math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < WATCH]
        check(
            "fire_towers_dispersed",
            not bunched,
            f"fire tower pair(s) {bunched} stand within one watch radius ({WATCH} px) of each other - a second "
            f"hinomi-yagura exists to watch a DIFFERENT quarter's rooftops; spread them across the settlement",
        )
    # EACH TOWER STANDS AMID THE DISTRICT IT WATCHES. Dispersal alone is not enough: two towers a
    # comfortable distance apart can still both sit in the SAME QUADRANT, leaving the dense commoner
    # quarter across the city unwatched (Tango's original pair both stood NW of center while the NE
    # laborer warren - the city's biggest rooftop mass - had no watch). Historically the watch was
    # parcelled by district, every commoner roof belonging to SOME tower's watch, and the tower stood
    # amid its blocks (it watched outward over rooftops on all sides, not a district it sat at the far
    # edge of). So: assign every commoner dwelling to its NEAREST tower - that partition IS the de
    # facto watch districting the drawn towers imply - and each tower must stand near its district's
    # center of mass: offset <= max(0.9 x the district's RMS radius, one WATCH radius). A tower parked
    # in the wrong quadrant inherits the whole far side of the city as its "district" and lands far
    # off that centroid, which is exactly the failure. Inside the walls only, when walled - the
    # extramural gate-market rows are not part of the enclosed core the towers exist for.
    # WHY: settlements.md "Fire towers".
    wallp = M.get("wall")
    core = [d for d in dwell if d[2] not in SAM and (not wallp or point_in_poly(d[0], d[1], wallp))]
    if len(towers) >= 2 and core:
        offside = []
        for ti, t in enumerate(towers):
            g = [d for d in core if ti == min(range(len(towers)), key=lambda j: math.hypot(d[0] - towers[j]["x"], d[1] - towers[j]["y"]))]
            if not g:
                continue
            gx, gy = sum(d[0] for d in g) / len(g), sum(d[1] for d in g) / len(g)
            rms = math.sqrt(sum((d[0] - gx) ** 2 + (d[1] - gy) ** 2 for d in g) / len(g))
            off = math.hypot(t["x"] - gx, t["y"] - gy)
            if off > max(0.9 * rms, WATCH):
                offside.append((round(t["x"]), round(t["y"]), round(off), round(rms)))
        check(
            "fire_tower_amid_its_district",
            not offside,
            f"fire tower(s) {offside} (x, y, offset, district rms) stand far off the center of the rooftop "
            f"district they are nearest to - the towers are bunched in one part of the city while a dense "
            f"commoner quarter goes unwatched; put one tower AMID each major commoner quarter",
        )
    # A TOWER KEEPS A SMALL STANDOFF FROM ITS NEIGHBORS (>= 5 px of daylight). The blanket
    # no_structure_overlaps SAT test only catches true footprint intersection, so a tower butted
    # flush against a house passes it while READING as a collision: the drawn glyph's roof cap
    # overhangs the recorded frame by ~2px a side, and an open braced-timber tower needs its
    # footing and ladder clear of the neighboring eaves anyway (it stands on a seam, not in a
    # party-wall row). GM rule: at least 5 px between a fire tower and any neighboring building.
    STANDOFF = 5
    if towers:
        neigh = [s for k in _OVERLAP_STRUCTS if k != "fire_towers" for s in M.get(k, [])]
        crowded = []
        for t in towers:
            tc = rect_corners(_struct_rect(t))
            for s in neigh:
                sc = rect_corners(_struct_rect(s))
                if math.hypot(t["x"] - s["x"], t["y"] - s["y"]) > 160:  # cheap prefilter
                    continue
                gap = min(min(seg_dist(px, py, sc[i], sc[(i + 1) % 4]) for px, py in tc for i in range(4)), min(seg_dist(px, py, tc[i], tc[(i + 1) % 4]) for px, py in sc for i in range(4)))
                if sat_overlap(tc, sc) or gap < STANDOFF:
                    crowded.append((round(t["x"]), round(t["y"]), round(gap, 1)))
                    break
        check(
            "fire_tower_standoff",
            not crowded,
            f"fire tower(s) {crowded} (x, y, gap px) stand within {STANDOFF} px of a neighboring building - "
            f"the open braced frame (and its overhanging roof cap) needs a little daylight around its footing; "
            f"nudge the tower onto clearer ground",
        )
    # A TOWER NEVER STANDS ON A WELLHEAD. Wells are overlap-EXEMPT (a wellhead's nominal footprint
    # may kiss a dense-city building - see _OVERLAP_EXEMPT), so neither the blanket
    # no_structure_overlaps pass nor fire_tower_standoff above (which walks _OVERLAP_STRUCTS only)
    # guards a tower dropped onto a well. But that exemption is about houses ringing a tenement
    # court closely - a fire tower must not ride it: its braced footing would stand in the well
    # court blocking the shared draw-point, and the two glyphs read as a plain collision. Same
    # 5 px daylight rule as fire_tower_standoff; circle (the well's clearance disc, radius r,
    # as in wells_clear_of_shrine_and_torii) vs the tower's rect.
    wells = M.get("wells", [])
    if towers and wells:
        on_well = []
        for t in towers:
            hw, hh = t["w"] / 2, t["h"] / 2
            for wl in wells:
                ddx = wl["x"] - t["x"] - max(-hw, min(hw, wl["x"] - t["x"]))
                ddy = wl["y"] - t["y"] - max(-hh, min(hh, wl["y"] - t["y"]))
                if math.hypot(ddx, ddy) < wl["r"] + STANDOFF:
                    on_well.append((round(t["x"]), round(t["y"])))
                    break
        check(
            "fire_tower_clear_of_wells",
            not on_well,
            f"fire tower(s) {on_well} stand on (or within {STANDOFF} px of) a wellhead - a hinomi-yagura's footing must not block a quarter's shared draw-point; nudge the tower off the well court",
        )
    # ... and clear of GRAVEYARDS (GM, 2026-07): a watch-tower's braced footing planted among
    # the graves reads as a plain collision - the dead get the same daylight as the living
    cems = M.get("cemeteries", [])
    if towers and cems:
        on_grave = []
        for t in towers:
            tc = rect_corners({"x": t["x"], "y": t["y"], "w": t["w"] + 2 * STANDOFF, "h": t["h"] + 2 * STANDOFF, "rot": 0})
            for cm in cems:
                if sat_overlap(tc, rect_corners({"x": cm["x"], "y": cm["y"], "w": cm["w"], "h": cm["h"], "rot": 0})):
                    on_grave.append((round(t["x"]), round(t["y"])))
                    break
        check("fire_tower_clear_of_graveyards", not on_grave, f"fire tower(s) {on_grave} stand on (or within {STANDOFF} px of) a graveyard - move the watch-tower off the burial ground")


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


def _fronts_route(bx: float, by: float, routes: Sequence[Poly], others: Sequence[dict[str, Any]], road_d: float = 115) -> bool:
    """True if (bx, by) is within road_d of a trade route (the Imperial road or a town street) AND no
    `others` building lies between it and the nearest route point - i.e. it FRONTS the road, not hides
    behind the shop rows. Used to keep the caravan inn on the road, not buried in the back blocks."""
    npt, bd = None, 1e18
    for r in routes:
        for k in range(len(r) - 1):
            cx, cy = seg_closest(bx, by, r[k], r[k + 1])
            d = math.hypot(cx - bx, cy - by)
            if d < bd:
                bd, npt = d, (cx, cy)
    if npt is None or bd > road_d:
        return False
    for o in others:
        oc = rect_corners(_struct_rect(o))
        if any(segments_cross((bx, by), npt, oc[e], oc[(e + 1) % 4]) for e in range(4)):
            return False
    return True


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
