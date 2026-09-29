"""The lane network a rolled hamlet must produce (feature 166).

Carries six rules the retired battery re-measured on every finished map: `lanes_form_one_network`,
`lanes_do_not_break_mid_run`, `lanes_bend_like_paths`, `lanes_reach_something`,
`lane_ends_front_different_houses` and `groves_clear_of_lanes`.

A LANE IS A WORN LINE, AND THAT IS THE GROUNDING BEHIND EVERY RULE HERE. Nobody laid these paths out;
they exist because inhabitants walked them, and a path exists only where somebody had a reason to go.
So a lane joins the rest of the network (you can get there from here), it does not stop in the middle of
a field (nothing wore that stretch), it bends the way a person walking bends rather than doubling back on
itself, and its ends front something worth walking to.

WHY THE WEB IS LAID AFTER THE HOUSES, WHICH IS WHAT MAKES THESE PROPERTIES OF THE PLACER. `stage_ways`
lays the skeleton and the connector BEFORE the homesteads, so the houses front them; `stage_web` lays the
lane web AFTER, because a web laid first competes for ground with the very houses it exists to serve
(measured: it grew the four pool clusters' long axes 15-97%, sprawl no check measures). The order is the
design, and these assertions are what pins it.
"""

from __future__ import annotations

import glob
import json
import math
import os

import pytest

from l7r.diagram.hamletgen.ways import law
from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)

# THE RULES' THRESHOLDS LIVE WITH THE RULES (feature 287, M1): the join tolerance, the double-back turn and the bend's run
# are `law.JOIN_TOL`, `law.DOUBLE_BACK_DEG` and `law.BEND_RUN_FT`, beside the predicates every test below calls.


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _min_dist(pt, poly) -> float:
    return min(_seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


def _ways(M):
    return [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or [])]


@pytest.fixture(scope="module")
def rolled():
    return _pool.rolled_map(SPEC)


@pytest.fixture(scope="module")
def lanes(rolled):
    """The drawn lanes, with the assertion that there ARE some. Every rule below would pass on an empty
    list, and a hamlet with no lanes is not a hamlet."""
    _plan, M = rolled
    ways = [p for p in _ways(M) if len(p) >= 2]
    assert len(ways) >= 2, "the roll drew fewer than two lanes, so the network rules would judge nothing"
    return M, ways


def _field_rings(M) -> list:
    from l7r.diagram.hamletgen.ways.sweeps import worked_ground_rings

    return worked_ground_rings(M)  # the sweep's own field, dry hem included (feature 261)


def _dangling_ends(M) -> list:
    """Every internal lane end that reaches nothing, read through the lane law's predicate (`law.dangling_ends`, feature
    287 M1), which asks the PLACER'S OWN `end_serves` - the body `_trim_to_service` trims with, which is what makes this a
    check on the placer rather than a second opinion about it (the skill's standing rule: "placement and its check must
    read the SAME source"). It had been a restatement, and it drifted twice - at the bar, which feature 227 fixed with
    `WAY_END_REACH_FT`, and then at what ARRIVAL is: both sides measured a farmhouse by its center and neither could see
    the garden fence a tread had actually stopped at, which is what `STEADING_ARRIVAL_FT` answers. Since 287 the other
    ways are asked less the one at the lane's own far end (the pool test's stronger set, one predicate for both)."""
    return law.dangling_ends(M)


def test_every_lane_belongs_to_one_network(lanes) -> None:
    """`lanes_form_one_network`. You can get from any door to any other, and to the connector that leaves
    the settlement. A lane in its own component is a path that starts nowhere a walker can reach - it is
    ink drawn where a path would look right, which is the difference between a map of a place and a
    picture of one."""
    M, _ways_all = lanes
    n = law.lane_networks(M)
    assert n == 1, f"the lanes fall into {n} disconnected networks - you cannot walk between them"


