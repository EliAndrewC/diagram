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
from l7r.diagram.settlement._knobs import bridge_crossed_waters


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
