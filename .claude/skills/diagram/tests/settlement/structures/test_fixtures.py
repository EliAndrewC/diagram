"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/fixtures.py`."""

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.structures.fixtures._helpers import first_clear_seat, kosatsuba_anchor
from tests.settlement._builders import _crop_settlement, _town


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
    assert s.M["labels"][-1][1] > 500  # default label sits BELOW the board
    s._labels_pending = True  # the phase above drained; re-open it for the second board
    s.kosatsuba(800, 500, label_above=True)  # gate-adjacent boards label ABOVE (clear of the gate)
    s.place_labels()
    assert s.M["labels"][-1][1] < 500


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


def test_pick_caption_seat_takes_the_nearest_seat_that_clears_the_ways() -> None:
    from l7r.diagram.settlement.structures.fixtures import pick_caption_seat

    seats = [(100.0, 0.0), (20.0, 0.0), (5.0, 0.0)]
    # every seat is legal; the two far ones clear the lane bar, the nearest one does not
    clearance = {(100.0, 0.0): 9.0, (20.0, 0.0): 9.0, (5.0, 0.0): 0.5}
    got = pick_caption_seat(seats, (0.0, 0.0), lambda _q: 1.0, 99.0, lambda q: clearance[q], 2.0)
    assert got == (20.0, 0.0), "nearest of the seats that CLEAR, not nearest overall"


def test_pick_caption_seat_falls_back_to_the_best_clearance_when_nothing_clears() -> None:
    """The board is placed even when its caption is hemmed - `labels_clear_of_other_buildings` reports
    that rather than the siter hiding it - so the fallback arm has to choose, and it chooses the
    roomiest legal seat regardless of distance."""
    from l7r.diagram.settlement.structures.fixtures import pick_caption_seat

    seats = [(5.0, 0.0), (200.0, 0.0)]
    clearance = {(5.0, 0.0): 0.4, (200.0, 0.0): 1.9}
    got = pick_caption_seat(seats, (0.0, 0.0), lambda _q: 1.0, 99.0, lambda q: clearance[q], 2.0)
    assert got == (200.0, 0.0), "nothing clears the 2 ft bar, so the roomiest seat wins on clearance alone"


def test_pick_caption_seat_keeps_every_seat_when_the_hug_cap_would_leave_none() -> None:
    """`_legal ... or _seats`: a caption that hugs nothing within the cap still needs a seat."""
    from l7r.diagram.settlement.structures.fixtures import pick_caption_seat

    seats = [(5.0, 0.0), (9.0, 0.0)]
    got = pick_caption_seat(seats, (0.0, 0.0), lambda _q: 500.0, 10.0, lambda _q: 8.0, 2.0)
    assert got in seats


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
    """A board with nowhere clear to put its caption is still placed and still labeled - the seat falls
    back to the default below (or above, when the caller has said so), and
    `labels_clear_of_other_buildings` reports it rather than the siter hiding the board."""
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
    assert 'y="514"' in seat[0], "on the default seat below the board - the fallback, since nothing cleared"


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


def test_the_caption_fallback_still_prefers_the_board_s_own_side() -> None:
    """THE PATH MOST BOARDS TAKE HAD NO WAY-SIDE TERM AT ALL (settlement-review x3, feature 154).

    `pick_caption_seat` applies `blocked` - "does this seat sit across a way from the board it names" -
    among the seats that clear the lane target. When NO seat clears it, which is the case for every
    board standing close beside a way, it used to fall back to `max(legal, key=box_clearance)` and skip
    the term entirely. Sawada shipped a caption with the full tread between it and its own board three
    reviews running, while the board's own side was measurably clear.

    The degradation is the same as everywhere else in this function: prefer unblocked, and drop the
    term rather than leave the map captionless when nothing is."""
    from l7r.diagram.settlement.structures.fixtures import pick_caption_seat

    near, across, far = (0.0, -10.0), (0.0, 10.0), (0.0, -40.0)
    seats = [across, near, far]
    at = (0.0, -20.0)

    # nothing reaches the lane target, so every seat takes the fallback; `across` clears best
    def _clearance(q):
        return {across: 9.0, near: 3.0, far: 1.0}[q]

    picked = pick_caption_seat(seats, at, lambda _q: 0.0, 100.0, _clearance, 50.0, lambda q: q is across)
    assert picked is near, "the fallback must not take the seat across the way from the board"

    # ...and when EVERY seat is across, the term drops rather than the caption
    every = pick_caption_seat(seats, at, lambda _q: 0.0, 100.0, _clearance, 50.0, lambda _q: True)
    assert every is across, "with nothing unblocked, best clearance wins rather than no caption at all"

    # the satisfied path is unchanged: a seat that clears the target still wins on nearness
    ok = pick_caption_seat(seats, at, lambda _q: 0.0, 100.0, lambda _q: 99.0, 50.0, lambda q: q is across)
    assert ok is near, "nearest among the seats that clear, with the blocked one refused"


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


