"""The access tree as lanes: judged whole at seating, drawn by construction (feature 287 wave 6; ways W01, W03).

WHY THIS REPLACES THE CORRIDOR SEARCH AT THE DRAW. The seating reserved, for every house it admitted, a corridor from its
door to a tree rooted at the track out (`settlement/rolling/access.py`; since feature 320 the tree is laid once the last house
stands, rooted at the way out's gate), and asked of each leg only the GROUND half of the
lane law. The web then drew a corridor where its lanes did not reach a house, stopping at the first contact with them - and
that run's joints with the ordinary lanes (a needle, a kink squared at a channel, a fold) were known only then, so a house
whose every run was refused was recorded (`meta.access_refused`) and shipped unreached (research R9: cohort seeds 8 and 39
under feature 284's probes). No later repair could be proven to succeed.

SO THE ORDER CHANGES, and the proof with it:

1. THE TREE IS JUDGED WHOLE AT SEATING (`tree_admits`). Its lanes - each house's corridor from where it leaves its own
   yard to its target on the tree, hung from the track out (`_root`) - are the only lanes there are besides it, so every joint among them is known. A seat whose corridor would make the tree
   unlawful (the whole `settle.Lawful` - ground, kink, hook, needle, fold, hairpin, doubled tail, dangling end, an end
   behind a house - and no sliver of grass among its lanes, no house discharging more than `law.DOORSTEP_MAX` ends, no way
   out over a brook and back) is refused there and the next seat tried, as the seating already refused on ground.
2. THE TREE IS DRAWN BEFORE THE REST OF THE LAW IS ASKED, AND THE ORDINARY LANES DEFER TO IT (`settle_tree`, then
   `settle_defer`): every household's way gets its chain of tree lanes - exactly those the gap pass judged, sub-runs of
   none - and an ordinary lane that breaks a rule
   against a tree lane is cut, never the tree.
3. NO TREE LANE IS DRAWN THAT THE MAP DOES NOT NEED (homes H40): the pruning step that took one away went in feature 417 T31,
   measured needless - the tree draws only the chains the gap pass judged.

So every house with a laid way is reached by construction: there is no fallback that ships one unreached; and on a brook
map a field no way reaches refuses the map (`last_resort.refuse_unreached`).

Research: access tree plumbing - NONE
"""

from __future__ import annotations

import copy
import math
from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_closest, seg_dist

from ..consts import WEB_CLEARANCE, Poly, Pt
from . import law
from .bund import BRANCH_WIDTH
from .checks import unreached_houses
from .corridors import ACCESS_ROLE, ACCESS_WIDTH, ON_TREE_PX, is_tree
from .forced import lazy_ground
from .geom import lane_owner

CARRY_FT = 20.0
"""How far off its host a tree run's end may stand and be set on its foot there rather than carried on by a leg of its own
(`lanes_of`, `strip_run`): past `law`'s hook leg (`_HOOK_FT`), so no leg short enough to hook is ever added.

Research: end set on its host - research/questions/0081-village-lanes.drawing.html: within 20 ft, past the hook leg"""


def _pt(q: Sequence[Any]) -> Pt:
    return (float(q[0]), float(q[1]))


def _rounded(run: Poly) -> Poly:
    """`run` at the record's 0.1 px, as it will be drawn (`Settlement.lane`) - so what is judged is what is drawn: two
    corridors meeting one host point rounded apart closed a face of no area (cohort seeds 21 and 25, `law.needle_loops`)."""
    return _dedup([(round(p[0], 1), round(p[1], 1)) for p in run])


def _dedup(run: Poly) -> Poly:
    return [p for j, p in enumerate(run) if j == 0 or math.dist(p, run[j - 1]) > 1e-6]