def test_no_lane_doubles_back_or_kinks(lanes) -> None:
    """`lanes_bend_like_paths`. A worn line bends around what is in the way; it does not turn back on
    itself, and it does not zig and immediately zag. Both shapes read as a routing artifact rather than as
    ground somebody walks, which is exactly what they are when they appear."""
    M, _ways_all = lanes
    bad = law.lanes_that_kink(M)
    assert not bad, f"lane(s) do not bend like paths: {bad[:4]}"


def test_no_two_lanes_meet_end_to_end_in_a_fold_and_no_lane_ends_in_a_hook(lanes) -> None:
    """Two records meeting end to end are ONE way to the walker, so the fold the per-lane rule above cannot see -
    one lane turning back at the point the next begins - is refused here, and so is a hook at a lane's end (GM
    2026-09-26: *"they are not going to walk in one direction and then turn at a 30-degree angle to keep
    walking"*). The joint rule and the hook thresholds are the engine's own (`hamletgen/ways/joints.py`)."""
    M, _ways_all = lanes
    folds = law.folded_joints(M.get("lanes") or [])
    hooks = law.hooked_ends(M)  # every lane, the connector included - the stricter of the two tests' readings (287 M1)
    assert not folds, f"two lanes meet end to end and double back at {folds[:4]}"
    assert not hooks, f"a lane ends in a hook at {hooks[:4]}"


def test_every_lane_end_reaches_something_worth_walking_to(lanes) -> None:
    """`lanes_reach_something`. A path exists because somebody had a reason to go there. An end that meets
    no other way, no house and no field is a line that stops in open ground, and there is nothing at the
    end of it for anyone to have worn the path to."""
    M, _ways_all = lanes
    assert (M.get("houses") or []) and any(len(o) >= 2 for o in _field_rings(M)), "the roll drew no house or no outlined field"
    dangling = _dangling_ends(M)
    assert not dangling, f"lane end(s) stop in open ground at {dangling[:4]} - nothing wore that path"


def test_a_lane_does_not_break_mid_run(lanes) -> None:
    """`lanes_do_not_break_mid_run`. A lane's drawn tread stops where something solid stands in it and
    resumes on the far side, which on the page reads as a path that vanishes and reappears. The physical
    claim is simpler than the geometry: ground either carries a path or it does not, and a gap in the ink
    with nothing in the gap is the drawing forgetting to finish the line."""
    M, _ways_all = lanes
    assert law.solid_boxes(M), "the roll placed nothing solid, so a break would have nothing to be explained by"
    gaps = law.breaks_mid_run(M)
    assert not gaps, f"lane(s) run straight through something solid at {gaps[:4]}"


def test_a_farmhouse_discharges_one_lane_end_not_three(lanes) -> None:
    """`lane_ends_front_different_houses`. A lane end is allowed to stop at a farmhouse - that is what it
    is for. What it may not do is let one farmhouse absolve three separate lane ends, because then the
    fabric grows a fan of stubs all pointing at the same door and the settlement reads as a diagram of
    frontage rather than as ground."""
    M, _ways_all = lanes
    assert M.get("houses") or [], "the roll placed no house"
    assert law.fronted_ends(M), "no lane end fronted a house, so this rule judged nothing"
    greedy = law.doorstep_ends(M)
    assert not greedy, f"house(s) discharge more than two lane ends apiece: {greedy}"


