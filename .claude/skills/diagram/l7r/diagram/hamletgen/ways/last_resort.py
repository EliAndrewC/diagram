"""The settle's last resort, and the refusal behind it (feature 287, FR-005; ways W01, W03, W08, homes H16).

WHY IT IS ITS OWN MODULE. `settle.settle_the_web` repairs the web round by round; should the rounds run out with a rule
still broken, what is left is decided here - and what it may NOT do is the point. It drops ORDINARY lanes whole, never a
TREE lane (`corridors.is_tree`): every tree lane was admitted lawful at seating (`tree.admits`, the whole tree judged as
lanes), so the tree is what the map's reach rests on. It used to drop a tree lane that carried a household's way out over
the brook and back, and a house or the field left unreached by that was recorded in `meta.roll_failures` and shipped - a
fallback that emitted the violation (research R12's caveat on ways W01 / W03, homes H16). Now a rule the tree still breaks
once every ordinary lane that could mend it is gone is an engine defect, refused by name (`WebRefused`): the map is not
produced. And a farmhouse, or the field its corridor was reserved to, left unreached when the settle ends - whichever way
it ended - is refused the same way (`refuse_unreached`), so nothing downstream records one."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement.city.bridges import flooded_ground

from . import law
from .checks import unreached_houses
from .clearance import kink_spans
from .corridors import FIELD_ROLE, is_tree
from .geom import memo_ground, worked_ground
from .settle import (
    _crossing_fault,
    _fabric,
    _ordinary,
    _pts,
    fouled_segment,
    settle_fragments,
    settle_husks,
    settle_joins,
    settle_network,
    settle_reach,
    settle_street_ends,
    settle_widths,
    unsettled,
)
from .tree import prune_the_tree, settle_defer, tree_faults, tree_records

LAST_RESORT_PASSES = 8
"""How many times the last resort drops and re-asks before it refuses. Each pass drops at least one ordinary lane, or it
ends; the steps between passes add tread only to close a join (`settle.settle_joins`) or as tree lanes, so this is a
bound, not a tuning - the settle's own `SETTLE_ROUNDS`."""


class WebRefused(ValueError):
    """The settled web still breaks a rule only the TREE could mend - a tree lane breaking a rule of the lane law, a way out
    over the brook and back carried on tree lanes alone - or leaves a farmhouse or the reserved field unreached. The seating
    admitted every tree lane lawful (`tree.admits`), so this is an engine defect named, never a lane dropped from the tree
    or a failure recorded on the map (FR-005)."""


def lanes_breaking(s: Any) -> set[int]:
    """Every lane but the connector - the tree's included - that some per-lane rule of the law names: a hook, a kink, a
    crossing fault, a foul of the fabric, and every joint rule that names a lane (a hairpin at the connector, a needle, a
    fold, a doubled tail, a dangling end, a crowded doorstep, an end behind a house, a sliver of grass); the ordinary lanes
    crossing a brook some household's way out crosses twice; and the ordinary lanes that break a rule against the tree
    (`tree.tree_faults`), which defer. The connector is held by its own placer (`track.connector_through`)."""
    M = s.M
    lanes = M.get("lanes") or []
    yards, houses = _fabric(s)
    solid = law.solid_boxes(M)
    fixtures = law.fixture_quads(M)
    wet = flooded_ground(M)
    bad: set[int] = set()
    for i, ln in enumerate(lanes):
        if ln.get("connector") or len(ln.get("pts") or []) < 2:
            continue
        p = _pts(ln)
        if law.hooked(p) or kink_spans(p) or _crossing_fault(M, i, p, wet) is not None or fouled_segment(p, float(ln.get("w") or 3.0), houses, yards, solid, fixtures, M) is not None:
            bad.add(i)
    ground = memo_ground(s, "worked", worked_ground)
    bad |= {i for _c, i, _e in law.connector_hairpin_ends(lanes)}
    bad |= {i for i, _e, _k, _u, _v in law.needle_ends(lanes)}
    bad |= {i for i, _ei, _j, _ej in law.folded_joint_pairs(lanes)}
    bad |= set(law.doubled_tails(M))
    bad |= {i for i, _e in law.dangling_lane_ends(M, ground)}
    bad |= {i for ends in law.fronting_ends(M).values() if len(ends) > law.DOORSTEP_MAX for i, _e in ends}
    bad |= {i for i, _e, _h in law.ends_behind(M, ground)}
    bad |= {i for _face, bounding in law.needle_loops(M) for i in bounding}
    if law.way_outs_crossing(M):
        bad |= {i for brook in law._brooks(M) for i in _ordinary(M) if law.crossing_points(_pts(lanes[i]), brook)}
    bad |= {i for i, _q in tree_faults(M)}
    return {i for i in bad if not lanes[i].get("connector")}


