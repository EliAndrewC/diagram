"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/fixtures.py`."""

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.structures.fixtures._helpers import kosatsuba_anchor
from tests.settlement._builders import _crop_settlement, _town


def test_place_kosatsuba_reads_road_and_lane_routes_and_skips_degenerate_segments():
    # the placer reads the SAME manifest route fields as the validator (road + lane + lanes);
    # a zero-length segment (duplicate consecutive points) is skipped, not divided by
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["road"] = [[100, 300], [100, 300], [900, 300]]
    s.M["lane"] = [[100, 700], [900, 700]]
    assert s.place_kosatsuba() is not None
    assert len(s.M["kosatsuba"]) == 1


def test_place_punishment_spot_probes_for_a_clear_caption_seat():
    """The display board's caption gets its own probe, because a verge-hugging feature's default
    below-label lands on the frontage it hugs - which is what 'hugging the frontage' means."""
    s = _crop_settlement()
    s.street([(200, 300), (800, 300)], width=10)
    # a shopfront row along the south verge, so the caption's DEFAULT seat below the board is taken
    # and the probe has to walk outward to a clear one
    for _bx in range(210, 800, 30):
        s.building(_bx, 322, 26, 16, "shop")
    # ...and existing CAPTIONS strung along the verge bands, so the probe also has to reject seats
    # that are clear of every building but would bury another label
    for _ly in range(240, 390, 9):
        for _lx in range(210, 820, 55):
            s.label(_lx, _ly, "riverside quarter", 9)
    spot = s.place_punishment_spot()
    assert spot is not None and s.M["punishment_spots"]
    s.place_labels()  # feature 157: the LABEL PHASE draws the queued caption
    cap = next(lb for lb in s.M["labels"] if len(lb) > 5 and lb[5] == "punishment ground")
    # the real property: wherever the probe put it, the caption sits on NO shopfront
    for b in s.M["buildings"]:
        bx0, by0 = b["x"] - b["w"] / 2, b["y"] - b["h"] / 2
        bx1, by1 = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
        assert not (cap[0] < bx1 and bx0 < cap[2] and cap[1] < by1 and by0 < cap[3]), f"caption on {b['kind']} at ({b['x']}, {b['y']})"


def test_place_punishment_spot_skips_a_degenerate_route_segment():
    s = _town()
    s.M["road"] = [[100, 500], [100, 500], [900, 500]]  # a repeated point: zero-length segment
    assert s.place_punishment_spot() is not None


def test_caption_lane_clearance_reads_a_tread_through_the_caption_box():
    """Three verdicts, and only the middle one is reached by a rolled map. A lane VERTEX inside the box
    is the worst case and returns a negative clearance (the tread's own half-width); a lane CROSSING an
    edge without a vertex inside is zero clearance; a lane passing well clear is measured."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.M["lanes"] = [{"pts": [[500, 500], [520, 500]], "w": 4}]  # both vertices inside the box
    assert s.caption_lane_clearance(510, 500, 40.0) == -2.0

    s.M["lanes"] = [{"pts": [[400, 500], [700, 500]], "w": 4}]  # crosses the box, no vertex inside
    assert s.caption_lane_clearance(510, 500, 40.0) == -2.0, "a crossing tread is zero clearance, less its half-width"

    s.M["lanes"] = [{"pts": [[400, 900], [700, 900]], "w": 4}]
    assert s.caption_lane_clearance(510, 500, 40.0) > 100.0, "well clear, and measured"


def test_a_notice_board_with_no_caption_is_sitable_anywhere():
    """`_sitable` ranks a board position by whether its caption could find a seat there. A board with no
    caption to place has nothing to rank, so every position is equally good - the arm no pool map takes,
    because every board on every map is labeled."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.M["lanes"] = [{"pts": [[100, 500], [900, 500]], "w": 4}]
    s.place_kosatsuba(label="")
    assert s.M.get("kosatsuba"), "a board is still placed"


