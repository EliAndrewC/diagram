"""The access tree as lanes: judged whole at seating, drawn by construction (feature 287 wave 6; ways W01, W03).

WHY THIS REPLACES THE CORRIDOR SEARCH AT THE DRAW. The seating reserved, for every house it admitted, a corridor from its
door to a tree rooted at the exit strip (`settlement/rolling/access.py`), and asked of each leg only the GROUND half of the
lane law. The web then drew a corridor where its lanes did not reach a house, stopping at the first contact with them - and
that run's joints with the ordinary lanes (a needle, a kink squared at a channel, a fold) were known only then, so a house
whose every run was refused was recorded (`meta.access_refused`) and shipped unreached (research R9: cohort seeds 8 and 39
under feature 284's probes). No later repair could be proven to succeed.

SO THE ORDER CHANGES, and the proof with it:

1. THE TREE IS JUDGED WHOLE AT SEATING (`tree_admits`). Its lanes - each house's corridor from where it leaves its own
   yard to its target on the tree, the field's corridor from the bund, and the exit strip from its innermost attachment
   out - are the only lanes there are, so every joint among them is known. A seat whose corridor would make the tree
   unlawful (the whole `settle.Lawful` - ground, kink, hook, needle, fold, hairpin, doubled tail, dangling end, an end
   behind a house - and no sliver of grass among its lanes, no house discharging more than `law.DOORSTEP_MAX` ends, no way
   out over a brook and back) is refused there and the next seat tried, as the seating already refused on ground.
2. THE TREE IS DRAWN BEFORE THE REST OF THE LAW IS ASKED, AND THE ORDINARY LANES DEFER TO IT (`settle_tree`, then
   `settle_defer`): every farmhouse the web does not reach, and the field where no way reaches it, gets its chain of tree
   lanes - exactly those the seating judged, sub-runs of none (the strip from the innermost chain's attachment, which the
   seating judged as the strip's inner end when that corridor was admitted) - and an ordinary lane that breaks a rule
   against a tree lane is cut, never the tree.
3. THE TREE IS PRUNED (`prune_the_tree`): a tree lane whose removal leaves no house, way target or field unreached, splits
   no network and leaves no other lane's end serving nothing goes (homes H40: no more corridors than the map needs).

So every house with a reserved corridor, and the field with a reserved corridor, is reached by construction: there is no
fallback that ships one unreached.

Research: access tree plumbing - NONE
"""

from __future__ import annotations

import copy
import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_closest, seg_dist

from ..consts import WEB_CLEARANCE, Poly, Pt
from . import law
from .bund import BRANCH_WIDTH
from .checks import unreached_houses
from .corridors import ACCESS_ROLE, ACCESS_WIDTH, FIELD_ROLE, ON_TREE_PX, is_tree
from .geom import memo_ground, polyline_len, worked_ground

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
        if c.get("field"):
            if cur is None or cur["role"] != FIELD_ROLE:
                cur = {"role": FIELD_ROLE, "of": None, "pts": [pts[0]]}
                out.append(cur)
        elif c.get("of"):
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
    """The tree's root (feature 320): the track out as drawn, from the gate the households' ways reach; before it is drawn,
    the stretch of it from the gate the ways are laid to (`way_out_root`, `household_ways.root_at_the_gate`). None where
    neither stands."""
    con = next((law.lane_pts(ln) for ln in M.get("lanes") or [] if ln.get("connector") and len(ln.get("pts") or []) >= 2), None)
    if con is None:
        con = M.get("way_out_root")
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


def lanes_of(
    M: Mapping[str, Any], recs: Sequence[Mapping[str, Any]], host: Sequence[int | None], chosen: Sequence[int], drawn: bool = True, square: Any = None, laid: Any = None
) -> list[dict[str, Any]]:
    """The tree lanes for the runs `chosen` (their chains' closure taken by the caller), squared at their water crossings as
    the web draws every lane (`settle.square_run`, or `square` - the seating's `Lawful.squared`, the same answer asked only
    where water comes near, and remembered per run), the exit strip first. `laid`, where given, is the whole of that - a run
    rejoined (`rejoined`) and squared - as the seating remembers it per run (`admits`).

    Research:
        tree lane tread by role - research/questions/0081-village-lanes.drawing.html: exit strip and house access 3 ft, field way 5 ft
        tree lanes assembled - NONE: the runs squared and set on their hosts as the web draws them"""
    if laid is not None:
        sq = laid
    else:
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
        r, pts = recs[i], drawn_of[i]
        # ...ITS END CARRIED ONTO ITS HOST AS DRAWN: the host is squared at its water crossings, and a run that met it on the
        # stretch the squaring moved (cohort seed 8: the exit strip over a channel) is carried on to the foot on it
        h = host[i]
        on = drawn_of.get(h) if h is not None else None
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
        out.append(lane)
    return out


