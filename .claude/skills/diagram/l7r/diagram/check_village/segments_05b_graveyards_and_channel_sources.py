"""Gate segments (graveyards and channel sources; keys 0286_025-0305) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import Pt, point_in_poly, seg_dist
from .common_02_overlap_policy import edge_dist, in_ellipse
from .common_03_capacity import _UNBOUND, _kept

# PRECINCT: a graveyard is a temple parish ground - it sits by a temple. (At CITY scale only an
# INSIDE-wall graveyard must; an OUTSIDE-wall one is the extramural common burial ground, exempt.)


# SPLIT: any WALLED settlement (town or city) keeps a graveyard both inside AND outside the
# walls - and the EXTERIOR common ground is noticeably larger than the cramped intramural one
# (there is room beyond the walls; inside, the temple grounds are hemmed in by the city).


def _seg_0286_026__walled_graveyards_inside_and_outside(
    *,
    _inside: Any = _UNBOUND,
    bi: Any = _UNBOUND,
    bo: Any = _UNBOUND,
    c: Any = _UNBOUND,
    cems: Any = _UNBOUND,
    check: Any = _UNBOUND,
    ins: Any = _UNBOUND,
    out: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    wall: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0286.026 (walled_exterior_cemetery_larger, walled_graveyards_inside_and_outside) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital') and wall and cems:
        ins = [c for c in cems if _inside(c["x"], c["y"])]
        out = [c for c in cems if not _inside(c["x"], c["y"])]
        check(
            "walled_graveyards_inside_and_outside",
            bool(ins) and bool(out),
            f"a walled settlement keeps a graveyard both inside AND outside the walls (inside {len(ins)}, outside {len(out)}) - keep at least one of each",
        )
        if ins and out:
            bi = max(c["w"] * c["h"] for c in ins)
            bo = max(c["w"] * c["h"] for c in out)
            check(
                "walled_exterior_cemetery_larger",
                bo >= 1.3 * bi,
                f"the exterior common burial ground should be noticeably larger than the cramped intramural "
                f"ground (outside {bo:.0f}px2 vs inside {bi:.0f}px2; want >= 1.3x) - there is room beyond the walls",
            )
    return _kept(locals(), ('bi', 'bo', 'c', 'ins', 'out'))


# BELL-AND-DRUM TOWER (GM 2026-07-24; settlements.md "The bell-and-drum tower"). The
# morning-bell/evening-drum institution followed the WALL, not the population: the tower
# signaled dawn gate-opening, the dusk gate-closing that began the street curfew, and the
# five night watches - so every WALLED seat (city or walled town) keeps EXACTLY ONE
# combined tower at the main street crossing (the county-seat kit; a paired gulou/zhonglou
# on an axis is capital grammar - Pingyao, a wealthy county seat, has exactly one). An
# UNWALLED town has no gates to close: its time signal is the monastery's bell (the Edo
# toki-no-kane pattern, usually a contracted temple bell), implied within the precinct -
# no tower, no glyph. Fire watch was a SEPARATE institution in both reference cultures
# (Song Kaifeng ran dedicated fire-lookout towers; Edo split the licensed time bell from
# the hinomi-yagura), so the fire towers do not satisfy this check and the drum tower is
# not fire watch. "At the main crossing" = within ~80px of two NON-PARALLEL road/street
# segments (a corner of the central crossroads).


def _seg_0286_027__walled_settlement_has_drum_tower(
    *,
    M: Any = _UNBOUND,
    _dt_at_crossing: Any = _UNBOUND,
    _inside: Any = _UNBOUND,
    a: Any = _UNBOUND,
    angs: Any = _UNBOUND,
    b: Any = _UNBOUND,
    check: Any = _UNBOUND,
    dts: Any = _UNBOUND,
    i: Any = _UNBOUND,
    ok_dt: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    st: Any = _UNBOUND,
    t: Any = _UNBOUND,
    wall: Any = _UNBOUND,
    ways: Any = _UNBOUND,
    wy: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0286.027 (walled_settlement_has_drum_tower) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital') and wall and scale in ("town", "city"):
        dts = M.get("drum_towers", [])
        ways = ([M["road"]] if M.get("road") else []) + [st.get("pts", []) for st in M.get("town_streets", [])]

        def _dt_at_crossing(t: dict[str, Any]) -> bool:
            angs = []
            for wy in ways:
                for i in range(len(wy) - 1):
                    if seg_dist(t["x"], t["y"], wy[i], wy[i + 1]) < 80:
                        angs.append(math.atan2(wy[i + 1][1] - wy[i][1], wy[i + 1][0] - wy[i][0]) % math.pi)
            return any(min(abs(a - b), math.pi - abs(a - b)) > 0.5 for a in angs for b in angs)

        ok_dt = len(dts) == 1 and _inside(dts[0]["x"], dts[0]["y"]) and _dt_at_crossing(dts[0])
        check(
            "walled_settlement_has_drum_tower",
            ok_dt,
            f"{len(dts)} bell-and-drum tower(s) at the main crossing - every walled seat keeps EXACTLY ONE "
            f"combined bell-and-drum tower (s.drum_tower) inside the walls at the main street crossing "
            f"(within ~80px of two non-parallel road/street segments); it signals the gate curfew and the "
            f"night watches, which the fire towers do not cover; an unwalled town is exempt (its time "
            f"signal is the monastery's bell)",
        )
    return _kept(locals(), ('_dt_at_crossing', 'angs', 'dts', 'ok_dt', 'st', 'ways'))


def _seg_0286_029__city_temples_have_graveyards(
    *,
    M: Any = _UNBOUND,
    URBAN: Any = _UNBOUND,
    _inside: Any = _UNBOUND,
    anchor: Any = _UNBOUND,
    b: Any = _UNBOUND,
    c: Any = _UNBOUND,
    cems: Any = _UNBOUND,
    check: Any = _UNBOUND,
    crem: Any = _UNBOUND,
    crem_out: Any = _UNBOUND,
    gov: Any = _UNBOUND,
    m2: Any = _UNBOUND,
    maus: Any = _UNBOUND,
    maus_ok: Any = _UNBOUND,
    needy: Any = _UNBOUND,
    o: Any = _UNBOUND,
    oss: Any = _UNBOUND,
    oss_ok: Any = _UNBOUND,
    r: Any = _UNBOUND,
    sam: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    temples: Any = _UNBOUND,
    unserved: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0286.029 (city_has_cremation_ground, city_has_mausoleum, city_has_ossuary, city_temples_have_graveyards) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital') and URBAN:
        # every temple that CAN host a graveyard has one in its precinct (graveyard=False opts out)
        needy = [r for r in temples if r.get("graveyard", True)]
        unserved = [r.get("label", (round(r["x"]), round(r["y"]))) for r in needy if not any(math.hypot(c["x"] - r["x"], c["y"] - r["y"]) < 230 for c in cems)]
        check(
            "city_temples_have_graveyards",
            not unserved,
            f"temple(s) with no graveyard in their precinct: {unserved[:3]} - Shinsei and Fortune worship are merged, so every temple keeps a burial ground unless it opts out (graveyard=False)",
        )
        # CLAN MAUSOLEUM: a walled crypt precinct inside the walls, by the samurai/government quarter
        gov = M.get("governor_mansion")
        sam = [b for b in M.get("buildings", []) if b.get("kind") in ("samurai", "samurai_large")]
        if gov:
            anchor = (gov["x"], gov["y"])
        elif sam:
            anchor = (sum(b["x"] for b in sam) / len(sam), sum(b["y"] for b in sam) / len(sam))
        else:
            anchor = None
        maus_ok = bool(maus) and any(_inside(m2["x"], m2["y"]) for m2 in maus) and (anchor is None or any(math.hypot(m2["x"] - anchor[0], m2["y"] - anchor[1]) < 640 for m2 in maus))
        check(
            "city_has_mausoleum",
            maus_ok,
            "a provincial city needs the ruling clan's ancestral MAUSOLEUM (s.mausoleum) inside the walls, by the samurai/government quarter - a walled crypt precinct for the elite dead",
        )
        # CREMATION GROUND: smoke, fire, and pollution push the crematory OUTSIDE the walls
        crem_out = [c for c in crem if not _inside(c["x"], c["y"])]
        check(
            "city_has_cremation_ground",
            bool(crem_out),
            "a city cremates its dead at a CREMATION GROUND (s.cremation_ground) OUTSIDE the walls - monk-run with burakumin assistants; smoke and fire keep it beyond a gate",
        )
        # PAUPER OSSUARY: outside the walls, beside the cremation ground
        oss_ok = any(not _inside(o["x"], o["y"]) and any(math.hypot(o["x"] - c["x"], o["y"] - c["y"]) < 320 for c in crem) for o in oss)
        check(
            "city_has_ossuary",
            oss_ok,
            "a city needs a pauper OSSUARY mound (s.ossuary) outside the walls by the cremation ground - the communal bones of the poor and the unconnected dead (muenbotoke)",
        )
    return _kept(locals(), ('anchor', 'b', 'c', 'crem_out', 'gov', 'm2', 'maus_ok', 'needy', 'o', 'oss_ok', 'r', 'sam', 'unserved'))


# GEOMETRY SANITY AT EVERY SCALE (GM audit 2026-07: this only ran for cities): a wall vertex
# millions of px off the canvas is malformed input at any scale - towns have walls too.


# LABEL TEXT renders ON TOP of everything: no part of a label may be covered. Labels live in the
# topmost layer (s.add_label), above the TOP-layer structures (gate furniture, kido, torii); the
# check guards it - a label overlapped by any structure drawn OVER it (higher draw-z) is covered.


def _seg_0288__occluders() -> dict[str, Any]:
    """Gate segment 288 (occluders) - body verbatim from the legacy gate() (feature 022)."""
    occluders = []  # type: ignore[var-annotated]
    return _kept(locals(), ('occluders',))


def _seg_0289__gs_1(*, M: Any = _UNBOUND, gs: Any = _UNBOUND, occluders: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 289 (gs, occluders) - body verbatim from the legacy gate() (feature 022)."""
    for gs in M.get("gate_structs", []):
        if gs.get("z") is not None:
            occluders.append((gs["x"] - gs["w"] / 2, gs["y"] - gs["h"] / 2, gs["x"] + gs["w"] / 2, gs["y"] + gs["h"] / 2, gs["z"]))
    return _kept(locals(), ('gs', 'occluders'))