def test_a_notice_board_hemmed_on_every_side_still_gets_its_caption():
    """A board with nowhere clear to put its caption is still placed and still labeled (feature 266, the GM: "we'll
    treat labels as mandatory") - every seat covers a building, and the seat covering the fewest wins."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    for dx in range(-150, 151, 30):
        for dy in range(-150, 151, 30):
            if abs(dx) < 20 and abs(dy) < 20:
                continue  # leave the board's own ground free
            s.M.setdefault("buildings", []).append({"x": 500 + dx, "y": 500 + dy, "w": 38, "h": 38, "rot": 0, "kind": "merchant"})
            s.placed.append((500 + dx, 500 + dy, 38, 38))
    s.kosatsuba(500, 500, label="notice board")
    s.place_labels()  # feature 157: the LABEL PHASE seats and draws it
    seat = [frag for frag in s.toplabels if "notice board" in frag]
    assert len(seat) == 1, "the caption is drawn all the same"
    rec = s.M["labels"][-1]
    assert rec[6] == [494.0, 497.5, 506.0, 502.5], "it records the board it names"


def test_the_board_can_be_sited_on_a_manifest_that_records_runs_but_no_lane_records() -> None:
    """THE LAST-DITCH CANDIDATE SOURCE, and it exists for the frozen fixtures. `place_kosatsuba` reads
    lane RECORDS to get each way's real width - a route carries its own width, and giving them all a
    nominal 8 ft put the board `(8 - w) / 2` too far out. Six hand-built regression manifests carry
    `lane` (singular) and no `lanes` at all, so there is no record to read a width from, and without
    this branch those maps offer the siter not one candidate seat and it returns None.

    The nominal 8 ft here is honest about being a guess: it is only reached when the manifest cannot
    say, and `kosatsuba_by_the_road` still judges the result."""
    s = Settlement(1400, 1000, seed=5)
    s.meta(name="Fixture", scale="hamlet")
    s.M["lane"] = [(200.0, 500.0), (1200.0, 500.0)]
    s.M["lanes"] = []
    s.M["houses"] = [{"x": x, "y": 430.0, "w": 46.0, "h": 28.0, "rot": 0.0} for x in (500.0, 620.0, 740.0, 860.0)]
    spot = s.place_kosatsuba()
    assert spot is not None, "a manifest with runs but no lane records must still seat a board"
    assert s.M["kosatsuba"], "and it is recorded"
    # ...it stands off the tread, on the verge of the one way there is
    x, y = spot
    assert 4.0 < abs(y - 500.0) < 60.0, f"the board should hug the verge, got {abs(y - 500.0):.1f} ft off"


def test_the_connector_is_not_a_main_way_the_web_is_offered_when_no_spine_is_declared() -> None:
    """A hamlet whose web declared no spine left the connector as its only 'main' route (it carries no `web`
    flag), the web lanes were kept out, and Kuwabata found no seat on the connector and shipped with no board
    (2026-09-26). With no main way the whole network is offered, as the frame's re-seat already did."""
    s = Settlement(1400, 1000, seed=5)
    s.meta(name="Fixture", scale="hamlet")
    s.M["lanes"] = [
        {"pts": [(1200.0, 900.0), (1210.0, 990.0)], "w": 5.0, "connector": True},  # a stub out to the road, hemmed in
        {"pts": [(200.0, 500.0), (1100.0, 500.0)], "w": 3.0, "web": True},
    ]
    s.M["houses"] = [{"x": x, "y": 430.0, "w": 46.0, "h": 28.0, "rot": 0.0} for x in (500.0, 620.0, 740.0, 860.0)]
    s.placed.append((1205.0, 945.0, 120.0, 120.0))  # nothing fits beside the connector
    spot = s.place_kosatsuba()
    assert spot is not None, "a hamlet with web lanes and no spine still seats its board"
    assert abs(spot[1] - 500.0) < 60.0, "on the web lane's verge, not the connector's"


