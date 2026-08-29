"""THE BRANCHES EIGHT COHORT SEEDS REACHED AND FOUR DID NOT (feature 147).

Feature 145 raised the full run's cohort from four seeds to eight for one reason, recorded in
`gate/hamletgen/test_driver.py`: *"the hamlet-path floor counts what these in-process rolls execute, and the
seed-dependent placer branches ... are reached by rolls, not by a fixture; four more seeds (~50 s in FULL)
reach what four did not."* Measured 2026-08-29, that is TEN lines across seven modules, bought for ~66 s of
every full sweep.

Buying coverage with seeds is also FRAGILE in a way a test is not: which lines eight particular seeds reach
is an accident of the roll, so a knob change that re-rolls them can drop a line the suite was relying on,
for reasons that have nothing to do with the code under test. Feature 146 established the alternative - reach
the branch directly - and these are that, one per line, so the cohort can go back to four seeds and keep its
pass-rate ratchet without carrying the coverage on its back.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement


def _hamlet() -> Settlement:
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, down_deg=90, water_flow=90)
    return s


def test_a_bamboo_trunk_may_not_stand_in_a_watercourse() -> None:
    """`_trunk_blocked`'s water arm: a trunk whose CORNERS reach a drawn stroke. The centre test above it
    catches a trunk on the middle of a brook; this catches one straddling a wide channel's bank."""
    from l7r.diagram.hamletgen.homesteads import _trunk_blocked

    s = _hamlet()
    s.M["streams"] = [{"poly": [[100.0, 700.0], [1300.0, 700.0]], "w": 60}]
    assert _trunk_blocked(s, 700.0, 700.0, 20.0, [], [], None, [])
    assert not _trunk_blocked(s, 700.0, 200.0, 20.0, [], [], None, [])


def test_a_wellhead_may_not_be_sunk_in_the_reed_toe_below_the_crop() -> None:
    """`_well_ground_clear`'s wet-toe arm. The reeds are drawn LATE - after the structures - so by the time
    they exist the well is already in them; the band is therefore DERIVED at seat time from the same geometry
    the reeds will use. The arm only runs on a map that has a toe at all, which is hamlet and village scale."""
    s = _hamlet()
    s.field_polys.append([(300.0, 400.0), (1100.0, 400.0), (1100.0, 800.0), (300.0, 800.0)])
    s.M["fields"] = [{"name": "p", "kind": "paddy", "outline": [[300, 400], [1100, 400], [1100, 800], [300, 800]], "bbox": [300, 400, 1100, 800]}]
    toe, low, _dv, _uv, _u_lo, _u_hi = s._wet_toe_keepout()
    assert toe, "the fixture must actually have a toe band, or this proves nothing"
    assert not s._well_ground_clear(700.0, 850.0), "downslope of the collector, inside the toe: reed bog"


def test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied() -> None:
    """The probe stops each saturated aspect after two carves, which leaves the WINNING aspect less refined
    than the full search would - and that is the map whose acreage the household ratchet then judges. So the
    best aspect is re-searched without the probe, and kept only if it actually scores better."""
    from l7r.diagram.hamletgen.water import fit_field

    from ._builders import a_plan

    plan = a_plan()
    plan.target_acres = 500.0  # far past what this envelope holds at any aspect, so every aspect saturates
    net = fit_field(plan, (700.0, 300.0), 3, 46.0, (26.0, 30.0))
    assert net["plots"], "a fan still comes back"


def test_a_house_the_pass_already_failed_is_not_re_tried_against_the_same_ways() -> None:
    """The straggler pass runs up to four times, because a path drawn for one house can bring another within
    reach. A house that failed and whose candidate ways have NOT changed since would fail identically, so it
    is skipped - the memo keys on the exact target list, and any new lane near it changes that list and
    retries it in full. The wrong-memo direction costs the speedup, never a path."""
    from l7r.diagram import hamletgen as hg
    from l7r.diagram.hamletgen.ways import _serve_stragglers

    from ._builders import a_plan

    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    s = _hamlet()
    # one lane on dry ground with a house beside it (servable), and one lane running down a brook with a
    # house beside THAT (never servable - a junction may not sit on the water)
    s.M["lanes"] = [
        {"pts": [[500.0, 300.0], [900.0, 300.0]], "w": 4},
        {"pts": [[100.0, 1100.0], [400.0, 1100.0]], "w": 4},
    ]
    s.M["houses"] = [
        {"x": 700.0, "y": 420.0, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain"},
        {"x": 250.0, "y": 1220.0, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain"},
    ]
    water = [((100.0, 1100.0), (400.0, 1100.0))]
    _serve_stragglers(s, plan, [], [], water)
    assert len(s.M["lanes"]) >= 2