def _seg_0290__kd(*, M: Any = _UNBOUND, kd: Any = _UNBOUND, occluders: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 290 (kd, occluders) - body verbatim from the legacy gate() (feature 022)."""
    for kd in M.get("kido", []):
        if kd.get("z") is not None and kd.get("bbox"):
            occluders.append((kd["bbox"][0], kd["bbox"][1], kd["bbox"][2], kd["bbox"][3], kd["z"]))
    return _kept(locals(), ('kd', 'occluders'))


def _seg_0291__occluders_1(*, M: Any = _UNBOUND, occluders: Any = _UNBOUND, t: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 291 (occluders, t) - body verbatim from the legacy gate() (feature 022)."""
    for t in M.get("torii", []):
        if len(t) >= 3:
            occluders.append((t[0] - 22, t[1] - 28, t[0] + 22, t[1] + 12, t[2]))  # the arch's drawn extent
    return _kept(locals(), ('occluders', 't'))


def _seg_0295__hill(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 295 (hill) - body verbatim from the legacy gate() (feature 022)."""
    hill = M.get("hill")
    return _kept(locals(), ('hill',))


# every watercourse - irrigation channel OR natural stream - must connect what it
# claims to: each end anchored to its pond / off-map edge / field / forest


def _seg_0297__pond(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 297 (pond) - body verbatim from the legacy gate() (feature 022)."""
    pond = M.get("pond")
    return _kept(locals(), ('pond',))


def _seg_0298__forest(*, M: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 298 (forest) - body verbatim from the legacy gate() (feature 022)."""
    forest = M.get("forest")
    return _kept(locals(), ('forest',))


def _seg_0299__anchored(
    *,
    EX0: Any = _UNBOUND,
    EX1: Any = _UNBOUND,
    EY0: Any = _UNBOUND,
    EY1: Any = _UNBOUND,
    M: Any = _UNBOUND,
    anchor: Any = _UNBOUND,
    dp: Any = _UNBOUND,
    fd: Any = _UNBOUND,
    field_by: Any = _UNBOUND,
    fo: Any = _UNBOUND,
    forest: Any = _UNBOUND,
    i: Any = _UNBOUND,
    k: Any = _UNBOUND,
    pond: Any = _UNBOUND,
    pt: Any = _UNBOUND,
    sp: Any = _UNBOUND,
    st: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 299 (anchored) - body verbatim from the legacy gate() (feature 022)."""

    def anchored(pt: Pt, anchor: dict[str, Any]) -> bool:
        k = anchor["kind"]
        if k == "pond":
            return bool(pond) and in_ellipse(pt[0], pt[1], pond, 1.02)
        if k == "offmap":
            return bool(min(pt[0] - EX0, EX1 - pt[0], pt[1] - EY0, EY1 - pt[1]) <= 32)
        if k == "forest":
            return bool(forest) and point_in_poly(pt[0], pt[1], forest)
        if k == "stream":
            return any(seg_dist(pt[0], pt[1], sp[i], sp[i + 1]) < 30 for st in M.get("streams", []) for sp in [st["poly"]] for i in range(len(sp) - 1))
        if k == "field":
            fo: Any = field_by.get(anchor["name"])
            return bool(fo) and point_in_poly(pt[0], pt[1], fo["outline"]) and edge_dist(pt[0], pt[1], fo["outline"]) >= 10
        if k == "moat":
            mo: Any = M.get("moat")
            return bool(mo) and any(seg_dist(pt[0], pt[1], mo[i], mo[i + 1]) < 34 for i in range(len(mo) - 1))
        if k == "river":  # a fan tapped straight off a river (Nagahara's Hayakawa far bank, 2026-07-23)
            rv2: Any = M.get("river")
            return bool(rv2) and any(seg_dist(pt[0], pt[1], rv2["pts"][i], rv2["pts"][i + 1]) < rv2.get("w", 40) / 2 + 14 for i in range(len(rv2["pts"]) - 1))
        if k == "drain":  # a brook empties FROM the field drain (akusui outfall)
            return any(seg_dist(pt[0], pt[1], dp[i], dp[i + 1]) < 30 for fd in M.get("field_ditches", []) if fd.get("role") == "drain" for dp in [fd["poly"]] for i in range(len(dp) - 1))
        if k == "ditch":
            # a weir/intake HANDS OFF to the irrigation works (a head-race, a canal): the mirror of
            # the stream-diverted-into-a-channel clause in stream_runs_off_edge (GM audit 2026-07)
            return any(seg_dist(pt[0], pt[1], dp[i], dp[i + 1]) < 22 for d2 in (M.get("field_ditches", []) + M.get("channels", [])) for dp in [d2["poly"]] for i in range(len(dp) - 1))
        return False

    return _kept(locals(), ('anchored',))


# A SUPPLY CONDUIT FEEDING A PADDY MUST BE VISIBLY SOURCED (GM 2026-07-24, Tango fs3): an
# irrigation canal can never just START in the middle of nowhere - it must tap on-map water
# or come in from the view edge (presumed to continue off-map). channel_source_anchored
# already checks the RECORDED topology, but a `drawn: False` conduit (an implied underground
# channel whose visual is carried by the comb's own drawn head-race) can lie visually: Tango's
# fs3 recorded its tap on a stream vertex, drew nothing between stream and comb, and the main
# canal's head hung in open ground 38px from the bank. So for every UNDRAWN supply conduit,
# the point where visible water actually starts - the comb origin, i.e. the fed field's
# main-ditch head nearest the recorded source - must itself (a) sit at/past the view edge,
# (b) sit on source water (stream/moat/pond/river/cargo-canal bed, or another comb's ditch -
# tail-water cascade, the standard way a city's drainage waters the fields below it), or
# (c) be joined to such a point by a DRAWN tap stroke. Tap strokes are read from
# M['drawn_channels'] (post-clip geometry - the check reads what was actually drawn, per the
# same-manifest rule in the dev-loop doc); a drawn stroke whose far end lies in or along the
# fed field's own outline is the comb's own canal heading downstream, not a tap.