def test_no_tree_is_planted_in_a_path(lanes) -> None:
    """`groves_clear_of_lanes`. You do not plant a tree in a path. Canopy OVER a way is fine and expected -
    a woodland path is a path under trees (GM 2026-08-29) - so what is measured is the TRUNK position, not
    the crown's reach. That distinction is the whole rule: an earlier form of it read the crown and would
    have forbidden the shaded lane the GM asked for.

    ON THE TREAD, NOT NEAR IT - and the difference was a made-up number for three weeks (GM 2026-09-12: *"In
    real life, I have seen many footpaths that are within four feet of a tree trunk. So why is that a problem?
    ... is that just a number that was made up in the middle of implementation without any actual basis?"* It
    was). The rule's own grounding, written when it was first made, is that "a lane/street/road is bare trodden
    earth - you do not plant trees ON it", and the original check measured exactly that: `seg_dist < half + r`,
    the corridor's OWN half-width. Feature 166 lifted the rule out of the retired battery and rewrote the
    distance as a flat 4.0 ft from the centerline, which on a 3 ft footpath demands 2.5 ft of bare ground BEYOND
    the tread - a clearance nothing in the record asks for and no placer implements, so the gate failed a map
    whose trees stood 3.1 ft off a footpath's centerline, which is to say 1.6 ft clear of the path itself.
    The width is read from the lane again. A trunk inside the tread is a tree standing in the path; a trunk
    beside it is what a path looks like."""
    M, ways = lanes
    # `tree_crowns` is one FLAT list of x, y, r, x, y, r ... - the trunk is the first two of each triple
    # and the crown's REACH is the third. Reading the third here is exactly the mistake the rule warns
    # against, and the flat packing is what makes that mistake easy, so it is named at the point of use.
    flat = [float(v) for v in (M.get("tree_crowns") or [])]
    assert len(flat) % 3 == 0, "tree_crowns is not a flat list of (x, y, r) triples - the trunk read below would be nonsense"
    trunks = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 3)]
    assert trunks, "the roll drew no tree, so this rule would judge nothing"
    # the lane's own half-width, as the rule was first written - `w` is the drawn tread, defaulted as the
    # engine defaults it, and a trunk is judged against the path it would stand in rather than against a figure
    halves = [float(ln.get("w", 6)) / 2.0 for ln in (M.get("lanes") or [])]
    on_path = [(round(x), round(y)) for x, y in trunks if any(_min_dist((x, y), p) < halves[i] for i, p in enumerate(ways) if len(p) >= 2 and i < len(halves))]
    assert not on_path, f"tree trunk(s) stand ON a lane at {on_path[:4]}"


_POOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pool")


@pytest.mark.parametrize("manifest", sorted(glob.glob(os.path.join(_POOL, "hamlets", "*", "*.json"))), ids=os.path.basename)
def test_every_shipped_hamlets_lanes_are_one_network_at_the_ink_tolerance(manifest: str) -> None:
    """ONE NETWORK OR NOTHING holds on every SHIPPED hamlet, read from the committed manifest (feature 220,
    settlement-review of Sawada): the rule had a reader on the reference roll only, and the doubled-remnant
    sweep left three pool maps in two pieces at the 4 ft ink tolerance the one-network pass itself uses -
    joined only at the gate's 40 ft REACH figure, which is not an ink-continuity figure. Static data, so it
    costs nothing to ask of every map."""
    with open(manifest) as fh:
        M = json.load(fh)
    if sum(1 for ln in M.get("lanes") or [] if len(ln.get("pts") or []) >= 2) < 2:
        pytest.skip("fewer than two lanes")
    n = law.lane_networks(M)
    assert n == 1, f"{os.path.basename(manifest)}: {n} lane networks at {law.JOIN_TOL} ft"


@pytest.mark.parametrize("manifest", sorted(glob.glob(os.path.join(_POOL, "hamlets", "*", "*.json"))), ids=os.path.basename)
def test_every_shipped_hamlets_lane_ends_reach_something(manifest: str) -> None:
    """EVERY SHIPPED HAMLET, not only the reference roll (feature 227 D11). The rule had one reader, on
    Inashiro, and two pool maps carried straggler ends it never looked at - which is the same blind spot
    feature 220 found for the one-network rule, in the same place, for the same reason. Static data, so
    asking it of every map costs no roll; and it is the guard against the regression this fix could
    have, since what it reads is the placer's own predicate."""
    with open(manifest) as fh:
        M = json.load(fh)
    ways = _ways(M)
    if not any(len(p) >= 2 for p in ways):
        pytest.skip("no drawn lane")
    assert M.get("houses"), f"{os.path.basename(manifest)} records no house, so the end rule would judge nothing"
    dangling = _dangling_ends(M)
    assert not dangling, f"{os.path.basename(manifest)}: lane end(s) reach nothing at {dangling[:4]}"