def tree_records(M: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The tree's corridors as runs, in the order the seating reserved them (`access_corridors`): a house's legs joined from
    its door end (the record naming the house, `of`, and the legs after it), the field's legs joined from the bund. Each is
    `{"role", "of", "pts"}`; the exit strip is not among them (`strip_run`)."""
    out: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None
    for c in M.get("access_corridors") or []:
        pts = [_pt(q) for q in c.get("pts") or []]
        if len(pts) < 2:
            continue
        if c.get("of"):
            cur = {"role": ACCESS_ROLE, "of": _pt(c["of"]), "pts": [pts[0]]}
            out.append(cur)
        elif cur is None or cur["role"] != ACCESS_ROLE:
            continue
        cur["pts"].append(pts[1])
    for r in out:
        r["pts"] = _dedup(r["pts"])
    return out


def _on(q: Pt, run: Poly) -> bool:
    return any(seg_dist(q[0], q[1], a, b) <= ON_TREE_PX for a, b in zip(run, run[1:], strict=False))


def _root(M: Mapping[str, Any]) -> Poly | None:
    """The tree's root (feature 320): the track out as drawn; before it is drawn, the track as chosen once the last house
    stood (`way_out_track`, `household_ways.chose_the_track`). None where neither stands."""
    con = next((law.lane_pts(ln) for ln in M.get("lanes") or [] if ln.get("connector") and len(ln.get("pts") or []) >= 2), None)
    if con is None:
        con = M.get("way_out_track")
    return [_pt(q) for q in con] if con else None


def hosts(recs: Sequence[Mapping[str, Any]], root: Poly | None) -> list[int | None]:
    """Each run's host: -1 where its last point stands on the root, the track out (`_root`), else the index of the EARLIEST run it stands on
    (a corridor is admitted onto the tree as it then stood, so its host was reserved before it), None where neither."""
    out: list[int | None] = []
    for i, r in enumerate(recs):
        q = r["pts"][-1]
        if root is not None and _on(q, root):
            out.append(-1)
            continue
        out.append(next((j for j in range(i) if _on(q, recs[j]["pts"])), None))
    return out


def chain_of(recs: Sequence[Mapping[str, Any]], host: Sequence[int | None], i: int) -> list[int]:
    """Run `i` and every run it hangs from, in to the one on the strip."""
    out = [i]
    while (h := host[out[-1]]) is not None and h >= 0 and h not in out:
        out.append(h)
    return out


def lanes_of(M: Mapping[str, Any], recs: Sequence[Mapping[str, Any]], host: Sequence[int | None], chosen: Sequence[int], drawn: bool = True, square: Any = None) -> list[dict[str, Any]]:
    """The tree lanes for the runs `chosen` (their chains' closure taken by the caller), squared at their water crossings as
    the web draws every lane (`settle.square_run`, or `square` - the seating's `Lawful.squared`, the same answer asked only
    where water comes near, and remembered per run). The seating's tree lays its runs one at a time on a kept base
    (`tree_base`, feature 387), each through `lane_record`.

    Research:
        tree lane tread by role - research/questions/0081-village-lanes.drawing.html: house access 3 ft
        tree lanes assembled - NONE: the runs squared and set on their hosts as the web draws them, each then asked the needle rule (`off_the_needle`)
        which way is cut - research/questions/0081-village-lanes.drawing.html: the lane whose end runs back along another way is cut where it comes alongside - each new lane against those drawn and the connector, then each drawn lane against the new one; the connector is never cut"""
    raw_sq = square if square is not None else (lambda run: square_run_of(M, run))
    waters = square_waters_of(M)

    def sq(run: Poly) -> Poly:
        return raw_sq(rejoined(run, waters))

    out: list[dict[str, Any]] = []
    root = _root(M)
    drawn_of: dict[int, Poly] = {-1: root} if root is not None else {}
    for i in chosen:
        drawn_of[i] = _rounded(sq(recs[i]["pts"]))
    for i in chosen:
        h = host[i]
        rec = lane_record(recs[i], drawn_of[i], drawn_of.get(h) if h is not None else None)
        rec["pts"] = off_the_needle(rec["pts"], [ln["pts"] for ln in out] + ([root] if root is not None else []))
        for ln in out:  # ...and an earlier lane whose own end runs along this one is cut instead (0081: the lane whose END runs back)
            ln["pts"] = off_the_needle(ln["pts"], [rec["pts"]])
        out.append(rec)
    return out


def off_the_needle(pts: Sequence[Any], drawn: Sequence[Sequence[Sequence[float]]]) -> list[Any]:
    """`pts`, a tree lane, ended on a way already drawn rather than run on beside it - the NEEDLE RULE asked where the lane is
    laid (feature 417 T45, `law.is_needle`): where the lane and one drawn before it bound a needle of grass, the lane is cut where its
    tail first comes within half the needle's width of that way (walked back from its end, every 2 ft), and carried onto that
    way's tread there - a tee. Fresh seed 723775 drew
    two households' ways onto the connector's start, the one's last leg 7 ft beside the other's, a 3 ft sliver between them.
    Left as it was where no needle is closed, or where the tee would still close one.

    Research:
        the doubled way drawn as one - research/questions/0081-village-lanes.drawing.html: two ways side by side are drawn as one
        its reach - GUESS: searched, the record silent (feature 417 T45, 2026-10-26); 0081 cuts a lane where it comes alongside and gives no distance - half of `law.NEEDLE_LOOP_FT` (10 ft); 2.0 (the walk's step)
        a lane beside the other its whole length - GUESS: searched, the record silent (feature 417 T45, 2026-10-26); left as drawn for the law to refuse, no stretch of it standing off to cut back to
        a needle left where the tee would close one - GUESS: searched, the record silent (feature 417 T45, 2026-10-26); the lane is left as drawn for the law to refuse rather than cut into another needle
    """
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union

    own = [[float(q[0]), float(q[1])] for q in pts]
    if len(own) < 2:
        return list(pts)
    moved = False
    for other in drawn:
        if len(other) < 2:
            continue
        line = LineString([(float(q[0]), float(q[1])) for q in other])

        def closes(p: Sequence[Sequence[float]], line: Any = line) -> bool:
            return any(law.is_needle(f) for f in polygonize(unary_union([LineString(p), line])))

        if not closes(own):
            continue
        mine = LineString(own)
        reach = law.NEEDLE_LOOP_FT / 2.0
        at = mine.length
        while at > 0.0 and line.distance(mine.interpolate(at)) < reach:
            at -= 2.0
        if at <= 0.0 or at >= mine.length:
            continue
        cut = mine.interpolate(at)
        foot = line.interpolate(line.project(cut))
        kept = [q for q in own if mine.project(_point(q)) < at]
        tee = [*kept, [round(cut.x, 1), round(cut.y, 1)], [round(foot.x, 1), round(foot.y, 1)]]
        if len(tee) >= 2 and not closes(tee):
            own = tee
            moved = True
    return own if moved else list(pts)


def _point(q: Sequence[float]) -> Any:
    from shapely.geometry import Point

    return Point(float(q[0]), float(q[1]))


def lane_record(r: Mapping[str, Any], pts: Poly, on: Poly | None) -> dict[str, Any]:
    """Run `r`'s tree lane, drawn at `pts` (laid and rounded), its end carried onto `on` - its host's drawn run - as
    `lanes_of` carries it; one lane at a time, so the base tree's lanes are built once and a candidate's alone after them
    (feature 387, `tree_base`). The carry onto the host within `CARRY_FT` is that constant's claim.

    Research:
        tree lane tread by role - research/questions/0081-village-lanes.drawing.html: house access 3 ft, a branch 5 ft"""
    # ...ITS END CARRIED ONTO ITS HOST AS DRAWN: the host is squared at its water crossings, and a run that met it on the
    # stretch the squaring moved (cohort seed 8: the exit strip over a channel) is carried on to the foot on it
    # ...UNLESS IT STANDS ON THE CONNECTOR'S TREAD ALREADY, where the strip is cut back to the connector's start: the web's
    # touch pass can carry the connector's start a few feet inward along the strip, past the point the seating hung
    # corridors from (Inashiro, feature 306: 2.6 ft), and a corridor's end carried back onto that start turned its 355 ft
    # leg a third of a degree - enough to make the corridor hung from it a 19.9 degree needle, a tree lane no settle may
    # cut. On the connector's tread the end meets the network as the seating judged it, so it is drawn where it was.
    if on is not None and len(on) >= 2 and not _on(pts[-1], on):
        q = pts[-1]
        k = min(range(len(on) - 1), key=lambda m: seg_dist(q[0], q[1], on[m], on[m + 1]))
        foot = seg_closest(q[0], q[1], on[k], on[k + 1])
        # a few feet off: the end is set on the foot (a leg that short would be a hook); farther, a leg on to it
        pts = _rounded([*pts[:-1], foot] if math.dist(q, foot) <= CARRY_FT and len(pts) >= 2 and math.dist(pts[-2], foot) > 1e-6 else [*pts, foot])
    lane: dict[str, Any] = {"pts": pts, "w": ACCESS_WIDTH if r["role"] == ACCESS_ROLE else BRANCH_WIDTH, "role": r["role"]}
    if r["of"] is not None:
        lane["of"] = [round(r["of"][0], 1), round(r["of"][1], 1)]
    return lane


class _Standing(dict):  # type: ignore[type-arg]
    """A trial manifest that still answers the registry of what stands (`registry.forbidden_segment` reads `.standing`)."""

    standing: Any = None


def _trial(M: Mapping[str, Any], **over: Any) -> _Standing:
    t = _Standing({**M, **over})
    t.standing = getattr(M, "standing", None)
    return t


def admits(base: Any, M: Mapping[str, Any], run: Poly, role: str = ACCESS_ROLE, house: Mapping[str, Any] | None = None, yard: Mapping[str, Any] | None = None) -> bool:
    """THE ONE PREDICATE OF THE TREE (feature 287 wave 6): would the access tree on `M`, with `run` added as a corridor of
    `role` (a house's, `house` its record-to-be and `yard` its threshing yard's), keep the lane law among
    its lanes? `base` (a `settle.Lawful` over `M`) is asked of the new lane against the rest, with the track out's root
    (`_root`) among them - in the whole tree, and in the tree the web draws for this corridor alone (its chain: `lanes_of`),
    since the web draws only the chains it owes - every rule of a pair is asked of the new lane against each lane it meets. And: no sliver of grass among the tree's lanes (`law.needle_loops`); no house
    discharging more than `law.DOORSTEP_MAX` free ends; the new house's way out along the tree crossing each brook at most once. The gap pass
    asks it of each household's way once the last house stands (`gap_ways`, feature 318), before it admits the way.

    Research:
        tree keeps the lane law - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way, laid once the last house stands, admitted with no hook, fold, hairpin or dangling end among the tree's lanes
        no sliver between the tree's lanes - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined (`as_joined`), two paths side by side are drawn as one (no needle, `needle_loops`), no stub run on past a crossing (no doubled tail)
        way out crosses each brook once - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        no doubled band - research/questions/0081-village-lanes.drawing.html: two paths running side by side are drawn as one, and two lanes met end to end are read as one (`walked_shadows`) - an access lane may not run beside another past a pitch
        free ends at a house - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25) - one main door served a minka's household (JAANUS, Edo period, pass A2); no page gives how many ends meet at one; at most DOORSTEP_MAX (2) free lane ends at a house
        track out's width as judged - research/questions/0081-village-lanes.drawing.html: the track out's stub judged at 6 ft, the track out as drawn"""
    from .tree_base import base_for

    def lay(run: Poly) -> Poly:
        return laid_run(base, M, run)

    # THE BASE TREE BUILT ONCE PER STATE (feature 387, plan D1): every earlier record's host, laid lane, free end and face is
    # the base's; this candidate costs its own host, its own lane, the ends it can change and the faces it meets
    tb = base_for(base, M, lay)
    rec: dict[str, Any] = {"role": role, "of": (float(house["x"]), float(house["y"])) if house is not None else None, "pts": _dedup([_pt(q) for q in run])}
    k = len(tb.recs)
    h = tb.host_of(rec["pts"][-1])
    if h is None or len(rec["pts"]) < 2:
        return False
    recs, host = [*tb.recs, rec], [*tb.host, h]
    stub = tb.stub
    houses = [*(M.get("houses") or []), *([house] if house is not None else [])]
    yards = [*(M.get("threshing_yards") or []), *([yard] if yard is not None else [])]
    view = _trial(M, houses=houses, threshing_yards=yards)
    law_ = copy.copy(base)
    law_.tree = False
    chain = chain_of(recs, host, k)
    new_lane = tb.lane_for(rec, h, lay)[1]
    whole = [*tb.lanes, new_lane]

    for lanes in (whole, [*(tb.lanes[i] for i in reversed(chain[1:])), new_lane]):
        new = lanes[-1]
        law_.M = _trial(view, lanes=[*lanes[:-1], *stub])
        law_.owner = lane_owner(new)  # ...a household's own way, beside its own garden (405 T18)
        if not law_(new["pts"], float(new["w"])):
            return False
        if lanes is whole:
            faces, joined_base, joined_faces = tb.judged()
            # ...NOR CLOSES A SLIVER WITH OTHER TREE LANES (the tree had none; two corridors on one host point did, cohort seeds
            # 21 and 25). A corridor may CROSS another - a crossroads is lawful, and was refused here at first for closing a loop
            # (seed 8: 44 of its seats, and the margin with them) - since only a face thinner than `law.NEEDLE_LOOP_FT` is a
            # fault, and a face in a part of the tree is never thinner than the faces the whole tree made of it. Judged on the
            # faces the new lane meets, the rest kept from the base (`tree_base.Faces`)
            if faces.needles_with([*lanes, *stub], [new["pts"]]):  # ...the track out among them, as the strip was (feature 320)
                return False
            # ...NOR CLOSES ONE ONCE THE WEB JOINS ITS ENDS (feature 317, plan D6): the settle carries a free end that stops
            # short of a way onto it (`law.near_misses`; the settle's join step went in feature 417 T44), and on seed 13 at 20 households a corridor's
            # start 15 ft from another's end was carried onto it and closed a sliver with a third - lawful as judged, refused
            # as drawn (feature 314 research R12). So the tree is asked again with its ends joined as the web will join them -
            # the faces judged where a lane the joining drew differently from the base's, or the new lane, meets them
            trial = _trial(view, lanes=[*lanes, *stub])
            joined = as_joined(trial, lanes)
            moved = [pts for i in range(k) if (old := joined_base[i]["pts"]) != (now := joined[i]["pts"]) for pts in (old, now)]
            if joined_faces.needles_with(joined, [*moved, joined[k]["pts"]]):
                return False
            if any(n > law.DOORSTEP_MAX for n in tb.ends.with_one_more(k, new, house, trial).values()):
                return False
            if not way_out_once(M, [lanes_chain(recs, host, lanes, k)]):
                return False
            # ...NOR RUNS BESIDE ANOTHER TREE LANE PAST A PITCH, either way round (feature 294: a Sawada roll joined one access
            # lane to its neighbor's at a shallow angle, 115 ft within 30 ft of it - the doubled band `_lay_web_lane` refuses
            # of a web run, never asked of the tree; the pool test of feature 293 reads it on the finished map).
            # ...AND AS THE WALKER READS THEM (feature 318, Inashiro): two records met end to end are one way (`joints.as_walked`),
            # and a corridor whose host chain ran beside a third access lane for 105 ft passed record by record - until the
            # web pulled the joint straight and the doubled band stood as one record, two tree lanes no settle may cut
            if tree_shadows([ln["pts"] for ln in lanes]) or walked_shadows(lanes):
                return False
    return True


def laid_run(base: Any, M: Mapping[str, Any], run: Poly) -> Poly:
    """`run` as the web lays it - rejoined (`rejoined`) and squared at its water crossings (`base.squared`) - each run once while
    the water stands.

    EACH RUN REJOINED AND SQUARED ONCE WHILE THE WATER STANDS (dev/performance.md, shape two): every seat asked re-laid every
    reserved run of the tree - `rejoined` tests each leg against every leg of the brook and the channels (312,044
    `segments_cross` on seed 44, most of the tree's question) - though a reserved run and the water are the same from one seat
    to the next. Remembered on `base` by the run's points, and forgotten whenever the water the squaring reads differs."""
    memo = base.__dict__.setdefault("_tree_squares", {})  # the water does not change while the seating asks
    waters = square_waters_of(M)
    laid = base.__dict__.get("_tree_laid")
    if laid is None or laid[0] != waters:
        laid = base.__dict__["_tree_laid"] = (waters, {})
    done: dict[tuple[Pt, ...], Poly] = laid[1]
    key = tuple(run)
    hit = done.get(key)
    if hit is None:
        joined = rejoined(run, waters)
        sk = tuple(joined)
        if sk not in memo:
            memo[sk] = base.squared(list(joined))
        hit = done[key] = list(memo[sk])
    return list(hit)


def as_joined(trial: Mapping[str, Any], lanes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """`lanes` (the first lanes of `trial`) with every end that stops short of a way carried onto it, as the settle carries it
    (`law.near_misses` reads them the same way)."""
    out = [dict(ln) for ln in lanes]
    for i, end, f in law.near_misses(trial):
        if i < len(out):
            p = [_pt(q) for q in out[i]["pts"]]
            out[i]["pts"] = [*p, f] if end == -1 else [f, *p]
    return out


def walked_shadows(lanes: Sequence[Mapping[str, Any]]) -> bool:
    """Does the way the last lane is read as (`joints.as_walked`: the lanes met end to end joined) run beside another way
    past a pitch, or another beside it (`tree_shadows`, on the walked ways)?

    Research: no doubled band - research/questions/0081-village-lanes.drawing.html: two paths running side by side are drawn as one, measured at less than 20 degrees and cut where the lane comes alongside - the test is 30 ft for more than a pitch, with no angle, cutting mid-stretch, a departure the code keeps until feature 417 T32; an access lane may not run beside another past a pitch, read as the walker reads it"""
    from .joints import as_walked  # joints reaches the web's smoothing; imported here, where the seating asks it

    ways, owner = as_walked(lanes)
    k = owner[len(lanes) - 1]
    order = [*(w for m, w in enumerate(ways) if m != k), ways[k]]
    return tree_shadows(order)


def tree_shadows(ways: Sequence[Sequence[Pt]]) -> bool:
    """Does the last way run beside another past a pitch, or another beside it (`serve.shadowed_by`, way against way)?

    Research: no doubled band - research/questions/0081-village-lanes.drawing.html: two paths running side by side are drawn as one, measured at less than 20 degrees and cut where the lane comes alongside - the test is 30 ft for more than a pitch, with no angle, cutting mid-stretch, a departure the code keeps until feature 417 T32; a way may not run beside another past a pitch"""
    from .serve import shadowed_by  # serve reaches the web's draw; imported here, where the seating asks it

    last = len(ways) - 1
    if shadowed_by(ways, last) is not None:
        return True
    return any(shadowed_by([ways[i], ways[last]], 0) is not None for i in range(last))


def lanes_chain(recs: Sequence[Mapping[str, Any]], host: Sequence[int | None], lanes: Sequence[Mapping[str, Any]], k: int) -> Poly:
    """The way out along the tree from run `k`'s door: its lane, then each host's lane on from where the run before met it,
    then the strip on to its end (`lanes` as `lanes_of` built them for every run, the strip first where there is one)."""
    path = [_pt(q) for q in lanes[k]["pts"]]
    for h in chain_of(recs, host, k)[1:]:
        path += _from(lanes[h]["pts"], path[-1])
    return _dedup(path)


def _from(run: Sequence[Any], q: Pt) -> Poly:
    """`run` on from the point of it nearest `q` to its far end."""
    pts = [_pt(p) for p in run]
    k = min(range(len(pts) - 1), key=lambda m: seg_dist(q[0], q[1], pts[m], pts[m + 1]))
    return [seg_closest(q[0], q[1], pts[k], pts[k + 1]), *pts[k + 1 :]]


def way_out_once(M: Mapping[str, Any], chains: Sequence[Poly]) -> bool:
    """Does each way out along the tree (`chains`) cross every brook at most once (ways W08)? A tree has one way from a door
    to its root, so that is the household's way out while the tree is all there is.

    Research: way out crosses each brook once - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html"""
    return all(len(law.crossing_points(c, brook)) <= 1 for brook in law._brooks(M) for c in chains)


# ---- the draw ------------------------------------------------------------------------------------------------------------


def _key(ln: Mapping[str, Any]) -> tuple[Any, ...] | None:
    role = ln.get("role")
    if role == ACCESS_ROLE and ln.get("of"):
        return (role, round(float(ln["of"][0]), 1), round(float(ln["of"][1]), 1))
    return None


def set_corridor(M: dict[str, Any], ln: Mapping[str, Any]) -> bool:
    """Household way `ln`'s reserved corridor (`access_corridors`, read by `tree_records`) rewritten as the lane now stands, so
    the settle's next draw of the tree (`settle_tree`) draws it so too - asked where a settle step re-lays a household's way
    (`knots.settle_knots`, its foot gathered onto the junction beside it). False where `ln` is no household's way or its
    record is not found.

    Research: plumbing - NONE: the reserved corridor kept in step with the way drawn"""
    key = _key(ln)
    acs = M.get("access_corridors") or []
    start = next((n for n, c in enumerate(acs) if key is not None and c.get("of") and _key({"role": ACCESS_ROLE, "of": c["of"]}) == key), None)
    pts = [[float(x), float(y)] for x, y in ln.get("pts") or []]
    if start is None or len(pts) < 2:
        return False
    end = start + 1
    while end < len(acs) and not acs[end].get("of"):
        end += 1
    acs[start:end] = [{"pts": [a, b], **({"of": acs[start]["of"]} if n == 0 else {})} for n, (a, b) in enumerate(zip(pts, pts[1:], strict=False))]
    return True


def owed(M: Mapping[str, Any]) -> list[int]:
    """The reserved runs the web owes a lane: EVERY HOUSEHOLD'S WAY (feature 318, FR-014: each household's way is laid once every
    house stands, in the gaps - `settlement/rolling/gap_ways.py` - and every farmhouse not reached across a neighbor's yard is
    served by a lane of its own from its dooryard; owed only where a house was unreached, four of Inashiro's fifteen ways were
    left undrawn, their dooryards 26-78 ft from any lane, glyph-check 2026-10-04) - with every run each hangs from.

    Research:
        every farmhouse served - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every other farmhouse is served by a lane of its own, its way leaving its dooryard; a household reached across a neighbor's yard has none
        the way of a household another is reached across - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: owed with every household's way, its own way always drawn
    """
    recs = tree_records(M)
    host = hosts(recs, _root(M))
    # ...AND THE CORRIDOR OF EVERY HOUSE ANOTHER IS REACHED ACROSS (feature 317, `rolling/passage.py`): the walk arrives at that
    # house's yard and goes on along its way, so its way is drawn however near the lanes its center stands - a glyph-check of
    # Inashiro found the anchor 90 ft from a lane, its corridor not owed, and the two farmsteads left with no way touching either
    want = [i for i, r in enumerate(recs) if r["of"] is not None]
    return sorted({j for i in want for j in chain_of(recs, host, i)})


def passage_anchors(M: Mapping[str, Any]) -> list[Pt]:
    """Where each household reached across a neighbor's yard is reached from - the neighbors' positions (`reached_across`)."""
    return [(float(h["reached_across"][0]), float(h["reached_across"][1])) for h in M.get("houses") or [] if h.get("reached_across")]


def settle_tree(s: Any) -> int:
    """Step 4 (ways W01, W03): the tree lanes the web owes (`owed`), drawn as the gap pass judged them (`lanes_of`) - each
    once - and then the ordinary lanes that break a rule against
    them cut (`settle_defer`). Returns the lanes drawn or re-laid.


    Research:
        tree lane's room - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a no-build corridor of WEB_CLEARANCE, 9 ft each side of the middle (the 18 ft room)
    Research: every farmhouse served - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every household's way, laid in the gaps once the last house stands, drawn as a lane of its own"""
    M = s.M
    need = owed(M)
    if not need:
        return 0
    recs = tree_records(M)
    host = hosts(recs, _root(M))
    drawn = {k: i for i, ln in enumerate(M.get("lanes") or []) if (k := _key(ln)) is not None}
    chosen = sorted({*need, *(i for i, r in enumerate(recs) if _key({"role": r["role"], "of": r["of"]}) in drawn)})
    n = 0
    for ln in lanes_of(M, recs, host, chosen):
        k = _key(ln)
        pts = [[float(x), float(y)] for x, y in ln["pts"]]  # as judged: `lanes_of` rounds all but the connector's start
        if k in drawn:
            i = drawn[k]
            if M["lanes"][i]["pts"] != pts and s.reshape_lane(M["lanes"][i], pts):
                s.reink_lane(i)
                n += 1
            continue
        s.lane([tuple(q) for q in pts], width=float(ln["w"]), clearance=WEB_CLEARANCE, worn=True)
        M["lanes"][-1].update({key: ln[key] for key in ("role", "of") if key in ln})
        n += 1
    return n + settle_defer(s)


def tree_faults(M: Mapping[str, Any]) -> list[tuple[int, Pt]]:
    """(ordinary lane, the point it must be cut at) for every rule an ordinary lane breaks AGAINST a tree lane, where the
    repair the settle would otherwise make names the tree lane, or would split the web to make: its end meets an ordinary
    lane's tread as a needle, its tail runs on beside an ordinary lane, the two close a sliver of grass (`law.needle_loops`;
    `settle_needles` cuts only where nothing splits, cohort seeds 15, 27 and 36), or a house discharges more than
    `law.DOORSTEP_MAX` free ends. The ordinary lane is cut there - it defers.

    Research: ordinary lane defers - NONE: which of two lanes a repair cuts"""
    lanes = M.get("lanes") or []
    out: list[tuple[int, Pt]] = []
    for i, end, k, u, v in law.needle_ends(lanes, lazy_ground(M)):  # ...a needle the ground forces is no fault (feature 385 plan D2)
        if is_tree(lanes[i]) and not is_tree(lanes[k]):
            q = law.lane_pts(lanes[i])[end]
            out.append((k, seg_closest(q[0], q[1], u, v)))
    ways = [law.lane_pts(ln) for ln in lanes]
    for i in law.doubled_tails(M):
        if is_tree(lanes[i]):
            from .sweeps import _DOUBLED_DEG, along_tail

            # ...EITHER END, as `law.doubled_tails` asks it (feature 293 on 291): asked of the tree lane's last end only, a field way
            # whose FIRST end ran 38 ft beside an ordinary lane named no lane to cut, the tree lane alone broke the rule, and the
            # web was refused (perf reference, seed 39, feature 306)
            for j, o in enumerate(ways):
                if j != i and not is_tree(lanes[j]) and len(o) >= 2 and any(along_tail(r, o, deg=_DOUBLED_DEG) is not None for r in (ways[i], ways[i][::-1])):
                    q = min((ways[i][0], ways[i][-1]), key=lambda e: min(seg_dist(e[0], e[1], a, b) for a, b in zip(o, o[1:], strict=False)))
                    out.append((j, q))
    # ...OR RUNS BESIDE ONE PAST A PITCH, either way round (feature 318, Sawada): a reserved corridor drawn again where a drop
    # left its house unreached (`settle_reach`) ran beside the web's orphan link, the link held the network together and the
    # tree lane is never cut, so the doubled band stood - the ordinary lane is cut at the middle of its stretch beside it
    out += [(j, q) for i, j, q in tree_shadow_cuts(lanes, ways)]
    for face, bounding in law.needle_loops(M):
        if any(is_tree(lanes[i]) for i in bounding):
            c = face.centroid.coords[0]
            out += [(i, (float(c[0]), float(c[1]))) for i in bounding if not is_tree(lanes[i])]
    for _h, ends in law.fronting_ends(M).items():
        if len(ends) > law.DOORSTEP_MAX:
            out += [(i, ways[i][e]) for i, e in ends if not is_tree(lanes[i])]
    return out


def tree_shadow_cuts(lanes: Sequence[Mapping[str, Any]], ways: Sequence[Sequence[Pt]]) -> list[tuple[int, int, Pt]]:
    """(tree lane, ordinary lane, the point to cut it at) for every ordinary lane running beside a tree lane past a pitch, or
    a tree lane beside it (`serve.shadowed_by`, way against way): the middle of the ordinary lane's longest stretch within
    `WEB_SHADOW_FT` of the tree lane - where a cut of `DEFER_GAP_FT` either side leaves no stretch past the pitch.

    Research: no doubled band - research/questions/0081-village-lanes.drawing.html: two paths running side by side are drawn as one, measured at less than 20 degrees and cut where the lane comes alongside - the test is 30 ft for more than a pitch, with no angle, cutting mid-stretch, a departure the code keeps until feature 417 T32; an ordinary lane may not run beside a tree lane for more than a bundle pitch; the ordinary lane defers"""
    from .serve import WEB_SHADOW_FT, sampled, shadowed_by

    out: list[tuple[int, int, Pt]] = []
    for i, p in enumerate(ways):
        if not is_tree(lanes[i]) or len(p) < 2:
            continue
        for j, o in enumerate(ways):
            if j == i or is_tree(lanes[j]) or lanes[j].get("connector") or len(o) < 2:
                continue
            if shadowed_by([p, o], 0) is None and shadowed_by([o, p], 0) is None:
                continue
            run = sampled(o)
            near = [min(seg_dist(q[0], q[1], a, b) for a, b in zip(p, p[1:], strict=False)) < WEB_SHADOW_FT for q in run]
            best = (0, 0)
            start = None
            for k, f in enumerate([*near, False]):
                if f and start is None:
                    start = k
                elif not f and start is not None:
                    best = max(best, (k - start, start))
                    start = None
            if best[0]:
                out.append((i, j, run[best[1] + best[0] // 2]))
    return out


DEFER_GAP_FT = 30.0
"""How much of an ordinary lane a cut for deference takes out either side of the point (`settle_defer`): past a needle's
20 ft leg and a doubled tread's 14 ft, so the stretch that met the tree lane goes with it.

Research: defer cut extent - NONE: past the law's own legs"""


ALONGSIDE_STEP_FT = 5.0
"""How far apart the points are that `cut_alongside` asks along a lane, walking in from an end (405 T26, D131).

Research: the walk's step - NONE: how finely the walk samples the lane for a cut point (coarser than a footpath's 3 ft tread by 2 ft), nothing read off the map"""


def alongside_points(seq: Sequence[Pt], trees: Sequence[tuple[int, Poly]]) -> Iterator[tuple[int, Pt, Pt]]:
    """Walking `seq` from its first point in `ALONGSIDE_STEP_FT` steps: each (leg, point, foot) where the point stands within
    `WEB_SHADOW_FT` of a tree lane's nearest leg and the lane's leg there runs under `_SIDE_BY_SIDE_DEG` to it - the foot its
    nearest point on that tree lane (405 T26, D131).

    Research:
        side by side - research/questions/0081-village-lanes.drawing.html: a lane that wanders over another way at less than 20 degrees would be walked into one path with it (a map drawing convention, the page's own reading)
        beside, as the map reads it - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25); 0081 gives the angle but no distance; read within `WEB_SHADOW_FT` (30 ft, the distance the shadow rule reads two ways together at), as `knots.teed_back` reads it"""
    from ..consts import WEB_SHADOW_FT
    from .knots import _SIDE_BY_SIDE_DEG

    for k in range(len(seq) - 1):
        a, b = seq[k], seq[k + 1]
        n = max(1, int(math.dist(a, b) // ALONGSIDE_STEP_FT))
        for t in range(n + 1):
            x = (a[0] + (b[0] - a[0]) * t / n, a[1] + (b[1] - a[1]) * t / n)
            for _j, o in trees:
                u, v = min(zip(o, o[1:], strict=False), key=lambda uv: seg_dist(x[0], x[1], *uv))
                turn = abs(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]) - math.atan2(v[1] - u[1], v[0] - u[0]))) % 180.0
                if seg_dist(x[0], x[1], u, v) <= WEB_SHADOW_FT and min(turn, 180.0 - turn) < _SIDE_BY_SIDE_DEG:
                    yield k, x, seg_closest(x[0], x[1], u, v)


def _joined(M: Mapping[str, Any]) -> dict[str, Any]:
    """The map with only the lanes joined to the connector's network (`settle.connector_component`): what reaches."""
    from .settle import connector_component

    keep = connector_component(M.get("lanes") or [])
    return {**M, "lanes": [ln for k, ln in enumerate(M.get("lanes") or []) if k in keep]}


def strands_the_reach(M: Mapping[str, Any], i: int, pieces: Sequence[Poly]) -> bool:
    """Would lane `i` cut into `pieces` leave the field or a house no longer reached from the connector's network - what
    `settle_network` keeps of a split web (405 T26, D131)? A piece the cut strands that reaches nothing goes with the network
    step as before; this asks only after what the map is owed.

    Research:
        the field reached - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a way runs from the network to the field's bund
        every house reached - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every other farmhouse is served by a lane of its own - a gap that leaves a house no longer joined to the connector's network strands it"""
    lanes = M["lanes"]
    trial = {**M, "lanes": [*lanes[:i], *({**lanes[i], "pts": [list(q) for q in pc]} for pc in pieces if len(pc) >= 2), *lanes[i + 1 :]]}
    now, then = _joined(M), _joined(trial)
    return law.field_unreached(then) > law.field_unreached(now) or len(unreached_houses(then)) > len(unreached_houses(now))


def cut_alongside(M: Mapping[str, Any], i: int, admit: Callable[[Poly], bool] = lambda run: True) -> Poly | None:
    """Ordinary lane `i` CUT WHERE IT COMES ALONGSIDE a tree lane and teed onto it there (405 T26, D131): walked in from each
    end (`alongside_points`), the first point whose cut `admit` takes (the overlap matrix, in `settle_defer`) and that leaves
    the lane no rule broken against the tree (`tree_faults`), the web in no more networks and no more knots (`knots.knots`;
    cohort seed 26 knotted where it did not), and no house nor the field newly unreached; None where no point does. Cohort seed 47 with T26's sheds: the field's join-orphans link ran 550 ft beside
    three households' ways; cut where it first came alongside one, past that household's threshing yard, the field kept it.

    Research:
        cut where it comes alongside, met as a T - research/questions/0081-village-lanes.drawing.html: "the maps cut it where it comes alongside and let it meet the other as a T" (a map drawing convention, the page's own reading)
        the field reached - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a way runs from the network to the field's bund
        each end walked, the nearer point first - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); the walk from the lane's first end is tried before the walk from its last, and on each the first point found - so the lane is kept from that end up to where it first comes alongside; only ordinary lanes are cut here (`tree_faults` names no tree lane), never a household's own way, so no door end is in question (0081 cuts that at its far end)
        no more knots - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point - a tee that leaves more knots is refused
        no house newly unreached - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every other farmhouse is served by a lane of its own - nor one that leaves more networks or a house unreached"""
    from .checks import unreached_houses

    lanes = M["lanes"]
    p = law.lane_pts(lanes[i])
    trees = [(j, law.lane_pts(ln)) for j, ln in enumerate(lanes) if j != i and is_tree(ln) and len(ln.get("pts") or []) >= 2]
    from .knots import knots

    nets, field, houses, tied = law.lane_networks(M), law.field_unreached(M), len(unreached_houses(M)), len(knots(lanes))
    for seq in (list(p), list(p)[::-1]):
        for k, x, foot in alongside_points(seq, trees):
            run: list[Pt] = []
            for q in (*seq[: k + 1], x, foot):
                if not run or math.dist(q, run[-1]) > 1e-6:
                    run.append(q)
            if len(run) < 2 or not admit(run):
                continue
            trial = {**M, "lanes": [*lanes[:i], {**lanes[i], "pts": [list(q) for q in run]}, *lanes[i + 1 :]]}
            if (
                len(knots(trial["lanes"])) <= tied
                and not any(j == i for j, _q in tree_faults(trial))
                and law.lane_networks(trial) <= nets
                and law.field_unreached(trial) <= field
                and len(unreached_houses(trial)) <= houses
            ):
                return run
    return None


def settle_defer(s: Any) -> int:
    """Every ordinary lane that breaks a rule against a tree lane (`tree_faults`) is cut `DEFER_GAP_FT` either side of the
    point - the tree is never cut - or, where that gap would leave the field or a house unreached (`strands_the_reach`), cut
    where it comes alongside a tree lane and teed onto it (`cut_alongside`, 405 T26, D131: tried on every such cut, it knotted
    cohort seed 26). Returns the lanes cut.

    Research: where the gap would strand the reach, cut where it comes alongside - research/questions/0081-village-lanes.drawing.html: a lane that wanders over another way at under 20 degrees is cut where it comes alongside and meets the other as a T (a map drawing convention, the page's own reading) - asked only where the defer's own gap would leave the field or a house unreached (the gap itself is the defer's older cut, carried to 405 T127); tried on every cut, the tee knotted cohort seed 26 (measured 2026-10-24, 405 T26)"""
    from .settle import apply_pieces, arc_at, cut_around

    faults = tree_faults(s.M)
    if not faults:
        return 0
    lanes = s.M["lanes"]
    edits: dict[int, list[Poly]] = {}
    for i, q in faults:
        if i in edits:
            continue
        p = law.lane_pts(lanes[i])
        k = min(range(len(p) - 1), key=lambda m: seg_dist(q[0], q[1], p[m], p[m + 1]))
        gap = cut_around(p, arc_at(p, k, seg_closest(q[0], q[1], p[k], p[k + 1])), DEFER_GAP_FT)
        # ...UNLESS THE GAP WOULD LEAVE A HOUSE OR THE FIELD UNREACHED: then cut where it comes alongside a tree lane, teed on it
        # (405 T26, D131) - cohort seed 47 with T26's sheds: the gap cut out of the field's join-orphans link stranded its field
        # half, and the field was reached by no way
        if strands_the_reach(s.M, i, gap):
            admit = lambda run, ln=lanes[i]: s.admits("lanes", {**ln, "pts": [[round(float(a), 1), round(float(b), 1)] for a, b in run]}, ignore=ln)  # noqa: E731
            if (teed := cut_alongside(s.M, i, admit)) is not None:
                edits[i] = [teed]
                continue
        edits[i] = gap
    return apply_pieces(s, edits)


REJOIN_PAD_FT = 4.0
"""How far beyond the square leg's reach (the water's half-width and `checks.SQUARE_LEG_PAD`) a tree run is given a vertex
either side of an oblique crossing before it is squared (`rejoined`) - past the squaring's elbow pass, so the vertex
stands and the run rejoins its own line there."""


def rejoined(run: Poly, waters: Sequence[tuple[Poly, float]]) -> Poly:
    """`run` with a vertex set on it either side of each crossing of the water it would be squared at (`waters`, as
    `settle.square_waters` lists them), far enough out to stand clear of the water: `checks.square_crossings` replaces the
    crossing's segment by a square leg joined straight to the segment's far end, so without them a long run moved along the
    whole of its length after the crossing - cohort seed 8's exit strip, over a channel, moved under every corridor hanging
    from it. The tree's runs are squared as they are drawn, and each corridor meets its host where the host still runs.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.2 (floor on sin, a divide-by-zero guard)
    """
    from l7r.diagram.settlement import seg_intersect, segments_cross

    from .checks import SQUARE_LEG_PAD
    from .clearance import _ZIGZAG_RUN_FT

    out: Poly = [run[0]] if run else []
    for a, b in zip(run, run[1:], strict=False):
        d = math.dist(a, b)
        cuts: list[float] = []
        for course, half in waters:
            for c, e in zip(course, course[1:], strict=False):
                if d == 0.0 or math.dist(c, e) == 0.0 or not segments_cross(a, b, c, e):
                    continue
                x = seg_intersect(a, b, c, e)
                if x is None:  # pragma: no cover - segments that cross are not parallel
                    continue
                sin = abs(((b[0] - a[0]) * (e[1] - c[1]) - (b[1] - a[1]) * (e[0] - c[0])) / (d * math.dist(c, e)))
                # ...clear of the LONGER square leg too, which the squaring takes where the short one leaves a zigzag
                # (`squaring.squared_against`, feature 328 wave 46): set inside it, the vertices were overrun and the run moved
                reach = (max(half, _ZIGZAG_RUN_FT / 2.0 + 1.0) + SQUARE_LEG_PAD + REJOIN_PAD_FT) / max(sin, 0.2)
                t = math.dist(a, x)
                cuts += [t - reach, t + reach]
        for t in sorted(c for c in cuts if 0.0 < c < d):
            out.append((a[0] + (b[0] - a[0]) * t / d, a[1] + (b[1] - a[1]) * t / d))
        out.append(b)
    return _dedup(out)


def square_waters_of(M: Mapping[str, Any]) -> list[tuple[Poly, float]]:
    """`settle.square_waters`, imported where it is asked (the settle imports this module)."""
    from .settle import square_waters

    return square_waters(M)


def square_run_of(M: Mapping[str, Any], run: Poly) -> Poly:
    """`settle.square_run`, imported where it is asked (the settle imports this module)."""
    from .settle import square_run

    return square_run(M, run)


# ---- the seating's questions -------------------------------------------------------------------------------------------


def seating_law(s: Any) -> Any:
    """The `settle.Lawful` the seating asks its corridors of, over the manifest as it stands - built ONCE per house seated
    (it reads the houses) and shared by the ground test (`homesteads.stages.corridor_ground`) and the tree's
    (`seating_judge`): built per question it re-derived the worked ground's union of the field's plots every time."""
    import types

    from .settle import Lawful

    houses = s.M.get("houses") or []
    key = (len(houses), id(houses[-1]) if houses else None)
    memo = s.__dict__.get("_seating_law")
    if memo is None or memo[0] != key:
        # ...OVER ONE VIEW OF THE MANIFEST FOR THE WHOLE SEATING: `Lawful` keeps the worked ground on the object it is given
        # (`geom.memo_ground`, rebuilt only when the field's registries change), so a fresh view per house seated threw it
        # away and re-took the union of the field's plots once per house (seed 44: 17 builds, most of the seating's rise)
        view = s.__dict__.get("_seating_view")
        if view is None or view.M is not s.M:
            view = s.__dict__["_seating_view"] = types.SimpleNamespace(M=s.M)
        law_ = Lawful(view)
        # ...and the runs the tree has laid so far carried on to it (`admits`: each remembered with the water it was laid
        # against, and dropped where that water differs): a reserved run is laid the same whichever house is being seated
        if memo is not None and "_tree_laid" in memo[1].__dict__:
            law_.__dict__["_tree_laid"] = memo[1].__dict__["_tree_laid"]
        memo = s.__dict__["_seating_law"] = (key, law_)
    return memo[1]


YARD_JITTER = 0.10
"""How far in a drawn threshing yard's corners may be pulled from its rect, as a share of its half-span (`_attach_yard`
draws it with `Settlement._quad`'s jitter 0.10): the yard the seating judges a corridor's door end against as a steading
it arrives at (`law.dangling_lane_ends`) is its rect shrunk by that much, which every drawn yard contains - Mizuguchi's
flank door, 11 ft off the rect, stood 12.4 ft off the drawn yard and was left serving nothing."""


def records_of(geom: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """The house and threshing-yard records a homestead's bundle (`geom`) will be drawn as - its house at the bundle's turn,
    its yard as the least that will be drawn of it (`YARD_JITTER`) - for the tree to judge a corridor against before they
    stand."""
    hx, hy, hw, hh = (float(v) for v in geom["house"])
    turn = float(geom.get("turn") or 0.0)
    house = {"x": hx, "y": hy, "w": hw, "h": hh, "rot": turn}
    if geom.get("yard") is None:
        return house, None
    yx, yy, yw, yh = (float(v) for v in geom["yard"])
    th, k = math.radians(turn), 1.0 - YARD_JITTER
    c, sn = math.cos(th), math.sin(th)
    inner = [(yx + dx * c - dy * sn, yy + dx * sn + dy * c) for dx, dy in ((-yw * k / 2, -yh * k / 2), (yw * k / 2, -yh * k / 2), (yw * k / 2, yh * k / 2), (-yw * k / 2, yh * k / 2))]
    return house, {"x": yx, "y": yy, "w": yw, "h": yh, "rot": turn, "of": [hx, hy], "poly": [list(q) for q in inner]}


def seating_judge(s: Any) -> Any:
    """The tree's question (`admits`) as the gap pass asks it of each household's way once the last house stands
    (`access.tree_admits`, `gap_ways`, feature 318), installed on the settlement as `_corridor_tree` - the settlement package
    cannot import the hamlet generator.

    Research: a corridor judged as the web will lay it - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way, laid once the last house stands, refused where its squared run crosses its own household's house, beds, sheds or fixtures (`own_clear`) or another standing homestead (`others_clear`), nothing built on a lane
    """

    def judge(corridor: Sequence[Pt], geom: Mapping[str, Any]) -> bool:
        house, yard = records_of(geom)
        base, run = seating_law(s), [_pt(q) for q in corridor]
        # ...AND THE HOUSEHOLD'S OWN HOUSE, BEDS AND FIXTURES CLEAR OF IT AS THE WEB WILL LAY IT (feature 317): squaring a water
        # crossing re-lays the approach (`laid_run`), and on cohort seed 18 at 15 households it took a routed path's bend out
        # and ran the lane across the household's own privy - asked of the path as found, never of the path as drawn, since
        # the household's parts are not yet on the manifest the tree reads (`OverlapRefused`, lanes over farm_fixtures).
        drawn = laid_run(base, s.M, run)
        if drawn != run and not own_clear(s, drawn, geom):
            return False
        # ...AND EVERY OTHER HOMESTEAD CLEAR OF IT AS THE WEB WILL LAY IT (feature 318, the reference at 40 households, seed 25):
        # the squaring dropped a bend that stood in a channel and the drawn chord ran through a neighbor's privy - the reserved
        # legs had cleared the standing homesteads (`access.standing_clear`), the drawn ones were never asked
        if drawn != run and not others_clear(s, drawn):
            return False
        return admits(base, s.M, run, ACCESS_ROLE, house, yard)

    return judge


def seating_drawn(s: Any) -> Any:
    """A corridor as the web will draw it (`laid_run`: rejoined and squared at its water crossings), installed on the settlement
    as `_corridor_drawn` for `access.reserve` - the settlement package cannot import the hamlet generator. Reserved as the gap
    pass lays each household's way once the last house stands (`gap_ways`, feature 318), so what is placed after keeps off it.

    Research: a corridor kept clear as the web will lay it - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: nothing built on a lane; each household's way laid once the last house stands
    """

    def drawn(corridor: Sequence[Pt]) -> Poly:
        return laid_run(seating_law(s), s.M, [_pt(q) for q in corridor])

    return drawn


def others_clear(s: Any, run: Poly) -> bool:
    """Does every leg of `run` clear the homesteads already standing, by the corridor's own test of them
    (`access.standing_clear`) - the leg onto the tree passing unasked where it has no length?

    Research: nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a way clears every other homestead, as the web will lay it
    """
    from l7r.diagram.settlement.rolling import access as A

    last = len(run) - 2
    return all((n == last and math.dist(a, b) < 1e-6) or A.standing_clear(s, a, b) for n, (a, b) in enumerate(zip(run, run[1:], strict=False)))


def own_clear(s: Any, run: Poly, geom: Mapping[str, Any]) -> bool:
    """Does every leg of `run` clear the household's own house, beds, sheds and fixtures, by the corridor's own leg tests
    (`access.house_clear`, `fixtures_clear`, `parts_clear`) - the leg onto the tree passing unasked where it has no length?

    Research: a lane clear of its own household - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: nothing built on a lane; a path routed round its own beds and fixtures, at the corridor's own leg gaps
    """
    from l7r.diagram.settlement.rolling import access as A

    hgap, last = A.house_gap(s), len(run) - 2
    return all(
        (n == last and math.dist(a, b) < 1e-6) or (A.house_clear(a, b, geom, hgap) and A.fixtures_clear(s, a, b, geom) and A.parts_clear(s, a, b, geom))
        for n, (a, b) in enumerate(zip(run, run[1:], strict=False))
    )
