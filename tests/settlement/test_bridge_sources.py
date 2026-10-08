"""What must be bridged, and the one deck that bridges it (feature 166).

Carries `ways_cross_water_on_a_deck` and the shared-source guarantee the bridge family rests on.

FEATURE 020'S LESSON, AND WHY THESE TWO FUNCTIONS EXIST AT ALL. The generator's `bridges()` and the
validator's crossing check used to build their way/water sets SEPARATELY, and both omitted the same three
things - `M["roads"]` (every road but the Imperial one), the river, and a castle's own moat. So they agreed
perfectly and were both wrong: four of six crossings on the first capital were unbridged behind a green
gate. Re-adding the missing keys on both sides would have reproduced the same silent symmetry the next
time a key was added, so the sets are derived ONCE and consumed by both.

That makes this the case showing the skill's "placement and its check must read the SAME manifest source"
rule guarantees AGREEMENT, not CORRECTNESS - which is worth carrying into a feature that is retiring every
check, because it is the argument for testing the SOURCE rather than either consumer.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._knobs import bridge_carried_ways, bridge_crossed_waters


def test_every_kind_of_watercourse_is_offered_for_bridging() -> None:
    """A way crossing a ditch needs a plank exactly as a way crossing a stream needs a bridge. The set
    is what both sides read, so an omission here is invisible on both."""
    M = {
        "streams": [{"poly": [(0, 0), (100, 0)], "w": 9}],
        "channels": [{"poly": [(0, 50), (100, 50)], "w": 4.2}],
        "field_ditches": [{"poly": [(0, 100), (100, 100)], "w": 4.2}],
        "canals": [{"poly": [(0, 150), (100, 150)], "w": 12}],
    }
    waters = bridge_crossed_waters(M)
    assert len(waters) == 4, f"one of the four kinds was dropped: {len(waters)} offered"


def test_an_undrawn_channel_is_not_bridged() -> None:
    """A buried conduit leaves no seam on the ground, so there is nothing to carry a way over. Bridging
    one would draw a plank across bare earth."""
    M = {"channels": [{"poly": [(0, 0), (100, 0)], "w": 4.2, "drawn": False}]}
    assert bridge_crossed_waters(M) == [], "a buried conduit was offered for bridging"

    M["channels"][0]["drawn"] = True
    assert len(bridge_crossed_waters(M)) == 1, "and a drawn one is offered"


def test_a_watercourse_carries_its_own_width_into_the_set() -> None:
    """The span has to reach both banks, so the width travels with the water rather than being guessed
    at the far end. A default is applied where the record omits it."""
    M = {"streams": [{"poly": [(0, 0), (100, 0)], "w": 30}], "channels": [{"poly": [(0, 9), (9, 9)]}]}
    widths = sorted(w for _pts, w in bridge_crossed_waters(M))
    assert 30 in widths, "the stream's own width"
    assert all(w > 0 for w in widths), "and a positive default where the record omitted one"


def test_one_crossing_gets_one_deck() -> None:
    """`ways_cross_water_on_a_deck`, and the defect it was written for. Minami carried two decks over the
    Hayakawa 3 px apart, and three hamlets each carried two footplanks at the SAME point - a way that
    crosses a stream where a channel joins it is ONE bridge on the ground. The dedup lives in `bridge()`
    so every caller is covered: the road pass, the plank pass, and any gen that hand-places a deck."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="Bridgely", scale="hamlet", ftpx=1, down_deg=90)
    s.bridge(500.0, 500.0, 0.0, 40.0, 12.0)
    assert len(s.M["bridges"]) == 1
    s.bridge(502.0, 500.0, 0.0, 40.0, 12.0)  # the same crossing, 2 px away
    assert len(s.M["bridges"]) == 1, "a second deck was drawn over the same crossing"