def test_a_settlement_is_only_offered_the_board_placements_it_can_site() -> None:
    """THE AFFORDANCE RULE IS THE TYPING RULE. A settlement with no recorded approach cannot put its
    board at one, and one recording no house for its official cannot put it at their gate - so those
    values are not in the rolled pool at all, rather than being rolled and then fudged.

    The two attested placements that are NOT in the value space are asserted here too, because their
    absence is a decision: a bridgehead and a shrine precinct are real sites in the record, withheld
    at these tiers because the pool's "bridges" are 10 ft ditch planks and its only "shrines" are
    household hokora in dooryards."""
    from l7r.diagram.settlement._knobs import KNOBS

    knob = KNOBS["kosatsuba_seat"]
    assert set(knob.value_space) == {"center", "entrance", "frontage"}
    assert "bridgehead" not in knob.value_space and "shrine" not in knob.value_space

    bare = {"has_approach": False, "has_headman_house": False}
    assert knob.allowed(bare) == ["center"], "every settlement can site the assembly ground"
    assert knob.allowed({"has_approach": True, "has_headman_house": False}) == ["center", "entrance"]
    assert knob.allowed({"has_approach": False, "has_headman_house": True}) == ["center", "frontage"]
    assert len(knob.allowed({"has_approach": True, "has_headman_house": True})) == 3


def test_the_board_affordances_are_read_from_the_manifest_the_checks_read() -> None:
    """Same-source doctrine. An approach is a recorded road OR a connector track; an official's gate is
    a house carrying `role == "headman"` - which every pool VILLAGE records exactly once and no hamlet
    records at all, which is why a hamlet is not offered that placement."""
    from l7r.diagram.settlement.structures.fixtures import kosatsuba_affordances

    assert kosatsuba_affordances({}) == {"has_approach": False, "has_headman_house": False}
    assert kosatsuba_affordances({"lanes": [{"pts": [], "connector": True}]})["has_approach"] is True
    assert kosatsuba_affordances({"road": [(0, 0), (10, 10)]})["has_approach"] is True
    assert kosatsuba_affordances({"roads": [{"pts": [(0, 0), (1, 1)]}]})["has_approach"] is True
    assert kosatsuba_affordances({"lanes": [{"pts": [], "connector": False}]})["has_approach"] is False
    houses = [{"x": 1.0, "y": 1.0}, {"x": 2.0, "y": 2.0, "role": "headman"}]
    assert kosatsuba_affordances({"houses": houses})["has_headman_house"] is True
    assert kosatsuba_affordances({"houses": houses[:1]})["has_headman_house"] is False


def test_the_center_placement_is_deliberately_unanchored() -> None:
    """`center` returns NO anchor, and that null case is the point. The settlement center is the
    TRAFFIC objective - "the village center ... or the place where villagers assembled" - which the
    siter already computes by counting dwellings around each seat. A centroid would measure where the
    middle IS rather than where people ARE, and on a crescent or ribbon cluster those differ."""
    from l7r.diagram.settlement.structures.fixtures import kosatsuba_anchor

    M = {"houses": [{"x": 0.0, "y": 0.0}, {"x": 100.0, "y": 0.0}]}
    assert kosatsuba_anchor(M, "center") is None
    assert kosatsuba_anchor({"houses": []}, "entrance") is None, "no dwellings, no settlement to enter"


def test_the_entrance_anchor_is_the_mouth_and_not_the_nearest_point() -> None:
    """THE APPROACH IS WALKED FROM ITS FAR END INWARD. Taking the nearest point on the track instead
    would anchor at the DEEPEST point of its run past the houses - inside the settlement, which is the
    opposite of an entrance. Here the track runs from far away (x=-900) straight through the cluster:
    the mouth is where it first reaches the houses, not where it passes the middle of them."""
    from l7r.diagram.settlement.structures.fixtures import kosatsuba_anchor

    houses = [{"x": float(x), "y": 0.0} for x in (0.0, 60.0, 120.0)]
    track = {"houses": houses, "lanes": [{"connector": True, "pts": [(-900.0, 0.0), (400.0, 0.0)]}]}
    got = kosatsuba_anchor(track, "entrance")
    assert got is not None and got[0] < 60.0, f"the mouth is the near side, got {got}"

    # ...and walked the other way round, the answer is the same end of the settlement it arrives at
    reversed_track = {"houses": houses, "lanes": [{"connector": True, "pts": [(400.0, 0.0), (-900.0, 0.0)]}]}
    assert kosatsuba_anchor(reversed_track, "entrance") == got, "direction of the record must not matter"

    assert kosatsuba_anchor({"houses": houses}, "entrance") is None, "no approach recorded, no mouth"


