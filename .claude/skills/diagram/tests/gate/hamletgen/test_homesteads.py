"""gate tests split out of `tests.hamletgen.test_homesteads` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported.

SERVED FROM THE ROLL CACHE, KEYED TO EACH TEST'S OWN SOURCE (feature 135): every test here monkeypatches a seating
pass, so `rollcache.keyed_to` hashes the test function - where the patch lives - into the key beside the engine
functions the roll executed. `produce` returns plain data; the assertions run on it served or fresh (15-30 s each)."""

from unittest import mock

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache


# ROLLED IN A CHILD (feature 213 FR-007): the produce closure is lifted to this module-level function - the
# feature-146 doctrine - so the roll cache's child can import it by name; its patches are applied inside it.
def roll_cloud_only() -> tuple[int, str, dict]:  # type: ignore[type-arg]
    from l7r.diagram.hamletgen import homesteads as HS

    with mock.patch.object(HS.stages, "front_row", lambda plan, count, standoff=46.0: []), mock.patch.object(HS.stages, "lane_frontage", lambda s, seat, step=86.0: []):
        plan = hg.plan_site(hg.HamletSpec(name="CloudOnly", seed=7, households=10))
        s = hg.build(plan)
    return plan.placed, plan.cluster_shape, s.M["meta"]


def roll_lane_only() -> tuple[int, int]:
    from l7r.diagram.hamletgen import homesteads as HS

    with mock.patch.object(HS.stages, "front_row", lambda plan, count, standoff=46.0: []):
        plan = hg.plan_site(hg.HamletSpec(name="LaneOnly", seed=5, households=10, settlement_form="linear"))
        s = hg.build(plan)
    return plan.placed, len(HS.lane_frontage(s, plan.seat, connector=True))


def roll_one_house() -> tuple[int, int]:
    from l7r.diagram.hamletgen import homesteads as HS

    with mock.patch.object(HS.stages, "front_row", lambda plan, count, standoff=46.0: []):
        plan = hg.plan_site(hg.HamletSpec(name="OneHouse", seed=5, households=10, settlement_form="linear"))
        object.__setattr__(plan.spec, "households", 1)  # frozen, and `replace` would re-run the band validator
        s = hg.build(plan)
    return len(s.M["houses"]), len(HS.lane_frontage(s, plan.seat, connector=True))


HERE_MOD = "tests.gate.hamletgen.test_homesteads"


@pytest.mark.rolls_map
def test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_rows_offer_nothing() -> None:
    """The front row + lane frontage seat every household on all four scripted hamlets, so the
    `cluster_seeds` CLOUD - the fallback behind them - runs on no real map. It got quieter still on
    2026-08-17, when `front_row` began sampling by bundle pitch instead of by household count.

    A fallback nothing exercises is a fallback nobody knows is broken, so drive it directly: with
    both row passes returning no seats, the cloud has to seat the hamlet by itself. This also pins
    the lean-toward-the-field transform (`ly = -wdep + (ly + wdep) * 0.75`), which is the only place
    that compression is applied."""
    placed, cluster_shape, meta = rollcache.keyed_to(test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_rows_offer_nothing, roll_cloud_only, child=f"{HERE_MOD}:roll_cloud_only")[0]
    assert placed > 0, "with both row passes silent, every farmstead must come from the cloud"
    assert meta["cluster_seeding"] == "cloud"
    # THE INVARIANT IS A TRACE EITHER WAY, not an unconditional stamp (updated 2026-08-19). The
    # declaration is validated against the DRAWN aspect now, so a cloud-seated cluster whose drawing
    # does not match its roll is correctly recorded `cluster_shape_unhonored` instead - which is the
    # whole point of the guard. Asserting the honored key unconditionally would re-assert the very
    # thing the honesty rule exists to deny.
    assert cluster_shape in (meta.get("cluster_shape"), meta.get("cluster_shape_unhonored")), "the cloud must record the rolled shape either as honored or as unhonored"


@pytest.mark.rolls_map
def test_lane_frontage_seats_the_hamlet_when_the_field_row_offers_nothing() -> None:
    """The lane-frontage pass seats the BACK RANK on a real map, but only the households past one
    rank's worth of the band - so on a small hamlet it can place very few, and for part of one day
    (while `front_row` sampled by density with no cap) it placed nothing at all and the cluster came
    out a single rank. Drive it directly, with the field row silent, so the code that puts a door on
    a lane is exercised whatever the cap leaves it."""
    placed, offered = rollcache.keyed_to(test_lane_frontage_seats_the_hamlet_when_the_field_row_offers_nothing, roll_lane_only, child=f"{HERE_MOD}:roll_lane_only")[0]
    assert placed > 0, "with the field row silent, the farmsteads must still be seated"
    assert offered, "a linear hamlet must be offered seats along the connector it fronts"


@pytest.mark.rolls_map
def test_the_linear_frontage_pass_stops_once_the_households_are_housed() -> None:
    """The connector offers more verge than the hamlet needs, and the pass must stop taking it.

    `lane_frontage` returns every seat the connector can carry, which is routinely more than there
    are farmsteads to put on them. Without the household check the pass keeps seating while the
    offers last, and the map ends up with more houses than the spec asked for - at which point the
    acreage checks are reading a hamlet nobody rolled.

    THE COUNT IS LOWERED AFTER PLANNING, on purpose. `HamletSpec` refuses anything under ten as an
    outlying farmstead rather than a hamlet, so a one-household spec cannot be constructed - but the
    guard under test is about the COUNT alone, and everything else the plan derives (canvas, acreage,
    connector) should stay a real hamlet's or the pass is being exercised on a site that could not
    exist. So the site is planned as a ten-household hamlet and only the target is cut, which is the
    smallest change that puts the guard on the critical path: the first offer is taken, and the
    second is refused by the count rather than by the verge running out.

    `front_row` is silenced for the same reason as the test above - so the frontage pass is what
    seats the hamlet, rather than whatever the field row happens to leave it."""
    houses, offered = rollcache.keyed_to(test_the_linear_frontage_pass_stops_once_the_households_are_housed, roll_one_house, child=f"{HERE_MOD}:roll_one_house")[0]
    assert houses == 1, "a one-household target gets one farmstead, however much verge is on offer"
    assert offered > 1, "the guard is only under test when more seats were offered than taken"