class _Standing(dict):  # type: ignore[type-arg]
    """A trial manifest that still answers the registry of what stands (`registry.forbidden_segment` reads `.standing`)."""

    standing: Any = None


def _trial(M: Mapping[str, Any], **over: Any) -> _Standing:
    t = _Standing({**M, **over})
    t.standing = getattr(M, "standing", None)
    return t


def admits(base: Any, M: Mapping[str, Any], run: Poly, role: str = ACCESS_ROLE, house: Mapping[str, Any] | None = None, yard: Mapping[str, Any] | None = None) -> bool:
    """THE ONE PREDICATE OF THE TREE (feature 287 wave 6): would the access tree on `M`, with `run` added as a corridor of
    `role` (a house's, `house` its record-to-be and `yard` its threshing yard's; or the field's), keep the lane law among
    its lanes? `base` (a `settle.Lawful` over `M`) is asked of the new lane against the rest, with the connector stood in
    for by `STUB_FT` on from the strip's end - in the whole tree, and in the tree the web draws for this corridor alone (its
    chain, the strip from the chain's attachment: `lanes_of`), since the web draws only the chains it owes - every rule of a
    pair is asked of the new lane against each lane it meets, so the strip's inner end, where the new lane is its innermost
    attachment, is judged there too. And: no sliver of grass among the tree's lanes (`law.needle_loops`); no house
    discharging more than `law.DOORSTEP_MAX` free ends; the new house's way out along the tree crossing each brook at most once. The gap pass
    asks it of each household's way once the last house stands (`gap_ways`, feature 318), before it admits the way.

    Research:
        tree keeps the lane law - research/questions/0081-village-lanes.drawing.html: each household's way, laid once the last house stands, admitted with no hook, fold, hairpin or dangling end among the tree's lanes
        no sliver between the tree's lanes - UNRESEARCHED: no needle (`needle_loops`), asked of the tree with its ends joined as the settle joins them (`as_joined`), and no doubled tail
        way out crosses each brook once - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        no doubled band - UNRESEARCHED: an access lane may not run beside another past a pitch
        free ends at a house - UNRESEARCHED: at most DOORSTEP_MAX (2) free lane ends at a house"""
    recs: list[dict[str, Any]] = [*tree_records(M), {"role": role, "of": (float(house["x"]), float(house["y"])) if house is not None else None, "pts": _dedup([_pt(q) for q in run])}]
    root = _root(M)
    host = hosts(recs, root)
    k = len(recs) - 1
    if host[k] is None or len(recs[k]["pts"]) < 2:
        return False
    stub: list[dict[str, Any]] = [{"pts": root, "w": 6.0, "connector": True}] if root is not None else []  # the track out as drawn
    houses = [*(M.get("houses") or []), *([house] if house is not None else [])]
    yards = [*(M.get("threshing_yards") or []), *([yard] if yard is not None else [])]
    view = _trial(M, houses=houses, threshing_yards=yards)
    law_ = copy.copy(base)
    law_.tree = False
    chain = chain_of(recs, host, k)
    whole = [*range(k), k]

    def lay(run: Poly) -> Poly:
        return laid_run(base, M, run)

    for ctx in (whole, [*reversed(chain[1:]), k]):
        lanes = lanes_of(M, recs, host, ctx, drawn=False, laid=lay)
        new = lanes[-1]
        law_.M = _trial(view, lanes=[*lanes[:-1], *stub])
        if not law_(new["pts"], float(new["w"])):
            return False
        if ctx is whole:
            # ...NOR CLOSES A SLIVER WITH OTHER TREE LANES (the tree had none; two corridors on one host point did, cohort seeds
            # 21 and 25). A corridor may CROSS another - a crossroads is lawful, and was refused here at first for closing a loop
            # (seed 8: 44 of its seats, and the margin with them) - since only a face thinner than `law.NEEDLE_LOOP_FT` is a
            # fault, and a face in a part of the tree is never thinner than the faces the whole tree made of it
            if law.needle_loops({"lanes": lanes}):
                return False
            # ...NOR CLOSES ONE ONCE THE WEB JOINS ITS ENDS (feature 317, plan D6): the settle carries a free end that stops
            # short of a way onto it (`settle.settle_joins`, `law.near_misses`), and on seed 13 at 20 households a corridor's
            # start 15 ft from another's end was carried onto it and closed a sliver with a third - lawful as judged, refused
            # as drawn (feature 314 research R12). So the tree is asked again with its ends joined as the web will join them.
            if law.needle_loops({"lanes": as_joined(_trial(view, lanes=[*lanes, *stub]), lanes)}):
                return False
            if any(len(ends) > law.DOORSTEP_MAX for ends in law.fronting_ends(_trial(view, lanes=[*lanes, *stub])).values()):
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
    (`settle.settle_joins`, which reads `law.near_misses` the same way)."""
    out = [dict(ln) for ln in lanes]
    for i, end, f in law.near_misses(trial):
        if i < len(out):
            p = [_pt(q) for q in out[i]["pts"]]
            out[i]["pts"] = [*p, f] if end == -1 else [f, *p]
    return out


def walked_shadows(lanes: Sequence[Mapping[str, Any]]) -> bool:
    """Does the way the last lane is read as (`joints.as_walked`: the lanes met end to end joined) run beside another way
    past a pitch, or another beside it (`tree_shadows`, on the walked ways)?

    Research: no doubled band - UNRESEARCHED: an access lane may not run beside another past a pitch, read as the walker reads it"""
    from .joints import as_walked  # joints reaches the web's smoothing; imported here, where the seating asks it

    ways, owner = as_walked(lanes)
    k = owner[len(lanes) - 1]
    order = [*(w for m, w in enumerate(ways) if m != k), ways[k]]
    return tree_shadows(order)


def tree_shadows(ways: Sequence[Sequence[Pt]]) -> bool:
    """Does the last way run beside another past a pitch, or another beside it (`serve.shadowed_by`, way against way)?

    Research: no doubled band - UNRESEARCHED: a way may not run beside another past a pitch"""
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
    return (role,) if role == FIELD_ROLE else None


def left_to_the_tree(M: Mapping[str, Any], i: int) -> bool:
    """Would taking ordinary lane `i` away keep every other lane on the connector's network and the web in no more networks,
    leaving unreached only farmhouses whose way the gap pass laid (`gap_ways`, feature 318) - which the settle then draws as
    judged (`owed`, `settle_tree`)? `settle.keeps_the_network` asks that no house be newly unreached at all.

    WHY (feature 306, Sawada): a join-orphans lane ran 105 ft within 30 ft of the exit strip - the doubled band
    `settle_shadows` takes away - but it was the one way reaching a farmhouse, so the web was not kept without it and the
    band stayed; that house had no corridor drawn only because the stray lane reached it first. Its way was laid and judged
    lawful by the gap pass, so the band goes and the house is reached by its own way.

    Research: every farmhouse served - research/questions/0081-village-lanes.drawing.html: a stray lane goes where the house's own way, laid in the gaps once the last house stands, will reach it"""
    from .corridors import _on_the_connector

    lanes = M.get("lanes") or []
    others = [k for k in range(len(lanes)) if k != i]
    if (_on_the_connector(lanes, range(len(lanes))) - {i}) - _on_the_connector(lanes, others):
        return False
    trial = {**M, "lanes": [lanes[k] for k in others]}
    if law.lane_networks(trial) > law.lane_networks(M):
        return False
    before = {(x, y) for x, y, _d in unreached_houses(M)}
    lost = [(x, y) for x, y, _d in unreached_houses(trial) if (x, y) not in before]
    reserved = [r["of"] for r in tree_records(M) if r["role"] == ACCESS_ROLE and r["of"] is not None]
    return bool(lost) and all(any(math.dist(h, c) <= 1.5 for c in reserved) for h in lost)