def test_the_caption_ladders_rung_is_the_same_question_with_a_lower_bar_each_time() -> None:
    """Feature 174, and the doctrine's own remedy (GM 2026-08-28) for a branch no constructed map
    could reach: `first_clear_seat` was lifted out of `_draw_board_caption`, where the identical
    expression appeared FOUR times and the rung that SUCCEEDS at the floor after failing at the
    target sat behind a narrow band of clearance that eight map geometries failed to hit.

    As a lifted function it is three lambdas. All four outcomes are asserted:
      - a seat that passes everything is taken;
      - one over the hug cap is skipped;
      - one that is blocked is skipped;
      - and the FLOOR rung finds a seat the TARGET rung refused, which is the whole point of the
        ladder having a second rung at all.
    """
    seats = [("far", 90.0, False, 30.0), ("blocked", 5.0, True, 30.0), ("middling", 5.0, False, 12.0), ("good", 6.0, False, 30.0)]
    hug = lambda q: q[1]  # noqa: E731 - three one-line probes read better inline than as defs
    blocked = lambda q: q[2]  # noqa: E731
    clearance = lambda q: q[3]  # noqa: E731

    assert first_clear_seat(seats, hug, 20.0, blocked, clearance, 20.0)[0] == "good", "the first seat clearing every bar"
    assert first_clear_seat(seats, hug, 20.0, blocked, clearance, 40.0) is None, "nothing clears an impossible target"

    # THE SECOND RUNG: the same seats, judged at the floor instead of the target. "middling" was
    # refused at 20 and is taken at 10 - "give up the MARGIN, never the 2 ft the rule asks".
    assert first_clear_seat(seats, hug, 20.0, blocked, clearance, 10.0)[0] == "middling", "the floor rung finds what the target refused"
    assert first_clear_seat([], hug, 20.0, blocked, clearance, 1.0) is None, "and no seats at all is no seat"


def test_the_ladders_rung_SHORT_CIRCUITS_in_the_order_the_four_call_sites_relied_on() -> None:
    """The property the lift had to preserve and the test above does not check (found by review):
    the predicates run `hug <= cap`, then `not blocked`, then `clearance >= want`, and each is only
    asked if the one before it passed.

    It matters because `_box_clearance` is the expensive one - it calls `_caption_lines` and walks
    every lane - so a reordering would make the caption search markedly slower on exactly the maps
    that have the most lanes. Counted rather than asserted by outcome, because a reordering gives
    the same ANSWER and only costs time.
    """
    calls: list[str] = []

    def hug(q):
        calls.append(f"hug{q}")
        return 90.0 if q == 0 else 5.0

    def blocked(q):
        calls.append(f"blocked{q}")
        return q == 1

    def clearance(q):
        calls.append(f"clearance{q}")
        return 30.0

    assert first_clear_seat([0, 1, 2], hug, 20.0, blocked, clearance, 20.0) == 2
    assert calls == ["hug0", "hug1", "blocked1", "hug2", "blocked2", "clearance2"], calls
    assert "blocked0" not in calls, "a seat over the hug cap is never asked whether it is blocked"
    assert "clearance1" not in calls, "and a blocked seat is never measured - the expensive probe is last"