def test_the_frontage_anchor_is_the_official_s_own_house() -> None:
    """Read, not proxied. An earlier draft approximated it by the largest dwelling; measurement retired
    that - across the 13 pool hamlets the largest and second-largest differ by 1.00 to 1.14x, so it
    would have been arbitrary."""
    from l7r.diagram.settlement.structures.fixtures import kosatsuba_anchor

    houses = [{"x": 10.0, "y": 10.0, "w": 90.0, "h": 90.0}, {"x": 300.0, "y": 40.0, "w": 20.0, "h": 20.0, "role": "headman"}]
    assert kosatsuba_anchor({"houses": houses}, "frontage") == (300.0, 40.0), "the recorded gate, not the biggest roof"
    assert kosatsuba_anchor({"houses": houses[:1]}, "frontage") is None


def test_the_placement_is_seeded_and_reproduces() -> None:
    """FR-002 / SC-004: the same seed yields the same placement, and it draws independently of every
    other knob (`knob_rng` derives its own sub-seed), so adding it perturbs nothing already rolled."""
    from l7r.diagram.settlement._knobs import resolve_knob

    ctx = {"has_approach": True, "has_headman_house": True}
    first = [resolve_knob("kosatsuba_seat", s, ctx, {}) for s in range(40)]
    again = [resolve_knob("kosatsuba_seat", s, ctx, {}) for s in range(40)]
    assert first == again, "a seeded knob reproduces"
    assert len(set(first)) > 1, "and it is a knob, not a constant"
    assert set(first) <= {"center", "entrance", "frontage"}
    # a pinned value overrides the roll, and one the map cannot site is a loud error
    assert resolve_knob("kosatsuba_seat", 3, ctx, {"kosatsuba_seat": "frontage"}) == "frontage"
    with pytest.raises(ValueError, match="typing rule"):
        resolve_knob("kosatsuba_seat", 3, {"has_approach": False, "has_headman_house": False}, {"kosatsuba_seat": "entrance"})


def test_kosatsuba_anchor_walks_the_imperial_road_and_ignores_a_run_too_short_to_walk() -> None:
    """Feature 174: the two unreached statements in the fixtures helpers.

    `M["road"]` is the Imperial road - a town/city key no scripted hamlet records, so the branch that
    adds it to the approach runs had never executed. The `len(run) < 2` skip beside it is the same
    shape: a recorded way with one point is not a walk. Both asserted, plus the case where the road
    IS the run that wins, so the test would fail if the branch simply stopped adding it.
    """
    houses = [{"x": 500.0, "y": 500.0, "role": "headman"}, {"x": 540.0, "y": 500.0}]
    M = {
        "houses": houses,
        "road": [(0.0, 500.0), (1000.0, 500.0)],
        "roads": [{"pts": [(500.0, 0.0)]}],  # a single point: not a walk, and must not raise
    }
    got = kosatsuba_anchor(M, "entrance")
    assert got is not None, "the Imperial road reaches the houses and anchors the board"
    assert abs(got[1] - 500.0) < 1e-6, "the anchor sits on the road's own line"
    assert kosatsuba_anchor({"houses": houses, "roads": [{"pts": [(500.0, 0.0)]}]}, "entrance") is None, "a one-point run alone leaves nothing to walk"


def test_kosatsuba_records_a_blocking_struct():
    # the notice board records its manifest entry at true size (~12x5 ft) and reserves its
    # verge (a later pack must not bury the board)
    s = _town()
    z = s.kosatsuba(500, 500, rot=15)
    kb = s.M["kosatsuba"][0]
    assert (kb["x"], kb["y"], kb["w"], kb["h"], kb["rot"]) == (500, 500, 12, 5, 15) and z > 0
    assert (kb["vw"], kb["vh"]) == (12, 5)  # at 1 ft/px the true frame already clears the marker floor
    assert not s._fits(500, 500, 20, 20)
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading M["labels"]
    rec = s.M["labels"][-1]
    # feature 266: the standard's first position - upper right in the board's own turned frame - at its angle
    assert rec[5] == "notice board" and rec[7] == 15


