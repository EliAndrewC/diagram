"""The lifted reach predicate (feature 166): which houses the connected lane network does not serve.

WHY THIS EXISTS. `hamletgen`'s re-roll ladder used to learn which seats stranded a farmhouse by running
the whole check battery and PARSING its printed output. Feature 166 retires the battery, so the predicate
moved into `ways.py`. It was LIFTED, not re-derived - `driver.py` records that a hand-rolled reach measure
"was wrong on five of six seeds... it over-counted and never read zero" - and the equivalence test at the
bottom is what proves the lift faithful.

THE EQUIVALENCE TEST DIES WITH THE CHECK, deliberately. It compares the lifted predicate against the gate,
so it can only run while the gate still exists. That is the whole reason feature 166's migration order has
the battery outliving its own replacements: the proof is only available before the safety net goes.
"""

from __future__ import annotations

import pytest

from l7r.diagram.hamletgen.ways import lanes_share_tread, served_network, unreached_houses

# two treads that come within 40 ft only at an interior VERTEX, never at an end - the case that separates
# this predicate from `_components`, which joins on ends alone
_L_END_APART = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]
_L_MID_NEAR = [(100.0, 20.0), (100.0, 400.0)]


def _lane(pts, **kw):
    return {"pts": [list(p) for p in pts], **kw}


# ---- lanes_share_tread: plain lists, no settlement ----------------------------------------------


def test_treads_that_pass_within_the_join_share_a_network():
    assert lanes_share_tread(_L_END_APART, _L_MID_NEAR) is True


def test_treads_that_stay_apart_do_not():
    assert lanes_share_tread(_L_END_APART, [(0.0, 500.0), (200.0, 500.0)]) is False


def test_the_join_is_measured_by_ANY_vertex_not_only_by_an_end():
    """The near-miss that would have moved maps, pinned on a pair that actually separates the two
    predicates. A long east-west lane, and a north-south lane crossing it whose ENDS are 500 ft away on
    either side but which has a VERTEX 20 ft off the tread. Any-vertex joins them; ends-only does not.

    My first fixture for this did NOT separate them - its near vertex was also an end - so the test passed
    for the wrong reason. Which is the feature's own subject in miniature: a test that cannot fail on the
    thing it names is not evidence."""
    from l7r.diagram.hamletgen.ways import _components

    east_west = [(0.0, 0.0), (500.0, 0.0), (1000.0, 0.0)]
    crossing = [(500.0, -500.0), (500.0, 20.0), (500.0, 500.0)]  # ends 500 ft off; middle vertex 20 ft off
    assert lanes_share_tread(east_west, crossing) is True, "any-vertex: the middle vertex is 20 ft off the tread"
    assert len(set(_components([east_west, crossing], 40.0))) == 2, "ends-only: every END is 500 ft away, so no join"


# ---- served_network: the component, seeded from the settlement's link to the world ---------------


def test_the_network_is_grown_from_the_connector_when_one_is_drawn():
    lanes = [_lane([(0, 0), (100, 0)]), _lane([(500, 500), (600, 500)], connector=True), _lane([(600, 500), (700, 500)])]
    segs = served_network(lanes)
    xs = {a[0] for a, _b in segs} | {b[0] for _a, b in segs}
    assert 500 in xs and 0 not in xs, "the isolated lane at the origin is not part of the connector's network"


def test_an_island_is_not_the_network():
    """A check satisfiable by an island rewards drawing an island - the defect two settlement-reviews
    found independently, where 7 of 19 houses were 'reached' only by a stub 136-296 ft from any real lane."""
    lanes = [_lane([(0, 0), (400, 0)], connector=True), _lane([(5000, 5000), (5100, 5000)])]
    segs = served_network(lanes)
    assert all(a[0] < 1000 and b[0] < 1000 for a, b in segs)


def test_no_lanes_means_no_network():
    assert served_network([]) == []


# ---- unreached_houses: the form condition, carried verbatim from the check -----------------------


def _M(**kw):
    base = {"meta": {"generated_by": "hamletgen", "settlement_form": "nucleated"}, "lanes": [], "houses": []}
    base.update(kw)
    return base


def test_a_house_on_the_network_is_reached():
    M = _M(lanes=[_lane([(0, 0), (400, 0)], connector=True)], houses=[{"x": 200, "y": 50}])
    assert unreached_houses(M) == []


def test_a_house_beyond_the_reach_is_reported_with_its_distance():
    M = _M(lanes=[_lane([(0, 0), (400, 0)], connector=True)], houses=[{"x": 200, "y": 300}])
    assert unreached_houses(M) == [(200, 300, 300)]


@pytest.mark.parametrize("meta", [{}, {"generated_by": "hamletgen", "settlement_form": "dispersed"}])
def test_the_rule_does_not_apply_to_a_hand_map_or_a_dispersed_one(meta):
    """FORM-CONDITIONAL, NOT WAIVED: a dispersed hamlet has no internal network by definition, so it does
    not BREAK this rule - the rule is not about it. Filing every dispersed map as an accepted exception
    would grow the waiver list with a form we chose deliberately."""
    M = _M(lanes=[_lane([(0, 0), (400, 0)], connector=True)], houses=[{"x": 200, "y": 9000}])
    M["meta"] = meta
    assert unreached_houses(M) == []


def test_an_undeclared_form_defaults_to_nucleated():
    M = _M(lanes=[_lane([(0, 0), (400, 0)], connector=True)], houses=[{"x": 200, "y": 300}])
    M["meta"] = {"generated_by": "hamletgen"}
    assert unreached_houses(M) == [(200, 300, 300)]