def owed(M: Mapping[str, Any]) -> list[int]:
    """The reserved runs the web owes a lane: EVERY HOUSEHOLD'S WAY (feature 318, FR-014: each household's way is laid once every
    house stands, in the gaps - `settlement/rolling/gap_ways.py` - and every farmhouse not reached across a neighbor's yard is
    served by a lane of its own from its dooryard; owed only where a house was unreached, four of Inashiro's fifteen ways were
    left undrawn, their dooryards 26-78 ft from any lane, glyph-check 2026-10-04) and the field's where no way reaches the
    field (`law.field_unreached`) - with every run each hangs from.

    Research:
        every farmhouse served - research/questions/0081-village-lanes.drawing.html: every other farmhouse is served by a lane of its own, its way leaving its dooryard; a household reached across a neighbor's yard has none
        the way of a household another is reached across - research/questions/0081-village-lanes.drawing.html: owed with every household's way, its own way always drawn
        field reached - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the field's corridor where no way reaches its bund"""
    recs = tree_records(M)
    host = hosts(recs, _root(M))
    # ...AND THE CORRIDOR OF EVERY HOUSE ANOTHER IS REACHED ACROSS (feature 317, `rolling/passage.py`): the walk arrives at that
    # house's yard and goes on along its way, so its way is drawn however near the lanes its center stands - a glyph-check of
    # Inashiro found the anchor 90 ft from a lane, its corridor not owed, and the two farmsteads left with no way touching either
    want = [i for i, r in enumerate(recs) if r["of"] is not None]
    if law.field_unreached(M):
        want += [i for i, r in enumerate(recs) if r["role"] == FIELD_ROLE]
    return sorted({j for i in want for j in chain_of(recs, host, i)})