def lane_violators(s: Any) -> list[int]:
    """The ORDINARY lanes `lanes_breaking` names - what the last resort drops. Never a tree lane (a way out carried over the
    brook and back on tree lanes alone is `refuse_unmended`'s, not a drop)."""
    lanes = s.M.get("lanes") or []
    return sorted(i for i in lanes_breaking(s) if not is_tree(lanes[i]))


def ordinary_carriers(M: Mapping[str, Any]) -> list[int]:
    """The ordinary lanes carrying a crossing of a household's way out over the brook and back (`law.way_out_carriers`)."""
    lanes = M.get("lanes") or []
    return sorted({i for i, _k, _y in law.way_out_carriers(M) if not is_tree(lanes[i])})


def last_resort(s: Any) -> int:
    """THE LAST RESORT (FR-005): the rounds ran out with a lane still breaking a rule, so every ORDINARY lane still breaking
    one goes whole - never kept as the least bad - with the network and husk rules asked again of what is left; then the
    rules no drop can break are asked once more (a join closed only where it meets cleanly, the reach a drop took away drawn
    again as the tree, the network, a fragment that no longer earns, one width a way); then an ordinary lane still carrying
    a way out over the brook and back goes too, and the whole is asked again - up to `LAST_RESORT_PASSES` times. A tree lane
    is never dropped here. Whatever is still broken after that is refused (`refuse_unmended`). Returns the lanes dropped."""
    dropped = 0
    for _ in range(LAST_RESORT_PASSES):
        while bad := lane_violators(s):
            s.drop_lanes(bad)
            dropped += len(bad)
            settle_network(s)
            settle_husks(s)
        for step in (settle_street_ends, settle_joins, settle_reach, settle_defer, settle_network, settle_fragments, prune_the_tree, settle_widths, settle_husks):
            step(s)
        carriers = ordinary_carriers(s.M)
        if not carriers and not lane_violators(s) and not unsettled(s.M, memo_ground(s, "worked", worked_ground)):
            break
        s.drop_lanes(carriers)
        dropped += len(carriers)
        settle_network(s)
        settle_husks(s)
    refuse_unmended(s)
    return dropped


def _named(lanes: Sequence[Mapping[str, Any]], idxs: Iterable[int]) -> str:
    return ", ".join(f"{i} ({lanes[i].get('role') or 'ordinary'})" for i in sorted(idxs))


def refuse_unmended(s: Any) -> None:
    """Raise `WebRefused` if, after the last resort, a lane still breaks a rule of the law (a tree lane, which no drop may
    take; or an ordinary one the passes ran out on) or a household's way out still crosses the brook and back (on tree lanes
    alone, since every ordinary carrier was dropped)."""
    M = s.M
    lanes = M.get("lanes") or []
    why = []
    if left := lanes_breaking(s):
        why.append(f"lanes {_named(lanes, left)} still break a rule of the lane law")
    if carriers := {i for i, _k, _y in law.way_out_carriers(M)}:
        why.append(f"a household's way out crosses the brook and back on lanes {_named(lanes, carriers)}")
    if broken := unsettled(M, memo_ground(s, "worked", worked_ground)):
        # ...AND THE WHOLE LAW IS ASKED, as the settle's exit asks it: a rule no lane above is named for (a split network, a
        # width step) still refuses, by the rule's name
        why.append(f"the web still breaks {', '.join(sorted(broken))}")
    if why:
        raise WebRefused("the web's last resort cannot mend it without dropping a tree lane: " + "; ".join(why))


def refuse_unreached(M: Mapping[str, Any]) -> None:
    """Raise `WebRefused` if the settled web leaves a farmhouse unreached (`unreached_houses`), or the field unreached where
    the seating reserved it a corridor (`law.field_unreached`, a `field` record in `access_corridors`): the seating reserved a
    lawful corridor for each, and the web draws it as the tree, so neither is ever shipped unreached (ways W01, W03)."""
    why = []
    if far := unreached_houses(M):
        why.append(f"{len(far)} farmhouse(s) stand off the connected way network, at {[(x, y) for x, y, _d in far[:4]]}")
    if law.field_unreached(M) and any(r["role"] == FIELD_ROLE for r in tree_records(M)):
        why.append("the field its reserved corridor runs to is reached by no way")
    if why:
        raise WebRefused("the settled web leaves unreached what the seating reserved a way for: " + "; ".join(why))