def test_a_caption_on_a_crown_is_on_the_canopy():
    """Feature 261 (settlement-review of Kuwabata): the caption's drawn quad and its halo, not a disc round its center."""
    from l7r.diagram.settlement.structures.fixtures._helpers import quad_on_canopy

    quad = [(0.0, 0.0), (50.0, 0.0), (50.0, 8.0), (0.0, 8.0)]
    assert quad_on_canopy(quad, lambda x, y, pad: [(25.0, 4.0, 5.0)]), "a crown under the words"
    assert quad_on_canopy(quad, lambda x, y, pad: [(48.0, 14.0, 5.0)]), "a crown the halo reaches at one end"
    assert not quad_on_canopy(quad, lambda x, y, pad: [(25.0, 40.0, 5.0)])


def test_a_board_under_a_canopy_still_takes_a_seat():
    # feature 261: a board whose caption would lie on crowns ranks below one clear of them, and is still offered - a
    # board may stand under trees (the GM, 2026-08-29)
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["road"] = [[100, 300], [900, 300]]
    s.M["tree_crowns"] = [500.0, 300.0, 600.0]
    assert s.place_kosatsuba() is not None


def test_a_board_whose_caption_cannot_fit_is_not_sitable():
    # feature 261: the siter asks the one placer, and a caption the placer can only seat on an obstacle or at a leader's
    # distance does not make the board's seat sitable - the board is still placed (a board is never dropped)
    s = Settlement(400, 400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["road"] = [[20, 200], [380, 200]]
    s.M["houses"] = [{"x": float(x), "y": float(y), "w": 30.0, "h": 30.0, "rot": 0.0} for x in range(40, 380, 34) for y in (170, 230)]
    assert s.place_kosatsuba() is not None


def test_a_hamlet_with_no_houses_or_no_handover_has_no_ways_out():
    # feature 261: the handover needs dwellings, and the routes need a handover
    from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes, kosatsuba_handover

    assert kosatsuba_handover({"lanes": [{"pts": [[0, 0], [100, 0]], "connector": True}]}) is None
    assert kosatsuba_handover({"houses": [{"x": 50.0, "y": 50.0}], "lanes": [{"pts": [[0, 0], [100, 0]], "connector": True}]}) is None, "a connector no lane meets"
    through = {"houses": [{"x": 500.0, "y": 100.0}], "lanes": [{"pts": [[-900, 0], [1900, 0]], "connector": True}, {"pts": [[500, 100], [500, 1]]}, {"pts": [[800, 90], [800, 2]]}]}
    assert kosatsuba_handover(through) == (500.0, 1.0), "a track that runs through hands over at the lane end nearest the houses"
    assert departure_routes({"houses": [{"x": 50.0, "y": 50.0}], "lanes": []}) == []


def test_the_entrance_is_the_last_join_on_the_way_out_and_every_route_walks_to_the_outer_end():
    # feature 261 (settlement-review of Inashiro): a household's lane met the track below its inner end, so the handover is
    # the first point walked in from the outer end that a way meets, and each route runs from the house to the outer end -
    # not up to the handover and back - so a board at the old inner end is missed by that household
    from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes, kosatsuba_handover, outermost_join, routes_missed

    M = {
        "houses": [{"x": 0.0, "y": 0.0}, {"x": 300.0, "y": 0.0}],
        "lanes": [
            {"pts": [[0, 0], [0, 100]]},  # the cluster's lane, meeting the track's inner end
            {"pts": [[300, 0], [300, 250], [0, 250]]},  # a household's own lane, meeting the track lower down
            {"pts": [[0, 100], [0, 400], [0, 2000]], "connector": True},
        ],
    }
    hand = kosatsuba_handover(M)
    assert hand is not None and abs(hand[1] - 250.0) <= 10.0 and hand[0] == 0.0, "the last join, walked in from the edge"
    routes = departure_routes(M)
    assert len(routes) == 2 and all(r[-1][1] >= 1990.0 for r in routes), "every route ends at the outer end"
    assert routes_missed(routes, 0.0, 100.0, 20.0) == 1 and routes_missed(routes, *hand, 20.0) == 0
    assert outermost_join([(0.0, 0.0), (0.0, 50.0)], [[(500.0, 500.0), (600.0, 500.0)]]) is None