def passage_anchors(M: Mapping[str, Any]) -> list[Pt]:
    """Where each household reached across a neighbor's yard is reached from - the neighbors' positions (`reached_across`)."""
    return [(float(h["reached_across"][0]), float(h["reached_across"][1])) for h in M.get("houses") or [] if h.get("reached_across")]


def settle_tree(s: Any) -> int:
    """Step 4 (ways W01, W03): the tree lanes the web owes (`owed`), drawn as the gap pass judged them (`lanes_of`) - each
    once, the exit strip re-laid to reach a new innermost attachment - and then the ordinary lanes that break a rule against
    them cut (`settle_defer`). Returns the lanes drawn or re-laid.

    Research: every farmhouse served - research/questions/0081-village-lanes.drawing.html: every household's way, laid in the gaps once the last house stands, drawn as a lane of its own"""
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
    for i, end, k, u, v in law.needle_ends(lanes):
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

    Research: no doubled band - UNRESEARCHED: an ordinary lane may not run beside a tree lane for more than a bundle pitch; the ordinary lane defers"""
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


def settle_defer(s: Any) -> int:
    """Every ordinary lane that breaks a rule against a tree lane (`tree_faults`) is cut `DEFER_GAP_FT` either side of the
    point - the tree is never cut. Returns the lanes cut."""
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
        edits[i] = cut_around(p, arc_at(p, k, seg_closest(q[0], q[1], p[k], p[k + 1])), DEFER_GAP_FT)
    return apply_pieces(s, edits)


def prune_the_tree(s: Any) -> int:
    """A tree lane the map no longer needs goes (homes H40): the first, longest first, whose removal leaves no farmhouse, way
    target or field newly unreached, the web in no more networks and no lane end breaking a rule it did not (`end_faults`).
    A drawn corridor goes only as a LEAF - no drawn corridor hanging from it - and the exit strip with it retracts to the
    innermost attachment still drawn, or goes (`strip_run`): the strip's inner end is that corridor's joint, and taken one
    at a time neither could go. One a round, as a fragment: two can each be redundant only while the other stands.

    Research:
        redundant tree lane pruned - UNRESEARCHED: no more corridors than the map needs; never a household's own way (research/questions/0081-village-lanes.drawing.html: every other farmhouse is served by a lane of its own)
        the way of a household another is reached across - research/questions/0081-village-lanes.drawing.html: its corridor never pruned, as no household's own way is
        street and door path never pruned - research/questions/0033-row-villages-resson.drawing.html: the way a row's farms are reached by"""
    M = s.M
    lanes = M.get("lanes") or []
    order = sorted(
        # ...never a row village's street or a grove farm's own door path (feature 291 FR-017 and FR-019): each is the way its
        # farms are reached by, not a corridor another way stands in for - pruned as one, Mizuguchi's door paths went as
        # redundant beside a street a frame's depth off, and the streets' ends were left dangling
        (
            i
            for i, ln in enumerate(lanes)
            if is_tree(ln)
            and not ln.get("connector")
            and not ln.get("street")
            and not ln.get("serves")
            and len(ln.get("pts") or []) >= 2
            and not ln.get("of")  # ...NOR A HOUSEHOLD'S OWN WAY (feature 318, FR-014): each is the lane its household is served by
        ),
        key=lambda i: -polyline_len(law.lane_pts(lanes[i])),
    )
    if not order:
        return 0
    recs = tree_records(M)
    host = hosts(recs, _root(M))
    run_of = {_key({"role": r["role"], "of": r["of"]}): k for k, r in enumerate(recs)}
    drawn = {run_of[k]: i for i, ln in enumerate(lanes) if (k := _key(ln)) in run_of}
    ground = memo_ground(s, "worked", worked_ground)
    reached, nets, targets, field = len(unreached_houses(M)), law.lane_networks(M), len(law.unreached_targets(M)), law.field_unreached(M)
    ends = end_faults(M, ground)
    for i in order:
        r = next((k for k, j in drawn.items() if j == i), None)
        if r is not None and any(host[k] == r for k in drawn):
            continue  # a corridor another drawn corridor hangs from: not a leaf
        without = {**M, "lanes": [ln for k, ln in enumerate(lanes) if k != i and len(ln.get("pts") or []) >= 2]}
        if (
            len(unreached_houses(without)) <= reached
            and law.lane_networks(without) <= nets
            and len(law.unreached_targets(without)) <= targets
            and law.field_unreached(without) <= field
            and all(a <= b for a, b in zip(end_faults(without, ground), ends, strict=True))
        ):
            s.drop_lanes([i])
            return 1
    return 0