def test_two_genuinely_distinct_crossings_both_draw() -> None:
    """The tolerance scales with the deck so it cannot swallow a real neighbour: two footplanks a few px
    apart on DIFFERENT waters must both appear. A dedup that ate them would be worse than the doubling."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="Bridgely", scale="hamlet", ftpx=1, down_deg=90)
    s.bridge(500.0, 500.0, 0.0, 40.0, 12.0)
    s.bridge(700.0, 500.0, 0.0, 40.0, 12.0)
    assert len(s.M["bridges"]) == 2


# ---- feature 174: the TOWN/CITY keys of both sources, from plain manifests ------------------------
# Eight of the 89 statements in the 2026-08-31 hamlet-path baseline were these branches. They are
# unreached not because they are wrong but because no scripted generator produces a town or a city
# yet, so no roll carries a `road`, a `ring_road`, a `moat` or an aqueduct. That makes them the exact
# case this file's own docstring argues for: test the SOURCE, with a manifest built by hand, rather
# than wait for a consumer that cannot run. A dict is the whole fixture.


def test_bridge_carried_ways_carries_the_imperial_road_and_every_other_trunk_road() -> None:
    M = {
        "road": [(0.0, 0.0), (100.0, 0.0)],
        "roads": [{"pts": [(0.0, 50.0), (100.0, 50.0)]}, {"pts": [(0.0, 80.0), (100.0, 80.0)], "w": 18}],
    }
    got = bridge_carried_ways(M)
    assert got[0] == ([(0.0, 0.0), (100.0, 0.0)], 30), "the Imperial road takes the 30 ft default"
    assert got[1] == ([(0.0, 50.0), (100.0, 50.0)], 26), "another trunk road takes the 26 ft default"
    assert got[2][1] == 18, "an explicit width wins over the default"
    assert len(got) == 3


def test_bridge_carried_ways_takes_its_widths_from_the_manifest_when_it_states_them() -> None:
    M = {"road": [(0.0, 0.0), (1.0, 0.0)], "road_width": 44, "ring_road": [(0.0, 9.0), (1.0, 9.0)], "ring_road_width": 11}
    assert bridge_carried_ways(M) == [([(0.0, 0.0), (1.0, 0.0)], 44), ([(0.0, 9.0), (1.0, 9.0)], 11)]


def test_bridge_carried_ways_carries_town_streets() -> None:
    """A town street records its own width - there is no default, so the key is read as `st["w"]`."""
    M = {"town_streets": [{"pts": [(0.0, 0.0), (60.0, 0.0)], "w": 20}]}
    assert bridge_carried_ways(M) == [([(0.0, 0.0), (60.0, 0.0)], 20)]


def test_bridge_crossed_waters_counts_a_city_moat_and_an_aqueduct() -> None:
    M = {
        "moat": [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)],
        "aqueducts": [{"poly": [(0.0, 5.0), (10.0, 5.0)]}, {"poly": [(0.0, 6.0), (10.0, 6.0)], "w": 3}],
    }
    got = bridge_crossed_waters(M)
    assert ([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], 22) in got, "the city moat takes the 22 ft default"
    assert ([(0.0, 5.0), (10.0, 5.0)], 8) in got, "an open supply cut is a seam like any channel"
    assert ([(0.0, 6.0), (10.0, 6.0)], 3) in got


def test_bridge_crossed_waters_reads_the_river_by_its_recorded_spelling() -> None:
    """`s.river` records `pts`; the `poly` spelling never occurs in a real manifest but is accepted.

    The comment at that branch says a reader of `poly` alone "is a check that never runs" - so both
    spellings are asserted here, which is the only place either is exercised.
    """
    assert bridge_crossed_waters({"river": {"pts": [(0.0, 0.0), (9.0, 0.0)]}}) == [([(0.0, 0.0), (9.0, 0.0)], 40)]
    assert bridge_crossed_waters({"river": {"poly": [(1.0, 1.0), (2.0, 2.0)], "w": 12}}) == [([(1.0, 1.0), (2.0, 2.0)], 12)]
    assert bridge_crossed_waters({"river": [(0.0, 0.0)]}) == [], "a bare list is not the recorded shape"
    assert bridge_crossed_waters({"river": {}}) == [], "a river with neither spelling contributes nothing"


def test_bridge_crossed_waters_counts_a_castles_own_moat_but_not_a_castle_without_one() -> None:
    M = {"castles": [{"moat": [(0.0, 0.0), (5.0, 0.0)]}, {"moat": [(9.0, 9.0), (9.0, 4.0)], "moat_width": 30}, {}]}
    got = bridge_crossed_waters(M)
    assert got == [([(0.0, 0.0), (5.0, 0.0)], 26), ([(9.0, 9.0), (9.0, 4.0)], 30)], "the moatless castle adds nothing"
