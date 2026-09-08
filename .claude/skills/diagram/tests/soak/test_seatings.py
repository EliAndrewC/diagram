"""THE THREE SEATINGS, in the tier ABOVE the gate (feature 217, GM 2026-09-08; moved from tests/gate/hamletgen/).

Each test drives one seating pass with the others silenced - the `cluster_seeds` cloud alone, the lane frontage alone,
the frontage stopping at one household - on copies of ONE partial roll (the stages before the homestead pass, then the
pass and the track per variant; feature 216). They assert BEHAVIOR: that a fallback nothing on a shipped map exercises
still seats a hamlet. Their one coverage line is a unit test now (`tests/hamletgen/homesteads/test_seats.py`), so under
constitution VI - the gate rolls only what the floor needs - the roll they share belongs here, where `make soak` runs
it and no ordinary run does. The GM accepted the loss at feature 217's landing: until the soak tier runs, these three
assertions are proved by nothing.

SERVED FROM THE ROLL CACHE, KEYED TO THE PRODUCER'S OWN SOURCE (feature 135): `rollcache.keyed_to` hashes `roll_seatings`
into the key beside the engine functions the roll executed, and the roll runs in a child shared across workers."""

import contextlib
from unittest import mock

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen import HamletSpec
from l7r.diagram.pipeline import rollcache

HERE_MOD = "tests.soak.test_seatings"
# THE SEATINGS' PARTIAL ROLL: the linear form LaneOnly and OneHouse need; the cloud's assertions hold on it too (specs/216 R1).
SEATINGS = HamletSpec(name="Seatings", seed=5, households=10, settlement_form="linear")


# ONE PARTIAL ROLL FOR THE THREE SEATINGS (feature 216, GM 2026-09-08: the gate rolls "only what is strictly necessary
# in order to reach one hundred percent code coverage"). The stages before the homestead pass run once, in a child;
# the state is copied three times and each seating runs with its patch - the cloud alone, the lane frontage alone, the
# one-household stop - followed by the track, whose connector the frontage seats along (measured: the frontage offers
# nothing until the track has drawn it). The three runs share the child's pid and request, so the census reads one
# roll with four attempts. What this no longer proves, stated (specs/216 FR-005 d): the stages after the track on the
# seated variants (their lines are unit tests), the cloud on a rolled NUCLEATED hamlet (it is asserted on the shared
# linear state), and three distinct maps.
def roll_seatings() -> dict[str, tuple]:  # type: ignore[type-arg]
    import copy

    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen import homesteads as HS
    from l7r.diagram.settlement import Settlement

    names = [st.__name__ for st in driver.STAGES]
    cut, track = names.index("stage_homesteads"), names.index("stage_track")
    plan = hg.plan_site(SEATINGS)
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s._avoid_seats = []  # type: ignore[attr-defined]
    with driver.roll_scope(plan.spec):
        for st in driver.STAGES[:cut]:
            st(s, plan)

    def seat(patches: dict[str, object], households: int | None = None) -> tuple:  # type: ignore[type-arg]
        s2, p2 = copy.deepcopy(s), copy.deepcopy(plan)
        if households is not None:
            object.__setattr__(p2.spec, "households", households)  # frozen, and `replace` would re-run the band validator
        with contextlib.ExitStack() as stack:
            for name, fake in patches.items():
                stack.enter_context(mock.patch.object(HS.stages, name, fake))
            with driver.roll_scope(p2.spec):
                driver.STAGES[cut](s2, p2)
                driver.STAGES[track](s2, p2)
        return s2, p2

    silent_row = {"front_row": lambda plan, count, standoff=46.0, **kw: []}
    silent_both = {**silent_row, "lane_frontage": lambda s, seat, step=86.0, **kw: []}
    c_s, c_p = seat(silent_both)
    l_s, l_p = seat(silent_row)
    o_s, o_p = seat(silent_row, households=1)
    return {
        "cloud": (c_p.placed, c_p.cluster_shape, c_s.M["meta"]),
        "lane": (l_p.placed, len(HS.lane_frontage(l_s, l_p.seat, connector=True))),
        "one": (len(o_s.M["houses"]), len(HS.lane_frontage(o_s, o_p.seat, connector=True))),
    }


@pytest.fixture(scope="module")
def seatings() -> dict[str, tuple]:  # type: ignore[type-arg]
    return rollcache.keyed_to(roll_seatings, roll_seatings, child=f"{HERE_MOD}:roll_seatings")[0]


@pytest.mark.rolls_map
def test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_rows_offer_nothing(seatings: dict[str, tuple]) -> None:  # type: ignore[type-arg]
    """The front row + lane frontage seat every household on all four scripted hamlets, so the
    `cluster_seeds` CLOUD - the fallback behind them - runs on no real map. It got quieter still on
    2026-08-17, when `front_row` began sampling by bundle pitch instead of by household count.

    A fallback nothing exercises is a fallback nobody knows is broken, so drive it directly: with
    both row passes returning no seats, the cloud has to seat the hamlet by itself. This also pins
    the lean-toward-the-field transform (`ly = -wdep + (ly + wdep) * 0.75`), which is the only place
    that compression is applied."""
    placed, cluster_shape, meta = seatings["cloud"]
    assert placed > 0, "with both row passes silent, every farmstead must come from the cloud"
    assert meta["cluster_seeding"] == "cloud"
    # THE INVARIANT IS A TRACE EITHER WAY, not an unconditional stamp (updated 2026-08-19). The
    # declaration is validated against the DRAWN aspect now, so a cloud-seated cluster whose drawing
    # does not match its roll is correctly recorded `cluster_shape_unhonored` instead - which is the
    # whole point of the guard. Asserting the honored key unconditionally would re-assert the very
    # thing the honesty rule exists to deny.
    assert cluster_shape in (meta.get("cluster_shape"), meta.get("cluster_shape_unhonored")), "the cloud must record the rolled shape either as honored or as unhonored"


@pytest.mark.rolls_map
def test_lane_frontage_seats_the_hamlet_when_the_field_row_offers_nothing(seatings: dict[str, tuple]) -> None:  # type: ignore[type-arg]
    """The lane-frontage pass seats the BACK RANK on a real map, but only the households past one
    rank's worth of the band - so on a small hamlet it can place very few, and for part of one day
    (while `front_row` sampled by density with no cap) it placed nothing at all and the cluster came
    out a single rank. Drive it directly, with the field row silent, so the code that puts a door on
    a lane is exercised whatever the cap leaves it."""
    placed, offered = seatings["lane"]
    assert placed > 0, "with the field row silent, the farmsteads must still be seated"
    assert offered, "a linear hamlet must be offered seats along the connector it fronts"


@pytest.mark.rolls_map
def test_the_linear_frontage_pass_stops_once_the_households_are_housed(seatings: dict[str, tuple]) -> None:  # type: ignore[type-arg]
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
    houses, offered = seatings["one"]
    assert houses == 1, "a one-household target gets one farmstead, however much verge is on offer"
    assert offered > 1, "the guard is only under test when more seats were offered than taken"