REJOIN_PAD_FT = 4.0
"""How far beyond the square leg's reach (the water's half-width and `checks.SQUARE_LEG_PAD`) a tree run is given a vertex
either side of an oblique crossing before it is squared (`rejoined`) - past the squaring's elbow pass, so the vertex
stands and the run rejoins its own line there."""


def rejoined(run: Poly, waters: Sequence[tuple[Poly, float]]) -> Poly:
    """`run` with a vertex set on it either side of each crossing of the water it would be squared at (`waters`, as
    `settle.square_waters` lists them), far enough out to stand clear of the water: `checks.square_crossings` replaces the
    crossing's segment by a square leg joined straight to the segment's far end, so without them a long run moved along the
    whole of its length after the crossing - cohort seed 8's exit strip, over a channel, moved under every corridor hanging
    from it. The tree's runs are squared as they are drawn, and each corridor meets its host where the host still runs."""
    from l7r.diagram.settlement import seg_intersect, segments_cross

    from .checks import SQUARE_LEG_PAD

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
                reach = (half + SQUARE_LEG_PAD + REJOIN_PAD_FT) / max(sin, 0.2)
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


def end_faults(M: Mapping[str, Any], ground: Any) -> tuple[int, ...]:
    """How many lane ends break each rule an end is judged by - serving nothing, behind a house, a house's third, a fold
    where two meet with no third way there, a join stopping short: what a lane taken away can leave another lane's end
    doing, since the ends that met it are then free (cohort seeds 14 and 40: a corridor's end left behind a house)."""
    return (
        len(law.dangling_lane_ends(M, ground)),
        len(law.ends_behind(M, ground)),
        len(law.doorstep_ends(M)),
        len(law.folded_joint_pairs(M.get("lanes") or [])),
        len(law.near_misses(M)),
    )


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

    Research: a corridor judged as the web will lay it - research/questions/0081-village-lanes.drawing.html: each household's way, laid once the last house stands, refused where its squared run crosses its own household's house, beds, sheds or fixtures (`own_clear`) or another standing homestead (`others_clear`), nothing built on a lane
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

    Research: a corridor kept clear as the web will lay it - research/questions/0081-village-lanes.drawing.html: nothing built on a lane; each household's way laid once the last house stands
    """

    def drawn(corridor: Sequence[Pt]) -> Poly:
        return laid_run(seating_law(s), s.M, [_pt(q) for q in corridor])

    return drawn


def others_clear(s: Any, run: Poly) -> bool:
    """Does every leg of `run` clear the homesteads already standing, by the corridor's own test of them
    (`access.standing_clear`) - the leg onto the tree passing unasked where it has no length?

    Research: nothing built on a lane - research/questions/0081-village-lanes.drawing.html: the strip clears every other homestead, as the web will lay it
    """
    from l7r.diagram.settlement.rolling import access as A

    last = len(run) - 2
    return all((n == last and math.dist(a, b) < 1e-6) or A.standing_clear(s, a, b) for n, (a, b) in enumerate(zip(run, run[1:], strict=False)))


def own_clear(s: Any, run: Poly, geom: Mapping[str, Any]) -> bool:
    """Does every leg of `run` clear the household's own house, beds, sheds and fixtures, by the corridor's own leg tests
    (`access.house_clear`, `fixtures_clear`, `parts_clear`) - the leg onto the tree passing unasked where it has no length?

    Research: a lane clear of its own household - research/questions/0081-village-lanes.drawing.html: nothing built on a lane; a path routed round its own beds and fixtures, at the corridor's own leg gaps
    """
    from l7r.diagram.settlement.rolling import access as A

    hgap, last = A.house_gap(s), len(run) - 2
    return all(
        (n == last and math.dist(a, b) < 1e-6) or (A.house_clear(a, b, geom, hgap) and A.fixtures_clear(s, a, b, geom) and A.parts_clear(s, a, b, geom))
        for n, (a, b) in enumerate(zip(run, run[1:], strict=False))
    )
